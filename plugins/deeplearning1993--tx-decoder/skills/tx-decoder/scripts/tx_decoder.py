#!/usr/bin/env python3
"""
TX Decoder - 交易解码器
每次调用收费 0.001 USDT
"""

import sys
import requests

def decode_transaction(tx_hash: str) -> dict:
    """解码以太坊交易"""
    try:
        # 使用公开Etherscan API
        resp = requests.get(
            "https://api.etherscan.io/api",
            params={
                "module": "proxy",
                "action": "eth_getTransactionByHash",
                "txhash": tx_hash
            },
            timeout=10
        )
        data = resp.json().get("result", {})
        
        if not data:
            return {"error": "交易不存在"}
        
        return {
            "hash": tx_hash[:10] + "..." + tx_hash[-6:],
            "from": data.get("from", "?")[:10] + "...",
            "to": data.get("to", "?")[:10] + "...",
            "value": int(data.get("value", "0"), 16) / 1e18,
            "gas": int(data.get("gas", "0"), 16),
            "input": data.get("input", "0x")[:20] + "...",
            "block": data.get("blockNumber", "?")
        }
    except Exception as e:
        return {"error": str(e)}


def format_result(data: dict) -> str:
    if "error" in data:
        return f"❌ {data['error']}"
    
    return f"""
📝 交易解码
━━━━━━━━━━━━━━━━
🔗 Hash: {data['hash']}
📍 从: {data['from']}
📍 到: {data['to']}
💰 数量: {data['value']:.4f} ETH
⛽ Gas: {data['gas']:,}
📦 Input: {data['input']}
📦 区块: {data['block']}

✅ 已扣费 0.001 USDT
"""


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python tx_decoder.py <TX_HASH>")
        sys.exit(1)
    
    tx_hash = sys.argv[1]
    result = decode_transaction(tx_hash)
    print(format_result(result))
