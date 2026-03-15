#!/usr/bin/env python3
"""
测试 xiaohongshutools skill 获取笔记详情
"""

import asyncio
import sys
import json

sys.path.insert(0, '/home/admin/.openclaw/workspace/skills/content-ops/xiaohongshutools/scripts')

from request.web.xhs_session import create_xhs_session

async def test_note_detail():
    """测试获取笔记详情"""
    
    print("🧪 测试 xiaohongshutools 获取笔记详情...\n")
    
    # 创建会话（无代理，游客模式）
    xhs = await create_xhs_session(proxy=None, web_session=None)
    
    # 测试笔记 ID 和 xsec_token（从我们之前抓取的数据）
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
        print(f"   ID: {case['note_id']}")
        
        try:
            # 获取笔记详情
            res = await xhs.apis.note.note_detail(case['note_id'], case['xsec_token'])
            data = await res.json()
            
            if data.get('success'):
                note_data = data.get('data', {}).get('note', {})
                
                title = note_data.get('title', note_data.get('display_title', '无标题'))
                desc = note_data.get('desc', '')
                liked = note_data.get('liked_count', 0)
                
                print(f"   ✅ 成功")
                print(f"   📝 标题: {title[:50]}...")
                print(f"   📄 正文: {len(desc)} 字")
                print(f"   👍 点赞: {liked}")
                
                if desc:
                    print(f"   📃 预览: {desc[:100]}...")
            else:
                print(f"   ❌ 失败: {data.get('msg', '未知错误')}")
                print(f"   返回: {json.dumps(data, ensure_ascii=False)[:200]}")
                
        except Exception as e:
            print(f"   ❌ 错误: {e}")
        
        print()
        await asyncio.sleep(2)
    
    # 测试获取评论
    print("💬 测试获取评论...")
    try:
        res = await xhs.apis.comments.get_comments(test_cases[0]['note_id'], test_cases[0]['xsec_token'])
        data = await res.json()
        
        if data.get('success'):
            comments = data.get('data', {}).get('comments', [])
            print(f"   ✅ 成功，获取 {len(comments)} 条评论")
            for c in comments[:3]:
                content = c.get('content', '')
                user = c.get('user', {}).get('nickname', '匿名')
                print(f"   👤 {user}: {content[:50]}...")
        else:
            print(f"   ❌ 失败: {data.get('msg', '未知错误')}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    await xhs.close_session()
    print("\n✅ 测试完成")

if __name__ == "__main__":
    asyncio.run(test_note_detail())
