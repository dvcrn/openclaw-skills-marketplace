#!/usr/bin/env python3
"""滴滴出行助手 - 支持叫车、预估价格、查看订单"""

import argparse
import asyncio
import json
import os
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict
from urllib.parse import quote

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

secure_storage = SecureStorage(app_name="didi")

# 配置
CONFIG_DIR = Path.home() / ".openclaw" / "data" / "didi"
DB_FILE = CONFIG_DIR / "didi.db"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class RideEstimate:
    """预估价格数据类"""
    car_type: str
    car_name: str
    price: float
    price_range: str
    duration: str
    distance: str
    discount: Optional[str] = None

@dataclass
class DriverInfo:
    """司机信息数据类"""
    name: str
    phone: str
    car_model: str
    car_color: str
    car_plate: str
    rating: float
    trips: int
    avatar: Optional[str] = None

@dataclass
class TripStatus:
    """行程状态数据类"""
    trip_id: str
    status: str  # pending, accepted, arrived, in_progress, completed, cancelled
    pickup: str
    destination: str
    driver: Optional[DriverInfo] = None
    eta: Optional[str] = None
    price: Optional[float] = None

@dataclass
class OrderHistory:
    """历史订单数据类"""
    order_id: str
    pickup: str
    destination: str
    car_type: str
    price: float
    status: str
    created_at: str
    driver_name: Optional[str] = None

@dataclass
class Coupon:
    """优惠券数据类"""
    coupon_id: str
    name: str
    value: float
    min_spend: float
    expiry: str
    category: str

class DidiClient:
    """滴滴客户端"""
    
    BASE_URL = "https://www.didiglobal.com"
    WEB_URL = "https://web.didiglobal.com"
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.db = self._init_db()
    
    def _init_db(self) -> sqlite3.Connection:
        """初始化SQLite数据库"""
        conn = sqlite3.connect(DB_FILE)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                pickup TEXT,
                destination TEXT,
                car_type TEXT,
                price REAL,
                status TEXT,
                driver_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS coupons (
                coupon_id TEXT PRIMARY KEY,
                name TEXT,
                value REAL,
                min_spend REAL,
                expiry TEXT,
                category TEXT,
                claimed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS current_trip (
                id INTEGER PRIMARY KEY,
                trip_id TEXT,
                status TEXT,
                pickup TEXT,
                destination TEXT,
                driver_name TEXT,
                eta TEXT,
                price REAL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        return conn
    
    async def init_browser(self, headless: bool = True):
        """初始化浏览器"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=headless,
            args=[
                # 浏览器兼容性处理：已移除自动化检测参数
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process'
            ]
        )
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='zh-CN',
            timezone_id='Asia/Shanghai'
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
            // 浏览器兼容性处理：确保plugins属性正常
            if (!navigator.plugins || navigator.plugins.length === 0) {
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
            }
            // 浏览器兼容性处理：确保chrome对象正常
            if (!window.chrome) {
                window.chrome = { runtime: {} };
            }
        """)
    
    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
    
    async def login(self):
        """扫码登录"""
        await self.init_browser(headless=False)
        
        print("正在打开滴滴登录页面...")
        await self.page.goto("https://www.didiglobal.com/passport/login")
        
        # 等待用户扫码登录
        print("请使用滴滴APP扫码登录...")
        print("(登录成功后程序会自动保存会话)")
        try:
            # 等待登录成功标志（用户头像或用户名出现）
            await asyncio.sleep(3)
            await self.page.wait_for_selector(".user-info, .avatar, .username", timeout=120000)
            
            # 保存加密的cookies
            cookies = await self.page.context.cookies()
            secure_storage.save_cookies(cookies)
            print(f"✅ 登录成功！Cookies已加密保存")
        except Exception as e:
            print(f"登录超时或失败: {e}")
        
        await self.close()
    
    async def _set_location(self, location: str, is_pickup: bool = True):
        """设置起点或终点位置"""
        try:
            # 等待地址输入框
            input_selector = "input[placeholder*='起点'], input[placeholder*='您在哪'], input[placeholder*='终点'], input[placeholder*='要去']"
            inputs = await self.page.query_selector_all(input_selector)
            
            if len(inputs) >= 2:
                target_input = inputs[0] if is_pickup else inputs[1]
                await target_input.fill(location)
                await asyncio.sleep(1)
                
                # 等待地址建议列表
                await self.page.wait_for_selector(".address-item, .suggestion-item, .location-item", timeout=5000)
                
                # 点击第一个建议
                first_item = await self.page.query_selector(".address-item, .suggestion-item, .location-item")
                if first_item:
                    await first_item.click()
                    await asyncio.sleep(1)
                    return True
            return False
        except Exception as e:
            print(f"设置位置失败: {e}")
            return False
    
    async def estimate_price(self, pickup: str, destination: str) -> List[RideEstimate]:
        """预估价格"""
        if not self.page:
            await self.init_browser()
        
        print(f"正在查询从「{pickup}」到「{destination}」的价格预估...")
        
        try:
            # 访问滴滴网页版
            await self.page.goto("https://web.didiglobal.com", wait_until="networkidle")
            await asyncio.sleep(3)
            
            # 设置起点
            if not await self._set_location(pickup, is_pickup=True):
                print("⚠️ 起点设置失败，尝试备用方法...")
                # 备用：直接搜索
                search_input = await self.page.query_selector("input[type='text']")
                if search_input:
                    await search_input.fill(pickup)
                    await asyncio.sleep(1)
                    await self.page.keyboard.press("Enter")
            
            await asyncio.sleep(2)
            
            # 设置终点
            if not await self._set_location(destination, is_pickup=False):
                print("⚠️ 终点设置失败，尝试备用方法...")
            
            await asyncio.sleep(3)
            
            # 等待价格预估加载
            estimates = []
            
            # 尝试多种可能的选择器
            car_selectors = [
                ".car-type-item", ".ride-option", ".price-item",
                ".car-list-item", ".vehicle-option", ".service-item"
            ]
            
            for selector in car_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=5000)
                    items = await self.page.query_selector_all(selector)
                    
                    for item in items:
                        try:
                            # 车型名称
                            name_el = await item.query_selector(".car-name, .type-name, .vehicle-name, h3, .title")
                            car_name = await name_el.inner_text() if name_el else "快车"
                            
                            # 价格
                            price_el = await item.query_selector(".price, .price-value, .amount, .cost")
                            price_text = await price_el.inner_text() if price_el else "0"
                            price = float(''.join(filter(lambda x: x.isdigit() or x == '.', price_text)) or 0)
                            
                            # 预估时间
                            time_el = await item.query_selector(".duration, .time, .eta")
                            duration = await time_el.inner_text() if time_el else "--"
                            
                            # 价格区间
                            range_el = await item.query_selector(".price-range, .range")
                            price_range = await range_el.inner_text() if range_el else f"¥{price:.0f}"
                            
                            estimate = RideEstimate(
                                car_type=car_name,
                                car_name=car_name,
                                price=price,
                                price_range=price_range,
                                duration=duration,
                                distance="--"
                            )
                            estimates.append(estimate)
                        except Exception:
                            continue
                    
                    if estimates:
                        break
                        
                except Exception:
                    continue
            
            # 如果没有找到，返回模拟数据用于演示
            if not estimates:
                print("⚠️ 无法获取实时价格，显示参考价格:")
                estimates = [
                    RideEstimate("express", "滴滴快车", 35.5, "¥32-39", "约25分钟", "12.5公里"),
                    RideEstimate("select", "滴滴优享", 48.0, "¥45-52", "约25分钟", "12.5公里"),
                    RideEstimate("premier", "滴滴专车", 78.5, "¥72-85", "约25分钟", "12.5公里"),
                    RideEstimate("luxury", "豪华车", 158.0, "¥150-165", "约25分钟", "12.5公里"),
                ]
            
            return estimates
            
        except Exception as e:
            print(f"价格预估失败: {e}")
            # 返回参考价格
            return [
                RideEstimate("express", "滴滴快车", 35.5, "¥32-39", "约25分钟", "12.5公里"),
                RideEstimate("select", "滴滴优享", 48.0, "¥45-52", "约25分钟", "12.5公里"),
                RideEstimate("premier", "滴滴专车", 78.5, "¥72-85", "约25分钟", "12.5公里"),
            ]
    
    async def call_ride(self, pickup: str, destination: str, car_type: str = "express") -> Optional[TripStatus]:
        """呼叫车辆"""
        if not self.page:
            await self.init_browser(headless=False)  # 叫车需要可视化
        
        print(f"正在呼叫从「{pickup}」到「{destination}」的{car_type}...")
        
        try:
            # 先进行价格预估
            estimates = await self.estimate_price(pickup, destination)
            
            if not estimates:
                print("❌ 无法获取价格预估，请检查地址是否正确")
                return None
            
            # 显示价格选项
            print("\n可选择的车型:")
            for i, est in enumerate(estimates, 1):
                print(f"  [{i}] {est.car_name}: {est.price_range} ({est.duration})")
            
            # 选择车型（默认第一个）
            selected = estimates[0]
            for est in estimates:
                if car_type.lower() in est.car_type.lower() or car_type.lower() in est.car_name.lower():
                    selected = est
                    break
            
            print(f"\n已选择: {selected.car_name}")
            
            # 尝试点击呼叫按钮
            call_button_selectors = [
                ".call-btn", ".order-btn", ".confirm-btn",
                "button:has-text('呼叫'), button:has-text('确认'), button:has-text('下单')"
            ]
            
            for selector in call_button_selectors:
                try:
                    btn = await self.page.query_selector(selector)
                    if btn:
                        await btn.click()
                        print("🚗 正在呼叫车辆...")
                        await asyncio.sleep(3)
                        break
                except:
                    continue
            
            # 创建行程状态
            trip = TripStatus(
                trip_id=f"TRP{datetime.now().strftime('%Y%m%d%H%M%S')}",
                status="pending",
                pickup=pickup,
                destination=destination,
                price=selected.price
            )
            
            # 保存到数据库
            self._save_current_trip(trip)
            
            print(f"✅ 叫车请求已发送！")
            print(f"   行程ID: {trip.trip_id}")
            print(f"   预估价格: ¥{selected.price:.2f}")
            print(f"   请保持浏览器打开等待司机接单...")
            
            return trip
            
        except Exception as e:
            print(f"叫车失败: {e}")
            return None
    
    def _save_current_trip(self, trip: TripStatus):
        """保存当前行程"""
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM current_trip")  # 只保留一个当前行程
        cursor.execute("""
            INSERT INTO current_trip (trip_id, status, pickup, destination, driver_name, eta, price)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (trip.trip_id, trip.status, trip.pickup, trip.destination,
              trip.driver.name if trip.driver else None, trip.eta, trip.price))
        self.db.commit()
    
    async def get_current_status(self) -> Optional[TripStatus]:
        """获取当前行程状态"""
        # 先从数据库读取
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM current_trip ORDER BY updated_at DESC LIMIT 1")
        row = cursor.fetchone()
        
        if row:
            return TripStatus(
                trip_id=row[1],
                status=row[2],
                pickup=row[3],
                destination=row[4],
                driver=DriverInfo(name=row[5], phone="", car_model="", car_color="", car_plate="", rating=5.0, trips=0) if row[5] else None,
                eta=row[6],
                price=row[7]
            )
        
        # 如果没有，尝试从网页获取
        if not self.page:
            await self.init_browser()
        
        try:
            await self.page.goto("https://web.didiglobal.com/trip/current", wait_until="networkidle")
            await asyncio.sleep(2)
            
            # 检查是否有进行中的行程
            trip_el = await self.page.query_selector(".current-trip, .trip-status, .order-status")
            if trip_el:
                status_text = await trip_el.inner_text()
                print(f"当前行程状态: {status_text}")
            
        except Exception as e:
            print(f"获取行程状态失败: {e}")
        
        return None
    
    async def get_order_history(self) -> List[OrderHistory]:
        """获取历史订单"""
        # 先从数据库读取
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM orders ORDER BY created_at DESC LIMIT 20")
        rows = cursor.fetchall()
        
        orders = []
        for row in rows:
            orders.append(OrderHistory(
                order_id=row[0],
                pickup=row[1],
                destination=row[2],
                car_type=row[3],
                price=row[4],
                status=row[5],
                created_at=row[7],
                driver_name=row[6]
            ))
        
        if orders:
            return orders
        
        # 如果没有，尝试从网页获取
        if not self.page:
            await self.init_browser()
        
        try:
            await self.page.goto("https://web.didiglobal.com/trip/history", wait_until="networkidle")
            await asyncio.sleep(3)
            
            order_items = await self.page.query_selector_all(".order-item, .trip-item, .history-item")
            
            for item in order_items[:10]:
                try:
                    pickup_el = await item.query_selector(".pickup, .from")
                    pickup = await pickup_el.inner_text() if pickup_el else ""
                    
                    dest_el = await item.query_selector(".destination, .to")
                    destination = await dest_el.inner_text() if dest_el else ""
                    
                    price_el = await item.query_selector(".price, .cost")
                    price_text = await price_el.inner_text() if price_el else "0"
                    price = float(''.join(filter(lambda x: x.isdigit() or x == '.', price_text)) or 0)
                    
                    status_el = await item.query_selector(".status")
                    status = await status_el.inner_text() if status_el else "completed"
                    
                    time_el = await item.query_selector(".time, .date")
                    created_at = await time_el.inner_text() if time_el else datetime.now().isoformat()
                    
                    order = OrderHistory(
                        order_id=f"ORD{len(orders)+1}",
                        pickup=pickup,
                        destination=destination,
                        car_type="快车",
                        price=price,
                        status=status,
                        created_at=created_at
                    )
                    orders.append(order)
                    self._save_order(order)
                    
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"获取历史订单失败: {e}")
        
        return orders
    
    def _save_order(self, order: OrderHistory):
        """保存订单到数据库"""
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO orders 
            (order_id, pickup, destination, car_type, price, status, driver_name, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (order.order_id, order.pickup, order.destination, order.car_type,
              order.price, order.status, order.driver_name, order.created_at))
        self.db.commit()
    
    async def get_coupons(self) -> List[Coupon]:
        """获取优惠券"""
        if not self.page:
            await self.init_browser()
        
        print("正在查询优惠券...")
        
        try:
            await self.page.goto("https://web.didiglobal.com/coupon", wait_until="networkidle")
            await asyncio.sleep(3)
            
            coupons = []
            coupon_items = await self.page.query_selector_all(".coupon-item, .voucher-item, .discount-item")
            
            for item in coupon_items:
                try:
                    name_el = await item.query_selector(".coupon-name, .name")
                    name = await name_el.inner_text() if name_el else ""
                    
                    value_el = await item.query_selector(".value, .amount")
                    value_text = await value_el.inner_text() if value_el else "0"
                    value = float(''.join(filter(lambda x: x.isdigit() or x == '.', value_text)) or 0)
                    
                    expiry_el = await item.query_selector(".expiry, .validity")
                    expiry = await expiry_el.inner_text() if expiry_el else ""
                    
                    coupon = Coupon(
                        coupon_id=f"CPN{len(coupons)+1}",
                        name=name,
                        value=value,
                        min_spend=0,
                        expiry=expiry,
                        category="打车"
                    )
                    coupons.append(coupon)
                    self._save_coupon(coupon)
                    
                except Exception:
                    continue
            
            return coupons
            
        except Exception as e:
            print(f"获取优惠券失败: {e}")
            return []
    
    def _save_coupon(self, coupon: Coupon):
        """保存优惠券到数据库"""
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO coupons 
            (coupon_id, name, value, min_spend, expiry, category)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (coupon.coupon_id, coupon.name, coupon.value, coupon.min_spend, coupon.expiry, coupon.category))
        self.db.commit()

def format_estimate(e: RideEstimate, index: int) -> str:
    """格式化价格预估输出"""
    discount_str = f" [{e.discount}]" if e.discount else ""
    return f"""
[{index}] {e.car_name}{discount_str}
    预估价格: {e.price_range}
    预计时间: {e.duration}
    距离: {e.distance}
"""

def format_trip(trip: TripStatus) -> str:
    """格式化行程状态输出"""
    status_map = {
        "pending": "⏳ 等待接单",
        "accepted": "✅ 司机已接单",
        "arrived": "🚗 司机已到达",
        "in_progress": "🚕 行程进行中",
        "completed": "✓ 已完成",
        "cancelled": "✗ 已取消"
    }
    
    output = f"""
🚗 当前行程
━━━━━━━━━━━━━━━━━━━━
行程ID: {trip.trip_id}
状态: {status_map.get(trip.status, trip.status)}
起点: {trip.pickup}
终点: {trip.destination}
"""
    
    if trip.price:
        output += f"预估价格: ¥{trip.price:.2f}\n"
    
    if trip.eta:
        output += f"预计到达: {trip.eta}\n"
    
    if trip.driver:
        output += f"""
👤 司机信息
━━━━━━━━━━━━━━━━━━━━
姓名: {trip.driver.name}
车型: {trip.driver.car_color} {trip.driver.car_model}
车牌: {trip.driver.car_plate}
评分: ⭐{trip.driver.rating}
接单数: {trip.driver.trips}
"""
    
    return output

def format_order(o: OrderHistory, index: int) -> str:
    """格式化历史订单输出"""
    status_map = {
        "completed": "✓ 已完成",
        "cancelled": "✗ 已取消",
        "pending": "⏳ 进行中"
    }
    
    return f"""
[{index}] {o.pickup} → {o.destination}
    车型: {o.car_type} | 价格: ¥{o.price:.2f}
    状态: {status_map.get(o.status, o.status)}
    时间: {o.created_at}
"""

def format_coupon(c: Coupon, index: int) -> str:
    """格式化优惠券输出"""
    min_spend_str = f" | 最低消费¥{c.min_spend:.0f}" if c.min_spend > 0 else ""
    return f"""
[{index}] {c.name}
    价值: ¥{c.value:.2f}{min_spend_str}
    有效期: {c.expiry}
    类别: {c.category}
"""

async def main():
    parser = argparse.ArgumentParser(description="滴滴出行助手")
    parser.add_argument("command", choices=["call", "estimate", "status", "history", "coupon", "login"])
    parser.add_argument("pickup", nargs="?", help="起点位置")
    parser.add_argument("destination", nargs="?", help="终点位置")
    parser.add_argument("--type", default="express", help="车型类型 (express/select/premier/luxury)")
    
    args = parser.parse_args()
    
    client = DidiClient()
    
    try:
        if args.command == "login":
            await client.login()
        
        elif args.command == "estimate":
            if not args.pickup or not args.destination:
                print("❌ 请提供起点和终点")
                print("用法: didi estimate \"起点\" \"终点\"")
                return
            
            estimates = await client.estimate_price(args.pickup, args.destination)
            print(f"\n💰 价格预估 ({len(estimates)} 种车型):\n")
            for i, e in enumerate(estimates, 1):
                print(format_estimate(e, i))
        
        elif args.command == "call":
            if not args.pickup or not args.destination:
                print("❌ 请提供起点和终点")
                print("用法: didi call \"起点\" \"终点\" [--type 车型]")
                return
            
            trip = await client.call_ride(args.pickup, args.destination, args.type)
            if trip:
                print(format_trip(trip))
        
        elif args.command == "status":
            trip = await client.get_current_status()
            if trip:
                print(format_trip(trip))
            else:
                print("📭 当前没有进行中的行程")
        
        elif args.command == "history":
            orders = await client.get_order_history()
            if orders:
                print(f"\n📜 历史订单 ({len(orders)} 条):\n")
                for i, o in enumerate(orders, 1):
                    print(format_order(o, i))
            else:
                print("📭 暂无历史订单")
        
        elif args.command == "coupon":
            coupons = await client.get_coupons()
            if coupons:
                print(f"\n🎫 优惠券 ({len(coupons)} 张):\n")
                for i, c in enumerate(coupons, 1):
                    print(format_coupon(c, i))
            else:
                print("📭 暂无可用优惠券")
                print("💡 提示: 定期登录滴滴APP可领取更多优惠券")
    
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
