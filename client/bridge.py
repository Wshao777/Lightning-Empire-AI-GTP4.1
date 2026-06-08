# client/bridge.py (於 Termux 執行)
import asyncio
import websockets
import subprocess

async def bridge():
    uri = "ws://<X86_IP>:8000/ws" # 區域網路 IP
    async with websockets.connect(uri) as websocket:
        while True:
            cmd = await websocket.recv() # 接收 AI 指令
            # 觸發本地動作 (如 termux-battery-status)
            result = subprocess.check_output(cmd, shell=True).decode()
            await websocket.send(result) # 回報數據給 AI 學習

asyncio.run(bridge())

