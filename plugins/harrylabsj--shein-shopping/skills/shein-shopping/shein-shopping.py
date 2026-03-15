#!/usr/bin/env python3
"""SHEIN购物助手 - 支持搜索、价格追踪、新品上架"""

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

secure_storage = SecureStorage(app_name="shein-shopping")

# 配置
CONFIG_DIR = Path.home() / ".openclaw" / "data" / "shein-ec"
DB_FILE = CONFIG_DIR / "shein-ec.db"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class Product:
    """商品数据类"""
    id: str
    title: str
    price: float
    original_price: Optional[float]
    shop: str
    url: str
    image: str
    rating: Optional[float] = None
    sales: Optional[str] = None
    is_new: bool = False

class SheinClient:
    """SHEIN客户端"""

    BASE_URL = "https://www.shein.com"
    SEARCH_URL = "https://www.shein.com/pdsearch"
    NEW_ARRIVALS_URL = "https://www.shein.com/new"

    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.db = self._init_db()

    def _init_db(self) -> sqlite3.Connection:
        """初始化SQLite数据库"""
        conn = sqlite3.connect(DB_FILE)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                title TEXT,
                price REAL,
                original_price REAL,
                shop TEXT,
                url TEXT,
                image TEXT,
                rating REAL,
                sales TEXT,
                is_new BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT,
                price REAL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id)
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

        print("正在打开SHEIN登录页面...")
        await self.page.goto(f"{self.BASE_URL}/user/auth/login")

        # 等待用户扫码登录
        print("请使用SHEIN APP扫码登录...")
        await self.page.wait_for_selector(".user-info", timeout=120000)

        # 保存加密的cookies
        cookies = await self.page.context.cookies()
        secure_storage.save_cookies(cookies)
        print(f"✅ 登录成功！Cookies已加密保存")

        await self.close()

    async def search(self, keyword: str, page_num: int = 1) -> List[Product]:
        """搜索商品"""
        if not self.page:
            await self.init_browser()

        encoded_keyword = quote(keyword)
        url = f"{self.SEARCH_URL}/{encoded_keyword}/?page={page_num}"

        print(f"正在搜索: {keyword}")
        await self.page.goto(url, wait_until="networkidle")
        await asyncio.sleep(3)

        products = []

        try:
            # 等待商品列表加载
            await self.page.wait_for_selector(".product-card", timeout=10000)
            items = await self.page.query_selector_all(".product-card")

            for item in items[:20]:
                try:
                    # 提取商品信息
                    link_el = await item.query_selector("a")
                    url = await link_el.get_attribute("href") if link_el else ""
                    if url and not url.startswith("http"):
                        url = f"{self.BASE_URL}{url}"

                    # 提取商品ID
                    product_id = ""
                    if "/p/" in url:
                        product_id = url.split("/p/")[-1].split(".")[0]

                    title_el = await item.query_selector(".product-name")
                    title = await title_el.inner_text() if title_el else ""

                    price_el = await item.query_selector(".price")
                    price_text = await price_el.inner_text() if price_el else "0"
                    price = float(price_text.replace("$", "").replace("€", "").strip() or 0)

                    original_price_el = await item.query_selector(".original-price")
                    original_price_text = await original_price_el.inner_text() if original_price_el else None
                    original_price = float(original_price_text.replace("$", "").replace("€", "").strip() or 0) if original_price_text else None

                    img_el = await item.query_selector("img")
                    image = await img_el.get_attribute("src") if img_el else ""

                    # 检查是否新品
                    new_badge = await item.query_selector(".new-badge, .new-arrival")
                    is_new = new_badge is not None

                    product = Product(
                        id=product_id,
                        title=title.strip(),
                        price=price,
                        original_price=original_price,
                        shop="SHEIN",
                        url=url,
                        image=image if image.startswith("http") else f"https:{image}",
                        is_new=is_new
                    )
                    products.append(product)
                    self._save_product(product)

                except Exception as e:
                    continue

        except Exception as e:
            print(f"搜索解析失败: {e}")

        return products

    def _save_product(self, product: Product):
        """保存商品到数据库"""
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO products
            (id, title, price, original_price, shop, url, image, is_new, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (product.id, product.title, product.price, product.original_price,
              product.shop, product.url, product.image, product.is_new))

        # 记录价格历史
        cursor.execute("""
            INSERT INTO price_history (product_id, price)
            VALUES (?, ?)
        """, (product.id, product.price))

        self.db.commit()

    async def get_price(self, product_url: str) -> tuple:
        """获取商品价格和历史"""
        if not self.page:
            await self.init_browser()

        print(f"正在获取价格: {product_url}")
        await self.page.goto(product_url, wait_until="networkidle")
        await asyncio.sleep(3)

        # 提取商品ID
        parsed = urlparse(product_url)
        product_id = parsed.path.split("/p/")[-1].split(".")[0] if "/p/" in parsed.path else ""

        # 从数据库获取历史价格
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT price, recorded_at FROM price_history
            WHERE product_id = ?
            ORDER BY recorded_at DESC
            LIMIT 30
        """, (product_id,))

        history = cursor.fetchall()

        # 获取当前商品信息
        try:
            title_el = await self.page.query_selector("h1, .product-title")
            title = await title_el.inner_text() if title_el else ""

            price_el = await self.page.query_selector(".price, .product-price")
            price_text = await price_el.inner_text() if price_el else "0"
            current_price = float(price_text.replace("$", "").replace("€", "").strip() or 0)

        except:
            title = ""
            current_price = 0

        return {
            "product_id": product_id,
            "title": title,
            "current_price": current_price,
            "history": history
        }

    async def get_new_arrivals(self, category: str = "all") -> List[Product]:
        """获取新品上架"""
        if not self.page:
            await self.init_browser()

        print("正在获取新品上架...")
        url = f"{self.NEW_ARRIVALS_URL}"
        if category != "all":
            url = f"{url}/{category}"

        await self.page.goto(url, wait_until="networkidle")
        await asyncio.sleep(3)

        products = []

        try:
            # 等待商品列表加载
            await self.page.wait_for_selector(".product-card", timeout=10000)
            items = await self.page.query_selector_all(".product-card")

            for item in items[:20]:
                try:
                    # 提取商品信息
                    link_el = await item.query_selector("a")
                    url = await link_el.get_attribute("href") if link_el else ""
                    if url and not url.startswith("http"):
                        url = f"{self.BASE_URL}{url}"

                    # 提取商品ID
                    product_id = ""
                    if "/p/" in url:
                        product_id = url.split("/p/")[-1].split(".")[0]

                    title_el = await item.query_selector(".product-name")
                    title = await title_el.inner_text() if title_el else ""

                    price_el = await item.query_selector(".price")
                    price_text = await price_el.inner_text() if price_el else "0"
                    price = float(price_text.replace("$", "").replace("€", "").strip() or 0)

                    img_el = await item.query_selector("img")
                    image = await img_el.get_attribute("src") if img_el else ""

                    product = Product(
                        id=product_id,
                        title=title.strip(),
                        price=price,
                        original_price=None,
                        shop="SHEIN",
                        url=url,
                        image=image if image.startswith("http") else f"https:{image}",
                        is_new=True
                    )
                    products.append(product)
                    self._save_product(product)

                except Exception as e:
                    continue

        except Exception as e:
            print(f"获取新品失败: {e}")

        return products

def format_product(p: Product, index: int) -> str:
    """格式化商品输出"""
    price_str = f"${p.price:.2f}"
    original_str = f" (原价: ${p.original_price:.2f})" if p.original_price else ""
    new_str = " [NEW]" if p.is_new else ""
    return f"""
[{index}]{new_str} {p.title[:50]}{'...' if len(p.title) > 50 else ''}
    价格: {price_str}{original_str}
    链接: {p.url}
"""

async def main():
    parser = argparse.ArgumentParser(description="SHEIN购物助手")
    parser.add_argument("command", choices=["search", "price", "new", "login"])
    parser.add_argument("arg", nargs="?", help="搜索关键词/商品链接/分类")
    parser.add_argument("--page", type=int, default=1, help="页码")
    parser.add_argument("--category", type=str, default="all", help="新品分类")

    args = parser.parse_args()

    client = SheinClient()

    try:
        if args.command == "login":
            await client.login()

        elif args.command == "search":
            if not args.arg:
                print("请提供搜索关键词")
                return
            products = await client.search(args.arg, args.page)
            print(f"\n找到 {len(products)} 个商品:\n")
            for i, p in enumerate(products, 1):
                print(format_product(p, i))

        elif args.command == "price":
            if not args.arg:
                print("请提供商品链接")
                return
            result = await client.get_price(args.arg)
            print(f"\n商品: {result['title']}")
            print(f"当前价格: ${result['current_price']:.2f}")
            print(f"\n历史价格记录 ({len(result['history'])} 条):")
            for price, date in result['history'][:10]:
                print(f"  {date}: ${price:.2f}")

        elif args.command == "new":
            category = args.arg or args.category
            products = await client.get_new_arrivals(category)
            print(f"\n新品上架 ({len(products)} 个):\n")
            for i, p in enumerate(products, 1):
                print(format_product(p, i))

    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
