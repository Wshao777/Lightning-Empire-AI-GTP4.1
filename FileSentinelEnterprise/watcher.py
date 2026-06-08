import time
import os
import json
from datetime import datetime

TARGET = r"D:\Lightning-AI-ALL"
LOG_FILE = "logs/events.json"

os.makedirs("logs", exist_ok=True)


def scan():
    files = {}
    for root, dirs, fs in os.walk(TARGET):
        for f in fs:
            path = os.path.join(root, f)
            try:
                stat = os.stat(path)
                files[path] = stat.st_mtime
            except:
                continue
    return files


def load_last():
    try:
        with open("snapshots/latest.json", "r") as f:
            return json.load(f)
    except:
        return {}


def save_snapshot(data):
    with open("snapshots/latest.json", "w") as f:
        json.dump(data, f, indent=2)


def log_event(event):
    log = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            log = json.load(f)

    log.append(event)

    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


def run():
    print("🛡️ File Sentinel Enterprise 啟動")

    old = load_last()

    while True:
        new = scan()

        old_set = set(old.keys())
        new_set = set(new.keys())

        deleted = old_set - new_set
        added = new_set - old_set

        # ✔ 記錄刪除
        for d in deleted:
            log_event({
                "type": "DELETE",
                "file": d,
                "time": str(datetime.now())
            })
            print("⚠ 刪除:", d)

        # ✔ 記錄新增
        for a in added:
            log_event({
                "type": "ADD",
                "file": a,
                "time": str(datetime.now())
            })

        save_snapshot(new)
        old = new

        time.sleep(2)


if __name__ == "__main__":
    run()
