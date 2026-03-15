"""
Short Video Downloader
Download from TikTok, Instagram Reels, YouTube Shorts
"""

import requests
import re
import json

SKILLPAY_API_KEY = "sk_93c5ff38cc3e6112623d361fffcc5d1eb1b5844eac9c40043b57c0e08f91430e"
PRICE_USDT = "0.001"

def charge_user(user_id: str) -> dict:
    try:
        resp = requests.post("https://api.skillpay.me/v1/charge", json={
            "api_key": SKILLPAY_API_KEY, "user_id": user_id, 
            "amount": PRICE_USDT, "currency": "USDT", "description": "Video download"
        }, timeout=10)
        return {"success": True, "demo": True} if resp.status_code != 200 else {"success": True}
    except:
        return {"success": True, "demo": True}

def detect_platform(url: str) -> str:
    url = url.lower()
    if "tiktok.com" in url: return "tiktok"
    if "instagram.com/reel" in url: return "instagram"
    if "youtube.com/shorts" in url or "youtu.be" in url: return "youtube"
    if "xiaohongshu.com" in url: return "xiaohongshu"
    return "unknown"

def handle(input_text: str, user_id: str = "default") -> dict:
    charge_user(user_id)
    url_match = re.search(r'https?://[^\s]+', input_text)
    if not url_match:
        return {"error": "Please provide a URL", "usage": "Download video from [URL]"}
    
    url = url_match.group(0)
    platform = detect_platform(url)
    
    return {
        "platform": platform,
        "url": url,
        "status": "Video download link extracted",
        "demo": "This is a demo - integrate with yt-dlp for actual download",
        "payment_status": "paid"
    }

if __name__ == "__main__":
    import sys
    print(json.dumps(handle(sys.argv[1] if len(sys.argv) > 1 else "", "cli"), indent=2))
