#!/usr/bin/env python3
"""
AI 环境保护系统 - 防御、修复、医疗、回溯
整合密钥轮换 + 环境监控 + 自动自愈
"""

import os
import time
import json
import shutil
import subprocess
import threading
import psutil
import schedule
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import requests
import hashlib

# ========== 初始化 ==========
load_dotenv()
ENV_FILE = Path(".env")
BACKUP_DIR = Path(os.getenv("BACKUP_DIR", "/var/backups/ai_env"))
STATE_DIR = Path("./state_snapshots")
STATE_DIR.mkdir(exist_ok=True)

# ========== 1. 医疗模块（健康监控） ==========
class HealthMonitor:
    @staticmethod
    def check_cpu():
        return psutil.cpu_percent(interval=1)
    
    @staticmethod
    def check_ram():
        return psutil.virtual_memory().percent
    
    @staticmethod
    def check_disk():
        return psutil.disk_usage('/').percent
    
    @staticmethod
    def check_gpu_temp():  # 需要 nvidia-smi
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader'],
                                    capture_output=True, text=True)
            return int(result.stdout.strip())
        except:
            return 0
    
    @staticmethod
    def log_alert(metric, value, threshold):
        alert = f"[ALERT] {metric}={value}% > {threshold}% at {datetime.now()}"
        with open("health_alerts.log", "a") as f:
            f.write(alert + "\n")
        print(f"⚠️ {alert}")
        return alert

# ========== 2. 防御模块（阻止异常请求 / 防火墙） ==========
class DefenseSystem:
    def __init__(self):
        self.failed_attempts = {}
    
    def rate_limit(self, client_ip):
        # 简化版令牌桶
        now = time.time()
        if client_ip not in self.failed_attempts:
            self.failed_attempts[client_ip] = []
        self.failed_attempts[client_ip] = [t for t in self.failed_attempts[client_ip] if now - t < 1]
        if len(self.failed_attempts[client_ip]) >= int(os.getenv("RATE_LIMIT_REQUESTS", 100)):
            return False
        self.failed_attempts[client_ip].append(now)
        return True
    
    def block_ip(self, ip):
        if os.getenv("ENABLE_FIREWALL") == "true":
            subprocess.run(f"iptables -A INPUT -s {ip} -j DROP", shell=True)
            print(f"🚫 已封禁 IP: {ip}")
    
    def detect_anomaly(self, metrics):
        # 简单规则：CPU + 网络流量突增
        if metrics["cpu"] > 90 and metrics["net_sent"] > 1e7:
            print("🚨 检测到挖矿或 DDoS 行为")
            return True
        return False

# ========== 3. 修复模块（自动重试、重启服务） ==========
class RepairEngine:
    @staticmethod
    def restart_failed_service(service_name):
        if os.getenv("AUTO_REPAIR_ENABLED") != "true":
            return
        try:
            subprocess.run(["systemctl", "restart", service_name], check=True)
            print(f"🔧 已重启服务: {service_name}")
            return True
        except:
            return False
    
    @staticmethod
    def kill_zombie_processes():
        for proc in psutil.process_iter(['pid', 'name', 'status']):
            if proc.info['status'] == 'zombie':
                proc.terminate()
                print(f"🧟 已清理僵尸进程 PID {proc.info['pid']}")

# ========== 4. 回溯模块（快照 + 回滚） ==========
class RollbackSystem:
    @staticmethod
    def take_snapshot(tag=""):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_file = STATE_DIR / f"snapshot_{ts}_{tag}.json"
        state = {
            "timestamp": ts,
            "env_vars": dict(os.environ),
            "process_list": [p.info for p in psutil.process_iter(['pid', 'name'])],
            "disk_usage": psutil.disk_usage('/')._asdict(),
        }
        with open(snapshot_file, "w") as f:
            json.dump(state, f, indent=2)
        print(f"📸 已创建快照: {snapshot_file}")
        # 自动清理过期快照
        RollbackSystem.clean_old_snapshots()
        return snapshot_file
    
    @staticmethod
    def clean_old_snapshots():
        retention_days = int(os.getenv("SNAPSHOT_RETENTION_DAYS", 7))
        now = time.time()
        for f in STATE_DIR.glob("snapshot_*.json"):
            if (now - f.stat().st_mtime) > retention_days * 86400:
                f.unlink()
                print(f"🗑️ 已删除过期快照: {f.name}")
    
    @staticmethod
    def rollback_to_snapshot(snapshot_path):
        if os.getenv("AUTO_ROLLBACK_ENABLED") != "true":
            print("自动回滚未启用")
            return False
        with open(snapshot_path, "r") as f:
            state = json.load(f)
        # 恢复环境变量（仅示例，实际需谨慎）
        for k, v in state["env_vars"].items():
            if k.startswith("KEY_"):
                os.environ[k] = v
        # 重新加载 .env
        load_dotenv(override=True)
        print(f"⏪ 已回滚至快照: {snapshot_path}")
        return True

# ========== 5. 主循环（调度器） ==========
def job_health_check():
    hm = HealthMonitor()
    metrics = {
        "cpu": hm.check_cpu(),
        "ram": hm.check_ram(),
        "disk": hm.check_disk(),
        "gpu_temp": hm.check_gpu_temp(),
    }
    print(f"💓 健康检查 | CPU:{metrics['cpu']}% RAM:{metrics['ram']}% DISK:{metrics['disk']}% GPU:{metrics['gpu_temp']}°C")
    
    if metrics['cpu'] > int(os.getenv("CPU_ALERT_THRESHOLD", 85)):
        hm.log_alert("CPU", metrics['cpu'], os.getenv("CPU_ALERT_THRESHOLD"))
        RepairEngine.kill_zombie_processes()
    
    if metrics['ram'] > int(os.getenv("RAM_ALERT_THRESHOLD", 90)):
        hm.log_alert("RAM", metrics['ram'], os.getenv("RAM_ALERT_THRESHOLD"))
        # 触发内存清理
        os.system("sync && echo 3 > /proc/sys/vm/drop_caches" if os.name == 'posix' else "")
    
    # 防御检测
    defense = DefenseSystem()
    if defense.detect_anomaly(metrics):
        print("🚨 异常行为已触发防御！")
        # 可在此调用 block_ip 等

def job_snapshot():
    RollbackSystem.take_snapshot("auto")

def job_key_rotation():
    # 调用之前的密钥轮换脚本
    subprocess.run(["python3", "rotate_keys.py", "--keys", "key_2", "--length", "64"])

def start_scheduler():
    schedule.every(int(os.getenv("HEALTH_CHECK_INTERVAL", 30))).seconds.do(job_health_check)
    schedule.every(int(os.getenv("STATE_SNAPSHOT_INTERVAL", 3600))).seconds.do(job_snapshot)
    schedule.every().day.at("03:00").do(job_key_rotation)  # 每天凌晨3点轮换生产密钥
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    print("🤖 AI 环境保护系统启动")
    print(f"防护模式: {os.getenv('PROTECTION_MODE')}")
    print(f"自动修复: {os.getenv('AUTO_REPAIR_ENABLED')}")
    print(f"自动回溯: {os.getenv('AUTO_ROLLBACK_ENABLED')}")
    # 启动快照一次
    RollbackSystem.take_snapshot("boot")
    start_scheduler()
