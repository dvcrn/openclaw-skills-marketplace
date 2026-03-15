"""
Token Unlock Pro - Main Application
专业的代币解锁预警系统
"""

import os
import asyncio
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum

from fastapi import FastAPI, HTTPException, Request, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import httpx

# ==================== 配置 ====================

class Config:
    """应用配置"""
    # SkillPay 配置
    SKILLPAY_API_KEY = os.getenv("SKILLPAY_API_KEY", "sk_4fcce5e213933a634f32a6d43ace17df562ff60c3cb114c122d46d1376fbec4b")
    SKILL_ID = os.getenv("SKILL_ID", "9eb32e1d-0bd4-4f1b-abaf-7398fe19e9aa")
    PRICE_PER_CALL = 0.001  # USDT

    # API 配置
    API_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"

    # 数据库配置
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./token_unlock.db")

# ==================== 数据模型 ====================

Base = declarative_base()

class UnlockType(str, Enum):
    """解锁类型"""
    SEED = "seed"           # 种子轮
    PUBLIC = "public"        # 公募
    ECOSYSTEM = "ecosystem" # 生态
    STAKING = "staking"     # 质押
    TEAM = "team"           # 团队
    ADVISOR = "advisor"     # 顾问
    COMMUNITY = "community" # 社区

class AlertLevel(str, Enum):
    """预警级别"""
    REALTIME = "realtime"  # 实时
    HOURS_6 = "6h"         # 6小时
    HOURS_24 = "24h"       # 24小时
    HOURS_48 = "48h"       # 48小时
    HOURS_72 = "72h"       # 72小时

class UnlockGrade(str, Enum):
    """解锁额度分级"""
    WHALE = "whale"        # 鲸鱼级 > $10M
    LARGE = "large"        # 大型 $1M-$10M
    MEDIUM = "medium"      # 中型 $100K-$1M
    SMALL = "small"        # 小型 < $100K

class CalendarView(str, Enum):
    """日历视图"""
    DAY = "day"
    WEEK = "week"
    MONTH = "month"

class TokenUnlock(Base):
    """代币解锁记录"""
    __tablename__ = "token_unlocks"

    id = Column(Integer, primary_key=True, index=True)
    token_symbol = Column(String(20), index=True)
    token_name = Column(String(100))
    contract_address = Column(String(100), index=True)
    unlock_type = Column(String(20))  # seed, public, ecosystem, etc.
    unlock_amount = Column(Float)
    unlock_value_usd = Column(Float)
    unlock_percentage = Column(Float)
    unlock_date = Column(DateTime, index=True)
    investors = Column(Text)  # JSON string
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserWatchlist(Base):
    """用户监控列表"""
    __tablename__ = "user_watchlist"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), index=True)
    token_symbol = Column(String(20))
    token_name = Column(String(100))
    contract_address = Column(String(100))
    added_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class UserPortfolio(Base):
    """用户持仓"""
    __tablename__ = "user_portfolio"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), index=True)
    wallet_address = Column(String(100), index=True)
    token_symbol = Column(String(20))
    token_name = Column(String(100))
    token_amount = Column(Float)
    token_value_usd = Column(Float)
    updated_at = Column(DateTime, default=datetime.utcnow)

class PaymentRecord(Base):
    """支付记录"""
    __tablename__ = "payment_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), index=True)
    transaction_id = Column(String(100), unique=True)
    amount = Column(Float)
    currency = Column(String(20))
    status = Column(String(20))
    endpoint = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

# ==================== 数据库 ====================

engine = create_engine(
    Config.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in Config.DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """初始化数据库"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== Pydantic 模型 ====================

class AlertRequest(BaseModel):
    """预警请求"""
    timeframe: Optional[AlertLevel] = None
    unlock_type: Optional[UnlockType] = None
    min_value: Optional[float] = None
    limit: int = Field(default=50, ge=1, le=200)

class CalendarRequest(BaseModel):
    """日历请求"""
    view: CalendarView = CalendarView.WEEK
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    unlock_type: Optional[UnlockType] = None

class AddWatchlistRequest(BaseModel):
    """添加监控请求"""
    token_symbol: str
    token_name: Optional[str] = None
    contract_address: Optional[str] = None

class ImportPortfolioRequest(BaseModel):
    """导入持仓请求"""
    wallet_address: str

class ChargeRequest(BaseModel):
    """支付请求"""
    user_id: str
    amount: float = Field(default=0.001)
    currency: str = Field(default="USDT")
    description: Optional[str] = None

class ChargeResponse(BaseModel):
    """支付响应"""
    success: bool
    transaction_id: Optional[str] = None
    message: str
    balance: Optional[float] = None

# ==================== Mock 数据 ====================

def generate_mock_unlocks() -> List[Dict[str, Any]]:
    """生成模拟解锁数据"""
    base_time = datetime.utcnow()

    mock_data = [
        # 72小时内
        {"token": "ARB", "name": "Arbitrum", "type": "seed", "amount": 456700000, "value": 386000000, "date": base_time + timedelta(hours=48)},
        {"token": "OP", "name": "Optimism", "type": "ecosystem", "amount": 31200000, "value": 78000000, "date": base_time + timedelta(hours=36)},
        {"token": "SAND", "name": "The Sandbox", "type": "team", "amount": 125000000, "value": 68750000, "date": base_time + timedelta(hours=24)},

        # 48-72小时
        {"token": "AXS", "name": "Axie Infinity", "type": "staking", "amount": 8900000, "value": 4450000, "date": base_time + timedelta(hours=60)},
        {"token": "GMT", "name": "GMT", "type": "public", "amount": 150000000, "value": 22500000, "date": base_time + timedelta(hours=70)},

        # 1周内
        {"token": "SOL", "name": "Solana", "type": "team", "amount": 9800000, "value": 117600000, "date": base_time + timedelta(days=3)},
        {"token": "APT", "name": "Aptos", "type": "seed", "amount": 45670000, "value": 82106000, "date": base_time + timedelta(days=4)},
        {"token": "BLUR", "name": "Blur", "type": "community", "amount": 250000000, "value": 18750000, "date": base_time + timedelta(days=5)},

        # 2周内
        {"token": "PEPE", "name": "Pepe", "type": "ecosystem", "amount": 1592000000000, "value": 3184000, "date": base_time + timedelta(days=7)},
        {"token": "IMX", "name": "Immutable", "type": "advisor", "amount": 6700000, "value": 4690000, "date": base_time + timedelta(days=8)},
        {"token": "DYDX", "name": "dYdX", "type": "public", "amount": 15000000, "value": 30000000, "date": base_time + timedelta(days=9)},
        {"token": "RNDR", "name": "Render", "type": "ecosystem", "amount": 1240000, "value": 14880000, "date": base_time + timedelta(days=10)},

        # 其他热门代币
        {"token": "ETH", "name": "Ethereum", "type": "ecosystem", "amount": 45000, "value": 112500000, "date": base_time + timedelta(days=12)},
        {"token": "MATIC", "name": "Polygon", "type": "team", "amount": 190000000, "value": 152000000, "date": base_time + timedelta(days=15)},
        {"token": "LINK", "name": "Chainlink", "type": "staking", "amount": 35000000, "value": 350000000, "date": base_time + timedelta(days=18)},
    ]

    return mock_data

# ==================== API 路由 ====================

app = FastAPI(
    title="Token Unlock Pro API",
    description="专业的代币解锁预警系统 - 每次调用需支付 0.001 USDT",
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
    """扣费函数 - 使用 skillpay.me SDK"""
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
        # 开发模式下跳过支付验证
        if Config.DEBUG:
            return {"ok": True, "balance": 999, "debug": True}
        return {"ok": False, "error": str(e)}

async def get_balance(user_id: str) -> float:
    """获取用户余额"""
    headers = {
        "X-API-Key": Config.SKILLPAY_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                BILLING_URL + "/balance",
                params={"user_id": user_id},
                headers=headers
            )
            return response.json().get("balance", 0)
    except:
        return 0

async def get_payment_link(user_id: str, amount: float = 8) -> str:
    """获取充值链接"""
    headers = {
        "X-API-Key": Config.SKILLPAY_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "user_id": user_id,
        "amount": amount
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                BILLING_URL + "/payment-link",
                json=payload,
                headers=headers
            )
            return response.json().get("payment_url", "")
    except:
        return ""

# ==================== 支付中间件 ====================

async def verify_payment(
    request: Request,
    x_user_id: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None)
) -> str:
    """验证支付"""
    user_id = x_user_id or "anonymous"

    # 如果是计费端点，跳过验证
    if request.url.path.startswith("/api/billing"):
        return user_id

    # 调用 SkillPay 扣费
    try:
        charge_result = await charge_user(user_id)

        if charge_result.get("ok"):
            # 扣费成功，继续执行
            return user_id
        else:
            # 余额不足，返回充值链接
            if Config.DEBUG:
                return user_id  # 开发模式跳过
            raise HTTPException(
                status_code=402,
                detail={
                    "message": "余额不足，请充值",
                    "payment_url": charge_result.get("payment_url", "")
                }
            )
    except Exception as e:
        # 开发模式下跳过支付验证
        if Config.DEBUG:
            return user_id
        raise HTTPException(
            status_code=402,
            detail=f"Payment verification failed: {str(e)}"
        )

    return user_id

# ==================== API 端点 ====================

@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "Token Unlock Pro API",
        "version": Config.API_VERSION,
        "description": "专业的代币解锁预警系统",
        "price_per_call": f"{Config.PRICE_PER_CALL} USDT",
        "endpoints": {
            "alerts": "/api/alerts - 获取预警列表",
            "calendar": "/api/calendar - 获取解锁日历",
            "projects": "/api/projects - 获取项目列表",
            "watchlist": "/api/watchlist - 用户监控列表",
            "trending": "/api/trending - 热门项目",
            "analysis": "/api/analysis/{token} - 历史分析",
            "billing": "/api/billing/charge - 支付计费"
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

# ---- 预警相关 ----

@app.post("/api/alerts")
async def get_alerts(
    request: AlertRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(verify_payment)
):
    """获取预警列表"""
    # 生成/获取解锁数据
    unlocks = generate_mock_unlocks()

    # 根据时间筛选
    now = datetime.utcnow()
    timeframe_hours = {
        AlertLevel.HOURS_72: 72,
        AlertLevel.HOURS_48: 48,
        AlertLevel.HOURS_24: 24,
        AlertLevel.HOURS_6: 6,
        AlertLevel.REALTIME: 0
    }

    filtered = []
    for unlock in unlocks:
        hours_until = (unlock["date"] - now).total_seconds() / 3600

        # 时间过滤
        if request.timeframe:
            max_hours = timeframe_hours.get(request.timeframe, 72)
            if hours_until > max_hours or hours_until < 0:
                continue

        # 类型过滤
        if request.unlock_type and unlock["type"] != request.unlock_type.value:
            continue

        # 额度过滤
        if request.min_value and unlock["value"] < request.min_value:
            continue

        # 计算预警级别
        if hours_until <= 6:
            alert_level = AlertLevel.REALTIME
        elif hours_until <= 24:
            alert_level = AlertLevel.HOURS_6
        elif hours_until <= 48:
            alert_level = AlertLevel.HOURS_24
        elif hours_until <= 72:
            alert_level = AlertLevel.HOURS_48
        else:
            alert_level = AlertLevel.HOURS_72

        # 计算额度分级
        value = unlock["value"]
        if value > 10000000:
            grade = UnlockGrade.WHALE
        elif value > 1000000:
            grade = UnlockGrade.LARGE
        elif value > 100000:
            grade = UnlockGrade.MEDIUM
        else:
            grade = UnlockGrade.SMALL

        filtered.append({
            "token": unlock["token"],
            "name": unlock["name"],
            "type": unlock["type"],
            "type_display": UnlockType(unlock["type"]).name if unlock["type"] in [t.value for t in UnlockType] else unlock["type"],
            "unlock_amount": unlock["amount"],
            "unlock_value_usd": unlock["value"],
            "unlock_date": unlock["date"].isoformat(),
            "hours_until_unlock": round(hours_until, 1),
            "alert_level": alert_level.value,
            "grade": grade.value,
            "grade_display": grade.name
        })

    # 排序
    filtered.sort(key=lambda x: x["hours_until_unlock"])

    return {
        "success": True,
        "count": len(filtered),
        "data": filtered[:request.limit],
        "filters": {
            "timeframe": request.timeframe.value if request.timeframe else "all",
            "unlock_type": request.unlock_type.value if request.unlock_type else "all",
            "min_value": request.min_value
        }
    }

@app.get("/api/alerts/{timeframe}")
async def get_alerts_by_timeframe(
    timeframe: AlertLevel,
    unlock_type: Optional[UnlockType] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    user_id: str = Depends(verify_payment)
):
    """根据时间框架获取预警"""
    request = AlertRequest(
        timeframe=timeframe,
        unlock_type=unlock_type,
        limit=limit
    )
    return await get_alerts(request, db, user_id)

# ---- 日历相关 ----

@app.post("/api/calendar")
async def get_calendar(
    request: CalendarRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(verify_payment)
):
    """获取解锁日历"""
    unlocks = generate_mock_unlocks()

    # 设置日期范围
    now = datetime.utcnow()
    if not request.start_date:
        request.start_date = now
    if not request.end_date:
        if request.view == CalendarView.DAY:
            request.end_date = now + timedelta(days=1)
        elif request.view == CalendarView.WEEK:
            request.end_date = now + timedelta(weeks=1)
        else:
            request.end_date = now + timedelta(days=30)

    # 筛选
    filtered = []
    for unlock in unlocks:
        if request.start_date <= unlock["date"] <= request.end_date:
            if request.unlock_type and unlock["type"] != request.unlock_type.value:
                continue

            # 计算额度分级
            value = unlock["value"]
            if value > 10000000:
                grade = UnlockGrade.WHALE
            elif value > 1000000:
                grade = UnlockGrade.LARGE
            elif value > 100000:
                grade = UnlockGrade.MEDIUM
            else:
                grade = UnlockGrade.SMALL

            filtered.append({
                "token": unlock["token"],
                "name": unlock["name"],
                "type": unlock["type"],
                "type_display": UnlockType(unlock["type"]).name if unlock["type"] in [t.value for t in UnlockType] else unlock["type"],
                "unlock_amount": unlock["amount"],
                "unlock_value_usd": unlock["value"],
                "unlock_date": unlock["date"].isoformat(),
                "grade": grade.value,
                "grade_display": grade.name
            })

    # 按日期分组
    grouped = {}
    for item in filtered:
        date_key = item["unlock_date"][:10]
        if date_key not in grouped:
            grouped[date_key] = []
        grouped[date_key].append(item)

    return {
        "success": True,
        "view": request.view.value,
        "start_date": request.start_date.isoformat(),
        "end_date": request.end_date.isoformat(),
        "total_events": len(filtered),
        "events": filtered,
        "grouped_by_date": grouped
    }

# ---- 项目相关 ----

@app.get("/api/projects")
async def get_projects(
    search: Optional[str] = None,
    unlock_type: Optional[UnlockType] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    user_id: str = Depends(verify_payment)
):
    """获取项目列表"""
    unlocks = generate_mock_unlocks()

    filtered = []
    for unlock in unlocks:
        # 搜索过滤
        if search:
            if search.upper() not in unlock["token"] and search.lower() not in unlock["name"].lower():
                continue

        # 类型过滤
        if unlock_type and unlock["type"] != unlock_type.value:
            continue

        # 计算额度分级
        value = unlock["value"]
        if value > 10000000:
            grade = UnlockGrade.WHALE
        elif value > 1000000:
            grade = UnlockGrade.LARGE
        elif value > 100000:
            grade = UnlockGrade.MEDIUM
        else:
            grade = UnlockGrade.SMALL

        filtered.append({
            "token": unlock["token"],
            "name": unlock["name"],
            "type": unlock["type"],
            "type_display": UnlockType(unlock["type"]).name if unlock["type"] in [t.value for t in UnlockType] else unlock["type"],
            "unlock_amount": unlock["amount"],
            "unlock_value_usd": unlock["value"],
            "grade": grade.value,
            "grade_display": grade.name,
            "next_unlock": unlock["date"].isoformat()
        })

    return {
        "success": True,
        "count": len(filtered),
        "data": filtered[:limit]
    }

# ---- 监控相关 ----

@app.post("/api/watchlist")
async def add_to_watchlist(
    request: AddWatchlistRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(verify_payment)
):
    """添加代币到监控列表"""
    watchlist = UserWatchlist(
        user_id=user_id,
        token_symbol=request.token_symbol.upper(),
        token_name=request.token_name or request.token_symbol,
        contract_address=request.contract_address or ""
    )
    db.add(watchlist)
    db.commit()
    db.refresh(watchlist)

    return {
        "success": True,
        "message": f"已添加 {request.token_symbol.upper()} 到监控列表",
        "data": {
            "id": watchlist.id,
            "token_symbol": watchlist.token_symbol,
            "token_name": watchlist.token_name
        }
    }

@app.get("/api/watchlist")
async def get_watchlist(
    db: Session = Depends(get_db),
    user_id: str = Depends(verify_payment)
):
    """获取用户监控列表"""
    watchlist = db.query(UserWatchlist).filter(
        UserWatchlist.user_id == user_id,
        UserWatchlist.is_active == True
    ).all()

    return {
        "success": True,
        "count": len(watchlist),
        "data": [
            {
                "id": w.id,
                "token_symbol": w.token_symbol,
                "token_name": w.token_name,
                "contract_address": w.contract_address,
                "added_at": w.added_at.isoformat()
            }
            for w in watchlist
        ]
    }

@app.delete("/api/watchlist/{token_symbol}")
async def remove_from_watchlist(
    token_symbol: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(verify_payment)
):
    """从监控列表移除"""
    watchlist = db.query(UserWatchlist).filter(
        UserWatchlist.user_id == user_id,
        UserWatchlist.token_symbol == token_symbol.upper()
    ).first()

    if watchlist:
        watchlist.is_active = False
        db.commit()
        return {"success": True, "message": f"已从监控列表移除 {token_symbol}"}

    raise HTTPException(status_code=404, detail="代币不在监控列表中")

# ---- 持仓导入 ----

@app.post("/api/portfolio/import")
async def import_portfolio(
    request: ImportPortfolioRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(verify_payment)
):
    """导入钱包持仓"""
    # 这里应该调用区块链 API 获取真实持仓
    # 模拟数据
    mock_holdings = [
        {"symbol": "ETH", "name": "Ethereum", "amount": 2.5, "value": 6250},
        {"symbol": "ARB", "name": "Arbitrum", "amount": 5000, "value": 4250},
        {"symbol": "OP", "name": "Optimism", "amount": 1000, "value": 2500},
        {"symbol": "SOL", "name": "Solana", "amount": 50, "value": 6000},
    ]

    # 保存到数据库
    for holding in mock_holdings:
        portfolio = UserPortfolio(
            user_id=user_id,
            wallet_address=request.wallet_address,
            token_symbol=holding["symbol"],
            token_name=holding["name"],
            token_amount=holding["amount"],
            token_value_usd=holding["value"]
        )
        db.add(portfolio)

    db.commit()

    # 自动添加到监控列表
    for holding in mock_holdings:
        existing = db.query(UserWatchlist).filter(
            UserWatchlist.user_id == user_id,
            UserWatchlist.token_symbol == holding["symbol"]
        ).first()

        if not existing:
            watchlist = UserWatchlist(
                user_id=user_id,
                token_symbol=holding["symbol"],
                token_name=holding["name"],
                contract_address=""
            )
            db.add(watchlist)

    db.commit()

    return {
        "success": True,
        "message": f"成功导入持仓并自动订阅解锁监控",
        "wallet_address": request.wallet_address,
        "holdings_count": len(mock_holdings),
        "data": mock_holdings
    }

@app.get("/api/portfolio")
async def get_portfolio(
    db: Session = Depends(get_db),
    user_id: str = Depends(verify_payment)
):
    """获取用户持仓"""
    portfolio = db.query(UserPortfolio).filter(
        UserPortfolio.user_id == user_id
    ).all()

    return {
        "success": True,
        "count": len(portfolio),
        "total_value_usd": sum(p.token_value_usd for p in portfolio),
        "data": [
            {
                "token_symbol": p.token_symbol,
                "token_name": p.token_name,
                "token_amount": p.token_amount,
                "token_value_usd": p.token_value_usd,
                "updated_at": p.updated_at.isoformat()
            }
            for p in portfolio
        ]
    }

# ---- 热门项目 ----

@app.get("/api/trending")
async def get_trending(
    limit: int = 10,
    db: Session = Depends(get_db),
    user_id: str = Depends(verify_payment)
):
    """获取热门订阅项目"""
    # 基于模拟数据的热门项目
    trending = [
        {"token": "ARB", "name": "Arbitrum", "subscribers": 15420, "unlock_value": 386000000},
        {"token": "OP", "name": "Optimism", "subscribers": 12350, "unlock_value": 78000000},
        {"token": "SOL", "name": "Solana", "subscribers": 9800, "unlock_value": 117600000},
        {"token": "APT", "name": "Aptos", "subscribers": 8750, "unlock_value": 82106000},
        {"token": "SAND", "name": "The Sandbox", "subscribers": 6500, "unlock_value": 68750000},
        {"token": "AXS", "name": "Axie Infinity", "subscribers": 5200, "unlock_value": 4450000},
        {"token": "BLUR", "name": "Blur", "subscribers": 4800, "unlock_value": 18750000},
        {"token": "PEPE", "name": "Pepe", "subscribers": 4200, "unlock_value": 3184000},
        {"token": "IMX", "name": "Immutable", "subscribers": 3900, "unlock_value": 4690000},
        {"token": "DYDX", "name": "dYdX", "subscribers": 3500, "unlock_value": 30000000},
    ]

    return {
        "success": True,
        "count": len(trending[:limit]),
        "data": trending[:limit]
    }

@app.post("/api/trending/subscribe")
async def subscribe_trending(
    token_symbol: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(verify_payment)
):
    """一键订阅热门项目"""
    # 检查是否已在监控列表
    existing = db.query(UserWatchlist).filter(
        UserWatchlist.user_id == user_id,
        UserWatchlist.token_symbol == token_symbol.upper()
    ).first()

    if existing:
        return {
            "success": True,
            "message": f"{token_symbol.upper()} 已在监控列表中"
        }

    # 添加到监控列表
    watchlist = UserWatchlist(
        user_id=user_id,
        token_symbol=token_symbol.upper(),
        token_name=token_symbol.upper(),
        contract_address=""
    )
    db.add(watchlist)
    db.commit()

    return {
        "success": True,
        "message": f"已成功订阅 {token_symbol.upper()} 的解锁监控"
    }

# ---- 历史分析 ----

@app.get("/api/analysis/{token}")
async def get_token_analysis(
    token: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(verify_payment)
):
    """获取代币历史解锁分析"""
    token = token.upper()

    # 模拟历史数据
    historical_unlocks = [
        {"date": "2024-01-15", "amount": 456700000, "value": 386000000, "price_before": 0.85, "price_after_24h": 0.78, "price_after_7d": 0.72, "change_24h": -8.2, "change_7d": -15.3},
        {"date": "2024-02-15", "amount": 312000000, "value": 249600000, "price_before": 0.80, "price_after_24h": 0.75, "price_after_7d": 0.68, "change_24h": -6.3, "change_7d": -15.0},
        {"date": "2024-03-15", "amount": 289000000, "value": 202300000, "price_before": 0.70, "price_after_24h": 0.65, "price_after_7d": 0.62, "change_24h": -7.1, "change_7d": -11.4},
        {"date": "2024-04-15", "amount": 356700000, "value": 285360000, "price_before": 0.80, "price_after_24h": 0.72, "price_after_7d": 0.68, "change_24h": -10.0, "change_7d": -15.0},
        {"date": "2024-05-15", "amount": 423400000, "value": 296380000, "price_before": 0.70, "price_after_24h": 0.68, "price_after_7d": 0.65, "change_24h": -2.9, "change_7d": -7.1},
    ]

    # 计算统计
    avg_change_24h = sum(h["change_24h"] for h in historical_unlocks) / len(historical_unlocks)
    avg_change_7d = sum(h["change_7d"] for h in historical_unlocks) / len(historical_unlocks)

    # 统计下跌次数
    bearish_count = sum(1 for h in historical_unlocks if h["change_24h"] < 0)
    bullish_count = sum(1 for h in historical_unlocks if h["change_24h"] > 0)

    # 预测
    prediction = "BEARISH" if avg_change_24h < -3 else "NEUTRAL" if avg_change_24h > -3 and avg_change_24h < 3 else "BULLISH"

    return {
        "success": True,
        "token": token,
        "analysis": {
            "total_historical_unlocks": len(historical_unlocks),
            "average_change_24h": round(avg_change_24h, 2),
            "average_change_7d": round(avg_change_7d, 2),
            "bearish_frequency": f"{bearish_count}/{len(historical_unlocks)} ({bearish_count/len(historical_unlocks)*100:.1f}%)",
            "bullish_frequency": f"{bullish_count}/{len(historical_unlocks)} ({bullish_count/len(historical_unlocks)*100:.1f}%)",
            "prediction": prediction,
            "recommendation": "建议在解锁前适当减仓或设置止损" if prediction == "BEARISH" else "建议观望，关注市场情绪"
        },
        "historical_data": historical_unlocks,
        "chart_data": {
            "labels": [h["date"] for h in historical_unlocks],
            "change_24h": [h["change_24h"] for h in historical_unlocks],
            "change_7d": [h["change_7d"] for h in historical_unlocks]
        }
    }

# ---- 计费相关 ----

@app.post("/api/billing/charge")
async def charge_user(
    request: ChargeRequest,
    db: Session = Depends(get_db)
):
    """用户支付计费"""
    # 生成交易ID
    timestamp = datetime.utcnow().timestamp()
    tx_id = hashlib.sha256(f"{request.user_id}{timestamp}".encode()).hexdigest()[:16]

    # 调用 SkillPay API
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.skillpay.me/v1/charge",
                json={
                    "api_key": Config.SKILLPAY_API_KEY,
                    "skill_id": Config.SKILL_ID,
                    "user_id": request.user_id,
                    "amount": request.amount,
                    "currency": request.currency,
                    "description": request.description or f"Token Unlock Pro API调用 - {request.amount} {request.currency}"
                },
                headers={
                    "Authorization": f"Bearer {Config.SKILLPAY_API_KEY}",
                    "Content-Type": "application/json"
                }
            )

            if response.status_code == 200:
                result = response.json()

                # 保存支付记录
                payment = PaymentRecord(
                    user_id=request.user_id,
                    transaction_id=tx_id,
                    amount=request.amount,
                    currency=request.currency,
                    status="success",
                    endpoint="charge"
                )
                db.add(payment)
                db.commit()

                return {
                    "success": True,
                    "transaction_id": tx_id,
                    "message": "支付成功",
                    "balance": result.get("balance", 0)
                }
            else:
                # 保存失败记录
                payment = PaymentRecord(
                    user_id=request.user_id,
                    transaction_id=tx_id,
                    amount=request.amount,
                    currency=request.currency,
                    status="failed",
                    endpoint="charge"
                )
                db.add(payment)
                db.commit()

                return {
                    "success": False,
                    "transaction_id": tx_id,
                    "message": f"支付失败: {response.text}"
                }

    except Exception as e:
        # 开发模式下返回模拟成功
        if Config.DEBUG:
            payment = PaymentRecord(
                user_id=request.user_id,
                transaction_id=tx_id,
                amount=request.amount,
                currency=request.currency,
                status="debug_success",
                endpoint="charge"
            )
            db.add(payment)
            db.commit()

            return {
                "success": True,
                "transaction_id": tx_id,
                "message": f"支付成功 (调试模式)",
                "debug": True
            }

        raise HTTPException(status_code=500, detail=f"支付处理失败: {str(e)}")

@app.get("/api/billing/balance")
async def get_balance(
    user_id: str = Depends(verify_payment)
):
    """获取用户余额"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"https://api.skillpay.me/v1/balance",
                params={"user_id": user_id},
                headers={
                    "Authorization": f"Bearer {Config.SKILLPAY_API_KEY}"
                }
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": True,
                    "balance": 0,
                    "message": "获取余额失败，使用默认余额"
                }
    except:
        return {
            "success": True,
            "balance": 0,
            "message": "服务暂不可用"
        }

@app.get("/api/billing/history")
async def get_payment_history(
    limit: int = 20,
    db: Session = Depends(get_db),
    user_id: str = Depends(verify_payment)
):
    """获取支付历史"""
    payments = db.query(PaymentRecord).filter(
        PaymentRecord.user_id == user_id
    ).order_by(PaymentRecord.created_at.desc()).limit(limit).all()

    return {
        "success": True,
        "count": len(payments),
        "total_spent": sum(p.amount for p in payments),
        "data": [
            {
                "transaction_id": p.transaction_id,
                "amount": p.amount,
                "currency": p.currency,
                "status": p.status,
                "endpoint": p.endpoint,
                "created_at": p.created_at.isoformat()
            }
            for p in payments
        ]
    }

# ==================== 启动 ====================

if __name__ == "__main__":
    import uvicorn
    init_db()
    uvicorn.run(app, host="0.0.0.0", port=8000)
