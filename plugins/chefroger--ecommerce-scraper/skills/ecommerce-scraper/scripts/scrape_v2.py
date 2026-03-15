#!/usr/bin/env python3
"""
电商爬虫脚本 v2 - 支持登录和Cookie管理
"""
import argparse
import json
import time
import os
import sys
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ 需要安装Playwright: pip install playwright && playwright install chromium")
    sys.exit(1)


class EcommerceScraper:
    """电商爬虫类 - 支持登录"""
    
    def __init__(self, headless=False):  # 默认非无头，方便扫码
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.cookies_file = 'data/cookies.json'
    
    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ]
        )
        # 加载保存的cookie
        self._load_cookies()
        return self
    
    def __exit__(self, *args):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def _load_cookies(self):
        """加载保存的cookie"""
        if os.path.exists(self.cookies_file):
            print(f"📂 加载Cookie: {self.cookies_file}")
    
    def _save_cookies(self, cookies):
        """保存cookie到文件"""
        os.makedirs('data', exist_ok=True)
        with open(self.cookies_file, 'w') as f:
            json.dump(cookies, f)
        print(f"💾 Cookie已保存到 {self.cookies_file}")
    
    def create_page(self, user_agent=None):
        """创建新页面"""
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='zh-CN',
            timezone_id='Asia/Shanghai',
            user_agent=user_agent or 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # 加载cookie
        if os.path.exists(self.cookies_file):
            with open(self.cookies_file, 'r') as f:
                cookies = json.load(f)
                self.context.add_cookies(cookies)
                print("✅ Cookie已加载")
        
        page = self.context.new_page()
        
        # 注入反检测脚本
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en-US', 'en']});
            window.chrome = {runtime: {}};
        """)
        
        return page
    
    def login_jd(self, page):
        """登录京东"""
        print("📱 打开京东登录页...")
        page.goto('https://passport.jd.com/new/login.aspx', wait_until='networkidle', timeout=60000)
        
        print("⚠️ 请扫码登录！")
        print("⏳ 等待登录成功...")
        
        # 等待登录成功 (检测用户名出现)
        try:
            page.wait_for_selector('#username', timeout=120000)  # 2分钟等待扫码
            # 如果找到用户名元素，说明已登录
            print("✅ 登录成功！")
            
            # 保存cookie
            cookies = self.context.cookies()
            self._save_cookies(cookies)
            return True
        except:
            # 也可能是直接跳转到首页了
            page.goto('https://www.jd.com/', wait_until='networkidle')
            if 'jd.com' in page.url:
                cookies = self.context.cookies()
                self._save_cookies(cookies)
                print("✅ 登录成功！")
                return True
        
        print("❌ 登录超时")
        return False
    
    def login_taobao(self, page):
        """登录淘宝"""
        print("📱 打开淘宝登录页...")
        page.goto('https://login.taobao.com/', wait_until='networkidle', timeout=60000)
        
        print("⚠️ 请扫码登录！")
        print("⏳ 等待登录成功...")
        
        try:
            # 等待淘宝会员名出现
            page.wait_for_selector('.member-name, .site-nav-login', timeout=120000)
            print("✅ 登录成功！")
            cookies = self.context.cookies()
            self._save_cookies(cookies)
            return True
        except:
            print("❌ 登录超时")
            return False
    
    def scrape_jd(self, keyword, max_pages=3):
        """爬取京东搜索结果"""
        page = self.create_page()
        
        # 构造搜索URL
        search_url = f"https://search.jd.com/Search?keyword={keyword}&enc=utf-8"
        print(f"🔍 搜索: {keyword}")
        
        results = []
        
        for page_num in range(1, max_pages + 1):
            url = f"{search_url}&page={page_num*2-1}"  # JD页面是奇数
            print(f"📄 爬取第 {page_num} 页...")
            
            page.goto(url, wait_until='networkidle', timeout=60000)
            time.sleep(2)
            
            # 等待商品加载
            try:
                page.wait_for_selector('.gl-item', timeout=10000)
            except:
                print("⚠️ 页面可能需要登录")
                break
            
            # 提取商品
            items = page.query_selector_all('.gl-item')
            print(f"   找到 {len(items)} 个商品")
            
            for item in items[:30]:
                try:
                    # 尝试多种选择器
                    title_el = item.query_selector('.p-name em, .p-name a, .gl-name a')
                    price_el = item.query_selector('.p-price strong i, .price')
                    shop_el = item.query_selector('.p-shop a, .shop-name')
                    
                    product = {
                        'title': title_el.inner_text().strip() if title_el else '',
                        'price': price_el.inner_text().strip() if price_el else '',
                        'shop': shop_el.inner_text().strip() if shop_el else '',
                    }
                    
                    if product['title']:
                        results.append(product)
                except:
                    continue
            
            time.sleep(random.uniform(1, 3))
        
        return results
    
    def scrape_taobao(self, keyword, max_pages=3):
        """爬取淘宝搜索结果"""
        page = self.create_page()
        
        # 淘宝搜索URL
        search_url = f"https://s.taobao.com/search?q={keyword}&imgfile=&initiative_id=staobaoz&ie=utf8"
        print(f"🔍 搜索淘宝: {keyword}")
        
        results = []
        
        for page_num in range(1, max_pages + 1):
            url = f"{search_url}&page={page_num}"
            print(f"📄 爬取第 {page_num}/{max_pages} 页...")
            
            page.goto(url, wait_until='networkidle', timeout=60000)
            time.sleep(3)
            
            # 淘宝商品选择器 (多种尝试)
            selectors = [
                '.item-wrap',
                '.item',
                '[data-category="auction"]',
                '.shop-hp-datalazy-item',
            ]
            
            items = []
            for sel in selectors:
                items = page.query_selector_all(sel)
                if len(items) > 5:
                    print(f"   使用选择器: {sel}, 找到 {len(items)} 个")
                    break
            
            for item in items[:30]:
                try:
                    # 淘宝结构复杂，多种选择器尝试
                    title = ''
                    for title_sel in ['.title', '.item-title', 'a.J_ClickStat', 'img']:
                        el = item.query_selector(title_sel)
                        if el:
                            if title_sel == 'img':
                                title = el.get_attribute('alt') or ''
                            else:
                                title = el.inner_text().strip()
                            if title:
                                break
                    
                    price = ''
                    for price_sel in ['.price', '.deal-price', '.real-price']:
                        el = item.query_selector(price_sel)
                        if el:
                            price = el.inner_text().strip()
                            if price:
                                break
                    
                    shop = ''
                    for shop_sel in ['.shop', '.shop-name', '.seller-nick']:
                        el = item.query_selector(shop_sel)
                        if el:
                            shop = el.inner_text().strip()
                            if shop:
                                break
                    
                    # 获取链接
                    link = ''
                    link_el = item.query_selector('a.J_ClickStat')
                    if link_el:
                        link = link_el.get_attribute('href') or ''
                    
                    if title:
                        results.append({
                            'title': title,
                            'price': price,
                            'shop': shop,
                            'link': link
                        })
                except Exception as e:
                    continue
            
            # 随机延迟防封
            time.sleep(random.uniform(2, 4))
        
        return results


import random

def main():
    parser = argparse.ArgumentParser(description="电商爬虫 - 支持登录")
    subparsers = parser.add_subparsers(dest='command')
    
    # 登录命令
    login_parser = subparsers.add_parser('login', help='登录电商平台')
    login_parser.add_argument('--platform', '-p', choices=['jd', 'taobao', 'pdd'], required=True)
    login_parser.add_argument('--headless', action='store_true', help='无头模式(不推荐)')
    
    # 爬取命令
    scrape_parser = subparsers.add_parser('scrape', help='爬取商品')
    scrape_parser.add_argument('--platform', '-p', choices=['jd', 'taobao', 'pdd'], required=True)
    scrape_parser.add_argument('--keyword', '-k', required=True, help='搜索关键词')
    scrape_parser.add_argument('--max-pages', '-m', type=int, default=2, help='最大页数')
    scrape_parser.add_argument('--output', '-o', help='输出文件')
    scrape_parser.add_argument('--headless', action='store_true', help='无头模式')
    
    args = parser.parse_args()
    
    if args.command == 'login':
        with EcommerceScraper(headless=getattr(args, 'headless', False)) as scraper:
            page = scraper.create_page()
            if args.platform == 'jd':
                scraper.login_jd(page)
            elif args.platform == 'taobao':
                scraper.login_taobao(page)
            elif args.platform == 'pdd':
                print("⚠️ 拼多多登录需要微信/QQ扫码")
                print("   请手动登录后按Enter...")
                input()
    
    elif args.command == 'scrape':
        headless = getattr(args, 'headless', True)  # 默认无头
        
        with EcommerceScraper(headless=headless) as scraper:
            if args.platform == 'jd':
                results = scraper.scrape_jd(args.keyword, args.max_pages)
            elif args.platform == 'taobao':
                results = scraper.scrape_taobao(args.keyword, args.max_pages)
            elif args.platform == 'pdd':
                # 拼多多需要特殊处理
                print("⚠️ 拼多多建议使用非无头模式")
                results = []
            
            print(f"\n📊 共获取 {len(results)} 个商品")
            
            # 显示前10个
            for i, p in enumerate(results[:10], 1):
                print(f"{i}. {p.get('title', '')[:40]}")
                print(f"   💰 {p.get('price', '')} | 🏪 {p.get('shop', '')}")
            
            # 保存
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                print(f"\n💾 已保存到 {args.output}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
