#!/usr/bin/env python3
"""
早期项目发现筛选器
从原始数据中筛选出项目发布/新工具类内容
"""

import csv
import re
from datetime import datetime

# ========== 配置 ==========
INPUT_FILE = "/Users/moer/.openclaw/workspace/skills/agentfarm-finder/output/results_2026-03-12.csv"
OUTPUT_FILE = "/Users/moer/.openclaw/workspace/skills/agentfarm-finder/output/results_2026-03-12_projects.csv"

# 排除的用户名或作者（完全匹配或包含）
EXCLUDE_USERS = [
    'gta6alerts', 'gta', 'clipstudiopaint', 'cryptopulse', 'cryptopulseglbl',
    'veizau', 'tippity', 'bl_zonee', 'sleezbomb', 'tokyo87313395'
]

# 排除的关键词（正文或用户名中包含）
EXCLUDE_KEYWORDS = [
    'gta', 'clip studio', 'pokemon', 'crypto pulse', 'bitcoin breaking',
    'breaking news', 'headlines', 'free agent', 'nba', 'nfl', 'sports',
    'pokimane', 'twitch', 'youtube video', 'music video', 'song', 'album'
]

# 正面关键词：项目发布、新工具、Alpha/Beta 等
POSITIVE_KEYWORDS = [
    # 发布/启动
    'launch', 'introducing', 'introduces', 'released', 'releasing', 'live now',
    'just launched', 'announcing', 'announces', 'coming soon', 'public launch',
    'mint soon', 'mint now', 'first ever', 'new project', 'new tool', 'new platform',
    # 版本/阶段
    'alpha', 'beta', 'v1', 'v2', 'version', 'update', 'upgrade', 'new version',
    # Agent/DeFi 相关
    'agent', 'openclaw', '8004', 'defi', 'yield', 'farm', 'trading bot',
    'autonomous', 'ai agent', 'decentralized', 'on-chain', 'onchain',
    # 其他项目特征
    'powered by', 'built on', 'ecosystem', 'hackathon', 'grant', 'airdrop'
]

def should_exclude_row(row):
    """判断是否应该排除该行"""
    username = row.get('用户名', '').lower()
    author = row.get('作者', '').lower()
    text = row.get('内容', '').lower()
    content = f"{username} {author} {text}"
    
    # 排除用户
    for exclude_user in EXCLUDE_USERS:
        if exclude_user in username or exclude_user in author:
            return True, f"排除用户: {exclude_user}"
    
    # 排除关键词
    for keyword in EXCLUDE_KEYWORDS:
        if keyword in content:
            return True, f"排除关键词: {keyword}"
    
    return False, ""

def is_positive_match(row):
    """判断是否为正面匹配（项目发布相关）"""
    username = row.get('用户名', '').lower()
    author = row.get('作者', '').lower()
    text = row.get('内容', '').lower()
    content = f"{username} {author} {text}"
    
    # 检查是否包含正面关键词
    for keyword in POSITIVE_KEYWORDS:
        if keyword in content:
            return True, keyword
    
    return False, None

def main():
    print("=" * 50)
    print("早期项目发现筛选器")
    print("=" * 50)
    
    # 读取原始数据
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        all_rows = list(reader)
    
    print(f"原始数据: {len(all_rows)} 条")
    
    # 筛选
    kept_rows = []
    excluded_info = []
    
    for row in all_rows:
        # 跳过热度为0的（可选）
        try:
            hotness = int(row.get('热度', 0))
        except:
            hotness = 0
        
        # 先检查是否应该排除
        should_exclude, reason = should_exclude_row(row)
        if should_exclude:
            excluded_info.append((row.get('用户名', ''), row.get('热度', '0'), reason))
            continue
        
        # 检查是否为正面匹配
        is_positive, matched_keyword = is_positive_match(row)
        
        # 如果是正面匹配，或者热度比较高（>10），保留
        if is_positive or hotness > 10:
            row['_matched_keyword'] = matched_keyword
            kept_rows.append(row)
    
    # 按热度排序
    kept_rows.sort(key=lambda x: int(x.get('热度', 0)), reverse=True)
    
    # 输出筛选后的数据
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['热度', '作者', '用户名', '内容', '链接', '发布时间']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in kept_rows:
            writer.writerow({k: row.get(k, '') for k in fieldnames})
    
    print(f"\n筛选后: {len(kept_rows)} 条")
    print(f"输出文件: {OUTPUT_FILE}")
    
    # 显示排除的信息
    print(f"\n排除的噪音: {len(excluded_info)} 条")
    print("\n前10条排除记录:")
    for username, hotness, reason in excluded_info[:10]:
        print(f"  [{hotness}] @{username} - {reason}")
    
    # 显示保留的内容
    print("\n" + "=" * 50)
    print("保留的项目/工具类内容:")
    print("=" * 50)
    for i, row in enumerate(kept_rows[:15], 1):
        keyword = row.get('_matched_keyword', '')
        print(f"{i}. [{row['热度']}❤️] @{row['用户名']}: {row['内容'][:60]}...")
        print(f"   匹配关键词: {keyword}")
        print(f"   🔗 {row['链接']}")
        print()

if __name__ == "__main__":
    main()
