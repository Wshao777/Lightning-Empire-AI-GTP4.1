import json

def analyze():
    with open("logs/events.json", "r") as f:
        events = json.load(f)

    deleted = [e for e in events if e["type"] == "DELETE"]

    report = {
        "deleted_count": len(deleted),
        "files": deleted
    }

    with open("reports/diff.json", "w") as f:
        json.dump(report, f, indent=2)

    print("✔ 分析完成")

if __name__ == "__main__":
    analyze()
