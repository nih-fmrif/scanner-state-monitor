#!/usr/bin/env python

# Code based on aiowatch, from:
#
#    https://gist.github.com/mivade/f4cb26c282d421a62e8b9a341c7c65f6
#
# and integrated with example code from:
#
#    https://levelup.gitconnected.com/how-to-monitor-file-system-events-in-python-e8e0ed6ec2c



import   asyncio

import   time, os, re, sys

from     pathlib                    import Path
from     typing                     import Optional

from     watchdog.events            import FileSystemEvent, FileSystemEventHandler, LoggingEventHandler, PatternMatchingEventHandler
from     watchdog.observers         import Observer
from     watchdog.observers.polling import PollingObserver

sys.path.insert(0, os.path.abspath('.'))
import   Siemens
import   GE



class _EventHandler(FileSystemEventHandler):

   def __init__(self, queue: asyncio.Queue, loop: asyncio.BaseEventLoop,
                *args, **kwargs):
      self._loop = loop
      self._queue = queue
      super(*args, **kwargs)

      self.scanner_event_detector = Siemens.handler.event_catcher()
      # self.scanner_event_detector = GE.handler.event_catcher()

   def on_created(self, event: FileSystemEvent) -> None:
      self._loop.call_soon_threadsafe(self._queue.put_nowait, event)
      print("on_created", event.src_path)

   def on_any_event(self, event: FileSystemEvent) -> None:
      self._loop.call_soon_threadsafe(self._queue.put_nowait, event)
      print(event.event_type, event.src_path)

   def on_deleted(self, event: FileSystemEvent) -> None:
      self._loop.call_soon_threadsafe(self._queue.put_nowait, event)
      print("on_deleted", event.src_path)

   def on_modified(self, event: FileSystemEvent) -> None:
      self._loop.call_soon_threadsafe(self._queue.put_nowait, event)
      print("on_modified", event.src_path)

      log_lines = self.scanner_event_detector.process_scanner_logs(os.getenv('MRI_SCANNER_LOG_DIR'), log_file_read_mode='r')    # Siemens
      # log_lines = self.scanner_event_detector.process_scanner_logs(os.getenv('MRI_SCANNER_LOG_DIR'), log_file_read_mode='rb')   # GE

      scanner_log_events_and_times = []
      scanner_log_events_and_times = self.scanner_event_detector.sort_dict(self.scanner_event_detector.generate_dict_of_scanner_events(log_lines))
      for event in scanner_log_events_and_times:

         print ("Event %36s happened at %s" % (event[0], event[1]))

   def on_moved(self, event: FileSystemEvent) -> None:
      self._loop.call_soon_threadsafe(self._queue.put_nowait, event)
      print("on_moved", event.src_path)



class EventIterator(object):

   def __init__(self, queue: asyncio.Queue,
                loop: Optional[asyncio.BaseEventLoop] = None):
       self.queue = queue

   def __aiter__(self):
      return self

   async def __anext__(self):
      item = await self.queue.get()

      if item is None:
         raise StopAsyncIteration

      return item



def watch(path: Path, queue: asyncio.Queue, loop: asyncio.BaseEventLoop,
          recursive: bool = False) -> None:

   """Watch a directory for changes."""

   handler = _EventHandler(queue, loop)
   # handler = LoggingEventHandler(queue, loop)

   # observer = Observer()
   observer = PollingObserver()
   observer.schedule(handler, str(path), recursive=True)
   observer.start()
   print("Observer started")
   observer.join(None) # Remove value or set to None, to allow to run indefinitely
   loop.call_soon_threadsafe(queue.put_nowait, None)



async def consume(queue: asyncio.Queue) -> None:

   async for event in EventIterator(queue):
      print("Got an event!", event)



if __name__ == "__main__":

   # reading logging location from environment from account running this.
   try:
      os.environ['MRI_SCANNER_LOG_DIR']
      scanner_log_dir = os.getenv('MRI_SCANNER_LOG_DIR') + '/' + 'MrMeas_container.log'   # Siemens
      # scanner_log_dir = os.getenv('MRI_SCANNER_LOG_DIR') + '/' + 'scn.out'                # GE
   except:
      print ('\n   !!! Please define the environment variable MRI_SCANNER_LOG_DIR !!!\n')
      sys.exit(1)

   loop = asyncio.get_event_loop()
   queue = asyncio.Queue(loop=loop)

   futures = [
      loop.run_in_executor(None, watch, Path(scanner_log_dir), queue, loop, False),
      consume(queue),
   ]

   loop.run_until_complete(asyncio.gather(*futures))

