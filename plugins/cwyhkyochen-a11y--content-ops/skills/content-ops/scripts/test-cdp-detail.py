#!/usr/bin/env python3
"""
使用 redbookskills 获取笔记详情
通过 Chrome DevTools Protocol (CDP)
"""

import sys
import os
import json
import time

# 添加 redbookskills 到路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REDBOOK_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'redbookskills', 'scripts')
sys.path.insert(0, REDBOOK_DIR)

from feed_explorer import FeedExplorer, FeedExplorerError

def get_feed_detail_via_cdp(feed_id, xsec_token):
    """使用 CDP 获取笔记详情"""
    
    print(f"🔍 获取笔记详情: {feed_id[:20]}...")
    print(f"   xsec_token: {xsec_token[:30]}...")
    
    # 构建详情页 URL
    detail_url = f"https://www.xiaohongshu.com/explore/{feed_id}?xsec_token={xsec_token}&xsec_source=pc_search"
    
    print(f"   URL: {detail_url[:80]}...")
    
    try:
        # 创建 FeedExplorer 实例 (使用 CDP)
        explorer = FeedExplorer(
            host="127.0.0.1",
            port=9222,
            headless=True,  # 无头模式
            reuse_tab=True
        )
        
        print("   🌐 连接到 Chrome...")
        explorer.connect()
        
        print("   📄 加载详情页...")
        explorer.navigate_to_detail(feed_id, xsec_token)
        
        print("   📊 提取数据...")
        detail = explorer.get_feed_detail(feed_id)
        
        print("   ✅ 成功获取!")
        
        # 提取关键信息
        title = detail.get('title', '')
        desc = detail.get('desc', '')
        author = detail.get('user', {}).get('nickname', '')
        
        print(f"\n   📝 标题: {title[:50]}...")
        print(f"   👤 作者: {author}")
        print(f"   📄 正文长度: {len(desc)} 字符")
        
        if desc:
            print(f"   📃 预览: {desc[:200]}...")
        
        explorer.close()
        
        return {
            'success': True,
            'feed_id': feed_id,
            'title': title,
            'author': author,
            'description': desc,
            'raw_data': detail
        }
        
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return {
            'success': False,
            'feed_id': feed_id,
            'error': str(e)
        }

def test_with_cdp():
    """测试 CDP 方式获取详情"""
    
    # 读取我们之前抓取的数据
    with open('/tmp/xhs_ai_crawled.json', 'r') as f:
        crawl_data = json.load(f)
    
    # 筛选高质量内容
    high_quality = [n for n in crawl_data['notes'] if n.get('quality_score', 0) >= 8][:2]
    
    print(f"🎯 测试 {len(high_quality)} 条高质量内容\n")
    print("=" * 70)
    
    results = []
    
    for i, note in enumerate(high_quality, 1):
        print(f"\n[{i}/{len(high_quality)}] {note['title'][:40]}...")
        result = get_feed_detail_via_cdp(note['id'], note.get('xsec_token', ''))
        results.append(result)
        time.sleep(3)
    
    # 保存结果
    output_path = '/tmp/xhs_cdp_results.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'fetched_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*70}")
    print(f"✅ 测试完成")
    success_count = sum(1 for r in results if r.get('success'))
    print(f"   成功: {success_count}/{len(high_quality)}")
    print(f"   保存: {output_path}")
    print(f"{'='*70}")
    
    return results

if __name__ == "__main__":
    test_with_cdp()
