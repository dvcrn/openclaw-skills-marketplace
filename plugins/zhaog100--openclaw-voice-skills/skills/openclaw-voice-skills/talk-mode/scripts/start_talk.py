#!/usr/bin/env python3
"""
Talk Mode - 持续对话模式
自动检测说话开始/结束并持续对话
"""

import audioop
import sys
import wave
import tempfile
from pathlib import Path
from collections import deque

# 导入依赖
try:
    import webrtcvad
    import pyaudio
    import whisper
    import pyttsx3
except ImportError as e:
    print(f"❌ 缺少依赖: {e}")
    print("\n安装命令:")
    print("  sudo apt install python3-pyaudio")
    print("  pip3 install --break-system-packages webrtcvad openai-whisper pyttsx3")
    sys.exit(1)

# 配置
VAD_MODE = 3  # VAD灵敏度 (0-3)
SAMPLE_RATE = 16000
FRAME_DURATION = 30  # ms
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION / 1000)
SILENCE_DURATION = 1.0  # 静音判定时长(秒)
MAX_RECORDING_TIME = 30  # 最大录音时长(秒)
WHISPER_MODEL = "medium"  # Whisper模型

class TalkMode:
    def __init__(self):
        self.vad = webrtcvad.Vad(VAD_MODE)
        self.audio = pyaudio.PyAudio()
        self.model = None
        self.tts_engine = None
        self.running = True

        print("🎤 Talk Mode - 持续对话模式")
        print("=" * 50)
        print(f"配置:")
        print(f"  VAD模式: {VAD_MODE}")
        print(f"  采样率: {SAMPLE_RATE}Hz")
        print(f"  静音判定: {SILENCE_DURATION}秒")
        print(f"  最大录音: {MAX_RECORDING_TIME}秒")
        print(f"  Whisper模型: {WHISPER_MODEL}")

    def init_whisper(self):
        """初始化Whisper模型"""
        print("\n⏳ 加载Whisper模型...")
        self.model = whisper.load_model(WHISPER_MODEL)
        print("✅ Whisper模型已加载")

    def init_tts(self):
        """初始化TTS引擎"""
        print("\n⏳ 初始化TTS引擎...")
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)
        self.tts_engine.setProperty('volume', 1.0)
        print("✅ TTS引擎已初始化")

    def is_speech(self, frame):
        """检测是否有人说话"""
        return self.vad.is_speech(frame, SAMPLE_RATE)

    def wait_for_speech(self):
        """等待说话开始"""
        print("\n👂 等待说话...")

        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=FRAME_SIZE
        )

        speech_detected = False
        speech_frames = 0

        try:
            while not speech_detected:
                frame = stream.read(FRAME_SIZE, exception_on_overflow=False)
                if self.is_speech(frame):
                    speech_frames += 1
                    if speech_frames >= 3:  # 连续3帧语音
                        speech_detected = True
                        print("🎤 检测到说话开始")
                else:
                    speech_frames = 0

        finally:
            stream.stop_stream()
            stream.close()

        return True

    def record_until_silence(self):
        """录音直到静音"""
        print("⏺️  开始录音...")

        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=FRAME_SIZE
        )

        frames = []
        silence_frames = 0
        max_frames = int(MAX_RECORDING_TIME * 1000 / FRAME_DURATION)
        silence_threshold = int(SILENCE_DURATION * 1000 / FRAME_DURATION)

        try:
            while len(frames) < max_frames:
                frame = stream.read(FRAME_SIZE, exception_on_overflow=False)
                frames.append(frame)

                if not self.is_speech(frame):
                    silence_frames += 1
                    if silence_frames >= silence_threshold:
                        print(f"🔇 检测到静音 (录音{len(frames)*FRAME_DURATION/1000:.1f}秒)")
                        break
                else:
                    silence_frames = 0

        finally:
            stream.stop_stream()
            stream.close()

        return b''.join(frames)

    def transcribe(self, audio_data):
        """语音识别"""
        print("⏳ 语音识别中...")

        # 保存为临时WAV文件
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            wf = wave.open(f, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_data)
            wf.close()
            temp_file = f.name

        # 使用Whisper识别
        result = self.model.transcribe(temp_file, language='zh')
        text = result['text'].strip()

        # 删除临时文件
        Path(temp_file).unlink()

        return text

    def speak(self, text):
        """语音合成"""
        print(f"💬 回复: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def process_text(self, text):
        """处理识别的文本（这里可以集成OpenClaw）"""
        # 简单的回复逻辑
        if not text or len(text) < 2:
            return "没听清，请再说一遍"

        # 检查退出命令
        if any(word in text for word in ['退出', '再见', '结束']):
            self.running = False
            return "好的，再见！"

        # 默认回复
        return f"收到: {text}"

    def run(self):
        """运行持续对话"""
        print("\n🚀 启动持续对话模式")
        print("说'退出'或'再见'结束对话\n")

        self.init_whisper()
        self.init_tts()

        try:
            while self.running:
                # 等待说话
                self.wait_for_speech()

                # 录音直到静音
                audio_data = self.record_until_silence()

                # 语音识别
                text = self.transcribe(audio_data)
                print(f"📝 识别: {text}")

                # 处理文本
                response = self.process_text(text)

                # 语音回复
                self.speak(response)

        except KeyboardInterrupt:
            print("\n\n👋 用户中断")

        print("\n✅ Talk Mode已退出")

def main():
    talk = TalkMode()
    talk.run()

if __name__ == "__main__":
    main()
