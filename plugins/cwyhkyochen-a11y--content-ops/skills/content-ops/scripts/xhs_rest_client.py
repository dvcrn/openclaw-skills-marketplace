#!/usr/bin/env python3
"""
小红书 REST API 客户端
使用 /api/v1/ 端点直接调用
"""

import json
import requests
import time

class XHSMCPClient:
    def __init__(self, base_url="http://localhost:18060"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def check_login_status(self):
        """检查登录状态"""
        resp = self.session.get(f"{self.base_url}/api/v1/login/status", timeout=10)
        return resp.json()
    
    def search_feeds(self, keyword, filters=None):
        """搜索内容"""
        data = {"keyword": keyword}
        if filters:
            data["filters"] = filters
        
        resp = self.session.post(
            f"{self.base_url}/api/v1/feeds/search",
            json=data,
            timeout=60
        )
        return resp.json()
    
    def list_feeds(self):
        """获取首页推荐"""
        resp = self.session.get(f"{self.base_url}/api/v1/feeds/list", timeout=30)
        return resp.json()


def main():
    print("🔌 连接小红书 MCP 服务 (REST API)...\n")
    
    client = XHSMCPClient()
    
    # 检查登录状态
    print("1. 检查登录状态...")
    status = client.check_login_status()
    print(f"   状态: {json.dumps(status, indent=2, ensure_ascii=False)}\n")
    
    is_logged_in = status.get("data", {}).get("is_logged_in", False)
    if not is_logged_in:
        print("   ❌ 未登录，请先登录")
        return
    
    # 搜索 AI 内容
    print("2. 搜索 AI 相关内容...")
    print("   关键词: AI人工智能")
    print("   排序: 最多点赞")
    print("   时间: 一周内\n")
    
    result = client.search_feeds("AI人工智能", {
        "sort_by": "最多点赞",
        "publish_time": "一周内"
    })
    
    if result.get("success"):
        feeds = result.get("data", {}).get("feeds", [])
        print(f"   ✅ 找到 {len(feeds)} 条内容\n")
        
        # 格式化输出
        notes = []
        for i, feed in enumerate(feeds[:10], 1):
            # 数据在 noteCard 字段中
            note_card = feed.get("noteCard", {})
            interact = note_card.get("interactInfo", {})
            
            title = note_card.get("displayTitle", "无标题")[:50]
            user = note_card.get("user", {}).get("nickname", "未知")
            
            # 点赞数可能是字符串格式
            likes_str = interact.get("likedCount", "0")
            likes = int(likes_str) if likes_str else 0
            
            collects_str = interact.get("collectedCount", "0")
            collects = int(collects_str) if collects_str else 0
            
            comments_str = interact.get("commentCount", "0")
            comments = int(comments_str) if comments_str else 0
            
            print(f"   {i}. {title}")
            print(f"      👤 {user} | 👍{likes} 💾{collects} 💬{comments}")
            
            # 内容类型: video 或 normal
            content_type = note_card.get("type", "unknown")
            
            notes.append({
                "id": feed.get("id"),
                "title": title,
                "user": user,
                "liked_count": likes,
                "collected_count": collects,
                "comment_count": comments,
                "xsec_token": feed.get("xsecToken"),
                "cover_url": note_card.get("cover", {}).get("urlDefault", ""),
                "type": content_type  # video | normal | unknown
            })
        
        # 保存结果
        output = {
            "source": "xiaohongshu",
            "query": "AI人工智能",
            "filters": {"sort_by": "最多点赞", "publish_time": "一周内"},
            "total": len(feeds),
            "notes": notes,
            "crawled_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open("/tmp/xhs_ai_crawled.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n   ✅ 已保存 {len(notes)} 条到 /tmp/xhs_ai_crawled.json")
        
    else:
        print(f"   ❌ 搜索失败: {result.get('message', '未知错误')}")

if __name__ == "__main__":
    main()
