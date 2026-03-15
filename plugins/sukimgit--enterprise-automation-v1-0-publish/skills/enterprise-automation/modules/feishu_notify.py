# -*- coding: utf-8 -*-
"""
飞书通知模块
"""

import urllib.request
import json
from typing import Optional


def send_feishu_message(
    content: str,
    webhook: Optional[str] = None
) -> bool:
    """发送飞书消息
    
    Args:
        content: 消息内容
        webhook: 飞书 Webhook URL（可选，默认从配置读取）
    
    Returns:
        bool: 发送是否成功
    """
    if not webhook:
        print("[ERROR] 未提供飞书 Webhook URL")
        return False
    
    try:
        data = {
            "msg_type": "text",
            "content": {"text": content}
        }
        req = urllib.request.Request(
            webhook,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        resp = urllib.request.urlopen(req, timeout=10)
        result = json.loads(resp.read().decode('utf-8'))
        
        if result.get('code') == 0 or result.get('StatusCode') == 0:
            print("[OK] 飞书消息已发送")
            return True
        return False
    except Exception as e:
        print(f"[ERROR] 飞书发送失败：{e}")
        return False
