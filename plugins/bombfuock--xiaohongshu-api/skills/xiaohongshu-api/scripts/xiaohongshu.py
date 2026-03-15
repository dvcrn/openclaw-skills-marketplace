#!/usr/bin/env python3
"""
小红书API - 基于TikHub
"""
import requests
import json
import argparse

class XiaohongshuAPI:
    def __init__(self, api_key=None):
        self.api_key = api_key or ""
        self.base_url = "https://api.tikhub.io/api/v1"
        
    def get_post(self, post_id):
        """获取帖子详情"""
        url = f"{self.base_url}/xiaohongshu/web/post/detail"
        params = {"post_id": post_id}
        headers = {"X-TikHub-Api-Key": self.api_key} if self.api_key else {}
        
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=10)
            return resp.json()
        except Exception as e:
            return {"error": str(e)}
    
    def search(self, keyword, page=1):
        """搜索帖子"""
        url = f"{self.base_url}/xiaohongshu/web/post/search"
        params = {"keyword": keyword, "page": page}
        headers = {"X-TikHub-Api-Key": self.api_key} if self.api_key else {}
        
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=10)
            return resp.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_trending(self):
        """获取热门"""
        url = f"{self.base_url}/xiaohongshu/web/post/hot"
        headers = {"X-TikHub-Api-Key": self.api_key} if self.api_key else {}
        
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description='小红书API')
    parser.add_argument("--post", help="帖子ID")
    parser.add_argument("--search", help="搜索关键词")
    parser.add_argument("--trending", action="store_true", help="热门帖子")
    parser.add_argument("--api-key", help="TikHub API Key")
    
    args = parser.parse_args()
    
    api = XiaohongshuAPI(args.api_key)
    
    if args.post:
        result = api.get_post(args.post)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.search:
        result = api.search(args.search)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.trending:
        result = api.get_trending()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
