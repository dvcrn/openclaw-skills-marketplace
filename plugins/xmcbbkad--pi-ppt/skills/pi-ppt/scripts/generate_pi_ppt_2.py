import os
import time
import uuid
from typing import Any, Dict, Tuple, List
import hashlib
import json
import requests


GENERATION_URL = "https://alpha-pi.deepvinci.tech/api/v1/integration/document/generation"
GET_STATUS_URL = "https://alpha-pi.deepvinci.tech/api/v1/integration/document/status"
APPID = ""
APP_SECRET = ""

def set_app_id_and_app_secret(app_id: str, app_secret: str):
    global APPID, APP_SECRET
    APPID = app_id
    APP_SECRET = app_secret

def generate_signature_payload(app_id: str, app_secret: str, timestamp: int, **payload: dict) -> Tuple[str, dict]:
    """
    生成请求签名，基于时间戳和提供的参数

    Args:
        timestamp: 请求的时间戳
        parameters: 需要包含在签名中的键值对参数

    Returns:
        携带签名的请求参数
    """

    # 按字母顺序排序请求参数key
    keys: List[str] = sorted(payload.keys())

    # 将非空参数格式化为"key=value"格式并按排序后的顺序组合
    formatted_params: List[str] = []
    for key in keys:
        value = payload[key]
        if isinstance(value, bool):
            formatted_params.append(f"{key}={str(value).lower()}")
        elif isinstance(value, dict):
            formatted_params.append(f"{key}={json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)}")
        elif value is not None:
            formatted_params.append(f"{key}={str(value)}")

    # 用冒号连接所有参数
    params_string: str = ":".join(formatted_params)

    # 构建签名字符串：app_secret:timestamp:params:app_secret
    signature_base = f"{app_secret}:{timestamp}:{params_string}:{app_secret}"

    # 计算SHA1哈希
    hash_result = hashlib.sha1(signature_base.encode("utf-8")).hexdigest()

    # 记录签名过程的日志
    print(signature_base)
    print(hash_result)
    print(payload)

    return {"app_id": app_id, "timestamp": timestamp, "sign": hash_result, **payload}


def create_document(content: str, cards: int = 8, language: str = "cn") -> Dict[str, Any]:
    """
    Trigger Pi PPT generation task only (no polling).
    """
    if not isinstance(content, str) or not content.strip():
        raise ValueError("content 不能为空字符串。")
    if not isinstance(cards, int) or cards <= 0:
        raise ValueError("cards 必须是大于 0 的整数。")
    if language not in {"cn", "zh", "en"}:
        raise ValueError("language 仅支持 'cn'、'zh' 或 'en'。")


    timestamp = int(time.time())
    resource_id = f"draft-{uuid.uuid4().hex[:12]}"

    payload = {
        "resource_id": resource_id,
        "uid": "user_1",
        "content": content.strip(),
        "cards": cards,
        "language": language,
        "outline_type": "aippt"
    }

    payload_with_sign = generate_signature_payload(APPID, APP_SECRET, timestamp, **payload)

    response = requests.post(GENERATION_URL, json=payload_with_sign, timeout=30)
    response.raise_for_status()
    data = response.json()

    return {
        "name": "generate_pi_ppt_2",
        "request": payload_with_sign,
        "response": data,
    }


def get_status(resource_id: str) -> Dict[str, Any]:
    if not isinstance(resource_id, str) or not resource_id.strip():
        raise ValueError("resource_id 不能为空字符串。")

    timestamp = int(time.time())
    payload = {
        "resource_id": resource_id.strip(),
    }
    payload_with_sign = generate_signature_payload(APPID, APP_SECRET, timestamp, **payload)
    response = requests.post(GET_STATUS_URL, json=payload_with_sign, timeout=30)
    response.raise_for_status()
    response_json = response.json()

    data = response_json.get("data")
    if not isinstance(data, dict):
        raise ValueError(f"状态接口返回格式异常: {response_json}")

    status = data.get("status")
    if status not in {"running", "fail", "done"}:
        raise ValueError(f"未知状态值: {status}, 原始响应: {response_json}")

    return {
        "resource_id": data.get("resource_id"),
        "status": status,
        "url": data.get("url"),
    }

def generate_pi_ppt_2(
    content: str,
    cards: int = 8,
    language: str = "cn",
    timeout_s: int = 300,
    poll_interval_s: int = 20,
) -> Dict[str, Any]:
    """
    完整流程：
    1) 调用 create_document 触发任务
    2) 调用 get_status 轮询，直到 done 返回 url
    """
    if not isinstance(timeout_s, int) or timeout_s <= 0:
        raise ValueError("timeout_s 必须是大于 0 的整数。")
    if not isinstance(poll_interval_s, int) or poll_interval_s <= 0:
        raise ValueError("poll_interval_s 必须是大于 0 的整数。")

    create_result = create_document(content=content, cards=cards, language=language)

    resource_id = create_result.get("request", {}).get("resource_id")
    if not isinstance(resource_id, str) or not resource_id:
        raise ValueError(f"触发接口未返回可用 resource_id: {create_result}")

    deadline = time.time() + timeout_s
    last_status: Dict[str, Any] = {}
    while time.time() < deadline:
        status_result = get_status(resource_id)
        last_status = status_result
        status = status_result.get("status")

        if status == "done":
            url = status_result.get("url")
            if not url:
                raise ValueError(f"status=done 但未返回 url: {status_result}")
            return {
                "name": "generate_pi_ppt_2",
                "resource_id": resource_id,
                "status": "done",
                "url": url,
                "create_result": create_result,
            }

        if status == "fail":
            raise RuntimeError(f"PPT 生成失败: {status_result}")

        time.sleep(poll_interval_s)

    raise TimeoutError(
        f"轮询超时（{timeout_s}s），resource_id={resource_id}，最后状态={last_status}"
    )

if __name__ == "__main__":
    set_app_id_and_app_secret("280341116439686106", "166e42311a4d4a3281d492d22121699933a5bb888c3cadf2f49ac72c")
    result = generate_pi_ppt_2(content="做一个关于比特币介绍的PPT", cards=8, language="zh")
    print(result)
    url = result.get("url")
    if not url:
        raise ValueError(f"生成失败: {result}")
    print(url)