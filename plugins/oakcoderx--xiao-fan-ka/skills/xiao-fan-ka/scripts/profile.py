#!/usr/bin/env python3
"""
小饭卡 - 口味画像管理
用法:
  python3 profile.py add "鲤承" --tags "中餐,精致小馆" --feeling "喜欢" --price 200
  python3 profile.py remove "鲤承"
  python3 profile.py list
  python3 profile.py analyze
  python3 profile.py tags
  python3 profile.py export
  python3 profile.py reset
"""

import sys
import json
import argparse
import os
from datetime import datetime
from pathlib import Path

# 数据目录：skill自身的data目录
DATA_DIR = Path(__file__).parent.parent / 'data'
PROFILE_PATH = DATA_DIR / 'taste-profile.json'


def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_profile() -> dict:
    ensure_data_dir()
    if PROFILE_PATH.exists():
        with open(PROFILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'user': {},
        'restaurants': [],
        'preferences': {},
        'updated_at': None,
    }


def save_profile(profile: dict):
    ensure_data_dir()
    profile['updated_at'] = datetime.now().isoformat()
    with open(PROFILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)


def add_restaurant(name, tags, feeling, price=None,
                   area=None, city=None,
                   notes=None, source=None):
    """添加或更新一家餐厅"""
    profile = load_profile()

    existing = next((r for r in profile['restaurants'] if r['name'] == name), None)
    if existing:
        existing['tags'] = list(set(existing.get('tags', []) + tags))
        if feeling:
            existing['feeling'] = feeling
        if price:
            existing['avg_price'] = price
        if area:
            existing['area'] = area
        if city:
            existing['city'] = city
        if notes:
            existing['notes'] = notes
        if source:
            existing['source'] = source
        existing['updated_at'] = datetime.now().isoformat()
        existing['visits'] = existing.get('visits', 0) + 1
        print(f"✏️  已更新: {name}")
    else:
        entry = {
            'name': name,
            'tags': tags,
            'feeling': feeling,
            'avg_price': price,
            'area': area,
            'city': city,
            'notes': notes,
            'source': source,
            'visits': 1,
            'added_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
        }
        profile['restaurants'].append(entry)
        print(f"✅ 已添加: {name}")

    save_profile(profile)


def remove_restaurant(name: str):
    """删除一家餐厅"""
    profile = load_profile()
    before = len(profile['restaurants'])
    profile['restaurants'] = [r for r in profile['restaurants'] if r['name'] != name]
    after = len(profile['restaurants'])
    if before > after:
        save_profile(profile)
        print(f"🗑️  已删除: {name}")
    else:
        print(f"⚠️  未找到: {name}")


def list_restaurants():
    """列出所有记录的餐厅"""
    profile = load_profile()
    restaurants = profile.get('restaurants', [])

    if not restaurants:
        print("还没有记录任何餐厅，试试 onboard.py 开始吧")
        return

    # 显示用户信息
    user = profile.get('user', {})
    if user:
        city = user.get('city', '')
        areas = ', '.join(user.get('areas', []))
        if city or areas:
            print(f"📍 {city} {areas}\n")

    groups = {}
    for r in restaurants:
        feeling = r.get('feeling', '未分类')
        groups.setdefault(feeling, []).append(r)

    feeling_order = ['喜欢', '常去', '去过', '感兴趣', '想去', '一般', '不喜欢', '未分类']
    feeling_emoji = {
        '喜欢': '❤️', '常去': '🔁', '去过': '✅', '感兴趣': '👀',
        '想去': '📌', '一般': '😐', '不喜欢': '👎', '未分类': '❓'
    }

    for feeling in feeling_order:
        if feeling in groups:
            emoji = feeling_emoji.get(feeling, '•')
            print(f"\n{emoji} {feeling}:")
            for r in groups[feeling]:
                price = f" ¥{r['avg_price']}" if r.get('avg_price') else ''
                area = f" 📍{r['area']}" if r.get('area') else ''
                tags = ' '.join(f'#{t}' for t in r.get('tags', []))
                visits = f" ({r['visits']}次)" if r.get('visits', 0) > 1 else ''
                print(f"  • {r['name']}{price}{area}{visits} {tags}")
                if r.get('notes'):
                    print(f"    💬 {r['notes']}")

    print(f"\n共 {len(restaurants)} 家餐厅")


def analyze():
    """分析口味偏好"""
    profile = load_profile()
    restaurants = profile.get('restaurants', [])

    if len(restaurants) < 3:
        print(f"数据太少（{len(restaurants)}家），至少3家才能分析")
        return

    tag_counts = {}
    liked_tags = {}
    disliked_tags = {}
    price_points = []
    area_counts = {}

    for r in restaurants:
        tags = r.get('tags', [])
        feeling = r.get('feeling', '')
        price = r.get('avg_price')
        area = r.get('area')
        is_positive = feeling in ('喜欢', '常去', '感兴趣', '想去')
        is_negative = feeling in ('不喜欢', '一般')

        for tag in tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
            if is_positive:
                liked_tags[tag] = liked_tags.get(tag, 0) + 1
            elif is_negative:
                disliked_tags[tag] = disliked_tags.get(tag, 0) + 1

        if price and is_positive:
            price_points.append(price)

        if area and is_positive:
            area_counts[area] = area_counts.get(area, 0) + 1

    # 输出
    print("🧠 口味画像分析\n")

    total = len(restaurants)
    liked = sum(1 for r in restaurants if r.get('feeling') in ('喜欢', '常去'))
    disliked = sum(1 for r in restaurants if r.get('feeling') == '不喜欢')
    print(f"📊 共 {total} 家：{liked} 家喜欢，{disliked} 家不喜欢\n")

    if liked_tags:
        sorted_tags = sorted(liked_tags.items(), key=lambda x: x[1], reverse=True)
        print("✅ 喜欢的标签:")
        for tag, count in sorted_tags[:10]:
            bar = '█' * count
            print(f"  #{tag}: {bar} ({count})")
        print()

    if disliked_tags:
        sorted_tags = sorted(disliked_tags.items(), key=lambda x: x[1], reverse=True)
        print("❌ 不喜欢的标签:")
        for tag, count in sorted_tags[:5]:
            print(f"  #{tag} ({count})")
        print()

    if price_points:
        avg = sum(price_points) / len(price_points)
        low = min(price_points)
        high = max(price_points)
        print(f"💰 偏好价位: ¥{low}-¥{high}，平均 ¥{avg:.0f}\n")

    if area_counts:
        sorted_areas = sorted(area_counts.items(), key=lambda x: x[1], reverse=True)
        print("📍 常去区域:")
        for area, count in sorted_areas[:5]:
            print(f"  {area}: {count}家")
        print()

    # 生成画像摘要
    top_liked = [t for t, _ in sorted(liked_tags.items(), key=lambda x: x[1], reverse=True)[:8]]
    top_disliked = [t for t, _ in sorted(disliked_tags.items(), key=lambda x: x[1], reverse=True)[:3]]
    top_areas = [a for a, _ in sorted(area_counts.items(), key=lambda x: x[1], reverse=True)[:3]]

    print("📝 画像摘要:")
    if top_liked:
        print(f"  喜欢: {', '.join(top_liked)}")
    if top_disliked:
        print(f"  不喜欢: {', '.join(top_disliked)}")
    if price_points:
        print(f"  价位: 人均¥{avg:.0f}左右 (¥{low}-¥{high})")
    if top_areas:
        print(f"  常去: {', '.join(top_areas)}")

    # 保存分析结果
    profile['preferences'] = {
        'liked_tags': top_liked,
        'disliked_tags': top_disliked,
        'avg_price': round(avg) if price_points else None,
        'price_range': [low, high] if price_points else None,
        'top_areas': top_areas,
        'total_restaurants': total,
        'analyzed_at': datetime.now().isoformat(),
    }
    save_profile(profile)
    print("\n✅ 画像已更新")


def show_tags():
    """显示所有标签"""
    profile = load_profile()
    tag_counts = {}
    for r in profile.get('restaurants', []):
        for tag in r.get('tags', []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    if not tag_counts:
        print("还没有标签")
        return

    print("🏷️  所有标签:")
    for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  #{tag} ({count})")


def export_json():
    """导出完整画像数据"""
    profile = load_profile()
    print(json.dumps(profile, ensure_ascii=False, indent=2))


def reset_profile():
    """重置画像"""
    if PROFILE_PATH.exists():
        PROFILE_PATH.unlink()
        print("🔄 画像已重置")
    else:
        print("画像本来就是空的")


def set_user(city: str = None, areas: list = None, dislikes: list = None):
    """设置用户基本信息"""
    profile = load_profile()
    user = profile.get('user', {})
    if city:
        user['city'] = city
    if areas:
        user['areas'] = areas
    if dislikes:
        user['dislikes'] = dislikes
    user['updated_at'] = datetime.now().isoformat()
    profile['user'] = user
    save_profile(profile)
    print(f"✅ 用户信息已更新")


def main():
    parser = argparse.ArgumentParser(description='小饭卡 - 口味画像管理')
    sub = parser.add_subparsers(dest='command')

    # add
    add_p = sub.add_parser('add', help='添加餐厅')
    add_p.add_argument('name', help='餐厅名')
    add_p.add_argument('--tags', default='', help='标签，逗号分隔')
    add_p.add_argument('--feeling', default='喜欢',
                       choices=['喜欢', '常去', '去过', '感兴趣', '想去', '一般', '不喜欢'],
                       help='感受')
    add_p.add_argument('--price', type=int, help='人均价格')
    add_p.add_argument('--area', help='区域')
    add_p.add_argument('--city', help='城市')
    add_p.add_argument('--notes', help='备注')
    add_p.add_argument('--source', help='信息来源(dianping/xiaohongshu/user)')

    # remove
    rm_p = sub.add_parser('remove', help='删除餐厅')
    rm_p.add_argument('name', help='餐厅名')

    # user
    user_p = sub.add_parser('user', help='设置用户信息')
    user_p.add_argument('--city', help='城市')
    user_p.add_argument('--areas', help='常去区域，逗号分隔')
    user_p.add_argument('--dislikes', help='不喜欢的，逗号分隔')

    sub.add_parser('list', help='列出所有餐厅')
    sub.add_parser('analyze', help='分析口味偏好')
    sub.add_parser('tags', help='显示所有标签')
    sub.add_parser('export', help='导出JSON')
    sub.add_parser('reset', help='重置画像')

    args = parser.parse_args()

    if args.command == 'add':
        tags = [t.strip() for t in args.tags.split(',') if t.strip()]
        add_restaurant(args.name, tags, args.feeling, args.price, args.area, args.city, args.notes, args.source)
    elif args.command == 'remove':
        remove_restaurant(args.name)
    elif args.command == 'user':
        areas = [a.strip() for a in args.areas.split(',') if a.strip()] if args.areas else None
        dislikes = [d.strip() for d in args.dislikes.split(',') if d.strip()] if args.dislikes else None
        set_user(args.city, areas, dislikes)
    elif args.command == 'list':
        list_restaurants()
    elif args.command == 'analyze':
        analyze()
    elif args.command == 'tags':
        show_tags()
    elif args.command == 'export':
        export_json()
    elif args.command == 'reset':
        reset_profile()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
