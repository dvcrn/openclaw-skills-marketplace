#!/usr/bin/env python3
"""
通过 MCP REST API 获取笔记详情（增强版）
使用浏览器自动化方式获取详情
"""

import json
import requests
import time

class XHSMCPClient:
    def __init__(self, base_url="http://localhost:18060"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_feed_detail(self, feed_id, xsec_token, load_all_comments=False):
        """获取帖子详情"""
        data = {
            "feed_id": feed_id,
            "xsec_token": xsec_token,
            "load_all_comments": load_all_comments,
            # 添加更多参数帮助页面加载
            "limit": 10,
            "click_more_replies": False
        }
        
        resp = self.session.post(
            f"{self.base_url}/api/v1/feeds/detail",
            json=data,
            timeout=120  # 增加超时时间
        )
        return resp.json()

def fetch_details_with_mcp():
    """使用 MCP 获取详情"""
    
    # 读取列表数据
    with open('/tmp/xhs_ai_crawled.json', 'r') as f:
        crawl_data = json.load(f)
    
    # 筛选高质量内容
    high_quality = [n for n in crawl_data['notes'] if n.get('quality_score', 0) >= 8]
    
    print(f"🎯 筛选出 {len(high_quality)} 条高质量内容")
    print("=" * 70)
    
    client = XHSMCPClient()
    
    results = []
    
    for i, note in enumerate(high_quality, 1):
        print(f"\n[{i}/{len(high_quality)}] 获取详情: {note['title'][:40]}...")
        print(f"   ID: {note['id']}")
        print(f"   xsec_token: {note.get('xsec_token', 'N/A')[:30]}...")
        
        try:
            result = client.get_feed_detail(
                note['id'], 
                note.get('xsec_token', ''),
                load_all_comments=False
            )
            
            if result.get('success'):
                feed = result.get('data', {}).get('feed', {})
                comments = result.get('data', {}).get('comments', [])
                
                # 提取关键信息
                note_card = feed.get('noteCard', {})
                title = note_card.get('displayTitle', note['title'])
                desc = note_card.get('desc', '')
                author = note_card.get('user', {}).get('nickname', '')
                
                print(f"   ✅ 成功")
                print(f"   📝 标题: {title[:50]}")
                print(f"   👤 作者: {author}")
                print(f"   📄 正文长度: {len(desc)} 字符")
                print(f"   💬 评论数: {len(comments)}")
                
                if desc:
                    print(f"   📃 正文预览:")
                    print(f"      {desc[:200]}...")
                
                results.append({
                    'note_id': note['id'],
                    'title': title,
                    'author': author,
                    'description': desc,
                    'comments': comments,
                    'success': True
                })
            else:
                print(f"   ❌ API返回失败: {result.get('message', '未知错误')}")
                results.append({
                    'note_id': note['id'],
                    'title': note['title'],
                    'success': False,
                    'error': result.get('message', '未知错误')
                })
            
            # 间隔 5 秒
            time.sleep(5)
            
        except Exception as e:
            print(f"   ❌ 请求错误: {e}")
            results.append({
                'note_id': note['id'],
                'title': note['title'],
                'success': False,
                'error': str(e)
            })
    
    # 保存结果
    output_path = '/tmp/xhs_detail_results.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'fetched_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total': len(high_quality),
            'success_count': sum(1 for r in results if r.get('success')),
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*70}")
    print(f"✅ 详情抓取完成")
    success = sum(1 for r in results if r.get('success'))
    print(f"   成功: {success}/{len(high_quality)}")
    print(f"   保存: {output_path}")
    print(f"{'='*70}")
    
    return results

if __name__ == "__main__":
    fetch_details_with_mcp()
