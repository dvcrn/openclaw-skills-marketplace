#!/usr/bin/env python3
"""
语音对话脚本
实现完整的语音对话流程：录音 → 识别 → AI处理 → 合成 → 播放
"""

import sys
import os
import tempfile
import time

def record_audio(duration: int = 5, output_file: str = None) -> str:
    """
    录制音频
    
    Args:
        duration: 录音时长（秒）
        output_file: 输出文件路径
    
    Returns:
        音频文件路径
    """
    if not output_file:
        output_file = tempfile.mktemp(suffix=".wav")
    
    print(f"🎤 录音中...（{duration}秒）")
    
    try:
        import sounddevice as sd
        import soundfile as sf
        
        # 录音
        fs = 44100  # 采样率
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()  # 等待录音完成
        
        # 保存
        sf.write(output_file, recording, fs)
        print(f"✅ 录音完成：{output_file}")
        
        return output_file
        
    except ImportError:
        print("❌ 错误：未安装sounddevice和soundfile")
        print("请运行：pip install sounddevice soundfile")
        sys.exit(1)


def recognize_audio(audio_file: str) -> str:
    """
    识别音频文件
    
    Args:
        audio_file: 音频文件路径
    
    Returns:
        识别出的文字
    """
    try:
        import whisper
        
        print("🔊 加载Whisper模型...")
        model = whisper.load_model("base")
        
        print(f"🎤 识别音频：{audio_file}...")
        result = model.transcribe(audio_file, language="zh")
        
        return result["text"]
        
    except ImportError:
        print("❌ 错误：未安装openai-whisper")
        print("请运行：pip install openai-whisper")
        sys.exit(1)


def ai_process(text: str) -> str:
    """
    AI处理文字（模拟）
    
    Args:
        text: 输入文字
    
    Returns:
        AI回复
    """
    # 简单模拟AI回复
    # 实际使用时应该调用OpenClaw API
    responses = {
        "你好": "你好！我是米粒儿，有什么可以帮你的吗？",
        "你是谁": "我是米粒儿，你的AI助手！",
        "今天天气": "抱歉，我还没有联网，不知道今天的天气。",
        "默认": "我听到了：{text}"
    }
    
    # 查找匹配的回复
    for key, response in responses.items():
        if key in text:
            if key == "默认":
                return response.format(text=text)
            return response
    
    return responses["默认"].format(text=text)


def speak_text(text: str, output_file: str = None) -> None:
    """
    合成并播放语音
    
    Args:
        text: 要合成的文字
        output_file: 输出文件路径（可选）
    """
    try:
        import pyttsx3
        
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)
        
        print(f"🔊 合成语音：{text}")
        
        if output_file:
            engine.save_to_file(text, output_file)
            engine.runAndWait()
            print(f"✅ 已保存到：{output_file}")
        else:
            engine.say(text)
            engine.runAndWait()
            print("✅ 播放完成")
            
    except ImportError:
        print("❌ 错误：未安装pyttsx3")
        print("请运行：pip install pyttsx3")
        sys.exit(1)


def voice_chat(duration: int = 5, save_audio: bool = False):
    """
    完整的语音对话流程
    
    Args:
        duration: 录音时长（秒）
        save_audio: 是否保存音频文件
    """
    print("\n" + "="*50)
    print("🌾 米粒儿语音对话")
    print("="*50)
    
    # 1. 录音
    audio_file = None
    if save_audio:
        audio_file = "voice_chat.wav"
    audio_file = record_audio(duration, audio_file)
    
    # 2. 识别
    print("\n📝 识别中...")
    user_text = recognize_audio(audio_file)
    print(f"👤 你说：{user_text}")
    
    # 3. AI处理
    print("\n🤖 AI处理中...")
    ai_response = ai_process(user_text)
    print(f"🌾 米粒儿：{ai_response}")
    
    # 4. 语音合成
    print("\n🔊 合成回复...")
    response_audio = "response.mp3" if save_audio else None
    speak_text(ai_response, response_audio)
    
    # 5. 清理临时文件
    if not save_audio and os.path.exists(audio_file):
        os.remove(audio_file)
    
    print("\n" + "="*50)
    print("✅ 对话完成")
    print("="*50 + "\n")


def continuous_chat():
    """
    持续对话模式
    """
    print("\n" + "="*50)
    print("🌾 米粒儿语音对话（持续模式）")
    print("按 Ctrl+C 退出")
    print("="*50 + "\n")
    
    try:
        while True:
            voice_chat(duration=5, save_audio=False)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 再见！")


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "continuous":
        continuous_chat()
    else:
        voice_chat()


if __name__ == "__main__":
    main()
