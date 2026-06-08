import os
import hashlib
import json
import time
from datetime import datetime

WATCH_DIR = r"D:\Lightning-AI-ALL"
SNAPSHOT_FILE = "snapshot.json"
LOG_FILE = "fileguard_log.txt"


# ===== HASH =====
def get_hash(file_path):
    sha = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha.update(chunk)
        return sha.hexdigest()
    except:
        return None


# ===== 掃描 =====
def scan_files():
    file_map = {}

    for root, _, files in os.walk(WATCH_DIR):
        for f in files:
            path = os.path.join(root, f)
            h = get_hash(path)
            if h:
                file_map[path] = h

    return file_map


# ===== 存快照 =====
def save_snapshot(data):
    with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ===== 讀快照 =====
def load_snapshot():
    if not os.path.exists(SNAPSHOT_FILE):
        return {}
    with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ===== 比對 =====
def diff(old, new):
    deleted = [k for k in old if k not in new]
    added = [k for k in new if k not in old]
    modified = [k for k in new if k in old and old[k] != new[k]]

    return deleted, added, modified


# ===== log =====
def log(msg):
    line = f"[{datetime.now()}] {msg}\n"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)


# ===== 主流程 =====
def run():
    log("掃描開始")

    old = load_snapshot()
    new = scan_files()

    deleted, added, modified = diff(old, new)

    log(f"刪除: {len(deleted)}")
    log(f"新增: {len(added)}")
    log(f"修改: {len(modified)}")

    if deleted:
        log("⚠ 刪除檔案清單:")
        for d in deleted:
            log(f" - {d}")

    save_snapshot(new)

    log("掃描完成")


if __name__ == "__main__":
    while True:
        run()
        time.sleep(5)   # 秒級監控
