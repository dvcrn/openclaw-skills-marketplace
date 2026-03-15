"""PollyReach HTTP 发送模块 - 通过 visuai.me API 发送聊天消息"""

import requests
import json
import uuid
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from login import signin_device

DEFAULT_BASE_URL = "https://www.visuai.me"
DEFAULT_MODEL = "PollyReach"


def send_message(
    message: str,
    chat_id: str,
    base_url: str = DEFAULT_BASE_URL,
    token: str = None,
    model: str = DEFAULT_MODEL,
    user_name: str = "Badwin Yang",
) -> dict:
    """
    发送消息到 PollyReach。

    Args:
        message: 要发送的消息内容
        chat_id: 会话 ID
        base_url: API 基础地址
        token: 认证 token
        model: 模型名称
        user_name: 用户名

    Returns:
        dict: {"success": True/False, "status_code": int, "error": str|None}
    """
    if token is None:
        token = signin_device(base_url).get("token", "")

    url = f"{base_url}/api/chat/completions"

    now = datetime.now()
    current_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")
    current_weekday = now.strftime("%A")

    session_id: str = "ZU7s43faNMEXAUi9AABh"
    message_id: str = str(uuid.uuid4())

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.3 Safari/605.1.15",
    }

    payload = {
        "action": 10004,
        "stream": True,
        "model": model,
        "messages": [{"role": "user", "content": message}],
        "params": {},
        "tool_servers": [],
        "features": {
            "voice": False,
            "image_generation": False,
            "code_interpreter": False,
            "web_search": False,
        },
        "variables": {
            "{{USER_NAME}}": user_name,
            "{{USER_LOCATION}}": "Unknown",
            "{{CURRENT_DATETIME}}": current_datetime,
            "{{CURRENT_DATE}}": current_date,
            "{{CURRENT_TIME}}": current_time,
            "{{CURRENT_WEEKDAY}}": current_weekday,
            "{{CURRENT_TIMEZONE}}": "Asia/Shanghai",
            "{{USER_LANGUAGE}}": "en-US",
        },
        "model_item": {
            "id": model,
            "name": model,
            "object": "model",
            "created": int(now.timestamp()),
            "owned_by": "ollama",
            "ollama": {
                "name": model,
                "model": model,
                "modified_at": now.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "size": 0,
                "digest": f"{model}-digest",
                "details": {
                    "format": "agent",
                    "family": "manus",
                    "families": ["manus"],
                    "parameter_size": "intelligent",
                    "quantization_level": "none",
                },
                "connection_type": "local",
                "urls": [0],
            },
            "connection_type": "local",
            "tags": [],
            "actions": [],
            "filters": [],
        },
        "session_id": session_id,
        "chat_id": chat_id,
        "id": message_id,
        "background_tasks": {
            "tags_generation": True,
            "follow_up_generation": True,
        },
    }

    try:
        response = requests.post(url, headers=headers, json=payload, stream=True)
        if response.status_code != 200:
            return {
                "success": False,
                "status_code": response.status_code,
                "error": response.text,
            }
        # 消耗 stream 响应（实际结果通过 WebSocket 接收）
        for _ in response.iter_lines():
            pass
        return {"success": True, "status_code": 200, "error": None}
    except Exception as e:
        return {"success": False, "status_code": 0, "error": str(e)}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python sendMessage.py <chat_id> <消息内容>")
        print("示例: python sendMessage.py 87c22dd7-64d1-4d7f-9212-463f2fc13851 '你好'")
        sys.exit(1)

    chat_id = sys.argv[1]
    message = " ".join(sys.argv[2:])

    result = send_message(message, chat_id)
    print(result)
