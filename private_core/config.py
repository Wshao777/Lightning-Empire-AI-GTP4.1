import os
from dotenv import load_dotenv

load_dotenv()

def get_secret(key: str):
    # 從系統環境變數讀取，永不寫入設定檔
    return os.getenv(key)

