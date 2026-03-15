#!/usr/bin/env python3
"""X (Twitter) API v2 投稿スクリプト - OAuth 1.0a"""

import json
import sys
import os
import hmac
import hashlib
import base64
import time
import urllib.parse
import uuid
import requests

# API認証情報（環境変数から取得）
CONSUMER_KEY = os.environ.get("X_CONSUMER_KEY", "")
CONSUMER_SECRET = os.environ.get("X_CONSUMER_SECRET", "")
ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN", "")
ACCESS_TOKEN_SECRET = os.environ.get("X_ACCESS_TOKEN_SECRET", "")

def create_oauth_signature(method, url, params, consumer_secret, token_secret):
    """OAuth 1.0a 署名を生成"""
    sorted_params = "&".join(f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(v, safe='')}" 
                            for k, v in sorted(params.items()))
    base_string = f"{method}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(sorted_params, safe='')}"
    signing_key = f"{urllib.parse.quote(consumer_secret, safe='')}&{urllib.parse.quote(token_secret, safe='')}"
    signature = base64.b64encode(
        hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
    ).decode()
    return signature

def create_oauth_header(method, url, body_params=None):
    """OAuth 1.0a ヘッダーを生成"""
    if not all([CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
        print("❌ X API credentials not set. Set X_CONSUMER_KEY, X_CONSUMER_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET")
        sys.exit(1)
    
    oauth_params = {
        "oauth_consumer_key": CONSUMER_KEY,
        "oauth_nonce": uuid.uuid4().hex,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": ACCESS_TOKEN,
        "oauth_version": "1.0",
    }
    
    all_params = {**oauth_params}
    if body_params:
        all_params.update(body_params)
    
    signature = create_oauth_signature(method, url, all_params, CONSUMER_SECRET, ACCESS_TOKEN_SECRET)
    oauth_params["oauth_signature"] = signature
    
    auth_header = "OAuth " + ", ".join(
        f'{urllib.parse.quote(k, safe="")}="{urllib.parse.quote(v, safe="")}"'
        for k, v in sorted(oauth_params.items())
    )
    return auth_header

def post_tweet(text, reply_to=None):
    """ツイートを投稿"""
    url = "https://api.twitter.com/2/tweets"
    
    payload = {"text": text}
    if reply_to:
        payload["reply"] = {"in_reply_to_tweet_id": reply_to}
    
    auth_header = create_oauth_header("POST", url)
    
    response = requests.post(
        url,
        headers={
            "Authorization": auth_header,
            "Content-Type": "application/json",
        },
        json=payload,
    )
    
    if response.status_code in (200, 201):
        data = response.json()
        tweet_id = data["data"]["id"]
        print(f"✅ Posted! https://x.com/i/status/{tweet_id}")
        return data
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return None

def upload_media(image_path):
    """画像をアップロード（v1.1 API）"""
    url = "https://upload.twitter.com/1.1/media/upload.json"
    
    auth_header = create_oauth_header("POST", url)
    
    with open(image_path, "rb") as f:
        response = requests.post(
            url,
            headers={"Authorization": auth_header},
            files={"media": f},
        )
    
    if response.status_code in (200, 201, 202):
        data = response.json()
        media_id = data["media_id_string"]
        print(f"📷 Media uploaded: {media_id}")
        return media_id
    else:
        print(f"❌ Media upload error: {response.status_code}")
        print(response.text)
        return None

def post_tweet_with_media(text, image_path):
    """画像付きツイートを投稿"""
    media_id = upload_media(image_path)
    if not media_id:
        print("Posting without image...")
        return post_tweet(text)
    
    url = "https://api.twitter.com/2/tweets"
    payload = {
        "text": text,
        "media": {"media_ids": [media_id]},
    }
    
    auth_header = create_oauth_header("POST", url)
    
    response = requests.post(
        url,
        headers={
            "Authorization": auth_header,
            "Content-Type": "application/json",
        },
        json=payload,
    )
    
    if response.status_code in (200, 201):
        data = response.json()
        tweet_id = data["data"]["id"]
        print(f"✅ Posted with image! https://x.com/i/status/{tweet_id}")
        return data
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python post.py 'tweet text' [reply_to_id] [image_path]")
        sys.exit(1)
    
    text = sys.argv[1]
    reply_to = None
    image_path = None
    
    if len(sys.argv) > 2:
        arg2 = sys.argv[2]
        if arg2.isdigit() and len(arg2) > 10:
            reply_to = arg2
            image_path = sys.argv[3] if len(sys.argv) > 3 else None
        else:
            image_path = arg2
    
    if image_path:
        post_tweet_with_media(text, image_path)
    elif reply_to:
        post_tweet(text, reply_to=reply_to)
    else:
        post_tweet(text)
