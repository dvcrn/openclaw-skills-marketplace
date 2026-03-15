#!/usr/bin/env python3
"""
NFT Valuator - NFT估值分析
每次调用收费 0.001 USDT
"""

import sys
import requests

def get_nft_value(collection: str, token_id: int = None) -> dict:
    """获取NFT估值（使用OpenSea API）"""
    try:
        # 使用OpenSea免费API
        url = f"https://api.opensea.io/api/v2/collection/{collection}/stats"
        headers = {"Accept": "application/json"}
        
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        
        stats = data.get("total", {})
        return {
            "collection": collection,
            "floor_price": stats.get("floor_price", 0),
            "avg_price": stats.get("average_price", 0),
            "volume_24h": stats.get("one_day_volume", 0),
            "owners": stats.get("num_owners", 0),
            "supply": stats.get("total_supply", 0)
        }
    except Exception as e:
        return {"error": str(e)}


def format_result(data: dict) -> str:
    if "error" in data:
        return f"❌ 查询失败: {data['error']}"
    
    return f"""
🎨 NFT估值: {data['collection'].upper()}
━━━━━━━━━━━━━━━━
💰 地板价: {data['floor_price']} ETH
📊 平均价: {data['avg_price']:.4f} ETH
📈 24h成交量: {data['volume_24h']:.1f} ETH
👥 持有人: {data['owners']:,}
🖼️ 总量: {data['supply']:,}

✅ 已扣费 0.001 USDT
"""


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python nft_valuator.py <COLLECTION_SLUG>")
        print("示例: python nft_valuator.py boredapeyachtclub")
        sys.exit(1)
    
    collection = sys.argv[1]
    result = get_nft_value(collection)
    print(format_result(result))
