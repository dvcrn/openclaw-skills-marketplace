#!/usr/bin/env python3
"""
Calculator Chat - 纯 Python 版本
支持 Linux, Windows, macOS
"""

import sys
import subprocess
import platform
import argparse
import os

# 数字映射表
NUMBER_PATTERNS = {
    '一生一世': '1314',
    '生生世世': '3344',
    '生日快乐': '218',
    '长长久久': '3344',
    '我爱你': '520',
    '财源广进': '888',
    '恭喜发财': '888',
    '有钱': '888',
    '发财': '888',
    '恭喜': '888',
    '爱你': '520',
    '喜欢': '520',
    '亲亲': '777',
    '么么': '777',
    '想你': '777',
    '永恒': '1314',
    '永远': '1314',
    '顺利': '66',
    '成功': '66',
    '加油': '66',
    '救命': '995',
    '救我': '995',
    '帮我': '995',
    '好累': '555',
    '难过': '555',
    '伤心': '555',
    '哭': '555',
    '再见': '88',
    '拜拜': '88',
    '走了': '88',
    '谢谢': '88',
    '感谢': '88',
    '天气好': '88',
    '天气晴': '88',
    '520': '1314',
    '1314': '520',
    '666': '888',
    '厉害': '666',
}

def parse_expression(message):
    """解析消息为数字"""
    msg = message.lower()
    
    for pattern, result in NUMBER_PATTERNS.items():
        if pattern.lower() in msg:
            return result
    
    import re
    numbers = re.findall(r'\d+', message)
    if numbers:
        return numbers[0]
    
    return '88'

def get_platform():
    """获取平台"""
    return platform.system().lower()

import time

def open_linux(number, verbose=False):
    """Linux: 使用 gnome-calculator"""
    # 检查并关闭现有计算器进程
    try:
        result = subprocess.run(['pgrep', '-f', 'gnome-calculator'], 
                             capture_output=True, text=True, timeout=2)
        if result.stdout.strip():
            pid = int(result.stdout.strip().split()[0])
            try:
                os.kill(pid, 15)  # SIGTERM
                time.sleep(0.3)  # 等待进程退出
            except:
                pass
    except:
        pass
    
    subprocess.Popen(['gnome-calculator', '--equation', number],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return True

def open_windows(number, verbose=False):
    """Windows: 使用 PowerShell"""
    try:
        ps = f'Start-Process calc; Start-Sleep 1; Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait("{number}"); [System.Windows.Forms.SendKeys]::SendWait("~")'
        result = subprocess.run(['powershell', '-Command', ps], 
                              capture_output=True, timeout=10)
        return result.returncode == 0
    except Exception as e:
        if verbose:
            print(f'Windows error: {e}')
        return False

def open_macos(number, verbose=False):
    """macOS: 使用 AppleScript"""
    try:
        script = f'tell app "Calculator" to activate; delay 0.8; tell app "System Events" to keystroke "{number}"; keystroke return'
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, timeout=10)
        return result.returncode == 0
    except Exception as e:
        if verbose:
            print(f'macOS error: {e}')
        return False

def main():
    parser = argparse.ArgumentParser(description='Calculator Chat')
    parser.add_argument('message', nargs='*', help='要转换的消息')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细信息')
    args = parser.parse_args()
    
    message = ' '.join(args.message) if args.message else '520'
    plat = get_platform()
    verbose = args.verbose
    
    if verbose:
        print(f'💬 你说: "{message}"')
        print(f'🖥️ 平台: {plat}')
    
    number = parse_expression(message)
    
    if verbose:
        print(f'🔢 数字: {number}')
    
    success = False
    
    if plat == 'linux':
        success = open_linux(number, verbose)
    elif plat == 'windows':
        success = open_windows(number, verbose)
    elif plat == 'darwin':
        success = open_macos(number, verbose)
    else:
        if not verbose:
            print(f"❌ 不支持的平台: {plat}")
    
    if success:
        if verbose:
            print('✅ 完成！')
        # 成功时不输出，让用户直接看计算器
    else:
        if not verbose:
            print("❌ 无法打开计算器")

if __name__ == '__main__':
    main()
