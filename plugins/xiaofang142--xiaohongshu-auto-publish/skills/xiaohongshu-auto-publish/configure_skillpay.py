#!/usr/bin/env python3
"""
配置 SkillPay 产品
"""

import requests
import json

API_KEY = "sk_4eacbcc9e4411bd1490794b27867199f9801e3150b4c354541e6a2927931a06e"
BASE_URL = "https://skillpay.me"

def create_product():
    """创建产品"""
    print("💳 创建 SkillPay 产品...")
    
    # 尝试不同的 API 路径
    endpoints = [
        "/api/v1/products",
        "/api/products",
        "/products",
        "/api/v1/product",
    ]
    
    payload = {
        "name": "小红书自动发布技能",
        "description": "一键发布小红书笔记 - AI 文案 + 中国风封面 + 自动发布",
        "price": 0.01,
        "currency": "CNY",
        "product_id": "xhs_auto_publish"
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    for endpoint in endpoints:
        url = f"{BASE_URL}{endpoint}"
        print(f"   尝试：{url}")
        
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=10)
            print(f"   状态码：{resp.status_code}")
            print(f"   响应：{resp.text[:200]}")
            
            if resp.status_code == 200:
                result = resp.json()
                print(f"   ✅ 创建成功！")
                print(f"   产品 ID: {result.get('id', 'N/A')}")
                return True
        except Exception as e:
            print(f"   ❌ 错误：{e}")
    
    return False

def check_products():
    """查看现有产品"""
    print("\n📋 查看现有产品...")
    
    url = f"{BASE_URL}/api/v1/products"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"   状态码：{resp.status_code}")
        print(f"   响应：{resp.text[:500]}")
    except Exception as e:
        print(f"   ❌ 错误：{e}")

if __name__ == "__main__":
    print("=" * 50)
    print("SkillPay 产品配置工具")
    print("=" * 50)
    print()
    
    # 1. 查看现有产品
    check_products()
    
    # 2. 创建新产品
    print()
    success = create_product()
    
    print()
    print("=" * 50)
    if success:
        print("✅ 配置完成！")
        print(f"   产品页面：{BASE_URL}/p/xhs_auto_publish")
    else:
        print("⚠️  需要手动创建产品")
        print(f"   访问：{BASE_URL}/dashboard/products")
