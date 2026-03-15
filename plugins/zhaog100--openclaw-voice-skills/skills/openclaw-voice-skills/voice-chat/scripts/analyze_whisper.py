#!/usr/bin/env python3
"""
分析Whisper识别错误并优化
"""

import whisper
import json

# 加载模型
model = whisper.load_model("medium")

# 测试音频
audio_file = "/home/zhaog/.openclaw/qqbot/downloads/240268c7add915f6649c7aeff0a8b14c_1772509376180.wav"

print("🔍 分析Whisper识别结果...")
print("=" * 60)

# 1. 标准识别
result1 = model.transcribe(audio_file, language="zh")
print(f"\n标准模式：{result1['text']}")

# 2. 增加temperature（提高准确性）
result2 = model.transcribe(audio_file, language="zh", temperature=0.2)
print(f"温度0.2：{result2['text']}")

# 3. 增加initial_prompt（引导识别）
prompt = "这是关于AI助手技能的对话。关键词：技能、能力、功能。"
result3 = model.transcribe(audio_file, language="zh", initial_prompt=prompt)
print(f"引导模式：{result3['text']}")

# 4. 组合优化
result4 = model.transcribe(
    audio_file, 
    language="zh", 
    temperature=0.2,
    initial_prompt=prompt,
    word_timestamps=True
)
print(f"组合优化：{result4['text']}")

# 5. 详细分析
print("\n" + "=" * 60)
print("📊 详细分析：")
if 'segments' in result4:
    for seg in result4['segments']:
        print(f"  [{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['text']}")

print("\n✅ 分析完成")
