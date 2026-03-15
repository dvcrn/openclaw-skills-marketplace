#!/usr/bin/env python3
"""
优化版Whisper语音识别
学习硅基流动优点，提升准确率
"""

import whisper
import sys
import os

def transcribe_optimized(audio_path):
    """使用优化参数识别语音"""
    
    # 加载Medium模型
    model = whisper.load_model("medium")
    
    # 优化参数（学习硅基流动）
    result = model.transcribe(
        audio_path,
        language="zh",
        temperature=0.2,  # 降低随机性，提高准确性
        initial_prompt=(
            "这是关于AI助手、技能、功能的对话。"
            "关键词：技能、能力、功能、帮助、服务。"
            "常用句式：你有什么技能？你会做什么？你能帮我什么？"
        ),
        word_timestamps=True,
        fp16=False  # CPU模式
    )
    
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 whisper_optimized.py <音频文件>")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    
    if not os.path.exists(audio_file):
        print(f"❌ 文件不存在: {audio_file}")
        sys.exit(1)
    
    print("🔊 优化版Whisper识别...")
    result = transcribe_optimized(audio_file)
    
    print("\n" + "=" * 60)
    print("📝 识别结果：")
    print("=" * 60)
    print(result["text"])
    
    if 'segments' in result:
        print("\n" + "=" * 60)
        print("📊 时间轴：")
        print("=" * 60)
        for seg in result['segments']:
            print(f"  [{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['text']}")
    
    print("\n✅ 识别完成")
