#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Camera Monitor - OpenClaw 简单集成

用法：
  python camera_control.py [命令]
  
命令：
  start   - 启动视频模式
  stop    - 关闭视频模式
  status  - 视频状态
  report  - 今日日报
"""

import os
import sys
import json
import subprocess
from datetime import datetime

# 配置
COMMAND_FILE = r"D:\OpenClawDocs\projects\camera-monitor\camera_command.json"
VISION_SCRIPT = r"D:\OpenClawDocs\projects\camera-monitor\vision_scheduler.py"
SCRIPT_DIR = r"D:\OpenClawDocs\projects\camera-monitor"

def check_running():
    """检查是否运行中"""
    import psutil
    for proc in psutil.process_iter(['cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'] or [])
            if 'vision_scheduler.py' in cmdline:
                return True
        except:
            pass
    return False

def start():
    """启动"""
    if check_running():
        return "WARN: Already running"
    
    subprocess.Popen(
        [sys.executable, VISION_SCRIPT],
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        cwd=SCRIPT_DIR
    )
    return "OK: Started"

def stop():
    """停止"""
    import psutil, signal
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            if 'vision_scheduler.py' in ' '.join(proc.info['cmdline'] or []):
                proc.send_signal(signal.CTRL_BREAK_EVENT)
                return "OK: Stopped"
        except:
            pass
    return "WARN: Not running"

def send_command(cmd):
    """发送命令到视觉系统"""
    with open(COMMAND_FILE, 'w', encoding='utf-8') as f:
        json.dump({"command": cmd}, f, ensure_ascii=False)
    return f"OK: Command sent - {cmd}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python camera_control.py [start|stop|status|report]")
        sys.exit(1)
    
    cmd = sys.argv[1].lower()
    
    if cmd == "start":
        print(start())
    elif cmd == "stop":
        print(stop())
    elif cmd == "status":
        if check_running():
            send_command("视频状态")
            print("OK: 状态已查询")
        else:
            print("WARN: 系统未运行")
    elif cmd == "report":
        if check_running():
            send_command("今日日报")
            print("OK: 日报已生成")
        else:
            print("WARN: 系统未运行")
    else:
        print(f"Unknown command: {cmd}")
