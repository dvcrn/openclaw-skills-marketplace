#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
币安撸毛助手 - 参赛版
核心功能：展示所有可参与的币安赚钱活动 + 详细解读
特点：
1. 每次显示全部活动（不依赖历史）
2. 每条活动详细解读
3. 支持导出 Markdown
"""

import json
import os
import requests
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# ==================== 配置区域 ====================

# 数据存储路径
DATA_DIR = Path.home() / ".openclaw" / "workspace" / ".binance_earning"
DATA_DIR.mkdir(parents=True, exist_ok=True)
CACHE_FILE = DATA_DIR / "cache.json"
EXPORT_DIR = DATA_DIR / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# 筛选配置
EXCLUDE_KEYWORDS = ["已结束", "ended", "closed", "下架", "维护", "已发放"]

# 币安公告 API
BINANCE_API = "https://www.binance.com/bapi/composite/v1/public/cms/article/list/query"

# 活动数据
BINANCE_ANNOUNCEMENTS = [
    # 理财产品
    {"title": "Enjoy Up to 8% APR with RLUSD Flexible Products", "code": "65317d61d1c445f99f73a04c05233dd2", "endDate": "2026-03-31"},
    {"title": "Binance Earn Yield Arena: Earn Up to 11.5% APR", "code": "7e9dbced380241c7a3fd8b927659ae2a", "endDate": "2026-03-18"},
    {"title": "Binance Will Add Midnight (NIGHT) on Earn", "code": "d99bba308e50404b889f677101ed5112", "endDate": "2026-03-20"},
    {"title": "Share 10 Million SHELL Rewards", "code": "611bfd0165cc46cb89e06a6549ce2ccf", "endDate": "2026-03-25"},
    {"title": "Subscribe to Binance Earn Products & Share 2,000 USDC", "code": "f6106586265d496faf88b135635d9203", "endDate": "2026-03-30"},
    {"title": "Join the Angels Square AMA & Win Rewards", "code": "5e315527b4574393bf02f6bd6bc5ae9f", "endDate": "2026-03-16"},
    {"title": "Binance Will Add Opinion (OPN) on Earn", "code": "b3ef81d0193c42e791d517481867b558", "endDate": "2026-03-15"},
    {"title": "Enjoy Up to 10.5% APR with U Flexible Products", "code": "4bbd4a6c37ef40f2b29189e72cbb0bbe", "endDate": "2026-03-20"},
    # 活动奖励
    {"title": "Tria Trading Competition", "code": "17fc30341dc0422488f62b94dc21ad96", "endDate": "2026-03-20"},
    {"title": "KITE Trading Tournament", "code": "c5b35c7e635e42ea96e290274e54fb15", "endDate": "2026-03-25"},
    {"title": "Grab a Share of 2,000,000 NIGHT Rewards", "code": "d6fd86054b00445a97897606033970d8", "endDate": "2026-03-22"},
    {"title": "Join the Binance Wallet On-Chain Perpetuals Milestone Challenge", "code": "4ad6e3210efc472d9836e172e930aa23", "endDate": "2026-03-26"},
    {"title": "Trade Tokenized Securities on Binance Alpha", "code": "748940924c614022af048669e2b087d9", "endDate": "2026-03-31"},
    {"title": "ETHGas Trading Competition", "code": "4a659cc17d464adb8ccc2890d202e39a", "endDate": "2026-03-19"},
    {"title": "Introducing Fabric Protocol (ROBO)", "code": "6512b63e046c4cad904aed12a9efbf9c", "endDate": "2026-03-20"},
    {"title": "Humanity Protocol Trading Competition", "code": "0d53b443694c475f9ef0b86370617985", "endDate": "2026-03-17"},
    {"title": "Introducing Opinion (OPN)", "code": "7588c8608e6f42cbb53e8d4d0f200d09", "endDate": "2026-03-18"},
    # 其他活动
    {"title": "Word of the Day: Test Your Knowledge on AI Agents", "code": "0638bbd50c2949d582bf4248f410a7c0", "endDate": "2026-03-15"},
]

# 空投预告
ALPHA_AIRDROPS = [
    {"project": "KAT (Katana)", "token": "KAT", "type": "即将开始", "end_date": "3 月 16 日 20:00", "url": "https://alpha123.uk/zh/"},
]


def get_binance_activities():
    """从币安 API 获取活动"""
    try:
        params = {"catalogId": "48", "page": 1, "pageSize": 50}
        resp = requests.get(BINANCE_API, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("code") == "000000":
                articles = data.get("data", {}).get("articles", [])
                return articles
    except:
        pass
    return BINANCE_ANNOUNCEMENTS


def categorize(title):
    """活动分类"""
    title_lower = title.lower()
    if "理财" in title or "Earn" in title or "APR" in title:
        return "💰 理财产品"
    elif "竞赛" in title or "Competition" in title or "Tournament" in title or "Trading" in title:
        return "🎁 活动奖励"
    elif "Reward" in title or "奖励" in title:
        return "🎁 活动奖励"
    elif "Alpha" in title:
        return "🎁 活动奖励"
    else:
        return "📢 其他活动"


def get_reward_text(title):
    """获取奖池文本"""
    if "8%" in title:
        return "8%"
    elif "11.5%" in title:
        return "11.5%"
    elif "1.5%" in title:
        return "1.5%"
    elif "10.5%" in title:
        return "10.5%"
    elif "200K" in title or "200,000" in title:
        return "200K"
    elif "SHELL" in title:
        return "1000 万 SHELL"
    elif "NIGHT" in title and "2,000,000" in title:
        return "200 万 NIGHT"
    elif "OPN" in title and "2,500,000" in title:
        return "250 万 OPN"
    elif "USDC" in title:
        return "2000 USDC"
    else:
        return "详见页面"


def get_participation_method(title):
    """获取参与方式"""
    if "理财" in title or "Earn" in title:
        return "1.打开理财 2.选择产品 3.申购确认"
    elif "竞赛" in title or "Competition" in title:
        return "1.报名 2.规定时间交易 3.按排名领奖"
    elif "Alpha" in title:
        return "1.打开 Web3 钱包 2.进入 Alpha 3.完成任务"
    else:
        return "详见活动页面"


def display_activities():
    """显示活动列表"""
    activities = get_binance_activities()
    
    # 分类
    by_type = defaultdict(list)
    for article in activities:
        title = article.get("title", "")
        end_date = article.get("endDate", "")
        code = article.get("code", "")
        
        # 检查是否已过期
        if end_date and "2026-03-14" > end_date:
            continue
        
        act_type = categorize(title)
        by_type[act_type].append({
            "title": title,
            "end_date": end_date,
            "code": code,
            "reward": get_reward_text(title),
            "method": get_participation_method(title)
        })
    
    # 显示
    print("\n" + "═" * 60)
    print("🚀 币安撸毛助手 - 当前可参与活动")
    print("═" * 60)
    print(f"更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()
    
    total = sum(len(acts) for acts in by_type.values())
    print(f"活动总数：{total} 个")
    print()
    
    # 显示每个分类
    type_order = ["💰 理财产品", "🎁 活动奖励", "📢 其他活动", "🚀 ALPHA 空投预告"]
    
    for act_type in type_order:
        if act_type == "🚀 ALPHA 空投预告":
            print("\n" + "═" * 60)
            print(f"{act_type}（{len(ALPHA_AIRDROPS)} 个）")
            print("═" * 60)
            for i, airdrop in enumerate(ALPHA_AIRDROPS, 1):
                print(f"\n【{i}】{airdrop['project']}")
                print(f" 🔗 链接：{airdrop['url']}")
                print(f" 💰 奖池：{airdrop['type']}")
                print(f" 📅 截止时间：{airdrop['end_date']}")
                print(f" 🎯 门槛：完成 Alpha 任务")
                print(f" 📝 参与方式：详见活动页面")
                print(f" ⚠️ 风险：空投有风险，参与需谨慎")
            continue
        
        if act_type not in by_type:
            continue
        
        acts = by_type[act_type]
        print("\n" + "═" * 60)
        print(f"{act_type}（{len(acts)} 个）")
        print("═" * 60)
        
        for i, act in enumerate(acts, 1):
            print(f"\n【{i}】{act['title']}")
            print(f" 🔗 链接：https://www.binance.com/zh-CN/support/announcement/{act['code']}")
            print(f" 💰 奖池：{act['reward']}")
            print(f" 📅 截止时间：{act['end_date']}")
            print(f" 🎯 门槛：无特殊要求")
            print(f" 📝 参与方式：{act['method']}")
            print(f" ⚠️ 风险：详见活动规则")
    
    print("\n" + "═" * 60)
    print("✅ 全部活动展示完毕")
    print("═" * 60)
    print()


if __name__ == "__main__":
    display_activities()
