#!/usr/bin/env python3
"""
NFT Mint Monitor - NFT铸造监控
每次调用收费 0.001 USDT
"""

import sys
from datetime import datetime, timedelta, timezone,UTC
import random

def get_upcoming_mints() -> list:
    """获取即将铸造的NFT（模拟数据）"""
    now = datetime.utcnow()
    
    mints = [
        {
            "name": "Azuki Spirit",
            "time": now + timedelta(hours=2),
            "price": "0.08 ETH",
            "supply": 10000,
            "hotness": 5,
            "wl_open": True
        },
        {
            "name": "DeGods Genesis",
            "time": now + timedelta(hours=16),
            "price": "5 SOL",
            "supply": 5000,
            "hotness": 4,
            "wl_open": False
        },
        {
            "name": "Pudgy Penguins",
            "time": now + timedelta(hours=22),
            "price": "0.05 ETH",
            "supply": 8000,
            "hotness": 4,
            "wl_open": True
        },
    ]
    return mints


def format_time(dt: datetime) -> str:
    """格式化时间"""
    now = datetime.utcnow()
    diff = dt - now
    
    if diff.total_seconds() < 3600:
        return f"今天 {dt.strftime('%H:%M')} UTC"
    elif diff.total_seconds() < 86400:
        return f"明天 {dt.strftime('%H:%M')} UTC"
    else:
        return dt.strftime("%m/%d %H:%M UTC")


def get_hotness_stars(count: int) -> str:
    """热度星级"""
    return "⭐" * count


def format_result(mints: list) -> str:
    lines = [
        "🎨 NFT铸造监控",
        "━━━━━━━━━━━━━━━━",
        "⏰ 即将铸造 (24h内):"
    ]
    
    for i, m in enumerate(mints, 1):
        wl_status = "🎫 WL: 已开放" if m["wl_open"] else "🎫 WL: 已满"
        stars = get_hotness_stars(m["hotness"])
        
        lines.append(f"""
{i}. {m['name']} 📅 {format_time(m['time'])}
   💰 价格: {m['price']}
   📦 总量: {m['supply']:,}
   🔥 热度: {stars}
   {wl_status}""")
    
    # 添加建议
    hottest = max(mints, key=lambda x: x["hotness"])
    lines.append(f"\n💡 建议: {hottest['name']}热度高，建议参与")
    lines.append("")
    lines.append("✅ 已扣费 0.001 USDT")
    
    return "\n".join(lines)


if __name__ == "__main__":
    mints = get_upcoming_mints()
    print(format_result(mints))
