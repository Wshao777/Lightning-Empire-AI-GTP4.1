#!/usr/bin/env python3
"""
密钥轮换脚本 - 支持 key_1 ~ key_10
用法: python rotate_keys.py [--keys key_1,key_2] [--length 48] [--dry-run]
"""

import os
import re
import secrets
import base64
import argparse
import datetime
import json
import subprocess
from pathlib import Path
from typing import List, Dict

# ========== 配置区域 ==========
ENV_FILE = Path(".env")                     # 环境变量文件路径
BACKUP_DIR = Path("key_backups")            # 旧密钥备份目录
SERVICE_RESTART_CMDS = {                    # key -> 重启命令（可选）
    "key_2": ["systemctl", "restart", "wind-prod"],
    "key_3": ["systemctl", "restart", "dispatch-bot"],
}
WEBHOOK_URL = None                          # 例如 "https://hooks.slack.com/..."
# ==============================

def generate_key(length: int = 48) -> str:
    """生成 URL-safe Base64 随机密钥（长度约 length 字符）"""
    rand_bytes = secrets.token_bytes(length)
    key = base64.urlsafe_b64encode(rand_bytes).decode('ascii').rstrip('=')
    return key[:length]  # 保证长度精确

def backup_current_key(key_name: str, old_value: str):
    """备份当前密钥到 JSON 文件"""
    BACKUP_DIR.mkdir(exist_ok=True)
    backup_file = BACKUP_DIR / f"{key_name}_{datetime.datetime.now():%Y%m%d_%H%M%S}.json"
    with open(backup_file, "w") as f:
        json.dump({key_name: old_value, "rotated_at": str(datetime.datetime.now())}, f, indent=2)
    print(f"📦 备份旧密钥 -> {backup_file}")

def update_env_file(key_name: str, new_value: str):
    """更新 .env 文件中的密钥值"""
    if not ENV_FILE.exists():
        print(f"⚠️ {ENV_FILE} 不存在，将创建新文件")
        with open(ENV_FILE, "w") as f:
            f.write(f"{key_name.upper()}={new_value}\n")
        return

    with open(ENV_FILE, "r") as f:
        lines = f.readlines()
    
    updated = False
    pattern = re.compile(rf"^{key_name.upper()}=.*", re.IGNORECASE)
    for i, line in enumerate(lines):
        if pattern.match(line):
            lines[i] = f"{key_name.upper()}={new_value}\n"
            updated = True
            break
    
    if not updated:
        lines.append(f"{key_name.upper()}={new_value}\n")
    
    with open(ENV_FILE, "w") as f:
        f.writelines(lines)
    print(f"✏️ 已更新 {ENV_FILE} 中的 {key_name.upper()}")

def restart_service(key_name: str):
    """如果需要，重启关联服务"""
    if key_name in SERVICE_RESTART_CMDS:
        cmd = SERVICE_RESTART_CMDS[key_name]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"🔄 已重启服务: {' '.join(cmd)}")
        except subprocess.CalledProcessError as e:
            print(f"❌ 重启服务失败: {e.stderr.decode()}")
    else:
        print(f"ℹ️ 密钥 {key_name} 无关联服务重启，跳过")

def send_webhook(key_name: str, new_value: str, dry_run: bool):
    """发送轮换通知（可选）"""
    if not WEBHOOK_URL or dry_run:
        return
    import requests
    payload = {
        "text": f"🔄 密钥轮换通知\n密钥: {key_name}\n新值: `{new_value[:8]}...`\n时间: {datetime.datetime.now()}"
    }
    try:
        requests.post(WEBHOOK_URL, json=payload, timeout=2)
    except Exception as e:
        print(f"⚠️ Webhook 发送失败: {e}")

def rotate_key(key_name: str, length: int, dry_run: bool):
    """轮换单个密钥"""
    print(f"\n🔑 正在轮换 {key_name} ...")
    new_key = generate_key(length)
    if dry_run:
        print(f"  [DRY-RUN] 新密钥: {new_key}")
        return
    
    # 尝试读取旧值（用于备份）
    old_value = None
    if ENV_FILE.exists():
        with open(ENV_FILE, "r") as f:
            for line in f:
                if line.startswith(f"{key_name.upper()}="):
                    old_value = line.strip().split("=", 1)[1]
                    break
    
    if old_value:
        backup_current_key(key_name, old_value)
    
    update_env_file(key_name, new_key)
    restart_service(key_name)
    send_webhook(key_name, new_key, dry_run)
    print(f"✅ {key_name} 轮换完成")

def main():
    parser = argparse.ArgumentParser(description="密钥轮换脚本")
    parser.add_argument("--keys", type=str, default="all",
                        help="要轮换的密钥，逗号分隔，例如 key_1,key_2 或 all")
    parser.add_argument("--length", type=int, default=48,
                        help="密钥长度（字符），默认 48")
    parser.add_argument("--dry-run", action="store_true",
                        help="仅模拟，不实际修改")
    args = parser.parse_args()
    
    all_keys = [f"key_{i}" for i in range(1, 11)]  # key_1 ~ key_10
    if args.keys.lower() == "all":
        keys_to_rotate = all_keys
    else:
        keys_to_rotate = [k.strip() for k in args.keys.split(",") if k.strip()]
        # 验证有效性
        for k in keys_to_rotate:
            if k not in all_keys:
                print(f"❌ 无效密钥名称: {k}，有效值: {', '.join(all_keys)}")
                return
    
    print(f"🚀 开始轮换密钥: {', '.join(keys_to_rotate)}")
    if args.dry_run:
        print("⚠️ DRY-RUN 模式，不会实际修改任何文件或服务")
    
    for key in keys_to_rotate:
        rotate_key(key, args.length, args.dry_run)
    
    print("\n🎉 所有密钥轮换任务完成")

if __name__ == "__main__":
    main()
