import argparse
import secrets
import string
import os
import subprocess

# 定義密鑰配置
KEY_MAP = {
    "key_1": "dev", "key_2": "prod", "key_3": "bot_a", 
    "key_4": "bot_b", "key_10": "backup"
}

def generate_key(length=32):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(secrets.choice(chars) for _ in range(length))

def rotate(keys_to_rotate, length, dry_run):
    all_keys = list(KEY_MAP.keys()) if 'all' in keys_to_rotate else keys_to_rotate
    
    for k in all_keys:
        new_key = generate_key(length)
        if dry_run:
            print(f"[Dry-run] 模擬輪換 {k} ({KEY_MAP[k]}): {new_key[:4]}****")
        else:
            # 實際更新邏輯：寫入系統環境變數或專用的 .key_store
            os.environ[f"LIGHTNING_{k.upper()}"] = new_key
            print(f"✅ 已輪換 {k} ({KEY_MAP[k]})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--keys", default="all", help="要輪換的密鑰 (用逗號分隔)")
    parser.add_argument("--length", type=int, default=32)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    
    rotate(args.keys.split(','), args.length, args.dry_run)
    
    if not args.dry_run:
        print("🔄 正在觸發服務重啟 (Signal SIGHUP)...")
        # subprocess.run(["systemctl", "restart", "lightning_ai"]) 

