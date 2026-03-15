"""
Smart Money Tracker - Main Application
聪明钱追踪系统
"""

import os
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum

from fastapi import FastAPI, HTTPException, Request, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx

# ==================== 配置 ====================

class Config:
    """应用配置"""
    # SkillPay 配置
    SKILLPAY_API_KEY = os.getenv("SKILLPAY_API_KEY", "sk_4fcce5e213933a634f32a6d43ace17df562ff60c3cb114c122d46d1376fbec4b")
    SKILL_ID = os.getenv("SKILL_ID", "a163d326-f0dc-4e67-b4e0-0273cc1bc0c8")
    PRICE_PER_CALL = 0.001  # USDT

    # API 配置
    API_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# ==================== 枚举类型 ====================

class Chain(str, Enum):
    """支持的链"""
    ETH = "eth"
    BSC = "bsc"
    SOL = "sol"
    ARBITRUM = "arbitrum"
    POLYGON = "polygon"

class TransactionType(str, Enum):
    """交易类型"""
    TRANSFER = "transfer"
    SWAP = "swap"
    STAKE = "stake"
    UNSTAKE = "unstake"
    MINT = "mint"
    BURN = "burn"

# ==================== Pydantic 模型 ====================

class LargeTransactionRequest(BaseModel):
    """大额交易请求"""
    chain: Optional[Chain] = Chain.ETH
    min_value: float = Field(default=10000, description="最小金额(USD)")
    limit: int = Field(default=50, ge=1, le=200)

class WhaleRequest(BaseModel):
    """巨鲸地址请求"""
    address: str
    chain: Optional[Chain] = Chain.ETH

class PortfolioRequest(BaseModel):
    """持仓分析请求"""
    address: str
    chain: Optional[Chain] = Chain.ETH

class HistoryRequest(BaseModel):
    """历史交易请求"""
    address: str
    chain: Optional[Chain] = Chain.ETH
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    tx_type: Optional[TransactionType] = None
    limit: int = Field(default=50, ge=1, le=200)

class TrendRequest(BaseModel):
    """趋势分析请求"""
    token: str
    chain: Optional[Chain] = Chain.ETH
    period: str = Field(default="24h", description="时间周期: 24h, 7d, 30d")

class AddWatchlistRequest(BaseModel):
    """添加监控请求"""
    address: str
    chain: Chain = Chain.ETH
    label: Optional[str] = None
    alert_threshold: float = Field(default=10000)

# ==================== Mock 数据 ====================

def generate_mock_whale_addresses() -> List[Dict[str, Any]]:
    """生成模拟巨鲸地址数据"""
    return [
        {"address": "0x8ba1f109551bD432803012645Hac136E7651236", "label": "Wintermute Trading", "type": "institution", "chain": "eth"},
        {"address": "0x2F2a2543B76A4166549F7aaB2e75Bfe0f5fA19e1", "label": "Jump Crypto", "type": "institution", "chain": "eth"},
        {"address": "0xF977814e90dA44bFA03b6295A0616a0971A2cd55", "label": "Binance Hot Wallet", "type": "exchange", "chain": "eth"},
        {"address": "0x28C6c06298d514Db08993407135593850c0a405", "label": "Coinbase Cold", "type": "exchange", "chain": "eth"},
        {"address": "0x21a31EeB6d7B5b0b1d42E84c49e8C23b6f15F8A5", "label": "Binance Cold 1", "type": "exchange", "chain": "eth"},
        {"address": "0xDFd5293D8e747d10cc5F8056F7bF47D1C41f3c4E", "label": "Bitwise ETF", "type": "institution", "chain": "eth"},
    ]

def generate_mock_transactions() -> List[Dict[str, Any]]:
    """生成模拟大额交易"""
    base_time = datetime.utcnow()

    return [
        # 大额转账
        {"hash": "0x1234...abcd1", "from": "0x8ba1f109551bD432803012645Hac136E7651236", "to": "0x742d35Cc6634C0532925a3b844Bc9e7595f8fE72", "token": "ETH", "amount": 1250, "value_usd": 3125000, "timestamp": base_time - timedelta(minutes=15), "type": "transfer", "chain": "eth"},
        {"hash": "0x1234...abcd2", "from": "0xF977814e90dA44bFA03b6295A0616a0971A2cd55", "to": "0x8ba1f109551bD432803012645Hac136E7651236", "token": "USDT", "amount": 5000000, "value_usd": 5000000, "timestamp": base_time - timedelta(minutes=32), "type": "transfer", "chain": "eth"},
        {"hash": "0x1234...abcd3", "from": "0x28C6c06298d514Db08993407135593850c0a405", "to": "0x21a31EeB6d7B5b0b1d42E84c49e8C23b6f15F8A5", "token": "BTC", "amount": 485, "value_usd": 19400000, "timestamp": base_time - timedelta(hours=1), "type": "transfer", "chain": "eth"},
        {"hash": "0x1234...abcd4", "from": "0x2F2a2543B76A4166549F7aaB2e75Bfe0f5fA19e1", "to": "0x742d35Cc6634C0532925a3b844Bc9e7595f8fE72", "token": "SOL", "amount": 150000, "value_usd": 18000000, "timestamp": base_time - timedelta(hours=2), "type": "transfer", "chain": "eth"},
        {"hash": "0x1234...abcd5", "from": "0x742d35Cc6634C0532925a3b844Bc9e7595f8fE72", "to": "0xDFd5293D8e747d10cc5F8056F7bF47D1C41f3c4E", "token": "ETH", "amount": 8500, "value_usd": 21250000, "timestamp": base_time - timedelta(hours=3), "type": "transfer", "chain": "eth"},
        # 更多交易
        {"hash": "0x1234...abcd6", "from": "0x8ba1f109551bD432803012645Hac136E7651236", "to": "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B", "token": "USDC", "amount": 3500000, "value_usd": 3500000, "timestamp": base_time - timedelta(hours=4), "type": "transfer", "chain": "eth"},
        {"hash": "0x1234...abcd7", "from": "0xF977814e90dA44bFA03b6295A0616a0971A2cd55", "to": "0xE37e2A9cA5d7f0C68e80dC2B0D5eD4f8b3f9C5A", "token": "BNB", "amount": 15000, "value_usd": 4500000, "timestamp": base_time - timedelta(hours=5), "type": "transfer", "chain": "bsc"},
        {"hash": "0x1234...abcd8", "from": "0x2F2a2543B76A4166549F7aaB2e75Bfe0f5fA19e1", "to": "0x742d35Cc6634C0532925a3b844Bc9e7595f8fE72", "token": "ARB", "amount": 2500000, "value_usd": 2750000, "timestamp": base_time - timedelta(hours=6), "type": "transfer", "chain": "arbitrum"},
    ]

def generate_mock_portfolio() -> Dict[str, Any]:
    """生成模拟持仓数据"""
    return {
        "total_value_usd": 45678900,
        "tokens": [
            {"symbol": "ETH", "name": "Ethereum", "amount": 8500, "value_usd": 21250000, "percentage": 46.5},
            {"symbol": "BTC", "name": "Bitcoin", "amount": 285, "value_usd": 11400000, "percentage": 24.9},
            {"symbol": "USDT", "name": "Tether", "amount": 5000000, "value_usd": 5000000, "percentage": 10.9},
            {"symbol": "USDC", "name": "USD Coin", "amount": 3500000, "value_usd": 3500000, "percentage": 7.7},
            {"symbol": "SOL", "name": "Solana", "amount": 85000, "value_usd": 10200000, "percentage": 22.3},
            {"symbol": "ARB", "name": "Arbitrum", "amount": 2500000, "value_usd": 2750000, "percentage": 6.0},
        ]
    }

def generate_mock_flow_data(period: str = "24h") -> Dict[str, Any]:
    """生成模拟资金流向数据"""
    return {
        "period": period,
        "total_inflow_usd": 125678900,
        "total_outflow_usd": 98234500,
        "net_flow_usd": 27444400,
        "by_token": [
            {"token": "ETH", "inflow": 45000000, "outflow": 32000000, "net": 13000000},
            {"token": "BTC", "inflow": 35000000, "outflow": 28000000, "net": 7000000},
            {"token": "USDT", "inflow": 22000000, "outflow": 18000000, "net": 4000000},
            {"token": "SOL", "inflow": 15000000, "outflow": 12300000, "net": 2700000},
            {"token": "ARB", "inflow": 8678900, "outflow": 7934500, "net": 744400},
        ],
        "by_type": [
            {"type": "exchange_inflow", "value": 55000000, "percentage": 43.8},
            {"type": "institution_inflow", "value": 42000000, "percentage": 33.4},
            {"type": "defi_inflow", "value": 28678900, "percentage": 22.8},
        ]
    }

def generate_mock_trend_data(token: str, period: str) -> Dict[str, Any]:
    """生成模拟趋势数据"""
    hours = {"24h": 24, "7d": 168, "30d": 720}.get(period, 24)

    # 生成时间序列数据
    data_points = []
    base_time = datetime.utcnow()
    for i in range(min(hours, 24)):  # 简化展示
        timestamp = base_time - timedelta(hours=hours-i)
        # 生成随机数据
        md5_hash = int(hashlib.md5(f"{token}{i}".encode()).hexdigest()[0:6], 16)
        data_points.append({
            "timestamp": timestamp.isoformat(),
            "smart_money_inflow": 1500000 + (i * 50000) + (md5_hash % 1000000),
            "smart_money_outflow": 1200000 + (i * 45000) + (md5_hash % 800000),
            "retail_inflow": 800000 + (i * 30000),
            "retail_outflow": 900000 + (i * 35000),
        })

    return {
        "token": token.upper(),
        "period": period,
        "summary": {
            "smart_money_total_inflow": 45678900,
            "smart_money_total_outflow": 32456700,
            "smart_money_net_flow": 13222200,
            "smart_money_win_rate": 68.5,
            "avg_hold_time_days": 45,
        },
        "data_points": data_points,
    }

# ==================== API 应用 ====================

app = FastAPI(
    title="Smart Money Tracker API",
    description="聪明钱追踪系统 - 每次调用需支付 0.001 USDT",
    version=Config.API_VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== SkillPay 支付 SDK ====================

BILLING_URL = "https://skillpay.me/api/v1/billing"

async def charge_user(user_id: str) -> dict:
    """扣费函数"""
    headers = {
        "X-API-Key": Config.SKILLPAY_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "user_id": user_id,
        "skill_id": Config.SKILL_ID,
        "amount": Config.PRICE_PER_CALL
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                BILLING_URL + "/charge",
                json=payload,
                headers=headers
            )
            data = response.json()
            if data.get("success"):
                return {"ok": True, "balance": data.get("balance")}
            return {
                "ok": False,
                "balance": data.get("balance"),
                "payment_url": data.get("payment_url")
            }
    except Exception as e:
        if Config.DEBUG:
            return {"ok": True, "balance": 999, "debug": True}
        return {"ok": False, "error": str(e)}

# ==================== 支付中间件 ====================

async def verify_payment(
    request: Request,
    x_user_id: Optional[str] = Header(None)
) -> str:
    """验证支付"""
    user_id = x_user_id or "anonymous"

    if request.url.path.startswith("/api/billing"):
        return user_id
    if request.url.path == "/" or request.url.path == "/api/health":
        return user_id

    try:
        charge_result = await charge_user(user_id)
        if not charge_result.get("ok"):
            if Config.DEBUG:
                return user_id
            raise HTTPException(
                status_code=402,
                detail={
                    "message": "余额不足，请充值",
                    "payment_url": charge_result.get("payment_url", "")
                }
            )
    except HTTPException:
        raise
    except Exception:
        if Config.DEBUG:
            return user_id
        raise HTTPException(status_code=402, detail="Payment verification failed")

    return user_id

# ==================== API 端点 ====================

@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "Smart Money Tracker API",
        "version": Config.API_VERSION,
        "description": "聪明钱追踪系统",
        "price_per_call": f"{Config.PRICE_PER_CALL} USDT",
        "endpoints": {
            "transactions": "/api/transactions/large - 大额交易",
            "whale": "/api/whale/{address} - 巨鲸追踪",
            "flow": "/api/flow/{chain} - 资金流向",
            "portfolio": "/api/portfolio/{address} - 持仓分析",
            "history": "/api/history/{address} - 历史记录",
            "trend": "/api/trend/{token} - 趋势分析",
            "watchlist": "/api/watchlist - 监控列表",
        }
    }

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": Config.API_VERSION
    }

# ---- 大额交易 ----

@app.get("/api/transactions/large")
async def get_large_transactions(
    chain: Optional[Chain] = Chain.ETH,
    min_value: float = 10000,
    limit: int = 50,
    user_id: str = Depends(verify_payment)
):
    """获取大额交易"""
    transactions = generate_mock_transactions()

    # 筛选
    filtered = [
        tx for tx in transactions
        if tx["value_usd"] >= min_value and tx["chain"] == chain.value
    ][:limit]

    return {
        "success": True,
        "count": len(filtered),
        "chain": chain.value,
        "min_value_usd": min_value,
        "data": filtered
    }

# ---- 巨鲸地址 ----

@app.get("/api/whale/{address}")
async def get_whale_info(
    address: str,
    chain: Optional[Chain] = Chain.ETH,
    user_id: str = Depends(verify_payment)
):
    """获取巨鲸地址信息"""
    whales = generate_mock_whale_addresses()

    # 查找地址
    whale = next((w for w in whales if w["address"].lower() == address.lower()), None)

    if not whale:
        # 假设是未知地址
        whale = {
            "address": address,
            "label": "Unknown",
            "type": "unknown",
            "chain": chain.value,
            "is_known_whale": False
        }
    else:
        whale["is_known_whale"] = True

    # 添加模拟交易数据
    whale["recent_transactions"] = generate_mock_transactions()[:5]

    return {
        "success": True,
        "data": whale
    }

@app.get("/api/whales/list")
async def get_whale_list(
    chain: Optional[Chain] = None,
    user_id: str = Depends(verify_payment)
):
    """获取已知巨鲸列表"""
    whales = generate_mock_whale_addresses()

    if chain:
        whales = [w for w in whales if w["chain"] == chain.value]

    return {
        "success": True,
        "count": len(whales),
        "data": whales
    }

# ---- 资金流向 ----

@app.get("/api/flow/{chain}")
async def get_fund_flow(
    chain: Chain,
    period: str = "24h",
    user_id: str = Depends(verify_payment)
):
    """获取资金流向"""
    flow_data = generate_mock_flow_data(period)

    return {
        "success": True,
        "chain": chain.value,
        "period": period,
        "data": flow_data
    }

# ---- 持仓分析 ----

@app.get("/api/portfolio/{address}")
async def get_portfolio(
    address: str,
    chain: Optional[Chain] = Chain.ETH,
    user_id: str = Depends(verify_payment)
):
    """获取地址持仓"""
    portfolio = generate_mock_portfolio()

    # 添加地址信息
    portfolio["address"] = address
    portfolio["chain"] = chain.value

    return {
        "success": True,
        "data": portfolio
    }

# ---- 历史交易 ----

@app.get("/api/history/{address}")
async def get_history(
    address: str,
    chain: Optional[Chain] = Chain.ETH,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 50,
    user_id: str = Depends(verify_payment)
):
    """获取历史交易"""
    transactions = generate_mock_transactions()

    # 筛选
    filtered = [tx for tx in transactions if tx["chain"] == chain.value][:limit]

    return {
        "success": True,
        "address": address,
        "chain": chain.value,
        "count": len(filtered),
        "data": filtered
    }

# ---- 趋势分析 ----

@app.get("/api/trend/{token}")
async def get_trend(
    token: str,
    chain: Optional[Chain] = Chain.ETH,
    period: str = "24h",
    user_id: str = Depends(verify_payment)
):
    """获取趋势分析"""
    trend_data = generate_mock_trend_data(token, period)

    return {
        "success": True,
        "data": trend_data
    }

# ---- 监控列表 ----

@app.post("/api/watchlist")
async def add_to_watchlist(
    request: AddWatchlistRequest,
    user_id: str = Depends(verify_payment)
):
    """添加地址到监控列表"""
    return {
        "success": True,
        "message": f"已添加 {request.address} 到监控列表",
        "data": {
            "address": request.address,
            "chain": request.chain.value,
            "label": request.label,
            "alert_threshold": request.alert_threshold
        }
    }

@app.get("/api/watchlist")
async def get_watchlist(
    user_id: str = Depends(verify_payment)
):
    """获取监控列表"""
    # 模拟数据
    watchlist = [
        {"address": "0x8ba1f109551bD432803012645Hac136E7651236", "chain": "eth", "label": "Wintermute", "added_at": "2024-01-15T10:00:00"},
        {"address": "0x2F2a2543B76A4166549F7aaB2e75Bfe0f5fA19e1", "chain": "eth", "label": "Jump Crypto", "added_at": "2024-01-16T14:30:00"},
    ]

    return {
        "success": True,
        "count": len(watchlist),
        "data": watchlist
    }

# ---- 计费相关 ----

@app.post("/api/billing/charge")
async def charge_endpoint(
    user_id: str,
    amount: float = 0.001,
    currency: str = "USDT"
):
    """手动扣费"""
    result = await charge_user(user_id)
    return result

@app.get("/api/billing/balance")
async def get_balance(
    user_id: str = Depends(verify_payment)
):
    """获取余额"""
    return {
        "success": True,
        "balance": 0,
        "message": "查看 skillpay.me 了解余额"
    }

# ==================== 启动 ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
