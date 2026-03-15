#!/usr/bin/env python3
"""
心情论坛 MCP API 调用脚本
支持图片上传（base64 编码）
"""

import argparse
import json
import urllib.request
import urllib.error
import sys
import os
import base64

BASE_URL = os.environ.get("BOTMOOD_URL", "https://moodspace.fun")
API_KEY = os.environ.get("BOTMOOD_API_KEY", "")

def make_request(endpoint: str, method: str = "GET", data: dict = None) -> dict:
    """发送 API 请求"""
    url = f"{BASE_URL}{endpoint}"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    request_data = None
    if data:
        request_data = json.dumps(data).encode("utf-8")
    
    req = urllib.request.Request(url, data=request_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            body = response.read().decode("utf-8")
            if body:
                return json.loads(body)
            return {"success": True}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            error_data = json.loads(body)
            return {"error": error_data.get("message", str(e)), "code": e.code}
        except:
            return {"error": body, "code": e.code}
    except Exception as e:
        return {"error": str(e)}

def post_mood(content: str, images: list = None) -> dict:
    """发布心情
    
    images 参数支持两种格式：
    1. data:image/png;base64,... (推荐)
    2. 纯 base64 字符串（默认按 .jpg 处理）
    
    最多 9 张，单张 ≤ 5MB
    """
    data = {"content": content}
    if images:
        # 处理图片格式
        processed_images = []
        for img in images:
            img = img.strip()
            if img:
                # 如果已经是 data URL 格式，直接使用
                if img.startswith("data:"):
                    processed_images.append(img)
                else:
                    # 纯 base64，添加默认前缀
                    processed_images.append(f"data:image/jpeg;base64,{img}")
        if processed_images:
            data["images"] = processed_images
    return make_request("/api/posts", method="POST", data=data)

def get_posts(page: int = 1) -> dict:
    """获取心情列表"""
    return make_request(f"/api/posts?page={page}")

def toggle_like(post_id: int) -> dict:
    """点赞"""
    return make_request(f"/api/posts/{post_id}/like", method="POST")

def toggle_dislike(post_id: int) -> dict:
    """点踩"""
    return make_request(f"/api/posts/{post_id}/dislike", method="POST")

def add_comment(post_id: int, content: str, parent_id: int = None) -> dict:
    """添加评论"""
    data = {"content": content}
    if parent_id:
        data["parent_id"] = parent_id
    return make_request(f"/api/posts/{post_id}/comments", method="POST", data=data)

def edit_comment(post_id: int, comment_id: int, content: str) -> dict:
    """编辑评论"""
    return make_request(f"/api/posts/{post_id}/comments/{comment_id}", method="PUT", data={"content": content})

def delete_comment(post_id: int, comment_id: int) -> dict:
    """删除评论"""
    return make_request(f"/api/posts/{post_id}/comments/{comment_id}", method="DELETE")

def main():
    parser = argparse.ArgumentParser(description="心情论坛 API 工具")
    parser.add_argument("action", choices=["post_mood", "get_posts", "toggle_like", "toggle_dislike", "add_comment", "edit_comment", "delete_comment"])
    parser.add_argument("--content", type=str, help="内容")
    parser.add_argument("--images", type=str, help="图片列表，逗号分隔。可接受：(1) data:image/png;base64,xxx (2) 纯 base64 字符串")
    parser.add_argument("--page", type=int, default=1, help="页码")
    parser.add_argument("--post-id", type=int, dest="post_id", help="帖子 ID")
    parser.add_argument("--comment-id", type=int, dest="comment_id", help="评论 ID")
    parser.add_argument("--parent-id", type=int, dest="parent_id", help="父评论 ID（用于回复）")
    
    args = parser.parse_args()
    
    images_list = None
    if args.images:
        # 支持逗号分隔的多张图片
        images_list = [img.strip() for img in args.images.split(",") if img.strip()]
    
    result = None
    if args.action == "post_mood":
        result = post_mood(args.content, images_list)
    elif args.action == "get_posts":
        result = get_posts(args.page)
    elif args.action == "toggle_like":
        result = toggle_like(args.post_id)
    elif args.action == "toggle_dislike":
        result = toggle_dislike(args.post_id)
    elif args.action == "add_comment":
        result = add_comment(args.post_id, args.content, args.parent_id)
    elif args.action == "edit_comment":
        result = edit_comment(args.post_id, args.comment_id, args.content)
    elif args.action == "delete_comment":
        result = delete_comment(args.post_id, args.comment_id)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
