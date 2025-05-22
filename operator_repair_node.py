import os
import shutil
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from capsule_auditor import scan_and_repair_capsules

WATCH_DIR = "/mnt/data"
BACKUP_DIR = "repair_backups"

class CapsuleEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith((".zip", ".camp")):
            os.makedirs(BACKUP_DIR, exist_ok=True)
            dest = os.path.join(BACKUP_DIR, os.path.basename(event.src_path))
            try:
                shutil.copy2(event.src_path, dest)
                print(f"Backed up {event.src_path} to {dest}")
            except Exception as e:
                print(f"Failed to back up {event.src_path}: {e}")
            try:
                scan_and_repair_capsules(base_dir=WATCH_DIR)
            except Exception as e:
                print(f"Error repairing capsules: {e}")


def main():
    observer = Observer()
    event_handler = CapsuleEventHandler()
    observer.schedule(event_handler, WATCH_DIR, recursive=False)
    observer.start()
    print(f"Watching {WATCH_DIR} for new capsules...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
