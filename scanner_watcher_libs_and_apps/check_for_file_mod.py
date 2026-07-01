#!/usr/bin/env python



import   asyncio
import   os, sys
import   subprocess
import   datetime

from     pathlib                    import Path

from     watchdog.events            import FileSystemEvent, FileSystemEventHandler
from     watchdog.observers.polling import PollingObserver



class _EventHandler(FileSystemEventHandler):

   def __init__(self, queue: asyncio.Queue, loop: asyncio.BaseEventLoop,
                *args, **kwargs):

      self._loop = loop
      self._queue = queue
      super(*args, **kwargs)

   # remove all separate def - filesystem events, i.e. "on_modified",
   # "on_deleted", "on_created", "on_moved" - as all we are concerned
   # with catching are *ANY* log changes, except for "on_deleted" -
   # which might be a little harder to deal with ... ;-)

   def on_any_event(self, event: FileSystemEvent) -> None:

      self._loop.call_soon_threadsafe(self._queue.put_nowait, event)
      print(event.event_type, event.src_path)

      if ((event.event_type == "modified") or (event.event_type == "created") or (event.event_type == "moved")):
         print ("File: %36s has event: %s" % (os.environ['MRI_SCANNER_RAW_POOL'], event.event_type))

      if (event.event_type == "modified"):
         header_reader_bin = os.environ['MRI_SCANNER_RAW_HEADER_READER']
         header_pool_file  = os.environ['MRI_SCANNER_RAW_POOL']
         command_to_run    = [header_reader_bin, '-verbose', header_pool_file]
         dest_file         = open ('/tmp/active_header_' + datetime.datetime.now().strftime("%Y%m%d_%H%M%S"), 'w+')
         read_pool_process = subprocess.Popen(
                                 command_to_run,
                                 stdout=dest_file,
                                 stderr=subprocess.PIPE,
                                 text=True   )

         stdout, stderr    = read_pool_process.communicate()
         dest_file.close()



def watch(path: Path, queue: asyncio.Queue, loop: asyncio.BaseEventLoop,
          recursive: bool = False) -> None:

   """Watch a file or directory for changes."""

   handler = _EventHandler(queue, loop)

   observer = PollingObserver()
   observer.schedule(handler, str(path), recursive=recursive)
   observer.start()
   print("Observer started")
   observer.join(None) # Remove value or set to None, to allow to run indefinitely
   loop.call_soon_threadsafe(queue.put_nowait, None)



if __name__ == "__main__":

   # reading logging location from environment from account running this.
   try:
      os.environ['MRI_SCANNER_RAW_POOL']
   except:
      print ('\n   !!! Please define the environment variable MRI_SCANNER_RAW_POOL !!!\n')
      sys.exit(1)

   loop = asyncio.get_event_loop()
   queue = asyncio.Queue()

   asyncio.run(watch(Path(os.getenv('MRI_SCANNER_RAW_POOL')), queue, loop, False))

