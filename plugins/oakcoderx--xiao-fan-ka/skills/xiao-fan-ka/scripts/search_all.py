#!/usr/bin/env python3
"""
小饭卡 - 双源搜索（大众点评 + 小红书）
自动合并两个来源，交叉验证，按画像匹配度排序。

用法:
  python3 search_all.py "三里屯 创意菜"
  python3 search_all.py "国贸 日料" --city 北京 --max 10 --json
"""

import sys
import json
import argparse
import os
from pathlib import Path

# 导入同目录的搜索模块
sys.path.insert(0, str(Path(__file__).parent))
from search import search_dianping
from search_xhs import search_xiaohongshu

DATA_DIR = Path(__file__).parent.parent / 'data'
PROFILE_PATH = DATA_DIR / 'taste-profile.json'


def load_preferences() -> dict:
    """加载用户偏好"""
    if PROFILE_PATH.exists():
        with open(PROFILE_PATH, 'r', encoding='utf-8') as f:
            profile = json.load(f)
            return profile.get('preferences', {})
    return {}


def match_score(restaurant: dict, preferences: dict) -> float:
    """计算餐厅与用户偏好的匹配度 (0-100)"""
    if not preferences:
        return 50  # 无画像时给中间分

    score = 50  # 基础分
    liked_tags = set(preferences.get('liked_tags', []))
    disliked_tags = set(preferences.get('disliked_tags', []))
    price_range = preferences.get('price_range', [])
    top_areas = set(preferences.get('top_areas', []))

    restaurant_tags = set(restaurant.get('categories', []) + restaurant.get('tags', []))

    # 标签匹配 (+5 每个匹配)
    matched = liked_tags & restaurant_tags
    score += len(matched) * 5

    # 踩雷标签 (-10 每个)
    anti_matched = disliked_tags & restaurant_tags
    score -= len(anti_matched) * 10

    # 价位匹配
    price = restaurant.get('avg_price')
    if price and price_range and len(price_range) == 2:
        low, high = price_range
        margin = (high - low) * 0.3  # 30%容差
        if low - margin <= price <= high + margin:
            score += 5
        elif price > high * 1.5 or price < low * 0.5:
            score -= 5

    # 区域匹配
    area = restaurant.get('area', '')
    if area and area in top_areas:
        score += 3

    # 小红书好评加分
    if restaurant.get('xhs_sentiment') == 'positive':
        score += 5
    elif restaurant.get('xhs_sentiment') == 'negative':
        score -= 8

    # 双源验证加分
    if restaurant.get('cross_verified'):
        score += 10

    return min(max(score, 0), 100)


def merge_results(dianping_results: list, xhs_results: list) -> list:
    """合并大众点评和小红书结果"""
    merged = {}

    # 大众点评结果为基础
    for r in dianping_results:
        name = r['name']
        merged[name] = {
            **r,
            'tags': r.get('categories', []),
            'sources': ['dianping'],
            'xhs_notes': [],
            'cross_verified': False,
        }

    # 匹配小红书结果
    for note in xhs_results:
        mentioned = note.get('restaurants_mentioned', [])
        for rname in mentioned:
            # 精确匹配或包含匹配
            matched_key = None
            for key in merged:
                if rname in key or key in rname:
                    matched_key = key
                    break

            if matched_key:
                # 交叉验证！
                merged[matched_key]['cross_verified'] = True
                merged[matched_key]['sources'].append('xiaohongshu')
                merged[matched_key]['xhs_notes'].append({
                    'title': note['title'],
                    'sentiment': note['sentiment'],
                    'url': note['url'],
                })
                if note['sentiment']:
                    merged[matched_key]['xhs_sentiment'] = note['sentiment']
            else:
                # 小红书独有的餐厅
                if rname and rname not in merged:
                    merged[rname] = {
                        'name': rname,
                        'avg_price': note.get('avg_price'),
                        'score': None,
                        'categories': [],
                        'tags': [],
                        'snippet': note.get('snippet', ''),
                        'url': note.get('url', ''),
                        'source': 'xiaohongshu',
                        'sources': ['xiaohongshu'],
                        'xhs_notes': [{'title': note['title'], 'sentiment': note['sentiment']}],
                        'xhs_sentiment': note.get('sentiment'),
                        'cross_verified': False,
                        'is_shop_page': False,
                    }

    return list(merged.values())


def main():
    parser = argparse.ArgumentParser(description='小饭卡 - 双源搜索')
    parser.add_argument('query', help='搜索关键词')
    parser.add_argument('--city', default='', help='城市')
    parser.add_argument('--max', type=int, default=10, help='最大结果数')
    parser.add_argument('--json', action='store_true', help='JSON输出')
    args = parser.parse_args()

    print(f"🔍 搜索中...\n", file=sys.stderr)

    # 双源搜索
    dp_results = search_dianping(args.query, args.city, max_results=args.max)
    xhs_results = search_xiaohongshu(args.query, max_results=args.max)

    print(f"📊 大众点评 {len(dp_results)} 条 | 小红书 {len(xhs_results)} 条\n", file=sys.stderr)

    # 合并
    merged = merge_results(dp_results, xhs_results)

    # 按画像匹配度排序
    preferences = load_preferences()
    for r in merged:
        r['match_score'] = match_score(r, preferences)

    merged.sort(key=lambda x: (x.get('cross_verified', False), x['match_score']), reverse=True)

    # 限制数量
    merged = merged[:args.max]

    if args.json:
        print(json.dumps(merged, ensure_ascii=False, indent=2))
    else:
        if not merged:
            print("没有找到相关餐厅")
            return

        has_prefs = bool(preferences.get('liked_tags'))
        print(f"🍜 小饭卡推荐: {args.query}")
        if has_prefs:
            print(f"   (已根据你的口味画像排序)")
        print()

        for i, r in enumerate(merged, 1):
            name = r['name']
            price = f"¥{r['avg_price']}" if r.get('avg_price') else ''
            score = f"⭐{r['score']}" if r.get('score') else ''
            match = f"匹配{r['match_score']:.0f}%" if has_prefs else ''

            # 来源标记
            sources = r.get('sources', [])
            if r.get('cross_verified'):
                src_mark = '✅双源验证'
            elif 'dianping' in sources and 'xiaohongshu' in sources:
                src_mark = '📊点评+📕小红书'
            elif 'xiaohongshu' in sources:
                src_mark = '📕小红书'
            else:
                src_mark = '📊点评'

            info = ' | '.join(p for p in [price, score, match, src_mark] if p)
            print(f"{i}. {name}")
            if info:
                print(f"   {info}")

            # 小红书评价
            for note in r.get('xhs_notes', [])[:1]:
                sentiment_emoji = {'positive': '👍', 'negative': '⚠️', 'neutral': ''}
                s_emoji = sentiment_emoji.get(note.get('sentiment', ''), '')
                print(f"   📕 {s_emoji} {note['title'][:50]}")

            if r.get('snippet'):
                print(f"   {r['snippet'][:60]}")
            print()


if __name__ == '__main__':
    main()
