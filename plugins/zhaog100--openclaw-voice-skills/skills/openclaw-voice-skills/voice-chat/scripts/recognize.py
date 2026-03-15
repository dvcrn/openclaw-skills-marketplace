#!/usr/bin/env python3
"""
语音识别脚本
使用OpenAI Whisper本地识别音频文件
"""

import sys
import os

def recognize_audio(audio_file: str, model_size: str = "base") -> str:
    """
    识别音频文件中的语音
    
    Args:
        audio_file: 音频文件路径
        model_size: Whisper模型大小 (tiny/base/small/medium/large)
    
    Returns:
        识别出的文字
    """
    try:
        import whisper
    except ImportError:
        print("❌ 错误：未安装openai-whisper")
        print("请运行：pip install openai-whisper")
        sys.exit(1)
    
    # 检查文件是否存在
    if not os.path.exists(audio_file):
        print(f"❌ 错误：文件不存在 - {audio_file}")
        sys.exit(1)
    
    # 加载模型
    print(f"🔊 加载Whisper模型：{model_size}...")
    model = whisper.load_model(model_size)
    
    # 识别音频
    print(f"🎤 识别音频：{audio_file}...")
    result = model.transcribe(audio_file, language="zh")
    
    # 输出结果
    text = result["text"]
    print(f"\n📝 识别结果：\n{text}")
    
    return text


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法：python recognize.py <音频文件> [模型大小]")
        print("模型大小：tiny/base/small/medium/large")
        print("示例：python recognize.py audio.mp3 base")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    model_size = sys.argv[2] if len(sys.argv) > 2 else "base"
    
    # 识别音频
    recognize_audio(audio_file, model_size)


if __name__ == "__main__":
    main()
