import websocket
import json
import subprocess

WS_URL = "ws://<x86-ip>:8000/ws/node"


def run(cmd):
    return subprocess.getoutput(cmd)


def on_message(ws, message):
    data = json.loads(message)

    if data["type"] == "exec":
        output = run(data["cmd"])

        ws.send(json.dumps({
            "node": "termux",
            "output": output
        }))


ws = websocket.WebSocketApp(
    WS_URL,
    on_message=on_message
)

ws.run_forever()
