import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from workflows.engine import run_workflow
from jobs.manager import manager
from events.bus import bus


class FolderHandler(FileSystemEventHandler):

    def __init__(self, path, workflow_name):
        self.path = path
        self.workflow_name = workflow_name

    def on_created(self, event):

     if event.is_directory:
        return

     asyncio.create_task(
        bus.publish("filesystem.created", {
            "path": event.src_path
        })
    )


class Watcher:

    def __init__(self):
        self.observer = Observer()
        self.active = []

    def watch(self, path, workflow_name):

        handler = FolderHandler(path, workflow_name)

        self.observer.schedule(handler, path, recursive=False)
        self.active.append((path, workflow_name))

    def start(self):
        self.observer.start()


watcher = Watcher()