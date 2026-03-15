"""PollyReach 创建新会话 - 通过 API 创建 chat_id"""

import requests
import uuid
import time
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from login import signin_device

DEFAULT_BASE_URL = "https://www.visuai.me"
DEFAULT_MODEL = "PollyReach"


def create_chat(
    base_url: str = DEFAULT_BASE_URL,
    token: str = None,
    model: str = DEFAULT_MODEL,
    title: str = "New Chat",
    initial_message: str = "Hello",
) -> dict:
    """
    创建新的聊天会话，返回 chat_id。

    Args:
        base_url: API 基础地址
        token: 认证 token
        model: 模型名称
        title: 会话标题
        initial_message: 初始消息内容

    Returns:
        dict: {"success": True/False, "chat_id": str|None, "error": str|None}
    """
    if token is None:
        token = signin_device(base_url).get("token", "")

    url = f"{base_url}/api/v1/chats/new"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.3 Safari/605.1.15",
    }

    message_id = str(uuid.uuid4())
    timestamp = int(time.time())
    timestamp_ms = int(time.time() * 1000)

    payload = {
        "chat": {
            "id": "",
            "title": title,
            "models": [model],
            "params": {},
            "history": {
                "messages": {
                    message_id: {
                        "id": message_id,
                        "parentId": None,
                        "childrenIds": [],
                        "role": "user",
                        "content": initial_message,
                        "timestamp": timestamp,
                        "models": [model],
                    }
                },
                "currentId": message_id,
            },
            "messages": [
                {
                    "id": message_id,
                    "parentId": None,
                    "childrenIds": [],
                    "role": "user",
                    "content": initial_message,
                    "timestamp": timestamp,
                    "models": [model],
                }
            ],
            "tags": [],
            "timestamp": timestamp_ms,
        },
        "folder_id": None,
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            return {
                "success": False,
                "chat_id": None,
                "error": f"HTTP {response.status_code}: {response.text}",
            }

        result = response.json()
        chat_id = result.get("id", "")
        print(f"[创建成功] chat_id: {chat_id}")
        return {"success": True, "chat_id": chat_id, "error": None}

    except Exception as e:
        return {"success": False, "chat_id": None, "error": str(e)}


if __name__ == "__main__":
    result = create_chat()
    print(result)
