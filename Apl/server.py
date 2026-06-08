#KEY_SCOPES = {
    "KEY_DEV_MASTER": [
        "config.read",
        "config.write"
    ],

    "KEY_BOT_DISPATCH": [
        "task.create",
        "queue.manage"
    ],

    "KEY_BOT_MONITOR": [
        "metrics.read",
        "logs.read"
    ],

    "KEY_PROD_MASTER": [
        "*"
    ]
}
from fastapi.responses import FileResponse

@app.get("/")
def home():
    return FileResponse("web/index.html")

@app.get("/dashboard")
def dashboard():
    return FileResponse("web/dashboard.html")
# 模拟数据（实际可从你的节点管理器、数据库获取）
@app.get("/api/status")
def system_status():
    # 示例：从全局节点管理器读取
    nodes = [
        {"id": "termux-1", "status": "online", "cpu": 12, "ram": 45, "last_heartbeat": "2026-06-08T10:23:00"},
        {"id": "x86-master", "status": "online", "cpu": 28, "ram": 52, "last_heartbeat": "2026-06-08T10:24:00"},
        {"id": "termux-2", "status": "offline", "cpu": 0, "ram": 0, "last_heartbeat": "2026-06-07T23:10:00"},
    ]
    online = sum(1 for n in nodes if n["status"] == "online")
    return {
        "total_nodes": len(nodes),
        "online_nodes": online,
        "pending_tasks": 5,
        "avg_cpu": round(sum(n["cpu"] for n in nodes if n["status"]=="online") / max(online,1), 1),
        "avg_ram": round(sum(n["ram"] for n in nodes if n["status"]=="online") / max(online,1), 1),
        "nodes": nodes
    }

@app.get("/api/tasks")
def task_list():
    return [
        {"id": "t1", "node_id": "termux-1", "command": "python3 /tmp/script.py", "status": "running"},
        {"id": "t2", "node_id": "x86-master", "command": "rotate_keys", "status": "pending"},
    ]
