#!/usr/bin/env python3
"""
硅基流动语音识别测试
"""

import requests
import sys
import os
import time

# API配置
API_KEY = "sk-mvntgiydawtmasivgmnozatkjrkwhcwmrclptszcyjdrdgto"
API_URL = "https://api.siliconflow.cn/v1/audio/transcriptions"

def recognize_audio(audio_path):
    """使用硅基流动识别音频"""

    if not os.path.exists(audio_path):
        print(f"❌ 文件不存在: {audio_path}")
        return None

    print(f"🔊 硅基流动识别: {audio_path}")
    print(f"   文件大小: {os.path.getsize(audio_path) / 1024:.1f} KB")

    # 读取音频文件
    with open(audio_path, "rb") as f:
        audio_data = f.read()

    print(f"🚀 发送请求...")

    # 计时
    start_time = time.time()

    # 发送请求
    response = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {API_KEY}"},
        files={"file": (os.path.basename(audio_path), audio_data, "audio/wav")},
        data={"model": "FunAudioLLM/SenseVoiceSmall"},
        timeout=60
    )

    elapsed_time = time.time() - start_time

    print(f"   响应时间: {elapsed_time:.1f}秒")

    # 解析结果
    if response.status_code == 200:
        result = response.json()
        text = result.get("text", "")
        print(f"\n✅ 识别成功")
        print(f"📝 结果: {text}")
        return text
    else:
        print(f"❌ 识别失败: {response.status_code}")
        print(f"   错误: {response.text}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 siliconflow_recognize.py <音频文件>")
        sys.exit(1)

    audio_file = sys.argv[1]
    recognize_audio(audio_file)
