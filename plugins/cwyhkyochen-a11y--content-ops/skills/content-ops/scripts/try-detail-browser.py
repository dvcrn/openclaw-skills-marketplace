#!/usr/bin/env python3
"""
重新尝试获取详情，使用新鲜的 token
"""

import requests
import json
import time

def try_get_detail(note_id, title):
    """尝试获取详情 - 先不指定 xsec_token，让服务端生成"""
    
    print(f"\n📄 尝试: {title[:40]}...")
    print(f"   ID: {note_id}")
    
    # 方法1: 直接访问笔记页面获取初始状态
    detail_url = f"https://www.xiaohongshu.com/explore/{note_id}"
    
    try:
        # 先用简单请求获取页面
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        
        # 从 MCP cookie 文件读取
        with open('/home/admin/.openclaw/workspace/bin/cookies.json', 'r') as f:
            cookies_list = json.load(f)
        
        # 转换为 dict
        cookies = {c['name']: c['value'] for c in cookies_list}
        
        print(f"   🍪 使用 cookies: {list(cookies.keys())[:5]}...")
        
        # 先请求页面获取 xsec_token
        resp = requests.get(detail_url, headers=headers, cookies=cookies, timeout=30)
        
        print(f"   📡 页面状态: {resp.status_code}")
        
        # 从 URL 或响应中提取 xsec_token
        if 'xsec_token=' in resp.url:
            import urllib.parse
            parsed = urllib.parse.urlparse(resp.url)
            params = urllib.parse.parse_qs(parsed.query)
            xsec_token = params.get('xsec_token', [''])[0]
            print(f"   🔑 从 URL 提取 xsec_token: {xsec_token[:30]}...")
        else:
            xsec_token = ""
            print(f"   ⚠️ URL 中没有 xsec_token")
        
        # 尝试从页面中提取 note 数据
        content = resp.text
        
        # 查找 INITIAL_STATE
        if 'window.__INITIAL_STATE__' in content:
            print(f"   ✅ 页面包含 INITIAL_STATE 数据")
            
            # 尝试提取
            import re
            match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.+?});', content, re.DOTALL)
            if match:
                try:
                    state = json.loads(match.group(1))
                    
                    # 查找 note 数据
                    if 'note' in state and 'noteDetailMap' in state['note']:
                        note_map = state['note']['noteDetailMap']
                        if note_id in note_map:
                            note_data = note_map[note_id]
                            
                            title = note_data.get('title', '') or note_data.get('displayTitle', '')
                            desc = note_data.get('desc', '')
                            
                            print(f"   📝 标题: {title[:50]}...")
                            print(f"   📄 正文长度: {len(desc)} 字符")
                            
                            if desc:
                                print(f"   📃 预览: {desc[:200]}...")
                                return {
                                    'success': True,
                                    'note_id': note_id,
                                    'title': title,
                                    'description': desc,
                                    'source': 'initial_state'
                                }
                except Exception as e:
                    print(f"   ⚠️ 解析失败: {e}")
        else:
            print(f"   ❌ 页面没有 INITIAL_STATE")
        
        # 如果页面抓取失败，尝试调用 MCP 详情接口
        print(f"   🔄 尝试 MCP 详情接口...")
        
        mcp_resp = requests.post(
            'http://localhost:18060/api/v1/feeds/detail',
            json={
                'feed_id': note_id,
                'xsec_token': xsec_token,
                'load_all_comments': False
            },
            timeout=60
        )
        
        mcp_data = mcp_resp.json()
        
        if mcp_data.get('success'):
            feed = mcp_data.get('data', {}).get('feed', {})
            note_card = feed.get('noteCard', {})
            
            title = note_card.get('displayTitle', '') or note_card.get('title', '')
            desc = note_card.get('desc', '')
            
            print(f"   ✅ MCP 接口成功")
            print(f"   📝 标题: {title[:50]}...")
            print(f"   📄 正文长度: {len(desc)} 字符")
            
            if desc:
                print(f"   📃 预览: {desc[:200]}...")
                return {
                    'success': True,
                    'note_id': note_id,
                    'title': title,
                    'description': desc,
                    'source': 'mcp_api'
                }
            else:
                print(f"   ⚠️ MCP 返回成功但正文为空")
        else:
            print(f"   ❌ MCP 接口失败: {mcp_data.get('message', '未知错误')}")
        
        return {
            'success': False,
            'note_id': note_id,
            'error': 'No content found'
        }
        
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return {
            'success': False,
            'note_id': note_id,
            'error': str(e)
        }

def main():
    # 测试几条内容
    test_notes = [
        {
            'id': '69a1686e0000000015021952',
            'title': '当吃货遇上人工智能'
        },
        {
            'id': '699f0139000000000e00fd1e',
            'title': '访谈谷歌AI科学家'
        },
        {
            'id': '699b183a000000002800b81a',
            'title': '盘点一周AI大事'
        }
    ]
    
    print("🧪 使用浏览器 Cookie 重新尝试获取详情\n")
    print("=" * 70)
    
    results = []
    for note in test_notes:
        result = try_get_detail(note['id'], note['title'])
        results.append(result)
        time.sleep(3)
    
    # 统计
    success_count = sum(1 for r in results if r.get('success'))
    with_content = sum(1 for r in results if r.get('success') and r.get('description'))
    
    print(f"\n{'='*70}")
    print(f"✅ 完成")
    print(f"   成功获取: {success_count}/{len(test_notes)}")
    print(f"   有正文内容: {with_content}/{len(test_notes)}")
    print(f"{'='*70}")
    
    return results

if __name__ == "__main__":
    main()
