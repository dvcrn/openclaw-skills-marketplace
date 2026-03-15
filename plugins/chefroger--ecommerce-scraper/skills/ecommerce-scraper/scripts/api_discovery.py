#!/usr/bin/env python3
"""
隐藏API发现脚本
帮助发现电商网站的隐藏API端点
"""
import argparse
import sys

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ 需要安装Playwright: pip install playwright && playwright install chromium")
    sys.exit(1)


def discover_api(url):
    """发现隐藏API"""
    api_endpoints = []
    
    print(f"🔍 扫描: {url}")
    print("="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='zh-CN',
        )
        
        page = context.new_page()
        
        # 收集API
        def handle_response(response):
            url = response.url
            # 只关注API相关URL
            keywords = ['api', 'json', 'data', '/v1/', '/v2/', 'ajax', 'product', 'list', 'item']
            if any(k in url.lower() for k in keywords):
                if url not in api_endpoints and 'http' in url:
                    api_endpoints.append(url)
        
        page.on("response", handle_response)
        
        try:
            print("📡 加载页面...")
            page.goto(url, wait_until="networkidle", timeout=30000)
            
            # 等待一下让更多请求发出
            page.wait_for_timeout(2000)
            
        except Exception as e:
            print(f"❌ 页面加载失败: {e}")
        
        # 尝试找 __NEXT_DATA__
        print("\n📦 检查预渲染数据...")
        try:
            next_data = page.evaluate("""
                () => {
                    // 查找各种预渲染数据
                    const candidates = [
                        document.getElementById('__NEXT_DATA__'),
                        document.getElementById('__INITIAL_STATE__'),
                        document.getElementById('__APP_STATE__'),
                        document.querySelector('script[type="application/json"]'),
                        document.querySelector('script[id*="data"]'),
                    ];
                    
                    for (const el of candidates) {
                        if (el) {
                            return {
                                id: el.id || el.type || 'unknown',
                                content: el.textContent ? el.textContent.substring(0, 500) : null
                            };
                        }
                    }
                    return null;
                }
            """)
            
            if next_data and next_data.get('content'):
                print(f"   ✅ 发现 {next_data['id']}")
                print(f"   📝 {next_data['content'][:200]}...")
            else:
                print("   ⚠️ 未发现预渲染数据")
        except Exception as e:
            print(f"   ⚠️ 检查失败: {e}")
        
        # 尝试滚动页面触发更多加载
        print("\n📜 滚动页面触发懒加载...")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1500)
        
        browser.close()
    
    # 去重和分类
    print(f"\n🔍 发现 {len(api_endpoints)} 个API端点:")
    print("="*60)
    
    # 分类
    products_api = []
    search_api = []
    other_api = []
    
    for url in api_endpoints:
        if 'product' in url.lower() or 'item' in url.lower() or 'goods' in url.lower():
            products_api.append(url)
        elif 'search' in url.lower() or 'list' in url.lower():
            search_api.append(url)
        else:
            other_api.append(url)
    
    if products_api:
        print("\n🛍️ 商品API:")
        for url in products_api[:10]:
            print(f"   {url[:100]}")
    
    if search_api:
        print("\n🔎 搜索API:")
        for url in search_api[:10]:
            print(f"   {url[:100]}")
    
    if other_api:
        print("\n📋 其他API:")
        for url in other_api[:10]:
            {print(f"   {url[:100]}")
    
    return api_endpoints


def main():
    parser = argparse.ArgumentParser(description="隐藏API发现工具")
    parser.add_argument('--url', '-u', required=True, help='目标URL')
    parser.add_argument('--output', '-o', help='保存到文件')
    
    args = parser.parse_args()
    
    apis = discover_api(args.url)
    
    if args.output:
        import json
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(apis, f, ensure_ascii=False, indent=2)
        print(f"\n💾 已保存到 {args.output}")


if __name__ == '__main__':
    main()
