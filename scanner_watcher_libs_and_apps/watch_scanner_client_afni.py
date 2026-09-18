
import   os, sys
import   asyncio
import   socket
import   datetime
import   logging
import   subprocess
import   signal

sys.path.insert(0, os.path.abspath('.'))
import   Shared

from     pathlib                    import Path

from     watchdog.events            import FileSystemEvent, FileSystemEventHandler
from     watchdog.observers.polling import PollingObserver

import   pydicom



state_poll_interval = 0.5   # in seconds
logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%Y_%m_%d %H:%M:%S :',
                    level=logging.WARNING)
scan_event_logger   = logging.getLogger(__name__)



# create a few global variables to help with scanner state tracking
global patient_in_scanner, afni_running, pid_afni, data_being_acquired, pid_dimon
global last_data_dir_dicom, scanner_vendor



async def poll_state(polling_interval, host = '127.0.0.1', port = 5555):

   global last_data_dir_dicom

   while True:

      current_state_dict  = {}

      await asyncio.sleep(polling_interval)

      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as watched_socket:

         watched_socket.connect ((host, int(port)))

         socket_data = watched_socket.recv(1 * 1024 * 1024)

      # Convert published JSON struct to Python dictionary
      data = eval(socket_data.decode('utf-8'))  # should find a way to use
                                                # ast.literal_eval() to do this
      # Extract desired information from packet
      current_state_dict = data['all_events']

      global scanner_vendor
      scanner_vendor = data['scanner vendor']

      scan_event_logger.info('Scanner: ' + data['scanner AE Title']
            + " from vendor: " + data['scanner vendor'] + " has events: "
            + str(data['all_events']) + ' detected at '
            + datetime.datetime.now().strftime("%Y_%m_%d_%H:%M:%S") + '\n')

      await process_current_state (data)  # Pass along request response as json, and
                                          # process appropriately in calling function.



async def process_current_state(state_to_process):

   scanner_events_dict = state_to_process['all_events']

   global patient_in_scanner, afni_running, data_being_acquired, afni_process
   global last_data_dir_dicom

   last_data_dir_dicom = scanner_events_dict['session image data directory']

   if ((scanner_events_dict['End scanning session'] <
        scanner_events_dict['Start scanning session']) and not patient_in_scanner):
      patient_in_scanner = True

   if ((scanner_events_dict['End scanning session'] >
        scanner_events_dict['Start scanning session']) and patient_in_scanner):
      patient_in_scanner = False

   if (patient_in_scanner and not afni_running):
      afni_running = True
      scan_event_logger.info("Should start AFNI now")
      dir_afni     = f'{os.path.join(os.environ['MRI_SCANNER_DATA_DIR_AFNI'],
                                     datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))}'
      os.makedirs(dir_afni, exist_ok=True)
      os.chmod(dir_afni, 0o5777) # When creating directory, allow users to interact with
                                 # data being written there, but not allow to delete them.
      os.chdir(dir_afni)
      afni_process = subprocess.Popen(['afni', '-rt'],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       text=False)

      scan_event_logger.warning(f"Starting AFNI in directory: {dir_afni}")

   if (afni_running and not patient_in_scanner):
      afni_running = False
      scan_event_logger.info("Should stop AFNI now")
      # Process ID returned by sub-process seems to be for the shell which
      # spawns the actual AFNI process, so use the following to get PID of
      # the acutal running AFNI real-time process.
      afni_process_stop = subprocess.run("ps -ef | grep 'afni -rt' | grep -v grep | tr -s ' ' | cut -d ' ' -f2 -",
                                         shell=True, text=True,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
      os.kill(int(afni_process_stop.stdout), signal.SIGTERM)

   if (afni_running    and     (scanner_events_dict['Pulse sequence prepped'] >
                                scanner_events_dict['Scanner is done acquiring data'])):
      if (data_being_acquired is False):
         await watch(Path(last_data_dir_dicom), True)

      data_being_acquired = True

   if (data_being_acquired and (scanner_events_dict['Pulse sequence prepped'] <
                                scanner_events_dict['Scanner is done acquiring data'])):
      data_being_acquired = False

   scan_event_logger.debug(f"patient_in_scanner = {patient_in_scanner}, afni_running = {afni_running}, data_being_acquired = {data_being_acquired}, current_data_dir_dicom = {last_data_dir_dicom}")

   return



class _EventHandler(FileSystemEventHandler):

   def __init__(self, observer: PollingObserver, *args, **kwargs):

      self._observer  = observer
      super(*args, **kwargs)

   def on_event(self, event: FileSystemEvent) -> None:

      print ("Path: %50s has event: %s" % (event.src_path, event.event_type))

   def on_modified(self, event: FileSystemEvent) -> None:

      self.on_event(event)

   def on_deleted(self, event: FileSystemEvent) -> None:

      self.on_event(event)

   def on_moved(self, event: FileSystemEvent) -> None:

      self.on_event(event)

   def on_created(self, event: FileSystemEvent) -> None:

      self.on_event(event)

      if (event.event_type == "created"):
         path_object = Path(event.src_path)
         if Path.is_file(path_object):
            send_image_data(event.src_path, 'localhost')
            self._observer.stop()
         elif Path.is_dir(path_object):
            scan_event_logger.debug(f"Directory {event.src_path} created, continue watching")
         else:
            scan_event_logger.debug(f"Unknown entity {event.src_path} created, continue watching")



async def watch(path: Path, recursive: bool = False) -> None:

   """Watch a file or directory for changes."""

   observer = PollingObserver()

   handler = _EventHandler(observer)

   observer.schedule(handler, str(path), recursive=recursive)
   observer.start()
   print("Watching for new data being written to disk ...")
   # observer.join(None) # Remove value or set to None, to allow to run indefinitely



def send_image_data(sample_image_file, host_dest):

   """
       Routine that will take first image file written to watched
       location, should do some basic parsing on that file to get
       a better idea of what actions to take, and then send data
       being written to host_dest.
   """

   global scanner_vendor

   delimiter_path  = '/'
   file_pattern    = delimiter_path.join(sample_image_file.split(delimiter_path)[:-1]) + delimiter_path + '*.dcm'
   sort_method     = '-dicom_org'
   drive_afni_opts = ''
   host_afni       = host_dest

   scan_event_logger.debug(f'Working on data from vendor {scanner_vendor} ...')

   if (scanner_vendor == 'GE'):

      file_pattern    = delimiter_path.join(sample_image_file.split(delimiter_path)[:-1] + ['i'])

      tag_values      = pydicom.dcmread(sample_image_file)
      sequence_name   = tag_values.get((0x0019, 0x109c), "Unknown")

      sort_method     = '-sort_by_num_suffix'
      file_pattern    = delimiter_path.join(['/export', 'home1', 'sdc_image_pool', 'images'] +
                                            file_pattern.split(delimiter_path)[-4:])

      print(f"Sequence name is: {sequence_name.value.lower()}")

      # SSH is being used to run Dimon back on the scanner console, as over NFS, image write
      # performance doesn't seem to be sufficient to allow Dimon to detect, read, and send
      # image data reliably to AFNI.  So run Dimon in way that is reads images 'locally' and
      # from there, will send to AFNI ...
      host_afni       = 'afnipc'
      dimon_cmd       = ['ssh', 'sdc@mrconsole', 'Dimon', '-quit', '-rt', '-host', host_afni,
                         sort_method, '-infile_prefix', file_pattern]

      if ('epi' in sequence_name.value.lower()):
         num_time_pts = tag_values.get((0x0020, 0x0105), "1")
         dimon_cmd   += ['-rt_cmd', f'"GRAPH_XRANGE {str(num_time_pts.value)}"']

   elif (scanner_vendor == 'Siemens'):

      delimiter       = '_'
      file_pattern    = delimiter.join(sample_image_file.split(delimiter)[:-1])

      # there should be at least 1 image written per series
      tag_values      = pydicom.dcmread(file_pattern + "_000001.dcm")
      sequence_name   = tag_values.get((0x0018, 0x0024), "Unknown")
      series_dscrpt   = tag_values.get((0x0008, 0x103e), "Unknown")

      print(f"Sequence name is: {sequence_name.value.lower()}")

      dimon_cmd     = ['Dimon', '-quit', '-rt', '-host', host_afni,
                        sort_method, '-infile_prefix', file_pattern]

      # Need to verify that 'ep' and '2d' in pulse sequence name is sufficient
      # to capture used EPI pulse sequences (from which real-time data would
      # be wanted), but verified that the below would work for Siemens product
      # and CMRR EPI sequences. No action taken yet - just verifying that this
      # state can be captured.
      if (('ep' in sequence_name.value.lower()) and
          ('2d' in sequence_name.value.lower())):
         scan_event_logger.warning ("Acquiring data from an EPI-based sequence")
         # fixing a number of time points for now, till I can figure out how
         # to get number of time points from header of EPI data.
         dimon_cmd   += ['-nt', '300']
      # Also handle MP-RAGE as that's of interest for real-time applications
      elif (('tfl'  in sequence_name.value.lower()) and
            ('3d'   in sequence_name.value.lower()) and
            ('mp'   in series_dscrpt.value.lower()) and
            ('rage' in series_dscrpt.value.lower())):
         scan_event_logger.warning ("Acquiring data from a 3D-FLASH sequence")

         # Without anything else - should 'just run' default dimon_cmd array
         # set above for this vendor

      # Otherwise, if other data are collected and needed, tell user how to
      # send to AFNI, but ignore by default for the time-being.
      else:
         print(f"Not sending data from this series to AFNI.  If AFNI data from this series are needed, run command: {
                 ' '.join(dimon_cmd)}")
         # And 'nullify' Dimon command, to not take any action here.
         dimon_cmd = ['echo']
   else:

      scan_event_logger.debug(f'Vendor {scanner_vendor} unsupported - not sending data ...')
      return

   if (dimon_cmd != ['echo']):
      scan_event_logger.warning(f'Launching Dimon on file pattern {file_pattern}')

   dimon_process = subprocess.Popen(dimon_cmd,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True)

   # stdout, stderr = dimon_process.communicate()



async def gather_and_run_client_tasks():

   # Check for all needed environment variables first!

   environment_vars = ['MRI_SCANNER_INFO_PUBLISH_TO_HOST',
                       'MRI_SCANNER_INFO_PUBLISH_TO_PORT',
                       'MRI_SCANNER_DATA_DIR_DICOM',
                       'MRI_SCANNER_DATA_DIR_AFNI']

   Shared.routines.check_env_vars(environment_vars)

   # If all necessary environment variables have been defined, proceed with program
   # execution.

   global patient_in_scanner
   patient_in_scanner = False
   global afni_running
   afni_running = False
   global data_being_acquired
   data_being_acquired = False
   global last_data_dir_dicom
   last_data_dir_dicom = os.environ['MRI_SCANNER_DATA_DIR_DICOM']

   await(poll_state(state_poll_interval, host=os.environ['MRI_SCANNER_INFO_PUBLISH_TO_HOST'],
                                         port=os.environ['MRI_SCANNER_INFO_PUBLISH_TO_PORT']))



if __name__ == "__main__":

   try:
      asyncio.run(gather_and_run_client_tasks())

   except KeyboardInterrupt:
      print("Stopping task.")
      exit(0)

