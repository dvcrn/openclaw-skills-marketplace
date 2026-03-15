#!/usr/bin/env python3
"""
飞书语音消息完整发送流程
1. 生成 OPUS 语音
2. 上传到飞书获取 file_key
3. 发送 audio 类型消息
"""
import subprocess
import os
import sys
import json
import requests

def get_feishu_token():
    """从 OpenClaw 配置获取飞书 Token"""
    # 读取配置文件
    config_path = os.path.expanduser("~/.openclaw/openclaw.json")
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        app_id = config.get('channels', {}).get('feishu', {}).get('appId')
        app_secret = config.get('channels', {}).get('feishu', {}).get('appSecret')
        return app_id, app_secret
    except Exception as e:
        print(f"❌ 读取配置失败: {e}")
        return None, None

def get_tenant_token(app_id, app_secret):
    """获取飞书 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json"}
    data = {"app_id": app_id, "app_secret": app_secret}
    
    resp = requests.post(url, headers=headers, json=data)
    if resp.status_code == 200:
        result = resp.json()
        if result.get("code") == 0:
            return result.get("tenant_access_token")
    print(f"❌ 获取 Token 失败: {resp.text}")
    return None

def text_to_opus(text, voice="zh-CN-XiaoxiaoNeural"):
    """生成 OPUS 语音文件"""
    mp3_file = "/tmp/feishu_tts_temp.mp3"
    opus_file = "/tmp/feishu_tts_16k.opus"
    
    # 1. TTS 生成 MP3
    tts_cmd = ["edge-tts", "--voice", voice, "--text", text, "--write-media", mp3_file]
    result = subprocess.run(tts_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ TTS 失败: {result.stderr}")
        return None, 0
    
    # 2. 获取时长
    duration_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1", mp3_file]
    duration_result = subprocess.run(duration_cmd, capture_output=True, text=True)
    duration_sec = int(float(duration_result.stdout.strip()))
    duration_ms = duration_sec * 1000  # 飞书要求毫秒
    
    # 3. 转换为 OPUS 16kHz
    ffmpeg_cmd = [
        "ffmpeg", "-y", "-i", mp3_file,
        "-acodec", "libopus", "-ac", "1", "-ar", "16000",
        opus_file
    ]
    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ OPUS 转换失败: {result.stderr}")
        return None, 0
    
    return opus_file, duration_ms

def upload_audio(token, opus_file, duration_ms):
    """上传音频到飞书，获取 file_key"""
    url = "https://open.feishu.cn/open-apis/im/v1/files"
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(opus_file, 'rb') as f:
        files = {'file': ('voice.opus', f, 'audio/opus')}
        data = {
            'file_type': 'opus',
            'file_name': 'voice.opus',
            'duration': str(duration_ms)  # 毫秒
        }
        resp = requests.post(url, headers=headers, files=files, data=data)
    
    if resp.status_code == 200:
        result = resp.json()
        if result.get("code") == 0:
            file_key = result.get("data", {}).get("file_key")
            print(f"✅ 上传成功，file_key: {file_key}")
            return file_key
    print(f"❌ 上传失败: {resp.text}")
    return None

def send_voice_message(token, chat_id, file_key):
    """发送语音消息"""
    url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    content = json.dumps({"file_key": file_key})
    data = {
        "receive_id": chat_id,
        "msg_type": "audio",
        "content": content
    }
    
    resp = requests.post(url, headers=headers, json=data)
    if resp.status_code == 200:
        result = resp.json()
        if result.get("code") == 0:
            msg_id = result.get("data", {}).get("message_id")
            print(f"✅ 语音消息发送成功！msg_id: {msg_id}")
            return True
    print(f"❌ 发送失败: {resp.text}")
    return False

def main():
    if len(sys.argv) < 2:
        print("用法: send_voice_full.py '要发送的文字'")
        sys.exit(1)
    
    text = sys.argv[1]
    chat_id = "oc_2c86ce057749a663ae2e852572d92574"
    voice = os.getenv("VOICE", "zh-CN-XiaoxiaoNeural")
    
    print(f"🎙️ 文字: {text[:30]}...")
    print(f"🎭 语音: {voice}")
    
    # 1. 生成 OPUS
    print("\n1️⃣ 生成语音...")
    opus_file, duration_ms = text_to_opus(text, voice)
    if not opus_file:
        sys.exit(1)
    print(f"   ✅ 时长: {duration_ms//1000}秒")
    
    # 2. 获取 Token
    print("\n2️⃣ 获取飞书 Token...")
    app_id, app_secret = get_feishu_token()
    if not app_id or not app_secret:
        print("   ❌ 无法获取 App ID/Secret")
        sys.exit(1)
    
    token = get_tenant_token(app_id, app_secret)
    if not token:
        sys.exit(1)
    print("   ✅ Token 获取成功")
    
    # 3. 上传文件
    print("\n3️⃣ 上传音频...")
    file_key = upload_audio(token, opus_file, duration_ms)
    if not file_key:
        sys.exit(1)
    
    # 4. 发送消息
    print("\n4️⃣ 发送语音消息...")
    if send_voice_message(token, chat_id, file_key):
        print("\n🎉 完成！")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
