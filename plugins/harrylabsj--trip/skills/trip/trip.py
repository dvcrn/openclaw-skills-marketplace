#!/usr/bin/env python3
"""
Trip.com (携程) CLI Tool - Flight and Hotel Search
"""

import asyncio
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# Import from bundled ecommerce_core module
from ecommerce_core import EcommerceBrowser, AuthManager, DataCache


class TripBrowser(EcommerceBrowser):
    """Browser automation for Trip.com / Ctrip"""
    
    def __init__(self, headless: bool = False):
        super().__init__(platform='trip', headless=headless)
        self.base_url = 'https://www.trip.com'
        self.cache = DataCache()
        self.auth = AuthManager()
        
    async def search_flights(self, origin: str, destination: str, 
                             date: str) -> List[Dict[str, Any]]:
        """
        Search flights between cities
        
        Args:
            origin: Departure city (e.g., '北京', '北京')
            destination: Arrival city (e.g., '上海', '上海')
            date: Departure date in YYYY-MM-DD format
            
        Returns:
            List of flight results
        """
        await self.init()
        
        try:
            # Navigate to flight search page
            await self.goto(f'{self.base_url}/flights/')
            
            # Wait for page to load
            await self._page.wait_for_selector('.flight-search-form', timeout=10000)
            
            # Fill origin city
            await self._fill_city('.origin-input', origin)
            
            # Fill destination city
            await self._fill_city('.destination-input', destination)
            
            # Select date
            await self._select_date(date)
            
            # Click search button
            await self._page.click('.search-btn')
            await self._page.wait_for_load_state('networkidle')
            
            # Wait for results
            await self._page.wait_for_selector('.flight-list', timeout=30000)
            
            # Extract flight data
            flights = await self._extract_flights()
            
            # Cache results
            cache_key = f'flights_{origin}_{destination}_{date}'
            self.cache.set(cache_key, flights, ttl_minutes=30, platform='trip')
            
            return flights
            
        except Exception as e:
            print(f"Flight search error: {e}")
            return []
        finally:
            await self.close()
            
    async def search_hotels(self, city: str, check_in: str, 
                            check_out: str) -> List[Dict[str, Any]]:
        """
        Search hotels in a city
        
        Args:
            city: City name (e.g., '上海', '上海')
            check_in: Check-in date in YYYY-MM-DD format
            check_out: Check-out date in YYYY-MM-DD format
            
        Returns:
            List of hotel results
        """
        await self.init()
        
        try:
            # Navigate to hotel search page
            await self.goto(f'{self.base_url}/hot/')
            
            # Wait for page to load
            await self._page.wait_for_selector('.hotel-search-form', timeout=10000)
            
            # Fill city
            await self._fill_city('.city-input', city)
            
            # Select dates
            await self._select_date_range(check_in, check_out)
            
            # Click search button
            await self._page.click('.search-btn')
            await self._page.wait_for_load_state('networkidle')
            
            # Wait for results
            await self._page.wait_for_selector('.hotel-list', timeout=30000)
            
            # Extract hotel data
            hotels = await self._extract_hotels()
            
            # Cache results
            cache_key = f'hotels_{city}_{check_in}_{check_out}'
            self.cache.set(cache_key, hotels, ttl_minutes=30, platform='trip')
            
            return hotels
            
        except Exception as e:
            print(f"Hotel search error: {e}")
            return []
        finally:
            await self.close()
            
    async def _fill_city(self, selector: str, city: str):
        """Fill city input and select from dropdown"""
        # Click on input
        await self._page.click(selector)
        await asyncio.sleep(0.5)
        
        # Type city name
        await self._page.fill(f'{selector} input', city)
        await asyncio.sleep(1)
        
        # Select first matching option
        await self._page.click('.city-dropdown .city-item:first-child')
        await asyncio.sleep(0.5)
        
    async def _select_date(self, date: str):
        """Select single date"""
        # Parse date
        dt = datetime.strptime(date, '%Y-%m-%d')
        date_str = dt.strftime('%Y-%m-%d')
        
        # Click date picker
        await self._page.click('.date-picker')
        await asyncio.sleep(0.5)
        
        # Select date using data attribute
        await self._page.click(f'[data-date="{date_str}"]')
        await asyncio.sleep(0.5)
        
    async def _select_date_range(self, check_in: str, check_out: str):
        """Select check-in and check-out dates"""
        # Parse dates
        check_in_dt = datetime.strptime(check_in, '%Y-%m-%d')
        check_out_dt = datetime.strptime(check_out, '%Y-%m-%d')
        
        check_in_str = check_in_dt.strftime('%Y-%m-%d')
        check_out_str = check_out_dt.strftime('%Y-%m-%d')
        
        # Click date picker
        await self._page.click('.date-picker')
        await asyncio.sleep(0.5)
        
        # Select check-in date
        await self._page.click(f'[data-date="{check_in_str}"]')
        await asyncio.sleep(0.3)
        
        # Select check-out date
        await self._page.click(f'[data-date="{check_out_str}"]')
        await asyncio.sleep(0.5)
        
    async def _extract_flights(self) -> List[Dict[str, Any]]:
        """Extract flight information from search results"""
        flights = []
        
        try:
            # Get all flight cards
            cards = await self._page.query_selector_all('.flight-item')
            
            for card in cards[:20]:  # Limit to 20 results
                try:
                    flight = {}
                    
                    # Airline
                    airline_el = await card.query_selector('.airline-name')
                    if airline_el:
                        flight['airline'] = await airline_el.inner_text()
                        
                    # Flight number
                    flight_no_el = await card.query_selector('.flight-no')
                    if flight_no_el:
                        flight['flight_no'] = await flight_no_el.inner_text()
                        
                    # Departure
                    dep_time_el = await card.query_selector('.departure-time')
                    if dep_time_el:
                        flight['departure_time'] = await dep_time_el.inner_text()
                        
                    dep_airport_el = await card.query_selector('.departure-airport')
                    if dep_airport_el:
                        flight['departure_airport'] = await dep_airport_el.inner_text()
                        
                    # Arrival
                    arr_time_el = await card.query_selector('.arrival-time')
                    if arr_time_el:
                        flight['arrival_time'] = await arr_time_el.inner_text()
                        
                    arr_airport_el = await card.query_selector('.arrival-airport')
                    if arr_airport_el:
                        flight['arrival_airport'] = await arr_airport_el.inner_text()
                        
                    # Duration
                    duration_el = await card.query_selector('.duration')
                    if duration_el:
                        flight['duration'] = await duration_el.inner_text()
                        
                    # Price
                    price_el = await card.query_selector('.price')
                    if price_el:
                        price_text = await price_el.inner_text()
                        flight['price'] = self._parse_price(price_text)
                        
                    # Direct/Stop info
                    stop_el = await card.query_selector('.stop-info')
                    if stop_el:
                        flight['stops'] = await stop_el.inner_text()
                    else:
                        flight['stops'] = '直飞'
                        
                    flights.append(flight)
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Error extracting flights: {e}")
            
        return flights
        
    async def _extract_hotels(self) -> List[Dict[str, Any]]:
        """Extract hotel information from search results"""
        hotels = []
        
        try:
            # Get all hotel cards
            cards = await self._page.query_selector_all('.hotel-item')
            
            for card in cards[:20]:  # Limit to 20 results
                try:
                    hotel = {}
                    
                    # Hotel name
                    name_el = await card.query_selector('.hotel-name')
                    if name_el:
                        hotel['name'] = await name_el.inner_text()
                        
                    # Rating
                    rating_el = await card.query_selector('.rating-score')
                    if rating_el:
                        hotel['rating'] = await rating_el.inner_text()
                        
                    # Star rating
                    star_el = await card.query_selector('.star-rating')
                    if star_el:
                        hotel['stars'] = await star_el.get_attribute('data-stars')
                        
                    # Location
                    location_el = await card.query_selector('.location')
                    if location_el:
                        hotel['location'] = await location_el.inner_text()
                        
                    # Price
                    price_el = await card.query_selector('.price')
                    if price_el:
                        price_text = await price_el.inner_text()
                        hotel['price'] = self._parse_price(price_text)
                        
                    # Distance from center
                    distance_el = await card.query_selector('.distance')
                    if distance_el:
                        hotel['distance'] = await distance_el.inner_text()
                        
                    # Image
                    img_el = await card.query_selector('.hotel-img img')
                    if img_el:
                        hotel['image'] = await img_el.get_attribute('src')
                        
                    hotels.append(hotel)
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Error extracting hotels: {e}")
            
        return hotels
        
    def _parse_price(self, price_text: str) -> Optional[float]:
        """Extract numeric price from text"""
        try:
            # Remove currency symbols and commas
            import re
            match = re.search(r'[\d,]+(?:\.\d+)?', price_text.replace(',', ''))
            if match:
                return float(match.group())
        except:
            pass
        return None
        
    async def login_qr(self) -> Optional[str]:
        """Get QR code for login"""
        await self.init()
        
        try:
            await self.goto(f'{self.base_url}/login')
            await self._page.wait_for_selector('.qr-code', timeout=10000)
            
            qr_data = await self.get_qr_code('.qr-code img')
            return qr_data
            
        except Exception as e:
            print(f"Login error: {e}")
            return None
            
    async def wait_for_login_complete(self) -> bool:
        """Wait for user to complete QR login"""
        return await self.wait_for_login('.user-info', timeout=120)
        
    async def get_orders(self) -> List[Dict[str, Any]]:
        """Get user's orders"""
        await self.init()
        
        try:
            await self.goto(f'{self.base_url}/orders/')
            await self._page.wait_for_selector('.order-list', timeout=10000)
            
            orders = []
            cards = await self._page.query_selector_all('.order-item')
            
            for card in cards:
                try:
                    order = {}
                    
                    order_no_el = await card.query_selector('.order-no')
                    if order_no_el:
                        order['order_no'] = await order_no_el.inner_text()
                        
                    status_el = await card.query_selector('.order-status')
                    if status_el:
                        order['status'] = await status_el.inner_text()
                        
                    total_el = await card.query_selector('.order-total')
                    if total_el:
                        order['total'] = await total_el.inner_text()
                        
                    orders.append(order)
                    
                except Exception:
                    continue
                    
            return orders
            
        except Exception as e:
            print(f"Get orders error: {e}")
            return []
        finally:
            await self.close()
            
    async def monitor_price(self, url: str) -> Dict[str, Any]:
        """Monitor price for a specific product"""
        await self.init()
        
        try:
            await self.goto(url)
            await self._page.wait_for_load_state('networkidle')
            
            # Try to extract price
            price_el = await self._page.query_selector('.price, .current-price')
            price = None
            if price_el:
                price_text = await price_el.inner_text()
                price = self._parse_price(price_text)
                
            # Record in database
            if price:
                self.cache.record_price('trip', url, url, price)
                
            # Get price history
            history = self.cache.get_price_history('trip', url, days=30)
            
            return {
                'current_price': price,
                'url': url,
                'history': history,
                'recorded_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Price monitor error: {e}")
            return {'error': str(e), 'url': url}
        finally:
            await self.close()


def print_flights(flights: List[Dict]):
    """Print flight results in formatted table"""
    if not flights:
        print("未找到航班信息")
        return
        
    print(f"\n找到 {len(flights)} 个航班:\n")
    print(f"{'航空公司':<12} {'航班号':<10} {'出发':<8} {'到达':<8} {'时长':<8} {'价格':<10} {'经停':<8}")
    print("-" * 80)
    
    for flight in flights:
        airline = flight.get('airline', 'N/A')[:10]
        flight_no = flight.get('flight_no', 'N/A')[:8]
        dep = flight.get('departure_time', 'N/A')[:6]
        arr = flight.get('arrival_time', 'N/A')[:6]
        duration = flight.get('duration', 'N/A')[:6]
        price = flight.get('price', 'N/A')
        price_str = f"¥{price}" if price else "N/A"
        stops = flight.get('stops', '直飞')[:6]
        
        print(f"{airline:<12} {flight_no:<10} {dep:<8} {arr:<8} {duration:<8} {price_str:<10} {stops:<8}")


def print_hotels(hotels: List[Dict]):
    """Print hotel results in formatted table"""
    if not hotels:
        print("未找到酒店信息")
        return
        
    print(f"\n找到 {len(hotels)} 家酒店:\n")
    print(f"{'酒店名称':<30} {'评分':<6} {'星级':<6} {'价格':<10} {'位置':<20}")
    print("-" * 90)
    
    for hotel in hotels:
        name = hotel.get('name', 'N/A')[:28]
        rating = hotel.get('rating', 'N/A')[:5]
        stars = hotel.get('stars', 'N/A')[:4]
        price = hotel.get('price', 'N/A')
        price_str = f"¥{price}" if price else "N/A"
        location = hotel.get('location', 'N/A')[:18]
        
        print(f"{name:<30} {rating:<6} {stars:<6} {price_str:<10} {location:<20}")


def print_orders(orders: List[Dict]):
    """Print orders in formatted table"""
    if not orders:
        print("暂无订单")
        return
        
    print(f"\n共 {len(orders)} 个订单:\n")
    print(f"{'订单号':<20} {'状态':<12} {'金额':<12}")
    print("-" * 50)
    
    for order in orders:
        order_no = order.get('order_no', 'N/A')[:18]
        status = order.get('status', 'N/A')[:10]
        total = order.get('total', 'N/A')[:10]
        
        print(f"{order_no:<20} {status:<12} {total:<12}")


async def main():
    parser = argparse.ArgumentParser(
        description='Trip.com (携程) CLI Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s flight 北京 上海 2026-03-15    # 搜索航班
  %(prog)s hotel 上海 2026-03-15 2026-03-17  # 搜索酒店
  %(prog)s order                          # 查看订单
  %(prog)s price <链接>                   # 监控价格
  %(prog)s login                          # 扫码登录
"""
    )
    
    parser.add_argument('command', choices=[
        'flight', 'hotel', 'order', 'price', 'login'
    ], help='要执行的命令')
    
    parser.add_argument('args', nargs='*', help='命令参数')
    parser.add_argument('--headless', action='store_true', help='无头模式运行')
    parser.add_argument('--json', action='store_true', help='JSON格式输出')
    
    args = parser.parse_args()
    
    browser = TripBrowser(headless=args.headless)
    
    if args.command == 'flight':
        if len(args.args) < 3:
            print("用法: trip flight <出发地> <目的地> <日期>")
            print("示例: trip flight 北京 上海 2026-03-15")
            sys.exit(1)
            
        origin, destination, date = args.args[0], args.args[1], args.args[2]
        
        # Validate date format
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            print("错误: 日期格式应为 YYYY-MM-DD")
            sys.exit(1)
            
        print(f"正在搜索 {origin} → {destination} 的航班 ({date})...")
        flights = await browser.search_flights(origin, destination, date)
        
        if args.json:
            print(json.dumps(flights, ensure_ascii=False, indent=2))
        else:
            print_flights(flights)
            
    elif args.command == 'hotel':
        if len(args.args) < 3:
            print("用法: trip hotel <城市> <入住日期> <离店日期>")
            print("示例: trip hotel 上海 2026-03-15 2026-03-17")
            sys.exit(1)
            
        city, check_in, check_out = args.args[0], args.args[1], args.args[2]
        
        # Validate date format
        try:
            datetime.strptime(check_in, '%Y-%m-%d')
            datetime.strptime(check_out, '%Y-%m-%d')
        except ValueError:
            print("错误: 日期格式应为 YYYY-MM-DD")
            sys.exit(1)
            
        print(f"正在搜索 {city} 的酒店 ({check_in} 至 {check_out})...")
        hotels = await browser.search_hotels(city, check_in, check_out)
        
        if args.json:
            print(json.dumps(hotels, ensure_ascii=False, indent=2))
        else:
            print_hotels(hotels)
            
    elif args.command == 'order':
        print("正在获取订单信息...")
        orders = await browser.get_orders()
        
        if args.json:
            print(json.dumps(orders, ensure_ascii=False, indent=2))
        else:
            print_orders(orders)
            
    elif args.command == 'price':
        if len(args.args) < 1:
            print("用法: trip price <链接>")
            sys.exit(1)
            
        url = args.args[0]
        print(f"正在监控价格: {url}")
        result = await browser.monitor_price(url)
        
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            if 'error' in result:
                print(f"错误: {result['error']}")
            else:
                print(f"\n当前价格: ¥{result['current_price']}")
                print(f"\n价格历史 (最近30天):")
                for record in result['history']:
                    print(f"  {record['recorded_at'][:10]}: ¥{record['price']}")
                    
    elif args.command == 'login':
        print("正在获取登录二维码...")
        qr_data = await browser.login_qr()
        
        if qr_data:
            print("\n请使用携程 App 扫描以下二维码登录:")
            print(f"\n[DING:IMAGE]{qr_data}[/DING:IMAGE]\n")
            print("等待登录完成...")
            
            if await browser.wait_for_login_complete():
                print("登录成功!")
                # Save session
                browser.auth.save_session('trip', {'logged_in': True})
            else:
                print("登录超时")
        else:
            print("无法获取二维码")


if __name__ == '__main__':
    asyncio.run(main())
