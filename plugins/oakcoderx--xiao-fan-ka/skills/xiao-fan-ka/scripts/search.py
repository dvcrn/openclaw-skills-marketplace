#!/usr/bin/env python3
"""
小饭卡 - 大众点评搜索
用法:
  python3 search.py "三里屯 创意菜"
  python3 search.py "国贸 日料 人均500" --city 北京
  python3 search.py "朝阳 素食" --max 15 --json
"""

import sys
import json
import argparse
import re
import os


PROXY = os.environ.get('DDGS_PROXY') or None


def search_dianping(query: str, city: str = '', max_results: int = 20) -> list:
    """搜索大众点评上的餐厅信息"""
    from ddgs import DDGS
    ddgs = DDGS(proxy=PROXY)

    city_str = f' {city}' if city else ''
    search_queries = [
        f'site:dianping.com {query}{city_str} 餐厅',
        f'{query}{city_str} 餐厅 大众点评 推荐',
    ]

    all_results = []
    seen_urls = set()

    for sq in search_queries:
        try:
            results = ddgs.text(sq, max_results=max_results, region='cn-zh')
            for r in results:
                url = r.get('href', '')
                if url not in seen_urls:
                    seen_urls.add(url)
                    all_results.append(r)
        except Exception as e:
            print(f"搜索出错 [{sq}]: {e}", file=sys.stderr)

    restaurants = []
    for r in all_results:
        parsed = parse_result(r)
        if parsed:
            restaurants.append(parsed)

    return restaurants


def parse_result(result):
    """从搜索结果中解析餐厅信息"""
    title = result.get('title', '')
    body = result.get('body', '')
    url = result.get('href', '')
    combined = f"{title} {body}"

    is_dianping = 'dianping.com' in url
    food_keywords = ['餐厅', '餐馆', '饭店', '菜', '人均', '推荐菜', '好吃', '味道', '料理', '火锅', '烤', '店', '馆']
    is_restaurant = any(kw in combined for kw in food_keywords)

    if not is_restaurant:
        return None

    # 过滤非餐厅页面
    skip_patterns = ['shopRank', 'pcChannelRanking', '/photos', '/album']
    if any(p in url for p in skip_patterns):
        return None

    non_food = ['按摩', '足浴', '养生馆', '美容', '美发', '酒店', 'KTV', '健身']
    if any(nf in combined for nf in non_food) and not any(kw in combined for kw in food_keywords[:6]):
        return None

    # 提取人均
    price_match = re.search(r'[人均¥￥](\d+)', combined)
    avg_price = int(price_match.group(1)) if price_match else None

    # 提取店名
    shop_name = None
    name_match = re.search(r'【(.+?)】', title)
    if name_match:
        shop_name = name_match.group(1)
    elif '(' in title and '大众点评' not in title:
        shop_name = title.split(' - ')[0].split('|')[0].strip()

    # 提取评分
    score_match = re.search(r'(\d\.\d)\s*分', combined)
    score = float(score_match.group(1)) if score_match else None

    # 提取菜系
    categories = []
    cat_keywords = {
        '中餐': ['中餐', '京菜', '鲁菜', '川菜', '粤菜', '湘菜', '浙菜', '苏菜', '徽菜', '闽菜'],
        '日料': ['日本料理', '日料', '寿司', '刺身', '居酒屋', 'omakase'],
        '西餐': ['西餐', '法餐', '意大利', '西班牙', '牛排'],
        '火锅': ['火锅', '涮肉', '涮锅'],
        '烧烤': ['烤肉', '烧烤', '炙子'],
        '素食': ['素食', '素菜', '蔬食'],
        '创意菜': ['创意菜', '融合菜', '新派'],
        '私房菜': ['私房菜', '私厨'],
        '东南亚': ['泰国菜', '越南菜', '东南亚', '泰餐'],
        '韩餐': ['韩国料理', '韩餐', '韩国菜'],
        '潮汕': ['潮汕', '潮州', '汕头'],
        '云南菜': ['云南菜', '滇菜', '云贵'],
        '贵州菜': ['贵州菜', '黔菜'],
    }
    for cat, keywords in cat_keywords.items():
        if any(kw in combined for kw in keywords):
            categories.append(cat)

    is_shop_page = '/shop/' in url or '/shopshare/' in url

    return {
        'name': shop_name or title[:40],
        'avg_price': avg_price,
        'score': score,
        'categories': categories,
        'snippet': body[:200] if body else '',
        'url': url,
        'source': 'dianping' if is_dianping else 'search',
        'is_shop_page': is_shop_page,
    }


def main():
    parser = argparse.ArgumentParser(description='小饭卡 - 大众点评搜索')
    parser.add_argument('query', help='搜索关键词')
    parser.add_argument('--city', default='', help='城市')
    parser.add_argument('--max', type=int, default=20, help='最大结果数')
    parser.add_argument('--json', action='store_true', help='JSON输出')
    args = parser.parse_args()

    restaurants = search_dianping(args.query, args.city, args.max)

    if args.json:
        print(json.dumps(restaurants, ensure_ascii=False, indent=2))
    else:
        if not restaurants:
            print("没有找到相关餐厅")
            return

        restaurants.sort(key=lambda x: (x['is_shop_page'], x['avg_price'] is not None), reverse=True)

        print(f"🔍 大众点评搜索: {args.query}\n")
        for i, r in enumerate(restaurants, 1):
            name = r['name']
            price = f"¥{r['avg_price']}" if r['avg_price'] else ''
            score = f"⭐{r['score']}" if r['score'] else ''
            cats = ' '.join(f'#{c}' for c in r['categories']) if r['categories'] else ''
            info = ' | '.join(p for p in [price, score, cats] if p)

            print(f"{i}. {name}")
            if info:
                print(f"   {info}")
            if r['snippet']:
                print(f"   {r['snippet'][:80]}")
            print()


if __name__ == '__main__':
    main()
