#!/usr/bin/env python3
"""
小红书优质内容详情抓取
基于列表结果，筛选高质量内容，抓取详情和评论
"""

import json
import requests
import time
import os

class XHSMCPClient:
    def __init__(self, base_url="http://localhost:18060"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_feed_detail(self, feed_id, xsec_token):
        """获取帖子详情（包含完整正文和评论）"""
        data = {
            "feed_id": feed_id,
            "xsec_token": xsec_token,
            "load_all_comments": True,  # 加载评论
            "limit": 20  # 前20条评论
        }
        
        resp = self.session.post(
            f"{self.base_url}/api/v1/feeds/detail",
            json=data,
            timeout=60
        )
        return resp.json()

def fetch_high_quality_details():
    """抓取高质量内容的详情"""
    
    # 读取列表数据
    with open('/tmp/xhs_ai_crawled.json', 'r') as f:
        crawl_data = json.load(f)
    
    # 筛选高质量内容（质量分 >= 8）
    high_quality = [n for n in crawl_data['notes'] if n.get('quality_score', 0) >= 8]
    
    print(f"🎯 筛选出 {len(high_quality)} 条高质量内容")
    print("=" * 70)
    
    client = XHSMCPClient()
    
    # 创建本地存储目录
    corpus_dir = os.path.expanduser('~/.openclaw/workspace/content-ops-workspace/corpus/raw')
    os.makedirs(corpus_dir, exist_ok=True)
    
    detailed_contents = []
    
    for i, note in enumerate(high_quality, 1):
        print(f"\n[{i}/{len(high_quality)}] 抓取详情: {note['title'][:40]}...")
        
        try:
            result = client.get_feed_detail(note['id'], note.get('xsec_token', ''))
            
            if result.get('success'):
                feed_data = result.get('data', {}).get('feed', {})
                note_card = feed_data.get('noteCard', {})
                
                # 提取完整数据
                full_content = {
                    'note_id': note['id'],
                    'title': note_card.get('displayTitle', note['title']),
                    'description': note_card.get('desc', ''),
                    'type': note_card.get('type', 'unknown'),
                    'author': {
                        'nickname': note_card.get('user', {}).get('nickname', ''),
                        'user_id': note_card.get('user', {}).get('userId', ''),
                    },
                    'interaction': note_card.get('interactInfo', {}),
                    'images': [img.get('urlDefault', '') for img in note_card.get('imageList', [])],
                    'tags': note_card.get('tagList', []),
                    'comments': feed_data.get('comments', []),
                    'fetched_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'source_url': f"https://www.xiaohongshu.com/explore/{note['id']}"
                }
                
                # 保存到本地文件
                filename = f"xhs_{note['id']}_{int(time.time())}.json"
                filepath = os.path.join(corpus_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(full_content, f, ensure_ascii=False, indent=2)
                
                detailed_contents.append(full_content)
                
                desc_len = len(full_content['description'])
                comment_count = len(full_content['comments'])
                img_count = len(full_content['images'])
                
                print(f"    ✅ 成功")
                print(f"    📝 正文: {desc_len} 字")
                print(f"    💬 评论: {comment_count} 条")
                print(f"    🖼️ 图片: {img_count} 张")
                print(f"    💾 已保存: {filename}")
                
            else:
                print(f"    ❌ 失败: {result.get('message', '未知错误')}")
                detailed_contents.append({
                    'note_id': note['id'],
                    'title': note['title'],
                    'fetch_success': False,
                    'error': result.get('message', '未知错误')
                })
            
            # 间隔 3 秒，避免风控
            time.sleep(3)
            
        except Exception as e:
            print(f"    ❌ 错误: {e}")
            detailed_contents.append({
                'note_id': note['id'],
                'title': note['title'],
                'fetch_success': False,
                'error': str(e)
            })
    
    # 保存汇总
    summary = {
        'query': crawl_data.get('query', ''),
        'total_selected': len(high_quality),
        'success_count': sum(1 for d in detailed_contents if d.get('fetch_success', True)),
        'contents': detailed_contents,
        'saved_to': corpus_dir,
        'generated_at': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    summary_path = os.path.join(corpus_dir, 'summary_ai_contents.json')
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*70}")
    print(f"✅ 详情抓取完成")
    print(f"   成功: {summary['success_count']}/{summary['total_selected']}")
    print(f"   保存位置: {corpus_dir}")
    print(f"   汇总文件: summary_ai_contents.json")
    print(f"{'='*70}")
    
    return summary

if __name__ == "__main__":
    fetch_high_quality_details()
