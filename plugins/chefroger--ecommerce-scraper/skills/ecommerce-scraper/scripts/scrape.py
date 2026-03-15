#!/usr/bin/env python3
"""
电商爬虫脚本
支持: JavaScript渲染、Cloudflare绕过、隐藏API发现、分页爬取
"""
import argparse
import json
import time
import random
import sys
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ 需要安装Playwright: pip install playwright && playwright install chromium")
    sys.exit(1)


SELECTORS = {
    'jd': {
        'product': '.gl-item',
        'title': '.p-name em',
        'price': '.p-price strong i',
        'shop': '.p-shop',
    },
    'taobao': {
        'product': '.item',
        'title': '.title',
        'price': '.price',
        'shop': '.shop',
    },
    'amazon': {
        'product': '[data-component-type="s-search-result"]',
        'title': 'h2 a span',
        'price': '.a-price-whole',
    },
    'generic': {
        'product': '[class*="product"], [class*="item"], li[class*="item"], div[class*="goods"]',
        'title': '[class*="title"], h2, h3, a[class*="title"]',
        'price': '[class*="price"], [class*="cost"], [class*="amount"], span[data-price]',
        'shop': '[class*="shop"], [class*="seller"], [class*="store"]',
        'link': 'a[href]',
        'image': 'img[src]',
    }
}


class EcommerceScraper:
    """电商爬虫类"""
    
    def __init__(self, headless=True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
    
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
        return self
    
    def __exit__(self, *args):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def create_page(self, user_agent=None):
        """创建新页面"""
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='zh-CN',
            timezone_id='Asia/Shanghai',
            user_agent=user_agent or 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = self.context.new_page()
        
        # 注入反检测脚本
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en-US', 'en']});
            window.chrome = {runtime: {}};
        """)
        
        return page
    
    def detect_platform(self, url):
        """检测电商平台"""
        if 'jd.com' in url or 'jd.hk' in url:
            return 'jd'
        elif 'taobao.com' in url:
            return 'taobao'
        elif 'amazon.' in url:
            return 'amazon'
        return 'generic'
    
    def extract_products(self, page, platform='generic'):
        """提取商品数据"""
        products = []
        selectors = SELECTORS.get(platform, SELECTORS['generic'])
        
        items = page.query_selector_all(selectors['product'])
        
        for item in items:
            try:
                product = {}
                
                # 标题
                title_el = item.query_selector(selectors['title'])
                product['title'] = title_el.inner_text().strip() if title_el else ''
                
                # 价格
                price_el = item.query_selector(selectors['price'])
                product['price'] = price_el.inner_text().strip() if price_el else ''
                
                # 店铺
                if 'shop' in selectors:
                    shop_el = item.query_selector(selectors['shop'])
                    product['shop'] = shop_el.inner_text().strip() if shop_el else ''
                
                # 链接
                link_el = item.query_selector(selectors.get('link', 'a'))
                if link_el:
                    href = link_el.get_attribute('href')
                    product['link'] = href if href else ''
                
                # 图片
                img_el = item.query_selector(selectors.get('image', 'img'))
                if img_el:
                    src = img_el.get_attribute('src') or img_el.get_attribute('data-src') or ''
                    product['image'] = src
                
                if product.get('title'):
                    products.append(product)
                    
            except Exception as e:
                continue
        
        return products
    
    def has_next_page(self, page, page_num):
        """检查是否有下一页"""
        selectors = [
            f'a:has-text("{page_num + 1}")',
            f'button:has-text("{page_num + 1}")',
            'a:has-text("下一页")',
            'button:has-text("下一页")',
            'a[class*="next"]',
            'button[class*="next"]',
        ]
        
        for sel in selectors:
            if page.query_selector(sel):
                return True
        return False
    
    def scrape(self, url, max_pages=1, wait_time=2):
        """爬取页面"""
        platform = self.detect_platform(url)
        all_products = []
        
        page = self.create_page()
        
        for page_num in range(1, max_pages + 1):
            if max_pages > 1:
                if '?' in url:
                    page_url = f"{url}&page={page_num}"
                else:
                    page_url = f"{url}?page={page_num}"
            else:
                page_url = url
            
            print(f"📄 爬取第 {page_num}/{max_pages} 页...")
            
            try:
                page.goto(page_url, wait_until="networkidle", timeout=30000)
                time.sleep(wait_time)
                
                products = self.extract_products(page, platform)
                print(f"   ✅ 获取 {len(products)} 个商品")
                
                if not products:
                    break
                
                for p in products:
                    p['collected_at'] = datetime.now().isoformat()
                
                all_products.extend(products)
                
                if max_pages > 1 and not self.has_next_page(page, page_num):
                    print("   ✅ 已到达最后一页")
                    break
                    
            except Exception as e:
                print(f"   ❌ 错误: {e}")
                break
        
        return all_products
    
    def discover_apis(self, url):
        """发现隐藏API"""
        api_endpoints = []
        page = self.create_page()
        
        def handle_response(response):
            url = response.url
            if 'api' in url.lower() or 'json' in url.lower() or 'data' in url.lower():
                if url not in api_endpoints and 'http' in url:
                    api_endpoints.append(url)
        
        page.on("response", handle_response)
        
        try:
            page.goto(url, wait_until="networkidle", timeout=30000)
            time.sleep(2)
        except Exception as e:
            print(f"页面加载失败: {e}")
        
        # 滚动触发懒加载
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1500)
        
        print(f"\n🔍 发现 {len(api_endpoints)} 个API端点:")
        for url in api_endpoints[:15]:
            print(f"   {url[:100]}")
        
        return api_endpoints


def scrape_page(url, headless=True, wait_time=2):
    """爬取单个页面"""
    with EcommerceScraper(headless=headless) as scraper:
        return scraper.scrape(url, max_pages=1, wait_time=wait_time)


def scrape_pagination(url, max_pages=5, headless=True, output=None):
    """分页爬取"""
    with EcommerceScraper(headless=headless) as scraper:
        products = scraper.scrape(url, max_pages=max_pages)
    
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        print(f"\n💾 已保存到 {output}")
    
    return products


def discover_api(url):
    """发现隐藏API"""
    with EcommerceScraper() as scraper:
        return scraper.discover_apis(url)


def main():
    parser = argparse.ArgumentParser(description="电商爬虫工具")
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # scrape 命令
    scrape_parser = subparsers.add_parser('scrape', help='爬取页面')
    scrape_parser.add_argument('--url', '-u', required=True, help='目标URL')
    scrape_parser.add_argument('--max-pages', '-m', type=int, default=1, help='最大页数')
    scrape_parser.add_argument('--output', '-o', help='输出文件')
    scrape_parser.add_argument('--headless', action='store_true', default=True, help='无头模式')
    scrape_parser.add_argument('--visible', action='store_false', dest='headless', help='显示浏览器')
    
    # api 命令
    api_parser = subparsers.add_parser('api', help='发现隐藏API')
    api_parser.add_argument('--url', '-u', required=True, help='目标URL')
    
    args = parser.parse_args()
    
    if args.command == 'scrape':
        if args.max_pages == 1:
            products = scrape_page(args.url, headless=args.headless)
            print(f"\n✅ 获取 {len(products)} 个商品:")
            for p in products[:5]:
                print(f"   - {p.get('title', '')[:50]}: {p.get('price', '')}")
        else:
            products = scrape_pagination(args.url, max_pages=args.max_pages, 
                                         headless=args.headless, output=args.output)
            print(f"\n📊 总共获取 {len(products)} 个商品")
    
    elif args.command == 'api':
        discover_api(args.url)
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
