
import os, sys
import asyncio
import socket
import datetime
import logging
import subprocess

sys.path.insert(0, os.path.abspath('.'))
import common


state_poll_interval = 0.5   # in seconds
logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%Y_%m_%d %H:%M:%S :',
                    level=logging.WARNING)
scan_event_logger   = logging.getLogger(__name__)



# create a few global variables to help with scanner state tracking
global patient_in_scanner, afni_running, pid_afni, data_being_acquired, pid_dimon



async def poll_state(polling_interval, host = '127.0.0.1', port = 5555):

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

      scan_event_logger.info('Scanner: ' + data['scanner AE Title']
            + " from vendor: " + data['scanner vendor'] + " has events: "
            + str(data['all_events']) + ' detected at '
            + datetime.datetime.now().strftime("%Y_%m_%d_%H:%M:%S") + '\n')

      process_current_state (data)  # Pass along request response as json, and
                                    # process appropriately in calling function.



def process_current_state(state_to_process):

   scanner_events_dict = state_to_process['all_events']

   global patient_in_scanner, afni_running, data_being_acquired, pid_afni

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
      os.chdir(dir_afni)
      pid_afni     = subprocess.Popen(['afni', '-rt'],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       text=False)

   if (afni_running and not patient_in_scanner):
      afni_running = False
      scan_event_logger.info("Should stop AFNI now")
      pid_afni.terminate()

   if (afni_running    and     (scanner_events_dict['Pulse sequence prepped'] >
                                scanner_events_dict['Scanner is done acquiring data'])):
      data_being_acquired = True

   if (data_being_acquired and (scanner_events_dict['Pulse sequence prepped'] <
                                scanner_events_dict['Scanner is done acquiring data'])):
      data_being_acquired = False

   scan_event_logger.warning(f"patient_in_scanner = {patient_in_scanner}, afni_running = {afni_running}, data_being_acquired = {data_being_acquired}")

   return



if __name__ == "__main__":

   # Check for all needed environment variables first!

   environment_vars = ['MRI_SCANNER_INFO_PUBLISH_TO_HOST',
                       'MRI_SCANNER_INFO_PUBLISH_TO_PORT',
                       'MRI_SCANNER_DATA_DIR_DICOM',
                       'MRI_SCANNER_DATA_DIR_AFNI']

   common.routines.check_env_vars(environment_vars)

   # If all necessary environment variables have been defined, proceed with program
   # execution.

   global patient_in_scanner
   patient_in_scanner = False
   global afni_running
   afni_running = False
   global data_being_acquired
   data_being_acquired = False

   loop = asyncio.get_event_loop()

   try:
      asyncio.ensure_future(poll_state(state_poll_interval,
                                       host=os.environ['MRI_SCANNER_INFO_PUBLISH_TO_HOST'],
                                       port=os.environ['MRI_SCANNER_INFO_PUBLISH_TO_PORT']))
      loop.run_forever()
   except KeyboardInterrupt:
      pass
   finally:
      print("Stopping task.")
      loop.close()

