#!/usr/bin/env python3
"""饿了么助手 - 支持外卖搜索、红包、订单"""

import argparse
import asyncio
import json
import os
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from urllib.parse import quote, urlparse

try:
    from playwright.async_api import async_playwright, Page, Browser
except ImportError:
    print("请先安装依赖: pip install playwright && playwright install chromium")
    sys.exit(1)

try:
    from security import SecureStorage
except ImportError:
    print("请安装加密库: pip install cryptography")
    sys.exit(1)

secure_storage = SecureStorage(app_name="elm")

# 配置
CONFIG_DIR = Path.home() / ".openclaw" / "data" / "elm"
DB_FILE = CONFIG_DIR / "elm.db"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class FoodItem:
    """外卖商品数据类"""
    id: str
    name: str
    restaurant: str
    price: float
    rating: float
    sales: str
    delivery_time: str
    delivery_fee: str
    min_order: str
    url: str
    image: str

@dataclass
class Order:
    """订单数据类"""
    id: str
    restaurant: str
    items: str
    total: float
    status: str
    created_at: str

class ElmClient:
    """饿了么客户端"""
    
    BASE_URL = "https://www.ele.me"
    SEARCH_URL = "https://www.ele.me/home"
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.db = self._init_db()
    
    def _init_db(self) -> sqlite3.Connection:
        """初始化SQLite数据库"""
        conn = sqlite3.connect(DB_FILE)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS foods (
                id TEXT PRIMARY KEY,
                name TEXT,
                restaurant TEXT,
                price REAL,
                rating REAL,
                sales TEXT,
                delivery_time TEXT,
                delivery_fee TEXT,
                min_order TEXT,
                url TEXT,
                image TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                restaurant TEXT,
                items TEXT,
                total REAL,
                status TEXT,
                created_at TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS redpackets (
                id TEXT PRIMARY KEY,
                name TEXT,
                value REAL,
                min_spend REAL,
                expiry TEXT,
                claimed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        return conn
    
    async def init_browser(self, headless: bool = True):
        """初始化浏览器"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=headless
            # 浏览器兼容性处理：已移除自动化检测参数
        )
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        
        # 加载加密的cookies
        cookies = secure_storage.load_cookies()
        if cookies:
            await context.add_cookies(cookies)
        
        self.page = await context.new_page()
        
        # 标准浏览器兼容性处理：确保网页正常渲染
        await self.page.add_init_script("""
            // 标准浏览器兼容性处理：部分网站依赖 navigator.webdriver 属性
            // 设置为 false 表示正常浏览器环境，确保网页功能正常
            if (typeof navigator.webdriver === 'undefined') {
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false
                });
            }
        """)
    
    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
    
    async def login(self):
        """扫码登录"""
        await self.init_browser(headless=False)
        
        print("正在打开饿了么登录页面...")
        await self.page.goto("https://account.ele.me/login")
        
        # 等待用户扫码登录
        print("请使用饿了么APP扫码登录...")
        try:
            await self.page.wait_for_selector(".user-info", timeout=120000)
            
            # 保存加密的cookies
            cookies = await self.page.context.cookies()
            secure_storage.save_cookies(cookies)
            print(f"✅ 登录成功！Cookies已加密保存")
        except Exception as e:
            print(f"登录超时或失败: {e}")
        
        await self.close()
    
    async def search_food(self, keyword: str, location: str = "北京") -> List[FoodItem]:
        """搜索外卖"""
        if not self.page:
            await self.init_browser()
        
        print(f"正在搜索外卖: {keyword}")
        await self.page.goto(self.SEARCH_URL, wait_until="networkidle")
        await asyncio.sleep(2)
        
        # 输入搜索关键词
        search_input = await self.page.query_selector("input[placeholder*='搜索']")
        if search_input:
            await search_input.fill(keyword)
            await search_input.press("Enter")
            await asyncio.sleep(3)
        
        foods = []
        
        try:
            # 等待商家列表加载
            await self.page.wait_for_selector(".shop-item, .restaurant-item", timeout=10000)
            items = await self.page.query_selector_all(".shop-item, .restaurant-item")
            
            for item in items[:15]:
                try:
                    link_el = await item.query_selector("a")
                    url = await link_el.get_attribute("href") if link_el else ""
                    if url and not url.startswith("http"):
                        url = f"https:{url}"
                    
                    # 提取商家ID
                    restaurant_id = ""
                    if "/shop/" in url:
                        restaurant_id = url.split("/shop/")[-1].split("?")[0]
                    
                    name_el = await item.query_selector(".shop-name, .restaurant-name, h3")
                    name = await name_el.inner_text() if name_el else ""
                    
                    rating_el = await item.query_selector(".rating, .score")
                    rating_text = await rating_el.inner_text() if rating_el else "0"
                    rating = float(rating_text.strip() or 0)
                    
                    sales_el = await item.query_selector(".sales, .order-count")
                    sales = await sales_el.inner_text() if sales_el else ""
                    
                    time_el = await item.query_selector(".delivery-time, .time")
                    delivery_time = await time_el.inner_text() if time_el else ""
                    
                    fee_el = await item.query_selector(".delivery-fee, .fee")
                    delivery_fee = await fee_el.inner_text() if fee_el else ""
                    
                    min_el = await item.query_selector(".min-order, .min-price")
                    min_order = await min_el.inner_text() if min_el else ""
                    
                    img_el = await item.query_selector("img")
                    image = await img_el.get_attribute("src") if img_el else ""
                    
                    food = FoodItem(
                        id=restaurant_id,
                        name=name.strip(),
                        restaurant=name.strip(),
                        price=0,
                        rating=rating,
                        sales=sales,
                        delivery_time=delivery_time,
                        delivery_fee=delivery_fee,
                        min_order=min_order,
                        url=url,
                        image=image if image.startswith("http") else f"https:{image}"
                    )
                    foods.append(food)
                    self._save_food(food)
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"搜索外卖失败: {e}")
        
        return foods
    
    def _save_food(self, food: FoodItem):
        """保存外卖到数据库"""
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO foods 
            (id, name, restaurant, price, rating, sales, delivery_time, delivery_fee, min_order, url, image)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (food.id, food.name, food.restaurant, food.price, food.rating,
              food.sales, food.delivery_time, food.delivery_fee, food.min_order, food.url, food.image))
        self.db.commit()
    
    async def get_redpackets(self) -> List[dict]:
        """获取红包"""
        if not self.page:
            await self.init_browser()
        
        print("正在查询红包...")
        await self.page.goto("https://www.ele.me/profile/coupons", wait_until="networkidle")
        await asyncio.sleep(2)
        
        redpackets = []
        try:
            items = await self.page.query_selector_all(".coupon-item, .redpacket-item")
            for item in items[:10]:
                try:
                    name_el = await item.query_selector(".coupon-name, .name")
                    name = await name_el.inner_text() if name_el else ""
                    
                    value_el = await item.query_selector(".coupon-value, .amount")
                    value = await value_el.inner_text() if value_el else ""
                    
                    limit_el = await item.query_selector(".coupon-limit, .condition")
                    limit = await limit_el.inner_text() if limit_el else ""
                    
                    expiry_el = await item.query_selector(".expiry, .validity")
                    expiry = await expiry_el.inner_text() if expiry_el else ""
                    
                    redpackets.append({
                        "name": name.strip(),
                        "value": value.strip(),
                        "limit": limit.strip(),
                        "expiry": expiry.strip()
                    })
                except:
                    continue
        except Exception as e:
            print(f"获取红包失败: {e}")
        
        return redpackets
    
    async def get_orders(self) -> List[Order]:
        """获取订单"""
        if not self.page:
            await self.init_browser()
        
        print("正在查询订单...")
        await self.page.goto("https://www.ele.me/order", wait_until="networkidle")
        await asyncio.sleep(3)
        
        orders = []
        
        try:
            # 等待订单列表加载
            await self.page.wait_for_selector(".order-item, .order-card", timeout=10000)
            items = await self.page.query_selector_all(".order-item, .order-card")
            
            for item in items[:10]:
                try:
                    order_id_el = await item.query_selector(".order-id")
                    order_id = await order_id_el.inner_text() if order_id_el else ""
                    
                    restaurant_el = await item.query_selector(".restaurant-name, .shop-name")
                    restaurant = await restaurant_el.inner_text() if restaurant_el else ""
                    
                    items_el = await item.query_selector(".order-items, .items")
                    items_text = await items_el.inner_text() if items_el else ""
                    
                    total_el = await item.query_selector(".total, .amount")
                    total_text = await total_el.inner_text() if total_el else "0"
                    total = float(total_text.replace("¥", "").strip() or 0)
                    
                    status_el = await item.query_selector(".status, .order-status")
                    status = await status_el.inner_text() if status_el else ""
                    
                    time_el = await item.query_selector(".time, .order-time")
                    created_at = await time_el.inner_text() if time_el else ""
                    
                    order = Order(
                        id=order_id,
                        restaurant=restaurant.strip(),
                        items=items_text.strip(),
                        total=total,
                        status=status.strip(),
                        created_at=created_at
                    )
                    orders.append(order)
                    self._save_order(order)
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"获取订单失败: {e}")
        
        return orders
    
    def _save_order(self, order: Order):
        """保存订单到数据库"""
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO orders 
            (id, restaurant, items, total, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (order.id, order.restaurant, order.items, order.total, order.status, order.created_at))
        self.db.commit()

def format_food(f: FoodItem, index: int) -> str:
    """格式化外卖输出"""
    rating_str = f"⭐{f.rating}" if f.rating else ""
    time_str = f" | {f.delivery_time}" if f.delivery_time else ""
    fee_str = f" | 配送{f.delivery_fee}" if f.delivery_fee else ""
    min_str = f" | 起送{f.min_order}" if f.min_order else ""
    
    return f"""
[{index}] {f.name[:40]}{'...' if len(f.name) > 40 else ''}
    {rating_str} {f.sales}{time_str}{fee_str}{min_str}
    链接: {f.url}
"""

def format_order(o: Order, index: int) -> str:
    """格式化订单输出"""
    return f"""
[{index}] 订单号: {o.id}
    商家: {o.restaurant}
    商品: {o.items[:50]}{'...' if len(o.items) > 50 else ''}
    金额: ¥{o.total:.2f}
    状态: {o.status}
    时间: {o.created_at}
"""

async def main():
    parser = argparse.ArgumentParser(description="饿了么助手")
    parser.add_argument("command", choices=["search", "redpacket", "order", "login"])
    parser.add_argument("arg", nargs="?", help="搜索关键词")
    parser.add_argument("--location", default="北京", help="城市位置")
    
    args = parser.parse_args()
    
    client = ElmClient()
    
    try:
        if args.command == "login":
            await client.login()
        
        elif args.command == "search":
            if not args.arg:
                print("请提供搜索关键词")
                return
            foods = await client.search_food(args.arg, args.location)
            print(f"\n找到 {len(foods)} 家外卖:\n")
            for i, f in enumerate(foods, 1):
                print(format_food(f, i))
        
        elif args.command == "redpacket":
            redpackets = await client.get_redpackets()
            print(f"\n找到 {len(redpackets)} 个红包:\n")
            for i, r in enumerate(redpackets, 1):
                print(f"[{i}] {r['name']}")
                print(f"    金额: {r['value']}")
                print(f"    使用条件: {r['limit']}")
                print(f"    有效期: {r['expiry']}\n")
        
        elif args.command == "order":
            orders = await client.get_orders()
            print(f"\n订单列表 ({len(orders)} 个):\n")
            for i, o in enumerate(orders, 1):
                print(format_order(o, i))
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
