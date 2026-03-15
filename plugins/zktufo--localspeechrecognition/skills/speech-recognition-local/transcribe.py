#!/usr/bin/env python3
"""本地语音识别脚本 - 优化版，使用更小的模型"""

import os
import sys
from faster_whisper import WhisperModel

# 模型缓存目录
MODEL_CACHE = os.path.expanduser("~/.cache/whisper")

def get_model():
    """获取或加载模型"""
    # 使用 base 模型（比 small 快 2 倍，内存减半）
    # 准确度略低但日常使用足够
    model_size = "base"
    
    print(f"正在加载 {model_size} 模型...")
    # 使用 float16 精度，GPU 更高效
    model = WhisperModel(
        model_size, 
        device="auto", 
        compute_type="int8"  # 更高效的计算类型
    )
    return model

def transcribe(audio_file, language="zh"):
    model = get_model()
    
    print(f"正在转录: {audio_file}")
    # 减少 beam_size 加快速度
    segments, info = model.transcribe(
        audio_file, 
        language=language,
        beam_size=1,  # 减少计算
        vad_filter=True,  # 语音活动检测，过滤静音
    )
    
    print(f"检测到语言: {info.language} (概率: {info.language_probability:.2f})")
    print("-" * 50)
    
    text = ""
    for segment in segments:
        text += segment.text.strip()
    
    print("转录结果:")
    print(text)
    return text

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 transcribe.py <audio_file> [language]")
        print("language: zh (默认) / en")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else "zh"
    
    transcribe(audio_file, language)
