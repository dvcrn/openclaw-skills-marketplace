#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Camera Monitor - OpenClaw 集成脚本

功能：
1. 监听飞书消息，识别控制命令
2. 创建命令文件，触发视觉系统响应
3. 支持命令：启动视频模式/关闭视频模式/视频状态/今日日报
"""

import os
import json
import sys
from datetime import datetime

# 配置
COMMAND_FILE = r"D:\OpenClawDocs\projects\camera-monitor\camera_command.json"
SCRIPT_DIR = r"D:\OpenClawDocs\projects\camera-monitor"
VISION_SCRIPT = os.path.join(SCRIPT_DIR, "vision_scheduler.py")

# 飞书 Webhook（可选，用于直接推送）
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/051ec7b9-364b-4df0-9d3c-7a9bd5071463"


def send_feishu_message(text):
    """发送飞书消息"""
    import requests
    
    headers = {'Content-Type': 'application/json'}
    payload = {"msg_type": "text", "content": {"text": text}}

    try:
        response = requests.post(FEISHU_WEBHOOK, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"[{datetime.now()}] [OK] 飞书消息发送成功")
            return True
        else:
            print(f"[{datetime.now()}] [FAIL] 飞书消息发送失败：{response.status_code}")
            return False
    except Exception as e:
        print(f"[{datetime.now()}] [ERROR] 飞书消息发送异常：{str(e)}")
        return False


def create_command(command):
    """创建命令文件"""
    try:
        data = {"command": command}
        with open(COMMAND_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        
        print(f"[{datetime.now()}] [OK] 命令已创建：{command}")
        return True
    except Exception as e:
        print(f"[{datetime.now()}] [ERROR] 创建命令失败：{e}")
        return False


def check_system_running():
    """检查系统是否运行中"""
    import psutil
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'] or [])
            if 'vision_scheduler.py' in cmdline:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    return False


def start_system():
    """启动视觉系统"""
    import subprocess
    
    if check_system_running():
        return "⚠️ 视频监控系统已在运行中"
    
    try:
        # 后台启动
        subprocess.Popen(
            [sys.executable, VISION_SCRIPT],
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            cwd=SCRIPT_DIR
        )
        
        # 等待 2 秒检查是否启动成功
        import time
        time.sleep(2)
        
        if check_system_running():
            return "✅ 视频监控系统已启动！"
        else:
            return "❌ 启动失败，请检查日志"
    except Exception as e:
        return f"❌ 启动异常：{str(e)}"


def stop_system():
    """停止视觉系统"""
    import psutil
    import signal
    
    stopped = False
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'] or [])
            if 'vision_scheduler.py' in cmdline:
                proc.send_signal(signal.CTRL_BREAK_EVENT)
                stopped = True
                print(f"[{datetime.now()}] [OK] 已停止进程 {proc.info['pid']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if stopped:
        return "✅ 视频监控系统已关闭"
    else:
        return "⚠️ 系统未在运行"


def handle_command(command):
    """处理飞书命令"""
    command = command.strip()
    
    if command == "启动视频模式":
        msg = start_system()
        send_feishu_message(msg)
        return msg
    
    elif command == "关闭视频模式":
        # 先创建命令文件让系统生成日报
        create_command("关闭视频模式")
        
        # 等待 2 秒让系统处理
        import time
        time.sleep(2)
        
        # 停止系统
        msg = stop_system()
        send_feishu_message(msg)
        return msg
    
    elif command == "视频状态":
        if check_system_running():
            create_command("视频状态")
            return "📹 系统运行中，状态已发送到飞书"
        else:
            return "📹 系统未运行，发送'启动视频模式'开启"
    
    elif command == "今日日报":
        if check_system_running():
            create_command("今日日报")
            return "📊 日报已生成，请查看飞书"
        else:
            return "📊 系统未运行，无法生成日报"
    
    else:
        return None


def main():
    """主函数"""
    print("=" * 60)
    print("Camera Monitor - OpenClaw Integration")
    print("=" * 60)
    
    # 检查依赖
    try:
        import cv2
        import mediapipe
        import psutil
        print("[OK] Dependencies check passed")
    except ImportError as e:
        print(f"[FAIL] Missing dependency: {e}")
        print("Please run: pip install opencv-python mediapipe psutil")
        return
    
    # 检查文件
    if not os.path.exists(VISION_SCRIPT):
        print(f"[FAIL] Script not found: {VISION_SCRIPT}")
        return
    
    print("[OK] Files check passed")
    print("=" * 60)
    
    # 交互式命令
    print("\nAvailable commands:")
    print("  1.启动视频模式 | 2.关闭视频模式 | 3.视频状态 | 4.今日日报 | q.Quit")
    print("-" * 60)
    
    while True:
        try:
            cmd = input("\nEnter command: ").strip()
            
            if cmd.lower() in ['q', 'quit', 'exit']:
                print("Exiting...")
                break
            
            response = handle_command(cmd)
            if response:
                print(f"Response: {response}")
            else:
                print("Unknown command")
        
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
