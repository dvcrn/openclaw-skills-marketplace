#!/usr/bin/env python3
"""
飞书图片发送工具
用法: python3 feishu_image.py <图片路径> <用户ID>
"""

import sys
import os
import json
import urllib.request
import urllib.parse

# 飞书配置
APP_ID = "cli_a92ae73480f89bc8"
APP_SECRET = "ilCqHkbr5DysHuq7ZPlA6e23eP2010uR"

def get_token():
    """获取飞书 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        if result.get("code") != 0:
            raise Exception(f"获取token失败: {result}")
        return result["tenant_access_token"]

def upload_image(token, image_path):
    """上传图片获取 image_key"""
    boundary = "----WebKitFormBoundary"
    
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    # 构建 multipart 请求
    content_type = f"multipart/form-data; boundary={boundary}"
    
    body = f"--{boundary}\r\n"
    body += f'Content-Disposition: form-data; name="image_type"\r\n\r\n'
    body += "message\r\n"
    body += f"--{boundary}\r\n"
    body += f'Content-Disposition: form-data; name="image"; filename="{os.path.basename(image_path)}"\r\n'
    body += "Content-Type: image/png\r\n\r\n"
    
    body = body.encode("utf-8") + image_data + f"\r\n--{boundary}--\r\n".encode("utf-8")
    
    url = "https://open.feishu.cn/open-apis/im/v1/images"
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": content_type
    }, method="POST")
    
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        if result.get("code") != 0:
            raise Exception(f"上传图片失败: {result}")
        return result["data"]["image_key"]

def send_image(token, user_id, image_key):
    """发送图片消息"""
    url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
    data = json.dumps({
        "receive_id": user_id,
        "msg_type": "image",
        "content": json.dumps({"image_key": image_key})
    }).encode("utf-8")
    
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }, method="POST")
    
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        if result.get("code") != 0:
            raise Exception(f"发送图片失败: {result}")
        return result["data"]["message_id"]

def main():
    if len(sys.argv) < 3:
        print("用法: python3 feishu_image.py <图片路径> <用户ID>")
        print("示例: python3 feishu_image.py /path/to/image.png ou_xxxxxxxxxxxxxx")
        sys.exit(1)
    
    image_path = sys.argv[1]
    user_id = sys.argv[2]
    
    if not os.path.exists(image_path):
        print(f"错误: 图片文件不存在: {image_path}")
        sys.exit(1)
    
    print(f"1. 获取 token...")
    token = get_token()
    print(f"   Token 获取成功")
    
    print(f"2. 上传图片: {image_path}")
    image_key = upload_image(token, image_path)
    print(f"   上传成功, image_key: {image_key}")
    
    print(f"3. 发送图片给用户: {user_id}")
    message_id = send_image(token, user_id, image_key)
    print(f"   发送成功, message_id: {message_id}")
    
    print("\n✅ 发送完成!")

if __name__ == "__main__":
    main()
