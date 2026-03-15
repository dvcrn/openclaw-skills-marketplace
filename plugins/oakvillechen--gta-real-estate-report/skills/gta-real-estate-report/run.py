import os
import requests
import sys

# Hardcoded for our test (in production we use os.environ)
API_KEY = "14915753668f2e6686dc08cceea917e357f02f4aa8247db9fd567a1ed4b7e33e"
SKILL_ID = "30f3c86a-aea9-4c79-8001-20c1c746ed19"

def charge_user(user_id):
    """Attempt to charge the user for calling this skill via SkillPay."""
    url = "https://skillpay.me/api/v1/billing/charge"
    headers = {
        "X-API-Key": f"sk_{API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "user_id": user_id,
        "skill_id": SKILL_ID
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.json()
    except Exception as e:
        return {"success": False, "message": f"Error connecting to SkillPay: {str(e)}"}

def main():
    # 1. Identify the user.
    # Automatically pulls Discord username/ID from OpenClaw's context.
    user_id = os.environ.get("OPENCLAW_SENDER_ID", "anonymous_user")

    print(f"🔄 Authenticating user: **{user_id}**...", sys.stderr)

    # 2. Charge the user before executing the skill
    charge_result = charge_user(user_id)

    # 3. Handle Insufficient Balance
    if not charge_result.get("success"):
        payment_url = charge_result.get("payment_url")
        if payment_url:
            print(f"💰 \n\n<@!{user_id}>, 你的账户余额不足以支付本次服务 (GTA房产投资财报生成的服务费为 **5 USDT**)。\n\n请点击以下链接，通过 BNB Chain (USDT) 完成充值：\n👉 [点击这里充值]({payment_url})\n\n*(充值一般几秒内到账，到账后请在此处重新呼叫我！)*")
        else:
            reason = charge_result.get("message", "Unknown error")
            print(f"⚠️ 账单支付失败: {reason}", file=sys.stderr)
        sys.exit(0) # Not an execution error, just an auth gate

    # 4. Handle Successful Payment (Execute Skill Logic)
    balance = charge_result.get("balance", "Unknown")
    
    # ---------------------------------------------------------
    # --- PUT YOUR ACTUAL PREMIUM SKILL LOGIC HERE ---
    # ---------------------------------------------------------

    result_text = f"""✅ **扣款成功！**

正在为您生成【GTA房产投资财报】... 📊

（此处可以内嵌前面我们做楼花和买卖的 AI Report 抓取逻辑，耗时生成 PDF 发送...）

*(您的 SkillPay 账户余额还剩：**{balance} USDT**)*"""

    print(result_text)

if __name__ == "__main__":
    main()
