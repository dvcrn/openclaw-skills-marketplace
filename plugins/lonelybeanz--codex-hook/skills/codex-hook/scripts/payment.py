#!/usr/bin/env python3
"""
SkillPay integration for codex-hook
Charges 0.001 USDT per task dispatch
"""

import os
import json
import requests

SKILLPAY_API_KEY = os.environ.get("SKILLPAY_API_KEY", "sk_46c2c771ec94f2628c1dcfee85ce36cb3c3573a68d88727042a060b1865e5977")
SKILLPAY_API_URL = "https://skillpay.me/api/billing/charge"

def charge(user_id: str, amount: float = 0.001) -> dict:
    """
    Charge a user via SkillPay
    
    Args:
        user_id: The user identifier (e.g., Telegram user ID or wallet address)
        amount: Amount in USDT (default: 0.001)
    
    Returns:
        dict with keys:
            - success: bool
            - payment_url: str (if success=False)
            - tx_hash: str (if success=True)
            - message: str
    """
    headers = {
        "Authorization": f"Bearer {SKILLPAY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "user_id": str(user_id),
        "amount": amount,
        "currency": "USDT",
        "skill": "codex-hook"
    }
    
    try:
        response = requests.post(
            SKILLPAY_API_URL,
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return {
                    "success": True,
                    "tx_hash": data.get("tx_hash"),
                    "message": data.get("message", "Payment successful")
                }
            else:
                return {
                    "success": False,
                    "payment_url": data.get("payment_url"),
                    "message": data.get("message", "Payment failed")
                }
        else:
            return {
                "success": False,
                "message": f"API error: {response.status_code}"
            }
            
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": f"Network error: {str(e)}"
        }


def check_balance(user_id: str) -> dict:
    """Check user's SkillPay balance"""
    headers = {
        "Authorization": f"Bearer {SKILLPAY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"https://skillpay.me/api/billing/balance/{user_id}",
            headers=headers,
            timeout=10
        )
        return response.json() if response.status_code == 200 else {"error": response.text}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    # Test
    import sys
    if len(sys.argv) > 1:
        user_id = sys.argv[1]
        result = charge(user_id)
        print(json.dumps(result, indent=2))
