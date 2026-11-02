import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from automations.engine import run_steps


class Handler(FileSystemEventHandler):

    def __init__(self, ext, steps):
        self.ext = ext
        self.steps = steps

    def on_created(self, event):

        if event.src_path.lower().endswith(self.ext):
            print("📂 Nuevo archivo detectado:", event.src_path)
            run_steps(self.steps)


def watch(folder, ext, steps):

    handler = Handler(ext, steps)

    observer = Observer()
    observer.schedule(handler, folder, recursive=False)
    observer.start()


def start_watchdog():
    pass
