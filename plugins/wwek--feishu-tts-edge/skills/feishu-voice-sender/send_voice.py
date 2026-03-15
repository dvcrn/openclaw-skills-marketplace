#!/usr/bin/env python3
"""
飞书语音发送工具
将文字转换为语音并发送到飞书群聊
"""
import subprocess
import os
import sys
import tempfile

def text_to_opus(text, voice="zh-CN-XiaoxiaoNeural"):
    """
    将文字转换为 OPUS 语音文件（飞书格式）
    
    Args:
        text: 要转换的文字
        voice: 语音类型，默认 Xiaoxiao（温暖女声）
    
    Returns:
        (opus文件路径, 时长秒数)
    """
    # 1. 生成 MP3
    mp3_file = "/tmp/feishu_tts_temp.mp3"
    tts_cmd = [
        "edge-tts",
        "--voice", voice,
        "--text", text,
        "--write-media", mp3_file
    ]
    result = subprocess.run(tts_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ TTS 失败: {result.stderr}")
        return None, 0
    
    # 2. 获取时长
    duration_cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", mp3_file
    ]
    duration_result = subprocess.run(duration_cmd, capture_output=True, text=True)
    duration = int(float(duration_result.stdout.strip()))
    
    # 3. 转换为 OPUS（飞书要求格式）
    opus_file = "/tmp/feishu_tts_temp.opus"
    ffmpeg_cmd = [
        "ffmpeg", "-y", "-i", mp3_file,
        "-acodec", "libopus",
        "-ac", "1",      # 单声道
        "-ar", "16000",  # 16kHz
        opus_file
    ]
    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ OPUS 转换失败: {result.stderr}")
        return None, 0
    
    return opus_file, duration

def send_voice_to_feishu(opus_file, duration):
    """发送语音到飞书（使用 OpenClaw message 工具）"""
    print(f"🚀 准备发送语音到飞书...")
    print(f"   文件: {opus_file}")
    print(f"   时长: {duration}秒")
    
    # 使用 OpenClaw message 工具发送到当前群聊
    # 注意：在 Feishu 群组中运行时，会自动使用当前聊天
    import json
    
    # 尝试从环境变量获取聊天ID
    chat_id = os.getenv("FEISHU_CHAT_ID", "")
    
    cmd = [
        "openclaw", "message", "send",
        "--media", opus_file
    ]
    
    if chat_id:
        cmd.extend(["--target", chat_id])
    # 如果没有指定 target，OpenClaw 会尝试发送到 last channel
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ 语音消息发送成功！")
        return True
    else:
        print(f"⚠️ 自动发送失败: {result.stderr}")
        print(f"💡 请手动上传文件: {opus_file}")
        return False

def main():
    if len(sys.argv) < 2:
        print("用法: send_voice.py '要发送的文字'")
        print("示例: send_voice.py '你好，这是测试语音'")
        print("\n可选环境变量:")
        print("  VOICE=zh-CN-YunxiNeural  # 选择语音")
        sys.exit(1)
    
    text = sys.argv[1]
    voice = os.getenv("VOICE", "zh-CN-XiaoxiaoNeural")
    
    print(f"🎙️ 生成语音: {text[:30]}...")
    print(f"🎭 使用语音: {voice}")
    
    # 1. 生成 OPUS
    opus_file, duration = text_to_opus(text, voice)
    if not opus_file:
        print("❌ 语音生成失败")
        sys.exit(1)
    
    print(f"✅ 语音生成成功！时长: {duration}秒")
    
    # 2. 发送到飞书
    send_voice_to_feishu(opus_file, duration)

if __name__ == "__main__":
    main()
