#!/usr/bin/env python3
"""
使用 MCP 的登录信息测试 xiaohongshutools
"""

import asyncio
import sys
import json

sys.path.insert(0, '/home/admin/.openclaw/workspace/skills/content-ops/xiaohongshutools/scripts')

from request.web.xhs_session import create_xhs_session

# 从 MCP cookies.json 读取 web_session
def load_web_session():
    with open('/home/admin/.openclaw/workspace/bin/cookies.json', 'r') as f:
        cookies = json.load(f)
    
    web_session = None
    for c in cookies:
        if c['name'] == 'web_session':
            web_session = c['value']
            break
    
    return web_session

async def test_with_login():
    """使用登录态测试"""
    
    web_session = load_web_session()
    if not web_session:
        print("❌ 未找到 web_session cookie")
        return
    
    print(f"🍪 找到 web_session: {web_session[:30]}...\n")
    
    # 创建会话（使用登录态）
    xhs = await create_xhs_session(proxy=None, web_session=web_session)
    
    # 测试笔记
    test_cases = [
        {
            "note_id": "69a1686e0000000015021952",
            "xsec_token": "ABt9kRSEceFsxy4_6Ej6Y3PKiCkbx5BRLs4O8_px4Du1M=",
            "title": "当吃货遇上人工智能"
        },
        {
            "note_id": "699f0139000000000e00fd1e", 
            "xsec_token": "",
            "title": "访谈谷歌AI科学家"
        }
    ]
    
    for case in test_cases:
        print(f"📄 测试: {case['title']}")
        
        try:
            res = await xhs.apis.note.note_detail(case['note_id'], case['xsec_token'])
            data = await res.json()
            
            if data.get('success'):
                note_data = data.get('data', {}).get('note', {})
                
                title = note_data.get('title', note_data.get('display_title', '无标题'))
                desc = note_data.get('desc', '')
                liked = note_data.get('liked_count', 0)
                
                print(f"   ✅ 成功")
                print(f"   📝 标题: {title[:50]}")
                print(f"   📄 正文: {len(desc)} 字")
                if desc:
                    print(f"   📃 预览: {desc[:150]}...")
                print()
            else:
                print(f"   ❌ 失败: {data.get('msg', '未知错误')}")
                print()
                
        except Exception as e:
            print(f"   ❌ 错误: {e}\n")
        
        await asyncio.sleep(2)
    
    await xhs.close_session()
    print("✅ 测试完成")

if __name__ == "__main__":
    asyncio.run(test_with_login())
