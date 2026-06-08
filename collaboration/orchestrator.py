# collaboration/orchestrator.py
from private_core.key_manager import KeyManager

class Orchestrator:
    async def execute(self, model_name: str, task: str):
        # 根據任務類型，自動選取對應的密鑰 (如：工程任務選 dev_key)
        key = KeyManager.get_key("dev") if "debug" in task else KeyManager.get_key("bot_a")
        print(f"[System] 使用權限執行任務: {task}")
        # ... 後續調用邏輯

