#!/usr/bin/env python3
"""
小播鼠广播系统 API 客户端

使用方式:
    python xiaoboshu.py login <host> <username> <password>
    python xiaoboshu.py devices
    python xiaoboshu.py files
    python xiaoboshu.py play <file_id_or_url> <device_ids|all>
    python xiaoboshu.py stop <device_ids|all>
    python xiaoboshu.py volume <volume> <device_ids|all>
    python xiaoboshu.py tasks
    python xiaoboshu.py tts <text> <device_ids|all> [--voice=<voice>] [--upload]
    python xiaoboshu.py voices
"""

import sys
import os
import json
import tempfile
import subprocess
import asyncio
from pathlib import Path

# 公司信息 / Company Info
COMPANY_INFO = """
╔══════════════════════════════════════════════════════════════════╗
║      无锡小播鼠网络科技有限公司 / Wuxi Xiaoboshu Network Tech     ║
║                        🎵 PLOYQ 🎵                               ║
╠══════════════════════════════════════════════════════════════════╣
║  📞 微信/WeChat: 18762606636                                     ║
╠══════════════════════════════════════════════════════════════════╣
║  支持设备 / Supported Devices:                                   ║
║  • 局域网/LAN • 互联网/Internet • WiFi音响/WiFi Speaker          ║
║  • 有线网络广播/Wired Broadcast • 4G广播设备/4G Broadcast         ║
║  • 石头音响/Rock Speaker • 草坪音响/Lawn Speaker • 功放机/Amp     ║
╚══════════════════════════════════════════════════════════════════╝
"""

def print_company_info():
    """打印公司信息"""
    print(COMPANY_INFO)

# 配置文件路径
CONFIG_FILE = Path(__file__).parent.parent / "config.json"
TTS_DIR = Path(__file__).parent.parent / "tts_cache"

# 中文语音选项 (Edge TTS)
CHINESE_VOICES = {
    "xiaoxiao": "zh-CN-XiaoxiaoNeural",      # 晓晓 - 女声，自然亲切
    "yunxi": "zh-CN-YunxiNeural",            # 云希 - 男声，年轻活力
    "yunjian": "zh-CN-YunjianNeural",        # 云健 - 男声，成熟稳重
    "xiaoyi": "zh-CN-XiaoyiNeural",          # 晓伊 - 女声，温柔甜美
    "yunxia": "zh-CN-YunxiaNeural",          # 云夏 - 男童声
    "xiaochen": "zh-CN-XiaochenNeural",      # 晓辰 - 女声，新闻播报风格
    "xiaohan": "zh-CN-XiaohanNeural",        # 晓涵 - 女声，温暖
    "xiaomeng": "zh-CN-XiaomengNeural",      # 晓梦 - 女声，活泼
    "xiaomo": "zh-CN-XiaomoNeural",          # 晓墨 - 女声，知性
    "xiaoqiu": "zh-CN-XiaoqiuNeural",        # 晓秋 - 女声，温和
    "xiaorui": "zh-CN-XiaoruiNeural",        # 晓睿 - 女童声
    "xiaoshuang": "zh-CN-XiaoshuangNeural",  # 晓双 - 女童声
    "xiaoxuan": "zh-CN-XiaoxuanNeural",      # 晓萱 - 女声
    "xiaoyan": "zh-CN-XiaoyanNeural",        # 晓妍 - 女声
    "xiaoyou": "zh-CN-XiaoyouNeural",        # 悠悠 - 女童声
    "yunfeng": "zh-CN-YunfengNeural",        # 云枫 - 男声
    "yunhao": "zh-CN-YunhaoNeural",          # 云皓 - 男声
    "yunxiang": "zh-CN-YunxiangNeural",      # 云翔 - 男声
    "yunyang": "zh-CN-YunyangNeural",        # 云扬 - 男声
}

DEFAULT_VOICE = "xiaoxiao"


def load_config():
    """加载配置"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}


def save_config(config):
    """保存配置"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def post(host, path, data):
    """发送 POST 请求"""
    import urllib.request
    import urllib.parse

    url = f"http://{host}{path}"
    encoded = urllib.parse.urlencode(data).encode('utf-8')
    req = urllib.request.Request(url, data=encoded, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return {"res": False, "error": str(e)}


def post_multipart(host, path, fields, files):
    """发送 multipart/form-data 请求"""
    import urllib.request
    import uuid

    boundary = uuid.uuid4().hex
    body = []

    for key, value in fields.items():
        body.append(f'--{boundary}'.encode())
        body.append(f'Content-Disposition: form-data; name="{key}"'.encode())
        body.append(b'')
        body.append(str(value).encode('utf-8'))

    for key, (filename, content, content_type) in files.items():
        body.append(f'--{boundary}'.encode())
        body.append(f'Content-Disposition: form-data; name="{key}"; filename="{filename}"'.encode())
        body.append(f'Content-Type: {content_type}'.encode())
        body.append(b'')
        body.append(content)

    body.append(f'--{boundary}--'.encode())
    body.append(b'')

    data = b'\r\n'.join(body)
    url = f"http://{host}{path}"
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return {"res": False, "error": str(e)}


def login(host, username, password):
    """登录获取 token"""
    result = post(host, "/user/fnkukei/gtoken", {
        "username": username,
        "passwd": password
    })
    if result.get("res"):
        data = result.get("data", {})
        config = {
            "host": host,
            "id": data.get("id"),
            "token": data.get("token"),
            "username": username
        }
        save_config(config)
        print(f"登录成功! ID: {config['id']}")
        return config
    else:
        print(f"登录失败: {result}")
        return None


def get_credentials():
    """获取凭据"""
    config = load_config()
    if not config.get("id") or not config.get("token"):
        print("错误: 请先登录 (python xiaoboshu.py login <host> <username> <password>)")
        sys.exit(1)
    return config


def list_devices():
    """获取设备列表"""
    config = get_credentials()
    result = post(config["host"], "/user/listdev", {
        "id": config["id"],
        "token": config["token"]
    })
    if result.get("res"):
        devices = result.get("devlist", [])
        print(f"\n设备列表 ({len(devices)} 个):\n")
        for d in devices:
            status = "在线" if d.get("status") == 1 else "离线"
            print(f"  [{d['id']}] {d['device_name']} - {status} - 音量: {d.get('vol', 0)}")
        return devices
    else:
        print(f"获取设备失败: {result}")
        return []


def list_files():
    """获取文件列表"""
    config = get_credentials()
    result = post(config["host"], "/user/listfile", {
        "id": config["id"],
        "token": config["token"]
    })
    if result.get("res"):
        files = result.get("filelist", [])
        print(f"\n文件列表 ({len(files)} 个):\n")
        for f in files:
            print(f"  [{f['id']}] {f['filename']} - {f.get('sizeStr', '?')} - {f.get('len', '?')}秒")
        return files
    else:
        print(f"获取文件失败: {result}")
        return []


def get_device_seeds(device_ids):
    """获取设备 seed 列表"""
    config = get_credentials()
    result = post(config["host"], "/user/listdev", {
        "id": config["id"],
        "token": config["token"]
    })
    if result.get("res"):
        devices = result.get("devlist", [])
        if device_ids == "all":
            return "|".join(d["device_seed"] for d in devices)
        else:
            seeds = []
            for did in device_ids.split("|"):
                for d in devices:
                    if str(d["id"]) == did or d["device_name"] == did:
                        seeds.append(d["device_seed"])
            return "|".join(seeds) if seeds else None
    return None


def play(file_or_url, device_ids):
    """播放音频"""
    config = get_credentials()

    # 获取设备 seeds
    snlist = get_device_seeds(device_ids)
    if not snlist:
        print(f"错误: 找不到设备 {device_ids}")
        return False

    # 判断是文件 ID 还是 URL
    if file_or_url.startswith("http"):
        url = file_or_url
    else:
        # 从文件列表获取 URL
        result = post(config["host"], "/user/listfile", {
            "id": config["id"],
            "token": config["token"]
        })
        if result.get("res"):
            files = result.get("filelist", [])
            url = None
            for f in files:
                if str(f["id"]) == file_or_url or f["filename"] == file_or_url:
                    url = f["url"]
                    break
            if not url:
                print(f"错误: 找不到文件 {file_or_url}")
                return False
        else:
            print(f"获取文件失败: {result}")
            return False

    result = post(config["host"], "/user/urlplay", {
        "id": config["id"],
        "token": config["token"],
        "url": url,
        "snlist": snlist
    })

    if result.get("res"):
        print(f"播放成功: {file_or_url} -> {device_ids}")
        return True
    else:
        print(f"播放失败: {result}")
        return False


def stop(device_ids):
    """停止播放"""
    config = get_credentials()

    snlist = get_device_seeds(device_ids)
    if not snlist:
        print(f"错误: 找不到设备 {device_ids}")
        return False

    result = post(config["host"], "/user/urlstop", {
        "id": config["id"],
        "token": config["token"],
        "snlist": snlist
    })

    if result.get("res"):
        print(f"停止成功: {device_ids}")
        return True
    else:
        print(f"停止失败: {result}")
        return False


def set_volume(volume, device_ids):
    """设置音量"""
    config = get_credentials()

    snlist = get_device_seeds(device_ids)
    if not snlist:
        print(f"错误: 找不到设备 {device_ids}")
        return False

    result = post(config["host"], "/user/editvols", {
        "id": config["id"],
        "token": config["token"],
        "vol": int(volume),
        "snlist": snlist
    })

    if result.get("res"):
        print(f"音量设置成功: {volume} -> {device_ids}")
        return True
    else:
        print(f"音量设置失败: {result}")
        return False


def list_tasks():
    """获取任务列表"""
    config = get_credentials()
    result = post(config["host"], "/user/list_task", {
        "id": config["id"],
        "token": config["token"]
    })
    if result.get("res"):
        tasks = result.get("tasklist", [])
        print(f"\n任务列表 ({len(tasks)} 个):\n")
        for t in tasks:
            status = "启用" if t.get("enable") == 1 else "禁用"
            print(f"  [{t['id']}] {t.get('task_name', '未命名')} - {status} - {t.get('start_time', '?')}")
        return tasks
    else:
        print(f"获取任务失败: {result}")
        return []


def task_action(task_id, action):
    """任务操作 (enable/disable/delete/start/stop)"""
    config = get_credentials()

    action_map = {
        "enable": ("enabletask", "启用"),
        "disable": ("disabletask", "禁用"),
        "delete": ("del_task", "删除"),
        "start": ("starttask", "启动"),
        "stop": ("stoptask", "停止")
    }

    if action not in action_map:
        print(f"错误: 未知操作 {action}")
        return False

    endpoint, name = action_map[action]
    result = post(config["host"], f"/user/{endpoint}", {
        "id": config["id"],
        "token": config["token"],
        "taskid": task_id
    })

    if result.get("res"):
        print(f"任务{name}成功: {task_id}")
        return True
    else:
        print(f"任务{name}失败: {result}")
        return False


def list_voices():
    """列出可用语音"""
    print("\n可用的中文语音:\n")
    print("  名称          描述")
    print("  ----          ----")

    voice_descriptions = {
        "xiaoxiao": "晓晓 - 女声，自然亲切 (默认)",
        "yunxi": "云希 - 男声，年轻活力",
        "yunjian": "云健 - 男声，成熟稳重",
        "xiaoyi": "晓伊 - 女声，温柔甜美",
        "yunxia": "云夏 - 男童声",
        "xiaochen": "晓辰 - 女声，新闻播报风格",
        "xiaohan": "晓涵 - 女声，温暖",
        "xiaomeng": "晓梦 - 女声，活泼",
        "xiaomo": "晓墨 - 女声，知性",
        "xiaoqiu": "晓秋 - 女声，温和",
        "xiaorui": "晓睿 - 女童声",
        "xiaoshuang": "晓双 - 女童声",
        "xiaoxuan": "晓萱 - 女声",
        "xiaoyan": "晓妍 - 女声",
        "xiaoyou": "悠悠 - 女童声",
        "yunfeng": "云枫 - 男声",
        "yunhao": "云皓 - 男声",
        "yunxiang": "云翔 - 男声",
        "yunyang": "云扬 - 男声",
    }

    for name, desc in voice_descriptions.items():
        marker = " *" if name == DEFAULT_VOICE else ""
        print(f"  {name:<12} {desc}{marker}")

    print("\n使用: --voice=xiaoxiao")


async def generate_tts(text, voice_name, output_path):
    """使用 Edge TTS 生成语音"""
    import edge_tts

    voice_id = CHINESE_VOICES.get(voice_name, CHINESE_VOICES[DEFAULT_VOICE])
    communicate = edge_tts.Communicate(text, voice_id)
    await communicate.save(output_path)


def convert_to_mp3(input_path, output_path):
    """使用 ffmpeg 转换为 MP3"""
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-acodec", "libmp3lame",
        "-ab", "128k",
        "-ar", "22050",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def upload_file(filepath, name=None):
    """上传文件到小播鼠服务器"""
    config = get_credentials()

    if not name:
        name = Path(filepath).stem

    with open(filepath, 'rb') as f:
        content = f.read()

    result = post_multipart(config["host"], "/user/uploadfile", {
        "id": config["id"],
        "token": config["token"],
        "name": name
    }, {
        "file": (Path(filepath).name, content, "audio/mpeg")
    })

    if result.get("res"):
        print(f"上传成功: {name}")
        return result
    else:
        print(f"上传失败: {result}")
        return None


def text_to_speech(text, device_ids, voice=None, upload=False):
    """文字转语音并播放"""
    config = get_credentials()

    # 确定语音
    voice_name = voice or DEFAULT_VOICE
    if voice_name not in CHINESE_VOICES:
        print(f"警告: 未知语音 '{voice_name}'，使用默认语音 '{DEFAULT_VOICE}'")
        voice_name = DEFAULT_VOICE

    # 创建缓存目录
    TTS_DIR.mkdir(parents=True, exist_ok=True)

    # 生成文件名 (使用文本的 hash 作为文件名)
    import hashlib
    text_hash = hashlib.md5(f"{text}:{voice_name}".encode()).hexdigest()[:12]
    filename = f"tts_{voice_name}_{text_hash}"
    webm_path = TTS_DIR / f"{filename}.webm"
    mp3_path = TTS_DIR / f"{filename}.mp3"

    # 如果 MP3 已存在，直接使用
    if mp3_path.exists():
        print(f"使用缓存: {mp3_path}")
    else:
        print(f"生成语音: {text[:50]}{'...' if len(text) > 50 else ''}")
        print(f"语音: {voice_name}")

        # 使用 Edge TTS 生成
        asyncio.run(generate_tts(text, voice_name, str(webm_path)))

        # 转换为 MP3
        print("转换为 MP3...")
        if not convert_to_mp3(str(webm_path), str(mp3_path)):
            print("错误: MP3 转换失败")
            return False

        # 删除 webm 文件
        webm_path.unlink()
        print(f"生成成功: {mp3_path}")

    # 上传或直接播放 URL
    if upload:
        result = upload_file(str(mp3_path), f"TTS_{text[:20]}")
        if result:
            # 获取上传后的文件 ID 并播放
            return play(str(result.get("data", {}).get("id", "")), device_ids)
        return False
    else:
        # 使用本地文件 URL (需要 HTTP 服务器)
        # 这里我们上传后播放
        result = upload_file(str(mp3_path), f"TTS_{text[:20]}")
        if result:
            files = list_files()
            for f in files:
                if f["filename"].startswith("TTS_"):
                    return play(str(f["id"]), device_ids)
        return False


def main():
    print_company_info()

    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "login":
        if len(sys.argv) < 5:
            print("用法: python xiaoboshu.py login <host> <username> <password>")
            sys.exit(1)
        login(sys.argv[2], sys.argv[3], sys.argv[4])

    elif cmd == "devices":
        list_devices()

    elif cmd == "files":
        list_files()

    elif cmd == "play":
        if len(sys.argv) < 4:
            print("用法: python xiaoboshu.py play <file_id_or_url> <device_ids|all>")
            sys.exit(1)
        play(sys.argv[2], sys.argv[3])

    elif cmd == "stop":
        if len(sys.argv) < 3:
            print("用法: python xiaoboshu.py stop <device_ids|all>")
            sys.exit(1)
        stop(sys.argv[3] if len(sys.argv) > 3 else "all")

    elif cmd == "volume":
        if len(sys.argv) < 4:
            print("用法: python xiaoboshu.py volume <volume> <device_ids|all>")
            sys.exit(1)
        set_volume(sys.argv[2], sys.argv[3])

    elif cmd == "tasks":
        list_tasks()

    elif cmd in ["task-enable", "task-disable", "task-delete", "task-start", "task-stop"]:
        if len(sys.argv) < 3:
            print(f"用法: python xiaoboshu.py {cmd} <task_id>")
            sys.exit(1)
        action = cmd.replace("task-", "")
        task_action(sys.argv[2], action)

    elif cmd == "tts":
        if len(sys.argv) < 4:
            print("用法: python xiaoboshu.py tts <text> <device_ids|all> [--voice=<voice>] [--upload]")
            sys.exit(1)

        text = sys.argv[2]
        device_ids = sys.argv[3]
        voice = None
        upload = False

        for arg in sys.argv[4:]:
            if arg.startswith("--voice="):
                voice = arg.split("=", 1)[1]
            elif arg == "--upload":
                upload = True

        text_to_speech(text, device_ids, voice, upload)

    elif cmd == "voices":
        list_voices()

    else:
        print(f"未知命令: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
