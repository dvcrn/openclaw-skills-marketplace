#!/usr/bin/env python3
"""Muse API 封装层 — v2 中间件接口（skill-api.muse.top）"""

import argparse
import hashlib
import json
import os
import platform
import sys
import uuid
import urllib.request
import urllib.error

BASE_URL = "https://skill-api.muse.top"

# 设备 ID 持久化路径
_DEVICE_ID_PATH = os.path.expanduser("~/.muse/device_id")


def _get_machine_id():
    """获取当前设备唯一 ID，首次生成后持久化到本地文件。

    生成规则：hostname + MAC 地址 + 用户名 → SHA256 取前 16 位 hex。
    若系统信息不可用则 fallback 到随机 UUID。
    已持久化的 ID 直接复用，不重新生成。
    """
    # 优先读取已持久化的 ID
    if os.path.isfile(_DEVICE_ID_PATH):
        stored = open(_DEVICE_ID_PATH).read().strip()
        if stored:
            return stored

    # 生成：基于设备指纹
    try:
        fingerprint = f"{platform.node()}:{uuid.getnode()}:{os.getlogin()}"
        machine_id = hashlib.sha256(fingerprint.encode()).hexdigest()[:16]
    except Exception:
        machine_id = uuid.uuid4().hex[:16]

    # 持久化
    os.makedirs(os.path.dirname(_DEVICE_ID_PATH), exist_ok=True)
    with open(_DEVICE_ID_PATH, "w") as f:
        f.write(machine_id)
    return machine_id


def _auth_headers(token):
    """需要认证的接口：Bearer token + 设备ID"""
    return {
        "Authorization": f"Bearer {token}",
        "X-Device-Id": _get_machine_id(),
        "Content-Type": "application/json",
    }


def _device_headers():
    """仅需设备ID的接口（验证码、登录）"""
    return {
        "X-Device-Id": _get_machine_id(),
        "Content-Type": "application/json",
    }


class MuseAPIError(Exception):
    """API 调用错误 — code 为 HTTP 状态码或 -1（网络错误）/-2（客户端拦截）"""
    def __init__(self, code, msg, data=None):
        self.code = code
        self.msg = msg
        self.data = data
        super().__init__(f"[{code}] {msg}")


def _post(path, body=None, headers=None, timeout=30):
    """通用 POST 请求"""
    url = f"{BASE_URL}{path}"
    data = json.dumps(body or {}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers or {}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        try:
            err_body = json.loads(body_text)
            err_msg = err_body.get("error", f"HTTP {e.code}")
        except (json.JSONDecodeError, KeyError):
            err_msg = f"HTTP {e.code}: {body_text}"
        raise MuseAPIError(e.code, err_msg)
    except urllib.error.URLError as e:
        raise MuseAPIError(-1, f"网络错误: {e.reason}")


def _get(path, headers=None, timeout=30):
    """通用 GET 请求"""
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, headers=headers or {}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        try:
            err_body = json.loads(body_text)
            err_msg = err_body.get("error", f"HTTP {e.code}")
        except (json.JSONDecodeError, KeyError):
            err_msg = f"HTTP {e.code}: {body_text}"
        raise MuseAPIError(e.code, err_msg)
    except urllib.error.URLError as e:
        raise MuseAPIError(-1, f"网络错误: {e.reason}")


# ─── 用户认证 ──────────────────────────────────────────

def send_code(phone):
    """发送手机验证码"""
    return _post("/user/code", {"phone": phone}, headers=_device_headers())


def login(phone, code):
    """手机号+验证码登录，返回 {authToken, newReg}"""
    return _post("/user/login", {"phone": phone, "code": code}, headers=_device_headers())


# ─── 会员信息 ──────────────────────────────────────────

def member_info(token):
    """查询会员信息，返回 {memberType, credits, expireTime}"""
    return _post("/member/info", {}, headers=_auth_headers(token))


# ─── 风格列表 ──────────────────────────────────────────

def get_styles():
    """获取音乐风格分类列表（GET，无需认证）
    返回值可能是列表或 {"list": [...]}，统一返回列表。
    """
    result = _get("/song/style")
    if isinstance(result, dict):
        return result.get("list", [])
    return result


# ─── 歌词生成 ──────────────────────────────────────────

def generate_lyrics(token, mode="lite", prompt="", title=""):
    """生成歌词

    mode="lite": 异步，返回 taskId
    mode="master": 同步，返回歌词文本
    """
    body = {"mode": mode}
    if prompt:
        body["prompt"] = prompt
    if title:
        body["title"] = title
    result = _post("/lyrics/generate", body, headers=_auth_headers(token))
    if mode == "master":
        return result.get("text", "")
    return result.get("taskId")


# ─── 歌曲生成 ──────────────────────────────────────────

def generate_song(
    token,
    description,
    mode="lite",
    title="",
    style="",
    voice="",
    song_model="general",
):
    """生成歌曲（异步），返回 taskId

    mode="lite": 灵感模式 — description 是自然语言描述
    mode="custom": 定制模式 — description 是完整歌词
    mode="instrumental": 纯音乐模式
    """
    if not description or not description.strip():
        raise MuseAPIError(-2, "歌曲描述不能为空，请输入至少一句话描述你想要的歌曲")
    if len(description.strip()) < 10 and mode != "custom":
        raise MuseAPIError(-2, "描述太短啦，请至少输入一句完整的话（10字以上），AI 才能理解你想要的歌曲")
    body = {
        "mode": mode,
        "description": description,
        "title": title,
        "songModel": song_model,
    }
    if style:
        body["style"] = style
    if voice:
        body["voice"] = voice
    result = _post("/song/generate", body, headers=_auth_headers(token))
    return result.get("taskId")


def query_song(token, task_id):
    """查询歌曲生成状态
    返回 {status: 0|1|2|3, songs: [...]}
    """
    return _post("/song/query", {"taskId": task_id}, headers=_auth_headers(token))


def get_song_info(work_id):
    """获取歌曲详情（无需认证）"""
    return _post("/song/info", {"workId": work_id})


# ─── CLI ───────────────────────────────────────────────

def _print_json(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Muse API CLI (v2)")
    sub = parser.add_subparsers(dest="command", required=True)

    # device-id
    sub.add_parser("device-id", help="输出当前设备唯一 ID（首次自动生成并持久化）")

    # member-info
    p = sub.add_parser("member-info", help="查询会员信息和积分")
    p.add_argument("--token", required=True, help="authToken")

    # styles
    sub.add_parser("styles", help="获取音乐风格列表")

    # generate
    p = sub.add_parser("generate", help="生成歌曲")
    p.add_argument("--token", required=True, help="authToken")
    p.add_argument("--description", required=True, help="歌曲描述或歌词")
    p.add_argument("--mode", default="lite", choices=["lite", "custom", "instrumental"], help="模式")
    p.add_argument("--title", default="", help="歌曲标题")
    p.add_argument("--style", default="", help="风格标签")
    p.add_argument("--voice", default="", choices=["male", "female", "random", ""], help="音色")
    p.add_argument("--song-model", default="general", help="音乐模型")

    # query
    p = sub.add_parser("query", help="查询歌曲生成状态")
    p.add_argument("--token", required=True, help="authToken")
    p.add_argument("--task-id", required=True, help="任务ID")

    # song-info
    p = sub.add_parser("song-info", help="获取歌曲详情")
    p.add_argument("--work-id", required=True, help="作品ID")

    # generate-lyrics
    p = sub.add_parser("generate-lyrics", help="生成歌词")
    p.add_argument("--token", required=True, help="authToken")
    p.add_argument("--mode", default="lite", choices=["lite", "master"], help="lite=异步, master=同步")
    p.add_argument("--prompt", default="", help="歌词描述或提示词")
    p.add_argument("--title", default="", help="歌曲标题")

    args = parser.parse_args()

    try:
        if args.command == "device-id":
            print(_get_machine_id())
            return

        elif args.command == "member-info":
            _print_json(member_info(args.token))

        elif args.command == "styles":
            _print_json(get_styles())

        elif args.command == "generate":
            task_id = generate_song(
                token=args.token,
                description=args.description,
                mode=args.mode,
                title=args.title,
                style=args.style,
                voice=args.voice,
                song_model=args.song_model,
            )
            _print_json({"taskId": task_id})

        elif args.command == "query":
            _print_json(query_song(args.token, args.task_id))

        elif args.command == "song-info":
            _print_json(get_song_info(args.work_id))

        elif args.command == "generate-lyrics":
            result = generate_lyrics(
                token=args.token,
                mode=args.mode,
                prompt=args.prompt,
                title=args.title,
            )
            if args.mode == "master":
                _print_json({"text": result})
            else:
                _print_json({"taskId": result})

    except MuseAPIError as e:
        print(json.dumps({"error": True, "code": e.code, "msg": e.msg}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
