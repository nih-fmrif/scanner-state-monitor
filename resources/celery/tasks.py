from celery import Celery
from scan_watcher import Watcher, ScannerFileHandler
import os

app = Celery('tasks')
app.config_from_object('celeryconfig')

@app.task
def watcher(fname):
    path = os.path.dirname(fname)
    scan_handler = ScannerFileHandler(fname)
    w = Watcher()
    w.run(scan_handler, path)


