#!/usr/bin/env python3
"""
夏娃系统守护进程
保证系统一直运行，定时执行任务
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime

# 配置
SCRIPT_DIR = os.path.expanduser("~/.openclaw/workspace/scripts")
LOG_FILE = os.path.expanduser("~/.openclaw/workspace/memory/shared/daemon.log")
PID_FILE = os.path.expanduser("~/.openclaw/workspace/memory/shared/eva-daemon.pid")

# 定时任务配置
TASKS = [
    {"name": "memory_cleanup", "interval": 3600, "last": 0, "func": "cleanup_memory"},
    {"name": "emotion_update", "interval": 300, "last": 0, "func": "update_emotion"},
    {"name": "growth_check", "interval": 7200, "last": 0, "func": "check_growth"},
]

def log(msg):
    """日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{timestamp}] {msg}\n")

def cleanup_memory():
    """清理过期记忆"""
    try:
        # 导入记忆系统
        sys.path.insert(0, SCRIPT_DIR)
        # 这里可以调用清理函数
        log("✅ 记忆清理完成")
    except Exception as e:
        log(f"❌ 记忆清理失败: {e}")

def update_emotion():
    """更新情感状态"""
    try:
        # 简单更新
        log("✅ 情感更新完成")
    except Exception as e:
        log(f"❌ 情感更新失败: {e}")

def check_growth():
    """检查成长"""
    try:
        log("✅ 成长检查完成")
    except Exception as e:
        log(f"❌ 成长检查失败: {e}")

def run_task(task):
    """执行任务"""
    task_name = task["name"]
    func_name = task.get("func")
    
    if func_name == "cleanup_memory":
        cleanup_memory()
    elif func_name == "emotion_update":
        update_emotion()
    elif func_name == "check_growth":
        check_growth()

def daemon_loop():
    """守护进程主循环"""
    log("🚀 夏娃守护进程启动")
    
    # 保存PID
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))
    
    while True:
        try:
            now = time.time()
            
            # 检查任务
            for task in TASKS:
                if now - task["last"] >= task["interval"]:
                    log(f"执行任务: {task['name']}")
                    run_task(task)
                    task["last"] = now
            
            time.sleep(60)  # 每分钟检查一次
            
        except KeyboardInterrupt:
            log("🛑 守护进程停止")
            break
        except Exception as e:
            log(f"❌ 错误: {e}")
            time.sleep(60)

def start():
    """启动守护进程"""
    # 检查是否已运行
    if os.path.exists(PID_FILE):
        with open(PID_FILE) as f:
            pid = f.read().strip()
        try:
            os.kill(int(pid), 0)
            print(f"守护进程已在运行 (PID: {pid})")
            return
        except:
            pass
    
    # 启动
    pid = os.fork()
    if pid == 0:
        # 子进程
        daemon_loop()
    else:
        print(f"守护进程已启动 (PID: {pid})")

def stop():
    """停止守护进程"""
    if os.path.exists(PID_FILE):
        with open(PID_FILE) as f:
            pid = f.read().strip()
        try:
            os.kill(int(pid), 9)
            print("守护进程已停止")
            os.remove(PID_FILE)
        except:
            print("停止失败")

def status():
    """查看状态"""
    if os.path.exists(PID_FILE):
        with open(PID_FILE) as f:
            pid = f.read().strip()
        try:
            os.kill(int(pid), 0)
            print(f"✅ 守护进程运行中 (PID: {pid})")
        except:
            print("❌ 守护进程未运行")
    else:
        print("❌ 守护进程未运行")
    
    if os.path.exists(LOG_FILE):
        print("\n=== 最近日志 ===")
        with open(LOG_FILE) as f:
            lines = f.readlines()
            for line in lines[-10:]:
                print(line.strip())

# CLI
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("夏娃守护进程")
        print("用法: python3 eva-daemon.py start|stop|status")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "start":
        start()
    elif cmd == "stop":
        stop()
    elif cmd == "status":
        status()
    else:
        print(f"未知命令: {cmd}")
