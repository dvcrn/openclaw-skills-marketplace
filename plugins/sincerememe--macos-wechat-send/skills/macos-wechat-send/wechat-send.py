#!/usr/bin/env python3
"""
微信自动发送消息脚本
使用 AppleScript 控制微信 Mac 版
通过剪贴板复制粘贴，避免输入法影响
"""

import subprocess
import sys
import pyautogui

def set_clipboard(text):
    """设置剪贴板内容 - 直接用 Python 设置，避免转义问题"""
    # 使用 macOS 的 pbcopy 命令，通过 stdin 传递内容
    proc = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE, text=True)
    proc.stdin.write(text)
    proc.stdin.close()
    proc.wait()

def activate_wechat():
    """激活微信窗口 - 使用多种方式确保成功"""
    import time
    
    # 方式 1：用 open 命令打开/激活应用
    try:
        subprocess.run(['open', '-a', 'WeChat'], check=True, timeout=5)
        time.sleep(0.3)
    except:
        pass
    
    # 方式 2：用 AppleScript activate
    try:
        subprocess.run(['osascript', '-e', 'tell application "WeChat" to activate'], check=True, timeout=5)
        time.sleep(0.3)
    except:
        pass
    
    # 方式 3：用 System Events 设置前台
    try:
        subprocess.run(['osascript', '-e', 'tell application "System Events" to set frontmost of process "WeChat" to true'], check=True, timeout=5)
        time.sleep(0.3)
    except:
        pass
    
    # 方式 4：用 NSAppleScript 强制激活（最底层）
    try:
        script = '''
        tell application "System Events"
            tell process "WeChat"
                set frontmost to true
                perform action "AXRaise" of window 1
            end tell
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True, timeout=5)
        time.sleep(0.3)
    except:
        pass
    
    return True

def send_wechat_message(contact_name, message):
    """发送微信消息 - 分两步：先搜索联系人，再发送消息"""
    
    # 第零步：激活微信窗口
    try:
        activate_wechat()
    except Exception as e:
        print(f"✗ 激活微信失败：{e}")
        return False
    
    # 第一步：先搜索"文件传输助手"（不发送），再搜索目标联系人
    set_clipboard("文件传输助手")
    
    dummy_script = '''
    tell application "System Events"
        tell process "WeChat"
            -- 先按 ESC 清除任何打开的窗口或搜索框
            key code 53
            delay 0.2
            
            -- 按 Cmd+F 搜索
            keystroke "f" using command down
            delay 0.3
            
            -- 粘贴"文件传输助手"
            keystroke "v" using command down
            delay 0.3
            
            -- 按回车打开文件传输助手
            keystroke return
            delay 0.3
        end tell
    end tell
    '''
    
    try:
        subprocess.run(['osascript', '-e', dummy_script], check=True, timeout=10)
    except Exception as e:
        print(f"✗ 搜索垫脚石失败：{e}")
        return False
    
    # 现在搜索真正的目标联系人
    set_clipboard(contact_name)
    
    search_script = '''
    tell application "System Events"
        tell process "WeChat"
            -- 先按 ESC 清除任何打开的窗口或搜索框
            key code 53
            delay 0.2
            
            -- 按 Cmd+A 全选清空搜索框
            keystroke "a" using command down
            delay 0.2
            
            -- 按 Cmd+F 重新搜索
            keystroke "f" using command down
            delay 0.3
            
            -- 粘贴联系人名字
            keystroke "v" using command down
            delay 0.5
            
            -- 按回车选择第一个搜索结果
            keystroke return
            delay 0.5
        end tell
    end tell
    '''
    
    try:
        subprocess.run(['osascript', '-e', search_script], check=True, timeout=10)
    except Exception as e:
        print(f"✗ 搜索联系人失败：{e}")
        return False
    
    # 第二步：设置消息内容到剪贴板，粘贴并发送
    set_clipboard(message)
    
    send_script = '''
    tell application "System Events"
        tell process "WeChat"
            -- 等待一下确保聊天窗口已打开，输入框已聚焦
            delay 0.3
            
            -- 粘贴消息内容
            keystroke "v" using command down
            delay 0.3
            
            -- 按回车发送
            keystroke return
        end tell
    end tell
    '''
    
    try:
        subprocess.run(['osascript', '-e', send_script], check=True, timeout=10)
        print(f"✓ 消息已发送给：{contact_name}")
        return True
    except subprocess.TimeoutExpired:
        print("✗ 操作超时")
        return False
    except Exception as e:
        print(f"✗ 错误：{e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法：python send_wechat.py <联系人名字> <消息内容>")
        sys.exit(1)
    
    contact = sys.argv[1]
    message = sys.argv[2]
    
    success = send_wechat_message(contact, message)
    sys.exit(0 if success else 1)
