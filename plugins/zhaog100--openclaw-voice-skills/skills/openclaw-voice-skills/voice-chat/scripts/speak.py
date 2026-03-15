#!/usr/bin/env python3
"""
语音合成脚本
使用pyttsx3本地合成语音
"""

import sys
import os

def speak_text(text: str, output_file: str = None, rate: int = 150) -> None:
    """
    将文字转换为语音
    
    Args:
        text: 要转换的文字
        output_file: 输出文件路径（可选，不指定则直接播放）
        rate: 语速（默认150）
    """
    try:
        import pyttsx3
    except ImportError:
        print("❌ 错误：未安装pyttsx3")
        print("请运行：pip install pyttsx3")
        sys.exit(1)
    
    # 初始化TTS引擎
    engine = pyttsx3.init()
    
    # 设置语速
    engine.setProperty('rate', rate)
    
    # 设置音量（0.0-1.0）
    engine.setProperty('volume', 1.0)
    
    # 获取中文语音（如果有）
    voices = engine.getProperty('voices')
    for voice in voices:
        if 'chinese' in voice.name.lower() or 'zh' in voice.id.lower():
            engine.setProperty('voice', voice.id)
            break
    
    print(f"🔊 合成语音：{text}")
    
    if output_file:
        # 保存到文件
        engine.save_to_file(text, output_file)
        engine.runAndWait()
        print(f"✅ 已保存到：{output_file}")
    else:
        # 直接播放
        engine.say(text)
        engine.runAndWait()
        print("✅ 播放完成")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法：python speak.py <文字> [输出文件] [语速]")
        print("示例：")
        print("  播放：python speak.py '你好，我是米粒儿'")
        print("  保存：python speak.py '你好，我是米粒儿' output.mp3")
        print("  自定义语速：python speak.py '你好' output.mp3 200")
        sys.exit(1)
    
    text = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    rate = int(sys.argv[3]) if len(sys.argv) > 3 else 150
    
    # 合成语音
    speak_text(text, output_file, rate)


if __name__ == "__main__":
    main()
