import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="private_core/.env")  # 你的 private 目錄

def get_api_key(provider):
    key = os.getenv(f"{provider.upper()}_API_KEY")
    if not key:
        raise ValueError(f"Missing {provider} key in private_core/.env")
    return key
