#!/usr/bin/env python3
"""
本地TTS语音生成工具
使用pyttsx3生成语音文件
"""

import sys
import os
import tempfile

def generate_voice(text: str, output_file: str = None) -> str:
    """
    生成语音文件
    
    Args:
        text: 要转换的文本
        output_file: 输出文件路径（可选）
    
    Returns:
        生成的语音文件路径
    """
    try:
        import pyttsx3
    except ImportError:
        print("❌ 错误：未安装pyttsx3")
        print("请运行：pip install pyttsx3")
        sys.exit(1)
    
    # 输出文件
    if output_file is None:
        output_file = os.path.join(tempfile.gettempdir(), f"voice_{os.getpid()}.wav")
    
    # 初始化TTS引擎
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # 语速
    engine.setProperty('volume', 1.0)  # 音量
    
    # 生成语音
    engine.save_to_file(text, output_file)
    engine.runAndWait()
    
    # 检查文件是否生成
    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        print(f"✅ 语音生成成功：{output_file}")
        print(f"   文件大小：{os.path.getsize(output_file)} 字节")
        return output_file
    else:
        print(f"❌ 语音生成失败：文件为空或不存在")
        sys.exit(1)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="本地TTS语音生成工具")
    parser.add_argument("text", help="要转换的文本")
    parser.add_argument("-o", "--output", help="输出文件路径")
    
    args = parser.parse_args()
    
    # 生成语音
    voice_file = generate_voice(args.text, args.output)
    print(f"\n🔊 语音文件：{voice_file}")


if __name__ == "__main__":
    main()
