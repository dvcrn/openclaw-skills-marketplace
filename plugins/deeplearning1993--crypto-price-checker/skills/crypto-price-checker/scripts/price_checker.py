#!/usr/bin/env python3
"""
Crypto Price Checker - 使用CoinGecko API
每次调用收费 0.001 USDT
"""

import os
import sys
import requests
import asyncio

# 尝试导入shared模块
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))
    from skillpay import SkillPay, format_charge_result
except ImportError:
    # 如果无法导入，使用简化版
    class SkillPay:
        def __init__(self):
            self.test_mode = True
        def charge(self, *args, **kwargs):
            return {"success": True, "test_mode": True}
    def format_charge_result(r):
        return "⚠️ 测试模式"

SKILLPAY_WALLET = "0x64f15739932c144b54ad12eb05a02ea64f755a53"

# CoinGecko API (免费，无需API Key)
COINGECKO_API = "https://api.coingecko.com/api/v3"

# 币种ID映射
COIN_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum", 
    "SOL": "solana",
    "BNB": "binancecoin",
    "XRP": "ripple",
    "DOGE": "dogecoin",
    "ADA": "cardano",
    "AVAX": "avalanche-2",
    "MATIC": "matic-network",
    "DOT": "polkadot",
    "LINK": "chainlink",
    "UNI": "uniswap",
    "ATOM": "cosmos",
    "LTC": "litecoin",
}


def get_price_coingecko(symbol: str) -> dict:
    """从CoinGecko获取价格"""
    symbol = symbol.upper().replace("-", "").replace("USDT", "")
    
    coin_id = COIN_IDS.get(symbol)
    if not coin_id:
        # 尝试搜索
        try:
            search_resp = requests.get(
                f"{COINGECKO_API}/search",
                params={"query": symbol},
                timeout=10
            )
            coins = search_resp.json().get("coins", [])
            if coins:
                coin_id = coins[0]["id"]
            else:
                return {"error": f"未找到币种: {symbol}"}
        except Exception as e:
            return {"error": f"搜索失败: {e}"}
    
    try:
        resp = requests.get(
            f"{COINGECKO_API}/simple/price",
            params={
                "ids": coin_id,
                "vs_currencies": "usd",
                "include_24hr_change": "true",
                "include_24hr_vol": "true"
            },
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
        
        if coin_id not in data:
            return {"error": f"无法获取价格: {symbol}"}
        
        return {
            "symbol": symbol,
            "price": data[coin_id].get("usd", 0),
            "change_24h": data[coin_id].get("usd_24h_change", 0),
            "volume_24h": data[coin_id].get("usd_24h_vol", 0)
        }
    except Exception as e:
        return {"error": str(e)}


def format_result(data: dict, charged: bool) -> str:
    """格式化输出"""
    if "error" in data:
        return f"❌ 查询失败: {data['error']}"
    
    symbol = data.get("symbol", "?")
    price = data.get("price", 0)
    change = data.get("change_24h", 0)
    volume = data.get("volume_24h", 0)
    
    change_emoji = "📈" if change >= 0 else "📉"
    charge_status = "✅ 已扣费 0.001 USDT" if charged else "⚠️ 未扣费（测试模式）"
    
    return f"""
💰 {symbol}/USDT
━━━━━━━━━━━━━━━━
📊 价格: ${price:,.2f}
{change_emoji} 24h: {change:+.2f}%
📦 成交量: ${volume:,.0f}

{charge_status}
💳 收款钱包: {SKILLPAY_WALLET[:10]}...{SKILLPAY_WALLET[-6:]}
"""


async def main():
    if len(sys.argv) < 2:
        print("用法: python price_checker.py <SYMBOL> [USER_ID]")
        print("示例: python price_checker.py BTC user123")
        print("\n支持的币种:", ", ".join(COIN_IDS.keys()))
        sys.exit(1)
    
    symbol = sys.argv[1]
    user_id = sys.argv[2] if len(sys.argv) > 2 else "anonymous"
    
    # 收费
    client = SkillPay()
    charge_result = client.charge(user_id, "0.001", skill_name="crypto-price-checker")
    charged = charge_result.get("success") and not charge_result.get("test_mode")
    
    if not charge_result.get("success"):
        print("💳 需要付费:")
        print(charge_result.get("payment_url", "无法获取支付链接"))
        sys.exit(1)
    
    # 获取价格
    data = get_price_coingecko(symbol)
    print(format_result(data, charged))


if __name__ == "__main__":
    asyncio.run(main())
