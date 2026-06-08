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
