#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.error

def get_token(url):
    if "admin" in url:
        return os.environ.get("FANGCLOUD_ADMIN_TOKEN")
    return os.environ.get("FANGCLOUD_USER_TOKEN")

def call_api(method, url, data=None, params=None):
    token = get_token(url)
    if not token:
        print(f"Error: Token not found for URL {url}")
        sys.exit(1)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Handle query params
    if params:
        # 兼容处理：如果是 recent_items 接口且没有 limit 参数，自动加上以防止 500 错误
        if "recent_items" in url and "limit" not in params:
            params["limit"] = 20
            
        query_string = urllib.parse.urlencode(params)
        url = f"{url}?{query_string}" if "?" not in url else f"{url}&{query_string}"

    # 处理 URL 中自带参数的情况 (兼容没有通过 params 传字典，而是直接写在 URL 里的情况)
    if "recent_items" in url and "limit=" not in url:
        url = f"{url}&limit=20" if "?" in url else f"{url}?limit=20"

    req_data = json.dumps(data).encode('utf-8') if data else None
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode('utf-8')
            return json.loads(res_body)
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} {e.reason}")
        print(e.read().decode('utf-8'))
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: fangcloud_client.py <method> <url> [data_json]")
        sys.exit(1)
    
    method = sys.argv[1].upper()
    url = sys.argv[2]
    data = json.loads(sys.argv[3]) if len(sys.argv) > 3 else None
    
    result = call_api(method, url, data)
    print(json.dumps(result, indent=2, ensure_ascii=False))
