#!/usr/bin/env python3
"""
小饭卡 - 小红书探店搜索（使用 Serper API）
用法:
  python3 search_xhs.py "三里屯 宝藏餐厅"
  python3 search_xhs.py "国贸 日料" --max 30 --json
"""

import sys
import json
import argparse
import re
import os
import subprocess

SERPER_API_KEY = os.environ.get('SERPER_API_KEY') or '380883ffc186cebf26d0681c1a65482f499f5fe7'


def search_xiaohongshu(query: str, max_results: int = 30) -> list:
    """搜索小红书探店笔记（使用 search-hub）
    
    Args:
        query: 搜索关键词
        max_results: 最大结果数（默认 30 条笔记）
    """
    search_query = f'site:xiaohongshu.com {query} 探店'
    
    try:
        # 调用 search-hub（用 python3.13）
        result = subprocess.run(
            ['python3.13', 'skills/search-hub/scripts/hub.py', 'search', search_query, '-t', 'text', '-l', str(max_results)],
            cwd='/Users/mac/.openclaw/workspace',
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"search-hub 出错：{result.stderr}", file=sys.stderr)
            return []
        
        # 解析 JSON 输出
        data = json.loads(result.stdout)
        results = data.get('results', [])
        
        # 解析笔记
        notes = []
        for r in results:
            parsed = parse_xhs_result(r)
            if parsed:
                notes.append(parsed)
        
        return notes
        
    except Exception as e:
        print(f"搜索出错：{e}", file=sys.stderr)
        return []


def serper_search(query: str, max_results: int = 25) -> list:
    """使用 Serper API 搜索"""
    url = "https://google.serper.dev/search"
    
    payload = {
        "q": query,
        "num": max_results,
        "gl": "cn",
        "hl": "zh-cn"
    }
    
    headers = {
        'X-API-TOKEN': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    return data.get('organic', [])


def parse_xhs_result(result):
    """解析小红书搜索结果"""
    title = result.get('title', '')
    snippet = result.get('snippet', '')
    url = result.get('link', '')
    combined = f"{title} {snippet}"

    # 判断是否餐厅相关
    food_keywords = ['餐厅', '探店', '好吃', '美食', '菜', '馆', '料理', '打卡', '必吃', '推荐', '人均']
    if not any(kw in combined for kw in food_keywords):
        return None

    # 提取提到的餐厅名（通常在标题或正文中以书名号标注）
    restaurant_names = re.findall(r'[「『【《](.+?)[」』】》]', combined)
    if not restaurant_names:
        # 尝试从标题提取
        name_match = re.search(r'^([^|!\n]+)', title)
        if name_match:
            restaurant_names = [name_match.group(1).strip()]

    # 提取人均
    price_match = re.search(r'[人均¥￥](\d+)', combined)
    avg_price = int(price_match.group(1)) if price_match else None

    # 判断情感（正面/负面）
    positive_words = ['好吃', '推荐', '绝了', '惊艳', '宝藏', '神仙', '必吃', '回购', '超赞', '满分', '爱了']
    negative_words = ['踩雷', '不好吃', '拔草', '失望', '难吃', '不推荐', '一般', '避雷', '翻车']
    
    pos_count = sum(1 for w in positive_words if w in combined)
    neg_count = sum(1 for w in negative_words if w in combined)

    if neg_count > pos_count:
        sentiment = 'negative'
    elif pos_count > neg_count:
        sentiment = 'positive'
    else:
        sentiment = 'neutral'

    return {
        'title': title,
        'snippet': snippet[:200],
        'url': url,
        'restaurants_mentioned': restaurant_names[:3],  # 最多提取 3 个餐厅名
        'avg_price': avg_price,
        'sentiment': sentiment,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='小饭卡 - 小红书搜索')
    parser.add_argument('query', help='搜索关键词')
    parser.add_argument('--max', type=int, default=30, help='最大结果数')
    parser.add_argument('--json', action='store_true', help='JSON 输出')
    args = parser.parse_args()

    results = search_xiaohongshu(args.query, max_results=args.max)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(f"📕 找到 {len(results)} 条笔记\n")
        for i, note in enumerate(results[:10], 1):
            sentiment_emoji = {'positive': '👍', 'negative': '⚠️', 'neutral': ''}
            s_emoji = sentiment_emoji.get(note.get('sentiment'), '')
            restaurants = ', '.join(note.get('restaurants_mentioned', [])[:2])
            print(f"{i}. {note['title'][:50]}")
            print(f"   {s_emoji} 提到：{restaurants}")
            print()
