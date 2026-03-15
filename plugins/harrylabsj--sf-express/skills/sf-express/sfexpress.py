#!/usr/bin/env python3
"""顺丰速运助手 - 专为顺丰用户提供深度集成的快递服务"""

import argparse
import asyncio
import json
import os
import re
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict

import aiohttp

# 安全存储
try:
    from security import SecureStorage
except ImportError:
    print("请安装加密库: pip install cryptography")
    sys.exit(1)

secure_storage = SecureStorage(app_name="sf-express")

# 配置
CONFIG_DIR = Path.home() / ".openclaw" / "data" / "sf-express"
DB_FILE = CONFIG_DIR / "sfexpress.db"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# 顺丰产品类型
SF_PRODUCTS = {
    'standard': {'name': '顺丰标快', 'code': 'S1', 'time': '1-2天', 'desc': '普通文件、包裹'},
    'express': {'name': '顺丰特快', 'code': 'S2', 'time': '次日达', 'desc': '紧急文件、时效要求高'},
    'same_day': {'name': '顺丰即日', 'code': 'S3', 'time': '当日达', 'desc': '同城急件'},
    'cold_chain': {'name': '顺丰冷链', 'code': 'S4', 'time': '1-2天', 'desc': '生鲜、医药'},
    'heavy': {'name': '顺丰重货', 'code': 'S5', 'time': '2-3天', 'desc': '大件物品'},
    'international': {'name': '顺丰国际', 'code': 'S6', 'time': '3-7天', 'desc': '跨境快递'},
    'economy': {'name': '顺丰特惠', 'code': 'S7', 'time': '2-3天', 'desc': '非紧急、经济型'},
}

# 顺丰单号规则
SF_PATTERN = r'^[A-Z]{2}\d{10,}$|^\d{12,15}$'


@dataclass
class TrackingEvent:
    """物流事件"""
    time: str
    description: str
    location: str
    status: str


@dataclass
class TrackingResult:
    """查询结果"""
    tracking_number: str
    product_name: str
    status: str
    events: List[TrackingEvent]
    estimated_delivery: Optional[str] = None
    last_updated: Optional[str] = None
    sender: Optional[str] = None
    receiver: Optional[str] = None


@dataclass
class TimeEstimate:
    """时效预估"""
    product: str
    product_name: str
    estimated_time: str
    price_range: str
    cutoff_time: str


@dataclass
class PriceEstimate:
    """运费估算"""
    product: str
    product_name: str
    weight: float
    base_price: float
    fuel_surcharge: float
    total_price: float
    delivery_time: str


class SFExpressClient:
    """顺丰客户端"""
    
    def __init__(self):
        self.db = self._init_db()
        self.session: Optional[aiohttp.ClientSession] = None
    
    def _init_db(self) -> sqlite3.Connection:
        """初始化数据库"""
        conn = sqlite3.connect(str(DB_FILE))
        cursor = conn.cursor()
        
        # 查询历史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tracking_number TEXT NOT NULL,
                product_name TEXT,
                status TEXT,
                result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 订阅表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tracking_number TEXT NOT NULL UNIQUE,
                last_status TEXT,
                notify_enabled BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 寄件地址表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS addresses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                is_default BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        return conn
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def is_sf_number(self, tracking_number: str) -> bool:
        """检查是否为顺丰单号"""
        return bool(re.match(SF_PATTERN, tracking_number.upper()))
    
    async def query(self, tracking_number: str) -> TrackingResult:
        """查询物流信息"""
        if not self.is_sf_number(tracking_number):
            raise ValueError(f"{tracking_number} 不是有效的顺丰单号")
        
        # 模拟查询结果
        result = TrackingResult(
            tracking_number=tracking_number,
            product_name="顺丰标快",
            status="in_transit",
            events=[
                TrackingEvent(
                    time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    description="快件已到达【北京顺义集散中心】",
                    location="北京市",
                    status="in_transit"
                ),
                TrackingEvent(
                    time=(datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
                    description="快件已从【上海虹桥集散中心】发出",
                    location="上海市",
                    status="in_transit"
                ),
            ],
            estimated_delivery=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            sender="上海市",
            receiver="北京市"
        )
        
        self._save_history(result)
        return result
    
    async def batch_query(self, tracking_numbers: List[str]) -> List[TrackingResult]:
        """批量查询"""
        tasks = [self.query(number) for number in tracking_numbers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if not isinstance(r, Exception)]
    
    def estimate_time(self, origin: str, destination: str, product: str = 'standard') -> TimeEstimate:
        """时效预估"""
        product_info = SF_PRODUCTS.get(product, SF_PRODUCTS['standard'])
        
        if product == 'same_day':
            estimated = "今日 18:00 前"
        elif product == 'express':
            estimated = "次日 12:00 前"
        else:
            estimated = f"{product_info['time']}"
        
        return TimeEstimate(
            product=product,
            product_name=product_info['name'],
            estimated_time=estimated,
            price_range="¥18-35",
            cutoff_time="当日 16:00"
        )
    
    def estimate_price(self, origin: str, destination: str, weight: float, product: str = 'standard') -> PriceEstimate:
        """运费估算"""
        product_info = SF_PRODUCTS.get(product, SF_PRODUCTS['standard'])
        
        base_price = 18.0
        if weight > 1:
            base_price += (weight - 1) * 5
        
        if product == 'express':
            base_price *= 1.5
        elif product == 'same_day':
            base_price *= 2.0
        elif product == 'cold_chain':
            base_price *= 1.3
        elif product == 'heavy':
            base_price = weight * 3
        
        fuel_surcharge = base_price * 0.1
        total = base_price + fuel_surcharge
        
        return PriceEstimate(
            product=product,
            product_name=product_info['name'],
            weight=weight,
            base_price=round(base_price, 2),
            fuel_surcharge=round(fuel_surcharge, 2),
            total_price=round(total, 2),
            delivery_time=product_info['time']
        )
    
    def _save_history(self, result: TrackingResult):
        """保存查询历史"""
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT INTO history (tracking_number, product_name, status, result)
            VALUES (?, ?, ?, ?)
        ''', (
            result.tracking_number,
            result.product_name,
            result.status,
            json.dumps(result.__dict__, default=lambda x: x.__dict__ if hasattr(x, '__dict__') else str(x))
        ))
        self.db.commit()
    
    def get_history(self, limit: int = 10, search: Optional[str] = None) -> List[dict]:
        """获取查询历史"""
        cursor = self.db.cursor()
        
        if search:
            cursor.execute('''
                SELECT * FROM history 
                WHERE tracking_number LIKE ? 
                ORDER BY created_at DESC LIMIT ?
            ''', (f'%{search}%', limit))
        else:
            cursor.execute('''
                SELECT * FROM history 
                ORDER BY created_at DESC LIMIT ?
            ''', (limit,))
        
        columns = [description[0] for description in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        return results
    
    def subscribe(self, tracking_number: str):
        """订阅物流提醒"""
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO subscriptions (tracking_number, last_status)
            VALUES (?, ?)
        ''', (tracking_number, 'pending'))
        self.db.commit()
        return True
    
    def unsubscribe(self, tracking_number: str):
        """取消订阅"""
        cursor = self.db.cursor()
        cursor.execute('DELETE FROM subscriptions WHERE tracking_number = ?', (tracking_number,))
        self.db.commit()
        return True
    
    def get_subscriptions(self) -> List[dict]:
        """获取所有订阅"""
        cursor = self.db.cursor()
        cursor.execute('SELECT * FROM subscriptions ORDER BY created_at DESC')
        columns = [description[0] for description in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        return results
    
    def format_tracking_result(self, result: TrackingResult) -> str:
        """格式化查询结果"""
        lines = [
            f"📦 顺丰速运 ({result.tracking_number})",
            f"产品: {result.product_name}",
            f"状态: {self._format_status(result.status)}",
            f"预计送达: {result.estimated_delivery or '未知'}",
            f"更新时间: {result.last_updated or '未知'}",
            "",
            "物流轨迹:",
        ]
        
        for event in result.events:
            lines.append(f"  [{event.time}] {event.location} - {event.description}")
        
        return "\n".join(lines)
    
    def format_time_estimate(self, estimate: TimeEstimate) -> str:
        """格式化工时效预估"""
        return f"""📋 时效预估
产品: {estimate.product_name}
预计时效: {estimate.estimated_time}
价格区间: {estimate.price_range}
截单时间: {estimate.cutoff_time}"""
    
    def format_price_estimate(self, estimate: PriceEstimate) -> str:
        """格式化运费估算"""
        return f"""💰 运费估算
产品: {estimate.product_name}
重量: {estimate.weight}kg
基础运费: ¥{estimate.base_price}
燃油附加费: ¥{estimate.fuel_surcharge}
预估总价: ¥{estimate.total_price}
配送时效: {estimate.delivery_time}"""
    
    def _format_status(self, status: str) -> str:
        """格式化状态"""
        status_map = {
            'pending': '⏳ 待揽收',
            'picked_up': '📦 已揽收',
            'in_transit': '🚚 运输中',
            'delivered': '✅ 已签收',
            'exception': '⚠️ 异常',
        }
        return status_map.get(status, status)


def print_products():
    """打印顺丰产品列表"""
    print("顺丰产品类型:\n")
    print(f"{'代码':<15} {'名称':<12} {'时效':<10} {'说明'}")
    print("-" * 60)
    for code, info in SF_PRODUCTS.items():
        print(f"{code:<15} {info['name']:<12} {info['time']:<10} {info['desc']}")


def print_history(client: SFExpressClient, limit: int = 10, search: Optional[str] = None):
    """打印查询历史"""
    history = client.get_history(limit, search)
    if not history:
        print("暂无查询记录")
        return
    
    print(f"最近 {len(history)} 条查询记录:\n")
    print(f"{'单号':<20} {'产品':<12} {'状态':<10} {'查询时间':<20}")
    print("-" * 70)
    
    for record in history:
        print(f"{record['tracking_number']:<20} {record['product_name'] or '-':<12} "
              f"{record['status']:<10} {record['created_at']:<20}")


def print_subscriptions(client: SFExpressClient):
    """打印订阅列表"""
    subs = client.get_subscriptions()
    if not subs:
        print("暂无订阅")
        return
    
    print(f"共 {len(subs)} 个订阅:\n")
    print(f"{'单号':<20} {'最后状态':<12} {'订阅时间':<20}")
    print("-" * 60)
    
    for sub in subs:
        print(f"{sub['tracking_number']:<20} {sub['last_status']:<12} {sub['created_at']:<20}")


def print_privacy_info():
    """打印隐私信息"""
    info = secure_storage.get_storage_info()
    print("存储信息:\n")
    print(f"存储目录: {info['base_dir']}")
    print(f"文件数量: {info['total_files']}\n")
    
    if info['files']:
        print("文件列表:")
        for f in info['files']:
            print(f"  - {f['name']} ({f['size']} bytes, 权限: {f['permissions']})")


async def main():
    parser = argparse.ArgumentParser(description='顺丰速运助手')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 单号查询
    query_parser = subparsers.add_parser('query', help='查询顺丰快递')
    query_parser.add_argument('tracking_number', help='顺丰单号')
    
    # 批量查询
    batch_parser = subparsers.add_parser('batch', help='批量查询')
    batch_parser.add_argument('tracking_numbers', nargs='+', help='顺丰单号列表')
    
    # 时效查询
    time_parser = subparsers.add_parser('time', help='时效预估')
    time_parser.add_argument('origin', help='寄件地')
    time_parser.add_argument('destination', help='收件地')
    time_parser.add_argument('--product', '-p', default='standard', 
                            choices=list(SF_PRODUCTS.keys()),
                            help='产品类型')
    
    # 运费估算
    price_parser = subparsers.add_parser('price', help='运费估算')
    price_parser.add_argument('origin', help='寄件地')
    price_parser.add_argument('destination', help='收件地')
    price_parser.add_argument('--weight', '-w', type=float, default=1.0, help='重量(kg)')
    price_parser.add_argument('--product', '-p', default='standard',
                            choices=list(SF_PRODUCTS.keys()),
                            help='产品类型')
    
    # 产品列表
    subparsers.add_parser('products', help='查看顺丰产品类型')
    
    # 历史记录
    history_parser = subparsers.add_parser('history', help='查询历史')
    history_parser.add_argument('--limit', '-l', type=int, default=10, help='显示数量')
    history_parser.add_argument('--search', '-s', help='搜索单号')
    
    # 订阅
    sub_parser = subparsers.add_parser('subscribe', help='订阅物流提醒')
    sub_parser.add_argument('tracking_number', help='顺丰单号')
    
    # 取消订阅
    unsub_parser = subparsers.add_parser('unsubscribe', help='取消订阅')
    unsub_parser.add_argument('tracking_number', help='顺丰单号')
    
    # 订阅列表
    subparsers.add_parser('subscriptions', help='查看所有订阅')
    
    # 隐私控制
    privacy_parser = subparsers.add_parser('privacy', help='隐私控制')
    privacy_parser.add_argument('action', choices=['info', 'clear', 'export'],
                                help='info: 查看信息, clear: 清除数据, export: 导出备份')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 显示产品列表
    if args.command == 'products':
        print_products()
        return
    
    # 隐私控制
    if args.command == 'privacy':
        if args.action == 'info':
            print_privacy_info()
        elif args.action == 'clear':
            clear_local_data()
            print("✅ 已清除本地 SQLite 历史/订阅数据，以及加密存储文件")
        elif args.action == 'export':
            storage = get_secure_storage()
            info = storage.get_storage_info()
            export_file = CONFIG_DIR / 'privacy_export.json'
            payload = {
                'config_dir': str(CONFIG_DIR),
                'db_file': str(DB_FILE),
                'db_exists': DB_FILE.exists(),
                'secure_storage': info,
            }
            with open(export_file, 'w') as f:
                json.dump(payload, f, indent=2)
            print(f"✅ 已导出到: {export_file}")
        return
    
    # 初始化客户端
    async with SFExpressClient() as client:
        # 单号查询
        if args.command == 'query':
            try:
                result = await client.query(args.tracking_number)
                print(client.format_tracking_result(result))
            except Exception as e:
                print(f"❌ 查询失败: {e}")
        
        # 批量查询
        elif args.command == 'batch':
            results = await client.batch_query(args.tracking_numbers)
            for result in results:
                print(client.format_tracking_result(result))
                print("\n" + "="*50 + "\n")
        
        # 时效查询
        elif args.command == 'time':
            estimate = client.estimate_time(args.origin, args.destination, args.product)
            print(client.format_time_estimate(estimate))
        
        # 运费估算
        elif args.command == 'price':
            estimate = client.estimate_price(args.origin, args.destination, args.weight, args.product)
            print(client.format_price_estimate(estimate))
        
        # 历史记录
        elif args.command == 'history':
            print_history(client, args.limit, args.search)
        
        # 订阅
        elif args.command == 'subscribe':
            if client.subscribe(args.tracking_number):
                print(f"✅ 已订阅 {args.tracking_number} 的物流提醒")
        
        # 取消订阅
        elif args.command == 'unsubscribe':
            if client.unsubscribe(args.tracking_number):
                print(f"✅ 已取消 {args.tracking_number} 的订阅")
        
        # 订阅列表
        elif args.command == 'subscriptions':
            print_subscriptions(client)


if __name__ == '__main__':
    asyncio.run(main())
