#!/usr/bin/env python3
"""
VAD测试 - 语音活动检测测试脚本
测试WebRTC VAD是否正常工作
"""

import audioop
import sys
from pathlib import Path

# 尝试导入webrtcvad
try:
    import webrtcvad
    print("✅ webrtcvad已安装")
except ImportError:
    print("❌ webrtcvad未安装")
    print("安装命令: pip3 install --break-system-packages webrtcvad")
    sys.exit(1)

# 尝试导入pyaudio
try:
    import pyaudio
    print("✅ pyaudio已安装")
except ImportError:
    print("❌ pyaudio未安装")
    print("安装命令: sudo apt install python3-pyaudio")
    sys.exit(1)

# VAD配置
VAD_MODE = 3  # 0-3, 3最敏感
SAMPLE_RATE = 16000  # 16kHz
FRAME_DURATION = 30  # 30ms帧长
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION / 1000)

def test_vad():
    """测试VAD功能"""
    print("\n🎤 开始VAD测试...")
    print(f"配置: VAD模式={VAD_MODE}, 采样率={SAMPLE_RATE}Hz, 帧长={FRAME_DURATION}ms")

    # 创建VAD实例
    vad = webrtcvad.Vad(VAD_MODE)

    # 初始化音频
    audio = pyaudio.PyAudio()

    # 打开麦克风流
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=FRAME_SIZE
    )

    print("✅ 麦克风已打开")
    print("\n📢 请说话测试VAD检测...")
    print("按Ctrl+C退出\n")

    try:
        frame_count = 0
        speech_frames = 0

        while True:
            # 读取音频帧
            frame = stream.read(FRAME_SIZE, exception_on_overflow=False)

            # VAD检测
            is_speech = vad.is_speech(frame, SAMPLE_RATE)

            frame_count += 1
            if is_speech:
                speech_frames += 1
                print(f"🎤 检测到说话 (帧{frame_count}, 语音帧{speech_frames})")
            else:
                if frame_count % 10 == 0:
                    print(f"🔇 静音中 (帧{frame_count}, 语音帧{speech_frames})")

    except KeyboardInterrupt:
        print(f"\n\n📊 测试结束:")
        print(f"  总帧数: {frame_count}")
        print(f"  语音帧: {speech_frames}")
        print(f"  语音比例: {speech_frames/frame_count*100:.1f}%")

    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()
        print("✅ 音频已关闭")

if __name__ == "__main__":
    test_vad()
