#!/usr/bin/env python3
"""美团助手 - 支持外卖搜索、红包、订单"""

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

# 配置
CONFIG_DIR = Path.home() / ".openclaw" / "data" / "meituan"
DB_FILE = CONFIG_DIR / "meituan.db"
COOKIES_FILE = CONFIG_DIR / "cookies.json"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class Restaurant:
    """餐厅数据类"""
    id: str
    name: str
    rating: float
    sales: str
    delivery_time: str
    delivery_fee: str
    min_order: str
    address: str
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

class MeituanClient:
    """美团客户端"""
    
    BASE_URL = "https://www.meituan.com"
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.db = self._init_db()
    
    def _init_db(self) -> sqlite3.Connection:
        """初始化SQLite数据库"""
        conn = sqlite3.connect(DB_FILE)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS restaurants (
                id TEXT PRIMARY KEY,
                name TEXT,
                rating REAL,
                sales TEXT,
                delivery_time TEXT,
                delivery_fee TEXT,
                min_order TEXT,
                address TEXT,
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
        )
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        
        # 加载cookies
        if COOKIES_FILE.exists():
            with open(COOKIES_FILE, 'r') as f:
                cookies = json.load(f)
            await context.add_cookies(cookies)
        
        self.page = await context.new_page()
        
        # 浏览器兼容性处理
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false
            });
        """)
    
    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
    
    async def login(self):
        """扫码登录"""
        await self.init_browser(headless=False)
        
        print("正在打开美团登录页面...")
        await self.page.goto("https://account.meituan.com/account/login")
        
        # 等待用户扫码登录
        print("请使用美团APP扫码登录...")
        try:
            await self.page.wait_for_selector(".user-info, .username", timeout=120000)
            
            # 保存cookies
            cookies = await self.page.context.cookies()
            with open(COOKIES_FILE, 'w') as f:
                json.dump(cookies, f)
            print(f"✅ 登录成功！Cookies已保存到 {COOKIES_FILE}")
        except Exception as e:
            print(f"登录超时或失败: {e}")
        
        await self.close()
    
    async def search_food(self, keyword: str, location: str = "北京", limit: int = 20) -> List[Restaurant]:
        """搜索外卖"""
        if not self.page:
            await self.init_browser()
        
        print(f"正在搜索: {keyword} (地点: {location})")
        search_url = f"https://waimai.meituan.com/home/{quote(location)}"
        await self.page.goto(search_url, wait_until="networkidle")
        await asyncio.sleep(2)
        
        # 输入搜索关键词
        search_input = await self.page.query_selector("input[placeholder*='搜索']")
        if search_input:
            await search_input.fill(keyword)
            await search_input.press("Enter")
            await asyncio.sleep(3)
        
        restaurants = []
        
        try:
            # 等待商家列表加载
            await self.page.wait_for_selector(".shop-item, .restaurant-item, .shop-card", timeout=10000)
            items = await self.page.query_selector_all(".shop-item, .restaurant-item, .shop-card")
            
            for item in items[:limit]:
                try:
                    link_el = await item.query_selector("a")
                    url = await link_el.get_attribute("href") if link_el else ""
                    if url and not url.startswith("http"):
                        url = f"https:{url}"
                    
                    # 提取商家ID
                    restaurant_id = ""
                    if "/shop/" in url:
                        restaurant_id = url.split("/shop/")[-1].split("?")[0]
                    elif "shopId=" in url:
                        restaurant_id = url.split("shopId=")[-1].split("&")[0]
                    
                    name_el = await item.query_selector(".shop-name, .restaurant-name, h3, .title")
                    name = await name_el.inner_text() if name_el else ""
                    
                    rating_el = await item.query_selector(".rating, .score, .rate")
                    rating_text = await rating_el.inner_text() if rating_el else "0"
                    try:
                        rating = float(rating_text.strip().replace("分", "").replace("评分", "") or 0)
                    except:
                        rating = 0
                    
                    sales_el = await item.query_selector(".sales, .order-count, .month-sales")
                    sales = await sales_el.inner_text() if sales_el else ""
                    
                    time_el = await item.query_selector(".delivery-time, .time, .avg-time")
                    delivery_time = await time_el.inner_text() if time_el else ""
                    
                    fee_el = await item.query_selector(".delivery-fee, .fee, .shipping-fee")
                    delivery_fee = await fee_el.inner_text() if fee_el else ""
                    
                    min_el = await item.query_selector(".min-order, .min-price, .start-price")
                    min_order = await min_el.inner_text() if min_el else ""
                    
                    addr_el = await item.query_selector(".address, .location")
                    address = await addr_el.inner_text() if addr_el else ""
                    
                    img_el = await item.query_selector("img")
                    image = await img_el.get_attribute("src") if img_el else ""
                    
                    restaurant = Restaurant(
                        id=restaurant_id,
                        name=name.strip(),
                        rating=rating,
                        sales=sales,
                        delivery_time=delivery_time,
                        delivery_fee=delivery_fee,
                        min_order=min_order,
                        address=address,
                        url=url,
                        image=image if image.startswith("http") else f"https:{image}"
                    )
                    restaurants.append(restaurant)
                    self._save_restaurant(restaurant)
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"搜索失败: {e}")
        
        return restaurants
    
    def _save_restaurant(self, restaurant: Restaurant):
        """保存餐厅到数据库"""
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO restaurants 
            (id, name, rating, sales, delivery_time, delivery_fee, min_order, address, url, image)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (restaurant.id, restaurant.name, restaurant.rating, restaurant.sales,
              restaurant.delivery_time, restaurant.delivery_fee, restaurant.min_order, 
              restaurant.address, restaurant.url, restaurant.image))
        self.db.commit()
    
    async def get_redpackets(self) -> List[dict]:
        """获取红包"""
        if not self.page:
            await self.init_browser()
        
        print("正在查询红包...")
        await self.page.goto("https://www.meituan.com/coupons", wait_until="networkidle")
        await asyncio.sleep(2)
        
        redpackets = []
        try:
            items = await self.page.query_selector_all(".coupon-item, .redpacket-item, .coupon-card")
            for item in items[:10]:
                try:
                    name_el = await item.query_selector(".coupon-name, .name, .title")
                    name = await name_el.inner_text() if name_el else ""
                    
                    value_el = await item.query_selector(".coupon-value, .amount, .value")
                    value = await value_el.inner_text() if value_el else ""
                    
                    limit_el = await item.query_selector(".coupon-limit, .condition, .limit")
                    limit = await limit_el.inner_text() if limit_el else ""
                    
                    expiry_el = await item.query_selector(".expiry, .validity, .expire-time")
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
        await self.page.goto("https://www.meituan.com/orders", wait_until="networkidle")
        await asyncio.sleep(2)
        
        orders = []
        try:
            items = await self.page.query_selector_all(".order-item, .order-card")
            for item in items[:20]:
                try:
                    id_el = await item.query_selector(".order-id, .order-no")
                    order_id = await id_el.inner_text() if id_el else ""
                    
                    rest_el = await item.query_selector(".restaurant-name, .shop-name")
                    restaurant = await rest_el.inner_text() if rest_el else ""
                    
                    items_el = await item.query_selector(".order-items, .items")
                    items_text = await items_el.inner_text() if items_el else ""
                    
                    total_el = await item.query_selector(".total, .amount")
                    total_text = await total_el.inner_text() if total_el else "0"
                    try:
                        total = float(total_text.replace("¥", "").replace("元", "").strip() or 0)
                    except:
                        total = 0
                    
                    status_el = await item.query_selector(".status, .order-status")
                    status = await status_el.inner_text() if status_el else ""
                    
                    time_el = await item.query_selector(".time, .create-time")
                    created_at = await time_el.inner_text() if time_el else ""
                    
                    order = Order(
                        id=order_id.strip(),
                        restaurant=restaurant.strip(),
                        items=items_text.strip(),
                        total=total,
                        status=status.strip(),
                        created_at=created_at.strip()
                    )
                    orders.append(order)
                    self._save_order(order)
                except:
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


def print_restaurants(restaurants: List[Restaurant]):
    """打印餐厅列表"""
    if not restaurants:
        print("未找到餐厅")
        return
    
    print(f"\n找到 {len(restaurants)} 家餐厅:\n")
    print(f"{'名称':<25} {'评分':<6} {'销量':<12} {'配送时间':<10} {'配送费':<10} {'起送价':<10}")
    print("-" * 90)
    
    for r in restaurants:
        name = r.name[:23] if len(r.name) > 23 else r.name
        rating = f"{r.rating:.1f}" if r.rating else "N/A"
        sales = r.sales[:10] if r.sales else "N/A"
        time = r.delivery_time[:8] if r.delivery_time else "N/A"
        fee = r.delivery_fee[:8] if r.delivery_fee else "N/A"
        min_order = r.min_order[:8] if r.min_order else "N/A"
        print(f"{name:<25} {rating:<6} {sales:<12} {time:<10} {fee:<10} {min_order:<10}")


def print_redpackets(redpackets: List[dict]):
    """打印红包列表"""
    if not redpackets:
        print("暂无红包")
        return
    
    print(f"\n找到 {len(redpackets)} 个红包:\n")
    print(f"{'名称':<30} {'金额':<10} {'使用条件':<20} {'有效期':<15}")
    print("-" * 80)
    
    for rp in redpackets:
        name = rp.get('name', '')[:28]
        value = rp.get('value', '')[:8]
        limit = rp.get('limit', '')[:18]
        expiry = rp.get('expiry', '')[:13]
        print(f"{name:<30} {value:<10} {limit:<20} {expiry:<15}")


def print_orders(orders: List[Order]):
    """打印订单列表"""
    if not orders:
        print("暂无订单")
        return
    
    print(f"\n找到 {len(orders)} 个订单:\n")
    print(f"{'订单号':<20} {'餐厅':<25} {'金额':<10} {'状态':<12} {'时间':<20}")
    print("-" * 95)
    
    for o in orders:
        order_id = o.id[:18] if len(o.id) > 18 else o.id
        restaurant = o.restaurant[:23] if len(o.restaurant) > 23 else o.restaurant
        total = f"¥{o.total:.2f}"
        status = o.status[:10] if o.status else "N/A"
        time = o.created_at[:18] if o.created_at else "N/A"
        print(f"{order_id:<20} {restaurant:<25} {total:<10} {status:<12} {time:<20}")


async def main():
    parser = argparse.ArgumentParser(description="美团助手")
    parser.add_argument("command", choices=["food", "login", "redpacket", "order"], help="命令")
    parser.add_argument("query", nargs="?", help="搜索关键词")
    parser.add_argument("--location", "-l", default="北京", help="地点 (默认: 北京)")
    parser.add_argument("--limit", "-n", type=int, default=20, help="结果数量 (默认: 20)")
    parser.add_argument("--headless", action="store_true", default=True, help="无头模式")
    parser.add_argument("--no-headless", action="store_false", dest="headless", help="显示浏览器")
    parser.add_argument("--json", "-j", action="store_true", help="JSON输出")
    
    args = parser.parse_args()
    
    client = MeituanClient()
    
    if args.command == "login":
        await client.login()
    
    elif args.command == "food":
        if not args.query:
            print("请提供搜索关键词，例如: meituan food 火锅")
            sys.exit(1)
        
        restaurants = await client.search_food(args.query, args.location, args.limit)
        
        if args.json:
            print(json.dumps([r.__dict__ for r in restaurants], ensure_ascii=False, indent=2))
        else:
            print_restaurants(restaurants)
        
        await client.close()
    
    elif args.command == "redpacket":
        redpackets = await client.get_redpackets()
        
        if args.json:
            print(json.dumps(redpackets, ensure_ascii=False, indent=2))
        else:
            print_redpackets(redpackets)
        
        await client.close()
    
    elif args.command == "order":
        orders = await client.get_orders()
        
        if args.json:
            print(json.dumps([o.__dict__ for o in orders], ensure_ascii=False, indent=2))
        else:
            print_orders(orders)
        
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
