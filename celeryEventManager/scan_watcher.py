import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


class ScannerFileHandler(PatternMatchingEventHandler):

    def __init__(self, fname):
        super(ScannerFileHandler, self).__init__(patterns=[fname], ignore_directories=True)

    def on_created(self, event):
        print("created")

    def on_deleted(self, event):
        print("deleted")

    def on_modified(self, event):
        print("modified")

    def on_moved(self, event):
        print("moved")

    def on_any_event(self, event):
        print("generic")


class Watcher:

    def __init__(self):
        self.observer = Observer()

    def run(self, event_handler, path):

        self.observer.schedule(event_handler, path, recursive=False)
        self.observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
            print("Watcher Stopped")

        self.observer.join()
