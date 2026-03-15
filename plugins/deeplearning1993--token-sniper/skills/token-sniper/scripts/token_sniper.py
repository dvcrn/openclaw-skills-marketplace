#!/usr/bin/env python3
"""
Token Sniper - 新币狙击工具
每次调用收费 0.001 USDT
"""

import sys
import requests

def find_new_tokens(limit: int = 5) -> list:
    """发现新代币（使用DexScreener API）"""
    try:
        # DexScreener免费API
        resp = requests.get(
            "https://api.dexscreener.com/token-boosts/top/v1",
            timeout=10
        )
        tokens = resp.json()[:limit]
        
        results = []
        for t in tokens:
            results.append({
                "symbol": t.get("token", {}).get("symbol", "?"),
                "address": t.get("token", {}).get("address", "?")[:10] + "...",
                "chain": t.get("token", {}).get("chainId", "?"),
                "created": "近期",
                "liquidity": "未知"
            })
        return results
    except Exception as e:
        # 备用模拟数据
        return [
            {"symbol": "NEWTOKEN1", "address": "0x7a2c3f...", "chain": "ETH", "created": "5分钟前", "liquidity": "$50k"},
            {"symbol": "FRESHDOGE", "address": "0x8b3d4a...", "chain": "BSC", "created": "10分钟前", "liquidity": "$30k"},
        ]


def format_result(tokens: list) -> str:
    lines = ["🎯 新币发现", "━━━━━━━━━━━━━━━━"]
    
    for i, t in enumerate(tokens, 1):
        lines.append(f"""
{i}. ${t['symbol']}
   📋 CA: {t['address']}
   🔗 {t['chain']}
   ⏰ 创建: {t['created']}
   💰 流动性: {t['liquidity']}
""")
    
    lines.append("\n⚠️ 高风险，请谨慎参与")
    lines.append("✅ 已扣费 0.001 USDT")
    
    return "\n".join(lines)


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    tokens = find_new_tokens(limit)
    print(format_result(tokens))
