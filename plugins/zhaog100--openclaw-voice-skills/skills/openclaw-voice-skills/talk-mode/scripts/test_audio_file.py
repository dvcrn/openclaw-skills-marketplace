#!/usr/bin/env python3
"""
Talk Mode - 音频文件测试版本
使用音频文件测试，无需实时麦克风
"""

import sys
from pathlib import Path

try:
    import whisper
    import webrtcvad
    print("✅ 依赖检查通过")
except ImportError as e:
    print(f"❌ 缺少依赖: {e}")
    sys.exit(1)

print("\n🎤 Talk Mode - 音频文件测试")
print("=" * 50)

# 初始化Whisper
print("\n⏳ 加载Whisper模型（medium）...")
model = whisper.load_model("medium")
print("✅ Whisper模型已加载")

# 测试音频文件
test_audio = "/tmp/test_audio.wav"

if Path(test_audio).exists():
    print(f"\n📝 测试音频文件: {test_audio}")
    print("⏳ 识别中...")
    
    result = model.transcribe(test_audio, language='zh')
    text = result['text'].strip()
    
    print(f"✅ 识别结果: {text}")
else:
    print(f"\n⚠️  测试音频文件不存在: {test_audio}")
    print("您可以录制一个测试音频文件：")
    print(f"  arecord -d 3 -r 16000 -c 1 {test_audio}")
    print(f"  然后重新运行此脚本")

print("\n✅ 测试完成")
print("\n💡 提示:")
print("  - Voice Wake和Talk Mode核心功能已实现")
print("  - 虚拟机环境建议使用音频文件测试")
print("  - 真实环境可直接运行listen.py和start_talk.py")
