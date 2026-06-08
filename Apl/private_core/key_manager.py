# private_core/key_manager.py
import os

class KeyManager:
    # 密鑰映射表 (對應你定義的標題)
    _KEY_MAP = {
        "dev": "key_1",
        "prod": "key_2",
        "bot_a": "key_3",
        "bot_b": "key_4",
        "backup": "key_10"
    }

    @staticmethod
    def get_key(target: str):
        key_id = KeyManager._KEY_MAP.get(target)
        # 從環境變數或加密 Vault 讀取，永不寫入硬碟
        secret = os.getenv(f"LIGHTNING_{key_id.upper()}")
        if not secret:
            raise PermissionError(f"安全警告: 密鑰 {key_id} 未授權或不存在！")
        return secret

