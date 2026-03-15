#!/usr/bin/env python3
"""
小红书自动发布技能
SkillPay 收费：¥0.01/次
"""

import subprocess
import sys
import os
import requests
import hashlib
import time

# SkillPay 配置
SKILLPAY_API_KEY = "sk_4eacbcc9e4411bd1490794b27867199f9801e3150b4c354541e6a2927931a06e"
SKILLPAY_API_URL = "https://skillpay.me/api/v1"
PRODUCT_ID = "xhs_auto_publish"
PRICE = 0.01

WORKSPACE = "/Users/xiaofang/.openclaw/workspace-taizi"
XHS_CLIENT = "/Users/xiaofang/.openclaw/workspace/skills/xiaohongshu-mcp/scripts/xhs_client.py"

def verify_payment(user_id, payment_token):
    """验证 SkillPay 支付"""
    try:
        headers = {
            "Authorization": f"Bearer {SKILLPAY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "product_id": PRODUCT_ID,
            "user_id": user_id,
            "payment_token": payment_token
        }
        
        resp = requests.post(
            f"{SKILLPAY_API_URL}/verify",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        result = resp.json()
        return result.get("success", False), result.get("message", "")
    except Exception as e:
        return False, str(e)

def check_mcp_status():
    """检查 MCP 服务器状态"""
    try:
        result = subprocess.run(
            ["python3", XHS_CLIENT, "status"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return "✅ Logged in" in result.stdout
    except:
        return False

def generate_cover(title):
    """生成中国风封面"""
    print("🎨 生成中国风封面...")
    
    cover_script = f"{WORKSPACE}/generate_cover_chinese.py"
    
    result = subprocess.run(
        ["python3", cover_script, title],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    cover_path = f"{WORKSPACE}/xhs_cover_chinese.png"
    if os.path.exists(cover_path):
        print(f"   ✅ 封面已生成")
        return cover_path, True
    else:
        print(f"   ❌ 封面生成失败")
        return None, False

def create_content(topic):
    """创作文案"""
    print("📝 创作文案...")
    
    sys.path.insert(0, WORKSPACE)
    from generate_content import create_content as gen_content
    
    title, content, tags = gen_content(topic)
    print(f"   标题：{title}")
    print(f"   字数：{len(content)}")
    
    return title, content, tags

def publish(title, content, image_path, tags):
    """发布到小红书"""
    print("🚀 发布到小红书...")
    
    cmd = [
        "python3", XHS_CLIENT, "publish",
        title, content, image_path,
        "--tags", tags
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    
    if "发布成功" in result.stdout or "success" in result.stdout.lower() or "✅" in result.stdout:
        return True, result.stdout
    else:
        return False, result.stdout + result.stderr

def main(topic=None, user_id=None, payment_token=None):
    """主流程"""
    print("=" * 50)
    print("📱 小红书自动发布技能 v1.0")
    print("=" * 50)
    print()
    
    # 1. 验证支付（跳过测试模式）
    if os.environ.get("SKIP_PAYMENT") != "true":
        print("💳 验证 SkillPay 支付...")
        if not user_id or not payment_token:
            print("❌ 缺少支付信息")
            print(f"   请先支付：¥{PRICE}")
            print(f"   支付链接：https://skillpay.me/p/{PRODUCT_ID}")
            sys.exit(1)
        
        success, msg = verify_payment(user_id, payment_token)
        if not success:
            print(f"❌ 支付验证失败：{msg}")
            sys.exit(1)
        print(f"   ✅ 支付验证成功")
        print()
    
    # 2. 检查登录状态
    print("🔐 检查小红书登录状态...")
    if not check_mcp_status():
        print("❌ MCP 未登录，请先扫码")
        print("运行：cd ~/.openclaw/workspace/skills/xiaohongshu-mcp/bin && ./xiaohongshu-login-darwin-arm64")
        sys.exit(1)
    print("✅ MCP 状态正常")
    print()
    
    # 3. 创作文案
    title, content, tags = create_content(topic)
    print()
    
    # 4. 生成封面
    cover_path, success = generate_cover(title)
    if not success:
        print("❌ 流程中断")
        sys.exit(1)
    print()
    
    # 5. 发布
    success, msg = publish(title, content, cover_path, tags)
    
    print()
    print("=" * 50)
    if success:
        print("✅ 发布成功！")
        print(f"   标题：{title}")
        print(f"   封面：{cover_path}")
        print(f"   标签：{tags}")
        print()
        print(f"💰 本次消费：¥{PRICE}")
        print(f"   感谢使用！")
    else:
        print(f"❌ 发布失败：{msg}")
    
    return success

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="小红书自动发布技能")
    parser.add_argument("topic", help="发布主题")
    parser.add_argument("--user-id", help="SkillPay 用户 ID")
    parser.add_argument("--payment-token", help="SkillPay 支付 Token")
    parser.add_argument("--skip-payment", action="store_true", help="跳过支付验证（测试用）")
    
    args = parser.parse_args()
    
    if args.skip_payment:
        os.environ["SKIP_PAYMENT"] = "true"
    
    main(
        topic=args.topic,
        user_id=args.user_id,
        payment_token=args.payment_token
    )
