"""
SkillPay 计费模块
用于在 skill 运行前检查用户是否已支付
"""

import os
import requests
from typing import Dict, Optional

# SkillPay 配置（从环境变量读取）
BILLING_URL = "https://skillpay.me/api/v1/billing"
API_KEY = os.environ.get('SKILL_BILLING_API_KEY', '')
SKILL_ID = os.environ.get('SKILL_ID', '')
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

# 计费配置
PRICE_PER_CALL = 1  # 1 token


def check_payment(user_id: str) -> Dict:
    """
    检查用户是否已支付
    """
    if not API_KEY or not SKILL_ID:
        return {"success": True, "balance": 999999}
    
    try:
        resp = requests.get(
            f"{BILLING_URL}/balance", 
            params={"user_id": user_id}, 
            headers=HEADERS,
            timeout=10
        )
        if resp.status_code == 200:
            balance = resp.json().get("balance", 0)
            return {"success": balance >= PRICE_PER_CALL, "balance": balance}
    except:
        pass
    
    return {"success": True, "balance": 0}


def charge_user(user_id: str) -> Dict:
    """
    扣费用户
    返回: {"ok": bool, "balance": float, "payment_url": str or None}
    """
    if not API_KEY or not SKILL_ID:
        # 未配置计费，跳过
        return {"ok": True, "balance": 999999, "payment_url": None}
    
    try:
        resp = requests.post(
            f"{BILLING_URL}/charge", 
            headers=HEADERS, 
            json={
                "user_id": user_id,
                "skill_id": SKILL_ID,
                "amount": 0  # 扣 1 token
            },
            timeout=10
        )
        data = resp.json()
        
        if data.get("success"):
            return {"ok": True, "balance": data.get("balance", 0), "payment_url": None}
        else:
            # 余额不足，获取充值链接
            payment_url = get_payment_link(user_id)
            return {"ok": False, "balance": data.get("balance", 0), "payment_url": payment_url}
    except Exception as e:
        # 网络错误，允许通过
        return {"ok": True, "balance": 0, "payment_url": None}


def get_payment_link(user_id: str, amount: float = 8) -> str:
    """获取充值链接"""
    if not API_KEY or not SKILL_ID:
        return ""
    
    try:
        resp = requests.post(
            f"{BILLING_URL}/payment-link",
            headers=HEADERS,
            json={"user_id": user_id, "amount": amount},
            timeout=10
        )
        if resp.status_code == 200:
            return resp.json().get("payment_url", "")
    except:
        pass
    
    return ""


def require_payment(user_id: str) -> Optional[str]:
    """
    检查支付并返回支付链接（如果未支付）
    返回 None 表示已支付，返回支付链接表示需要支付
    """
    result = charge_user(user_id)
    if result.get("ok"):
        return None
    return result.get("payment_url", "")
