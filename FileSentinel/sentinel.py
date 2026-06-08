import os
import json
import time
from hashlib import md5
from datetime import datetime

TARGET_PATH = r"D:\Lightning-AI-ALL"

SNAPSHOT_FILE = "snapshot.json"
DIFF_FILE = "diff_report.json"
RESTORE_INDEX = "restore_index.json"


# ✔ 1. 建立檔案指紋
def file_fingerprint(path):
    try:
        stat = os.stat(path)
        return {
            "path": path,
            "size": stat.st_size,
            "mtime": stat.st_mtime,
            "hash": md5(path.encode()).hexdigest()[:10]
        }
    except:
        return None


# ✔ 2. 掃描全部檔案
def scan_all():
    data = {}

    for root, dirs, files in os.walk(TARGET_PATH):
        for f in files:
            full = os.path.join(root, f)
            fp = file_fingerprint(full)
            if fp:
                data[full] = fp

    return data


# ✔ 3. 存快照
def save_snapshot(data):
    with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ✔ 4. 讀快照
def load_snapshot():
    if not os.path.exists(SNAPSHOT_FILE):
        return {}
    with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ✔ 5. 差異比對
def diff(old, new):
    old_set = set(old.keys())
    new_set = set(new.keys())

    added = list(new_set - old_set)
    removed = list(old_set - new_set)
    unchanged = list(old_set & new_set)

    report = {
        "time": datetime.now().isoformat(),
        "added": added,
        "removed": removed,
        "unchanged_count": len(unchanged)
    }

    with open(DIFF_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    return report


# ✔ 6. 還原索引（找回消失檔案）
def build_restore_index(old, new):
    lost_files = set(old.keys()) - set(new.keys())

    index = []
    for f in lost_files:
        index.append({
            "lost_file": f,
            "status": "missing",
            "hint": "可能被移動 / 同步 / 防毒隔離"
        })

    with open(RESTORE_INDEX, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)


# ✔ 7. 主流程
def run():
    print("📦 開始掃描檔案...")

    old = load_snapshot()
    new = scan_all()

    print(f"✔ 當前檔案數: {len(new)}")

    if old:
        report = diff(old, new)
        build_restore_index(old, new)

        print("⚠ 差異報告已產生")
        print(f"新增: {len(report['added'])}")
        print(f"消失: {len(report['removed'])}")
    else:
        print("📌 首次建立快照")

    save_snapshot(new)
    print("✔ 快照已更新")


# ✔ 8. 秒級監控模式
def watch(interval=3):
    print("👁 進入監控模式...")

    while True:
        run()
        time.sleep(interval)


if __name__ == "__main__":
    run()
    # watch(3)  # 開啟即時監控
