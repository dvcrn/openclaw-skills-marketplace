#!/usr/bin/env python3
"""
尝试不同关键词搜索，找到可以访问详情的笔记
"""

import requests
import json
import time

class XHSMCPClient:
    def __init__(self, base_url="http://localhost:18060"):
        self.base_url = base_url
        self.session = requests.Session()
    
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
    
    def get_feed_detail(self, feed_id, xsec_token):
        """获取帖子详情"""
        data = {
            "feed_id": feed_id,
            "xsec_token": xsec_token,
            "load_all_comments": False
        }
        
        resp = self.session.post(
            f"{self.base_url}/api/v1/feeds/detail",
            json=data,
            timeout=120
        )
        return resp.json()

def test_detail_access():
    """测试详情访问"""
    
    # 尝试多个关键词
    keywords = [
        "ChatGPT",
        "AI教程", 
        "人工智能入门",
        "AI工具推荐"
    ]
    
    client = XHSMCPClient()
    
    print("🔍 搜索不同关键词，测试详情可访问性\n")
    print("=" * 70)
    
    accessible_notes = []
    
    for keyword in keywords:
        print(f"\n📌 关键词: {keyword}")
        print("-" * 70)
        
        try:
            result = client.search_feeds(keyword, {
                "sort_by": "最多点赞",
                "publish_time": "一周内"
            })
            
            if not result.get('success'):
                print(f"   ❌ 搜索失败: {result.get('message', '未知错误')}")
                continue
            
            feeds = result.get('data', {}).get('feeds', [])
            print(f"   ✅ 找到 {len(feeds)} 条内容")
            
            # 测试前3条的详情
            test_count = 0
            for feed in feeds[:3]:
                note_card = feed.get('noteCard', {})
                title = note_card.get('displayTitle', '无标题')
                note_id = feed.get('id', '')
                xsec_token = feed.get('xsecToken', '')
                
                print(f"\n   测试: {title[:40]}...")
                print(f"   ID: {note_id[:20]}...")
                
                try:
                    detail = client.get_feed_detail(note_id, xsec_token)
                    
                    if detail.get('success'):
                        feed_data = detail.get('data', {}).get('feed', {})
                        note_data = feed_data.get('noteCard', {})
                        desc = note_data.get('desc', '')
                        
                        if desc and len(desc) > 10:
                            print(f"   ✅ 可访问! 正文 {len(desc)} 字")
                            print(f"   📄 预览: {desc[:100]}...")
                            
                            accessible_notes.append({
                                'keyword': keyword,
                                'note_id': note_id,
                                'title': title,
                                'xsec_token': xsec_token,
                                'description': desc,
                                'author': note_data.get('user', {}).get('nickname', ''),
                                'type': note_data.get('type', 'unknown')
                            })
                            test_count += 1
                        else:
                            print(f"   ⚠️ 可访问但正文为空")
                    else:
                        error_msg = detail.get('details', detail.get('message', '未知错误'))
                        if '不可访问' in error_msg or 'Page' in error_msg:
                            print(f"   ❌ App-only 限制")
                        else:
                            print(f"   ❌ 其他错误: {error_msg[:50]}")
                    
                    time.sleep(3)  # 间隔
                    
                except Exception as e:
                    print(f"   ❌ 请求错误: {e}")
            
            if accessible_notes:
                print(f"\n   📊 本关键词可访问: {test_count} 条")
            
        except Exception as e:
            print(f"   ❌ 搜索错误: {e}")
        
        time.sleep(2)
    
    # 保存结果
    print(f"\n{'='*70}")
    print(f"✅ 测试完成")
    print(f"   找到 {len(accessible_notes)} 条可访问详情的笔记")
    print(f"{'='*70}")
    
    if accessible_notes:
        output_path = '/tmp/xhs_accessible_notes.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'tested_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'accessible_count': len(accessible_notes),
                'notes': accessible_notes
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n📁 已保存到: {output_path}")
        print("\n可访问的笔记列表:")
        for i, note in enumerate(accessible_notes[:5], 1):
            print(f"   {i}. [{note['keyword']}] {note['title'][:40]}... ({len(note['description'])}字)")
    
    return accessible_notes

if __name__ == "__main__":
    test_detail_access()
