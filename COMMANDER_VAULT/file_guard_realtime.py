import os
import time
import shutil
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

WATCH_DIR = r"D:\Lightning-AI-ALL"
BACKUP_DIR = r"D:\FG_BACKUP"
LOG_FILE = "fg_realtime.log"


def log(msg):
    line = f"[{datetime.now()}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def backup_file(path):
    try:
        if os.path.exists(path):
            rel = os.path.relpath(path, WATCH_DIR)
            backup_path = os.path.join(BACKUP_DIR, rel)
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            shutil.copy2(path, backup_path)
            return backup_path
    except Exception as e:
        log(f"BACKUP ERROR: {e}")
    return None


class GuardHandler(FileSystemEventHandler):

    # 建立 / 修改
    def on_modified(self, event):
        if not event.is_directory:
            backup_file(event.src_path)
            log(f"MODIFIED: {event.src_path}")

    def on_created(self, event):
        if not event.is_directory:
            backup_file(event.src_path)
            log(f"CREATED: {event.src_path}")

    # 刪除（重點）
    def on_deleted(self, event):
        log(f"DELETED DETECTED: {event.src_path}")
        # 嘗試還原
        rel = os.path.relpath(event.src_path, WATCH_DIR)
        backup_path = os.path.join(BACKUP_DIR, rel)

        if os.path.exists(backup_path):
            os.makedirs(os.path.dirname(event.src_path), exist_ok=True)
            shutil.copy2(backup_path, event.src_path)
            log(f"RESTORED: {event.src_path}")


def run():
    os.makedirs(BACKUP_DIR, exist_ok=True)

    event_handler = GuardHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIR, recursive=True)

    observer.start()
    log("FILE GUARD STARTED (REALTIME MODE)")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":
    run()
