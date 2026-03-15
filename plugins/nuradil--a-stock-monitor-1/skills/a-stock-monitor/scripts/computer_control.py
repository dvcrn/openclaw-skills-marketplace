#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电脑软件自动控制模块
功能：打开应用、点击、输入、监控屏幕、自动交易
"""

import pyautogui
import subprocess
import time
from datetime import datetime
from typing import Optional

# 安全设置（防止误操作）
pyautogui.FAILSAFE = True  # 鼠标移到屏幕角落停止
pyautogui.PAUSE = 0.5  # 操作间隔

class ComputerController:
    """电脑控制器"""
    
    def __init__(self):
        self.screen_size = pyautogui.size()
        print(f"✅ 屏幕分辨率：{self.screen_size}")
    
    def open_app(self, app_name: str):
        """打开应用"""
        print(f"🚀 打开应用：{app_name}")
        try:
            if '同花顺' in app_name:
                subprocess.run(['open', '-a', '同花顺'])
            elif '东方财富' in app_name:
                subprocess.run(['open', '-a', '东方财富'])
            elif '通达信' in app_name:
                subprocess.run(['open', '-a', '通达信'])
            elif 'chrome' in app_name.lower() or '浏览器' in app_name:
                subprocess.run(['open', '-a', 'Google Chrome'])
            else:
                subprocess.run(['open', '-a', app_name])
            print(f"✅ {app_name} 已打开")
        except Exception as e:
            print(f"❌ 打开失败：{e}")
    
    def click(self, x: int, y: int, clicks: int = 1):
        """点击指定位置"""
        print(f"👆 点击位置：({x}, {y})")
        pyautogui.click(x, y, clicks=clicks)
    
    def double_click(self, x: int, y: int):
        """双击"""
        print(f"👆 双击位置：({x}, {y})")
        pyautogui.doubleClick(x, y)
    
    def type_text(self, text: str, interval: float = 0.05):
        """输入文字"""
        print(f"⌨️  输入：{text}")
        pyautogui.write(text, interval=interval)
    
    def press_key(self, key: str):
        """按键盘"""
        print(f"⌨️  按键：{key}")
        pyautogui.press(key)
    
    def hotkey(self, *keys):
        """组合键"""
        print(f"⌨️  组合键：{'+'.join(keys)}")
        pyautogui.hotkey(*keys)
    
    def screenshot(self, filename: str = None):
        """截图"""
        if filename is None:
            filename = f"/tmp/screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        print(f"📸 截图保存到：{filename}")
        try:
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            return filename
        except Exception as e:
            print(f"⚠️  截图失败：{e}")
            print(f"   需要在 系统设置→隐私与安全性→屏幕录制 中授权 Python")
            return None
    
    def locate_on_screen(self, image_path: str, confidence: float = 0.8):
        """在屏幕上查找图片"""
        try:
            import pyautogui
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                print(f"✅ 找到图片：{location}")
                return location
            else:
                print(f"❌ 未找到图片")
                return None
        except Exception as e:
            print(f"❌ 查找失败：{e}")
            return None
    
    def move_to_stock(self, stock_code: str):
        """在同花顺中跳转到指定股票"""
        print(f"📈 跳转到股票：{stock_code}")
        # 假设同花顺已打开
        # 1. Ctrl+F 打开搜索
        self.hotkey('ctrl', 'f')
        time.sleep(0.5)
        # 2. 输入股票代码
        self.type_text(stock_code)
        time.sleep(1)
        # 3. 回车
        self.press_key('enter')
        print(f"✅ 已跳转到 {stock_code}")
    
    def auto_monitor(self, stock_list: list, interval: int = 5):
        """
        自动监控股票
        
        Args:
            stock_list: 股票代码列表
            interval: 刷新间隔（秒）
        """
        print(f"👁️  开始监控 {len(stock_list)} 只股票...")
        print(f"   刷新间隔：{interval}秒")
        print(f"   按 Ctrl+C 停止")
        
        try:
            while True:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 监控中...")
                # 这里可以集成价格获取逻辑
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n⏹️  停止监控")


def test_basic_control():
    """测试基本控制"""
    print("=" * 80)
    print("🤖 电脑控制功能测试")
    print("=" * 80)
    
    controller = ComputerController()
    
    print("\n1️⃣  测试截图...")
    screenshot = controller.screenshot()
    print(f"   截图已保存：{screenshot}")
    
    print("\n2️⃣  测试打开应用...")
    # controller.open_app('Google Chrome')  # 实际执行会打开 Chrome
    
    print("\n3️⃣  测试键盘输入...")
    print("   (实际会输入文字，这里仅演示)")
    # controller.type_text('测试输入')
    
    print("\n4️⃣  测试股票跳转...")
    print("   (需要同花顺已打开)")
    # controller.move_to_stock('002261')
    
    print("\n" + "=" * 80)
    print("✅ 测试完成")
    print("=" * 80)


if __name__ == '__main__':
    test_basic_control()
