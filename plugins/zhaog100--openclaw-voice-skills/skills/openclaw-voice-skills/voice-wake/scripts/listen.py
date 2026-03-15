#!/usr/bin/env python3
"""
Voice Wake - 语音唤醒功能（简化版）
使用Whisper检测唤醒词，无需Porcupine
"""

import sys
import signal
from pathlib import Path

try:
    import pyaudio
    import whisper
    import numpy as np
except ImportError as e:
    print(f"❌ 缺少依赖: {e}")
    print("\n安装命令:")
    print("  sudo apt install python3-pyaudio")
    print("  pip3 install --break-system-packages openai-whisper numpy")
    sys.exit(1)

# 配置
SAMPLE_RATE = 16000
FRAME_SIZE = 512  # 32ms
WAKE_WORDS = ["嘿米粒", "嗨米粒", "你好米粒", "小助手", "米粒儿"]
WHISPER_MODEL = "medium"
LISTEN_DURATION = 2.0  # 每次监听2秒

class VoiceWake:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.model = None
        self.running = True

        print("🎤 Voice Wake - 语音唤醒（简化版）")
        print("=" * 50)
        print(f"唤醒词: {', '.join(WAKE_WORDS)}")
        print(f"监听时长: {LISTEN_DURATION}秒")
        print(f"Whisper模型: {WHISPER_MODEL}")

    def init_whisper(self):
        """初始化Whisper"""
        print("\n⏳ 加载Whisper模型...")
        self.model = whisper.load_model(WHISPER_MODEL)
        print("✅ Whisper模型已加载")

    def listen_audio(self):
        """监听一段音频"""
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=FRAME_SIZE
        )

        frames = []
        frames_needed = int(LISTEN_DURATION * SAMPLE_RATE / FRAME_SIZE)

        try:
            for _ in range(frames_needed):
                frame = stream.read(FRAME_SIZE, exception_on_overflow=False)
                frames.append(frame)
        finally:
            stream.stop_stream()
            stream.close()

        # 转换为numpy数组
        audio_data = b''.join(frames)
        audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

        return audio_array

    def detect_wake_word(self, audio_array):
        """检测唤醒词"""
        print("🔍 检测唤醒词...")

        # 使用Whisper识别
        result = self.model.transcribe(audio_array, language='zh', temperature=0.2)
        text = result['text'].strip().lower()

        print(f"📝 识别: {text}")

        # 检查是否包含唤醒词
        for wake_word in WAKE_WORDS:
            if wake_word in text:
                return True, text

        return False, text

    def activate(self):
        """激活助手"""
        print("\n✨ 唤醒成功！")
        print("🎤 请说指令...")
        # 这里可以集成OpenClaw处理指令
        print("（功能待集成）")

    def run(self):
        """运行唤醒检测"""
        print("\n🚀 启动语音唤醒检测")
        print(f"请说唤醒词: {', '.join(WAKE_WORDS)}")
        print("按Ctrl+C退出\n")

        self.init_whisper()

        try:
            cycle = 0
            while self.running:
                cycle += 1
                print(f"[周期{cycle}] 👂 监听中...")

                # 监听音频
                audio_array = self.listen_audio()

                # 检测唤醒词
                detected, text = self.detect_wake_word(audio_array)

                if detected:
                    self.activate()
                    # 暂停一下避免连续触发
                    import time
                    time.sleep(2)

        except KeyboardInterrupt:
            print("\n\n👋 用户中断")

        print("\n✅ Voice Wake已退出")

    def stop(self):
        """停止监听"""
        self.running = False

def main():
    wake = VoiceWake()

    # 信号处理
    def signal_handler(sig, frame):
        wake.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    wake.run()

if __name__ == "__main__":
    main()
