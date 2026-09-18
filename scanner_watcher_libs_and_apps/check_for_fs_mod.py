#!/usr/bin/env python



import   asyncio
import   sys
import   subprocess

from     pathlib                    import Path

from     watchdog.events            import FileSystemEvent, FileSystemEventHandler
from     watchdog.observers.polling import PollingObserver



global   file_written

def send_image_data(sample_image_file, host_dest):

   """
       Routine that will take first image file written to watched
       location, should do some basic parsing on that file to get
       a better idea of what actions to take, and then send data
       being written to host_dest.
   """

   # Sample code to parse path of written DICOM file, so that in turn can be
   # used to get a file pattern that Dimon can use to watch for, and send to
   # AFNI in real-time or near-real-time
   #
   # For GE:
   #
   # >>> file_written = '/home/data0/DICOM/p333/e4444/s55555/i88888888.MRDC.1'

   # delimiter = '/'
   # file_pattern = delimiter.join(sample_image_file.split(delimiter)[:-1]) + delimiter + 'i'

   # For Siemens:
   #
   delimiter = '_'
   file_pattern = delimiter.join(sample_image_file.split(delimiter)[:-1])

   # For GE:
   #
   # for EPI images, Dicom tag 0043,107a gives number of time points, and
   #
   # tags 0019,109C/109E should give the pulse sequence name

   print(f'Launching Dimon on file pattern {file_pattern}')

   global dimon_process
   dimon_process = subprocess.Popen(['Dimon', '-quit', '-rt',
                                     '-host', host_dest,
                                     '-sort_by_num_suffix',
                                     '-infile_prefix', file_pattern],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     text=True)



class _EventHandler(FileSystemEventHandler):

   def __init__(self, queue: asyncio.Queue, loop: asyncio.BaseEventLoop,
                observer: PollingObserver, *args, **kwargs):

      self._loop      = loop
      self._queue     = queue
      self._observer  = observer
      super(*args, **kwargs)

   def on_event(self, event: FileSystemEvent) -> None:

      self._loop.call_soon_threadsafe(self._queue.put_nowait, event)

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
            global file_written
            file_written = str(event.src_path)
            send_image_data(event.src_path, 'localhost')
            self._observer.stop()
         elif Path.is_dir(path_object):
            print(f"Directory {event.src_path} created, continue watching")
         else:
            print(f"Unknown entity {event.src_path} created, continue watching")



async def watch(path: Path, queue: asyncio.Queue, loop: asyncio.BaseEventLoop,
          recursive: bool = False) -> None:

   """Watch a file or directory for changes."""

   observer = PollingObserver()

   handler = _EventHandler(queue, loop, observer)

   observer.schedule(handler, str(path), recursive=recursive)
   observer.start()
   print("Observer started")
   observer.join(None) # Remove value or set to None, to allow to run indefinitely
   loop.call_soon_threadsafe(queue.put_nowait, None)



if __name__ == "__main__":

   if len(sys.argv[1:]) > 0:
      watched_path = sys.argv[1]
   else:
      print("Please specify directory or file to observe")
      sys.exit(-1)

   loop   = asyncio.new_event_loop()
   queue  = asyncio.Queue()

   global file_written
   file_written = ''

   try:
      asyncio.run(watch(Path(watched_path), queue, loop, True))
   except KeyboardInterrupt:
      loop.close()
      print("Exiting ...")
   finally:
      print(f"File written is: {file_written}")
      sys.exit(0)

