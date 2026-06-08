#opt/ai_protector/server.py
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
import os
from datetime import datetime
import hashlib

app = FastAPI()

# 数据目录
RECEIPTS_DIR = "receipts"
os.makedirs(RECEIPTS_DIR, exist_ok=True)

# 模拟资金数据存储
def load_receipts():
    receipts = []
    for f in os.listdir(RECEIPTS_DIR):
        if f.endswith(".json"):
            with open(os.path.join(RECEIPTS_DIR, f)) as fp:
                receipts.append(json.load(fp))
    return receipts

def save_receipt(data):
    filename = f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(os.path.join(RECEIPTS_DIR, filename), "w") as f:
        json.dump(data, f, indent=2)
    return filename

@app.get("/api/funds/total")
def total_locked():
    # 累加所有 receipts 中的 amount
    total = sum(r.get("amount", 0) for r in load_receipts())
    return {"total": total}

@app.get("/api/funds/pending")
def pending():
    # 这里简化：未分润的标记为 pending_amount>0 且 distributed=false
    pending_list = [r for r in load_receipts() if not r.get("distributed", False)]
    return {"pending": [{"from": r["from"], "amount": r["amount"]} for r in pending_list]}

@app.get("/api/funds/history")
def history():
    # 已分润的记录
    history_list = [r for r in load_receipts() if r.get("distributed", False)]
    return {"history": history_list}

class ReceiptCreate(BaseModel):
    from_addr: str
    amount: int
    merkle_root: str = ""

@app.post("/api/funds/receipt")
def create_receipt(receipt: ReceiptCreate):
    data = receipt.dict()
    data["timestamp"] = datetime.now().isoformat()
    data["distributed"] = False
    # 模拟 Merkle 根计算（简单取 SHA256）
    if not data["merkle_root"]:
        data["merkle_root"] = hashlib.sha256(f"{data['from_addr']}{data['amount']}{data['timestamp']}".encode()).hexdigest()[:8]
    save_receipt(data)
    return {"status": "received", "merkle": data["merkle_root"]}

@app.get("/api/health")
def health():
    # 对接 ai_protector.py 的状态文件
    try:
        with open("health_alerts.log", "r") as f:
            last_alert = f.readlines()[-1] if f else ""
    except:
        last_alert = ""
    return {
        "cpu": 42,  # 实际可从 psutil 获取
        "ram": 38,
        "status": "healthy",
        "last_alert": last_alert
    }

# 提供静态文件
app.mount("/", StaticFiles(directory="static", html=True), name="static")
