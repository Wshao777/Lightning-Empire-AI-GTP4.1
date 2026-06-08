import os
import json

def restore_hints():
    with open("logs/events.json", "r") as f:
        events = json.load(f)

    deleted = [e["file"] for e in events if e["type"] == "DELETE"]

    index = []
    for f in deleted:
        index.append({
            "file": f,
            "status": "missing",
            "action": "check recycle bin / oneDrive / antivirus quarantine"
        })

    with open("reports/restore_index.json", "w") as f:
        json.dump(index, f, indent=2)

    print("✔ 還原索引建立完成")

if __name__ == "__main__":
    restore_hints()
