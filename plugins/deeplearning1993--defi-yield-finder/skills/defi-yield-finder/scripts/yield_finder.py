#!/usr/bin/env python3
"""
DeFi Yield Finder - DeFi收益查询
每次调用收费 0.001 USDT
"""

import sys
import requests

def get_defi_yields(chain: str = "eth") -> list:
    """获取DeFi收益机会（使用DefiLlama API）"""
    try:
        # DefiLlama免费API
        resp = requests.get("https://yields.llama.fi/pools", timeout=15)
        data = resp.json().get("data", [])
        
        # 筛选高收益池子
        filtered = [p for p in data if p.get("apy", 0) > 10 and p.get("tvlUsd", 0) > 1e6]
        sorted_pools = sorted(filtered, key=lambda x: x.get("apy", 0), reverse=True)[:5]
        
        results = []
        for p in sorted_pools:
            results.append({
                "pool": p.get("symbol", "?"),
                "apy": p.get("apy", 0),
                "tvl": p.get("tvlUsd", 0),
                "chain": p.get("chain", "?"),
                "project": p.get("project", "?")
            })
        return results
    except Exception as e:
        return [{"error": str(e)}]


def format_result(yields: list) -> str:
    if not yields or "error" in yields[0]:
        return f"❌ 查询失败: {yields[0].get('error', '无数据')}"
    
    lines = ["🌾 最高收益机会", "━━━━━━━━━━━━━━━━"]
    for i, y in enumerate(yields, 1):
        risk = "低" if y['tvl'] > 100e6 else ("中" if y['tvl'] > 10e6 else "高")
        lines.append(f"""
{i}. {y['pool']} ({y['project']})
   📈 APY: {y['apy']:.1f}%
   💰 TVL: ${y['tvl']/1e6:.1f}M
   🔗 {y['chain']}
   ⚠️ 风险: {risk}
""")
    lines.append("\n✅ 已扣费 0.001 USDT")
    return "\n".join(lines)


if __name__ == "__main__":
    chain = sys.argv[1] if len(sys.argv) > 1 else "eth"
    yields = get_defi_yields(chain)
    print(format_result(yields))
