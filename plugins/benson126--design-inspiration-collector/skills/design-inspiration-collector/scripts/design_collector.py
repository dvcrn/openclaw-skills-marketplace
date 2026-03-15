#!/usr/bin/env python3
"""
多平台设计灵感收集器
从 Behance、Dribbble、Pinterest 收集设计灵感并整理成飞书文档
"""

import os
import sys
import json
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# 配置
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "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")
OUTPUT_DIR = "/root/.openclaw/workspace/design_inspirations"

def search_platform(query, platform, max_results=10):
    """
    搜索单个平台
    
    Args:
        query: 搜索主题
        platform: 平台名称 (pinterest, dribbble, behance)
        max_results: 最大结果数
    
    Returns:
        list: 搜索结果列表
    """
    try:
        from tavily import TavilyClient
    except ImportError:
        print("Error: tavily-python not installed")
        return []
    
    site_map = {
        "pinterest": "site:pinterest.com",
        "dribbble": "site:dribbble.com", 
        "behance": "site:behance.net"
    }
    
    search_query = f"{site_map[platform]} {query} ui ux design 2026"
    
    try:
        client = TavilyClient(api_key=TAVILY_API_KEY)
        response = client.search(
            query=search_query,
            search_depth="basic",
            max_results=max_results
        )
        return response.get('results', [])
    except Exception as e:
        print(f"搜索 {platform} 失败: {e}")
        return []

def screenshot_url(url, output_path):
    """
    使用 Playwright 截图
    
    Args:
        url: 网页 URL
        output_path: 保存路径
    
    Returns:
        bool: 是否成功
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Error: playwright not installed")
        return False
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
            )
            page = browser.new_page(viewport={'width': 1920, 'height': 1200})
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            page.wait_for_timeout(3000)
            page.screenshot(path=output_path, full_page=False)
            browser.close()
            return True
    except Exception as e:
        print(f"截图失败 {url}: {e}")
        return False

def collect_all_platforms(topic, max_per_platform=10):
    """
    从三个平台收集内容
    
    Args:
        topic: 搜索主题
        max_per_platform: 每个平台最大结果数
    
    Returns:
        dict: 按平台分类的结果
    """
    results = {
        "pinterest": [],
        "dribbble": [],
        "behance": []
    }
    
    print(f"\n🔍 开始搜索主题: {topic}")
    print("=" * 50)
    
    for platform in results.keys():
        print(f"\n📡 搜索 {platform.upper()}...")
        search_results = search_platform(topic, platform, max_per_platform)
        
        # 按相关度排序并取前 5 条
        sorted_results = sorted(search_results, key=lambda x: x.get('score', 0), reverse=True)[:5]
        results[platform] = sorted_results
        
        print(f"   找到 {len(sorted_results)} 条结果")
    
    return results

def screenshot_all_results(results, output_dir):
    """
    对所有结果截图
    
    Args:
        results: 搜索结果
        output_dir: 输出目录
    
    Returns:
        dict: 截图路径映射
    """
    screenshots = {}
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n📸 开始截图...")
    print("=" * 50)
    
    total = sum(len(items) for items in results.values())
    current = 0
    
    for platform, items in results.items():
        for i, item in enumerate(items, 1):
            current += 1
            url = item.get('url', '')
            if not url:
                continue
                
            screenshot_path = os.path.join(output_dir, f"{platform}_{i:02d}.png")
            print(f"   [{current}/{total}] 截图 {platform} #{i}...", end=" ")
            
            success = screenshot_url(url, screenshot_path)
            if success:
                screenshots[url] = screenshot_path
                print("✅")
            else:
                print("❌")
                screenshots[url] = None
    
    return screenshots

def generate_feishu_markdown(topic, results, screenshots, trend_summary=""):
    """
    生成飞书文档 Markdown 内容
    
    Args:
        topic: 主题
        results: 搜索结果
        screenshots: 截图路径
        trend_summary: 趋势摘要
    
    Returns:
        str: Markdown 内容
    """
    now = datetime.now()
    date_str = now.strftime("%Y年%m月%d日 %H:%M")
    
    md = f"""# {topic} 设计灵感收集

> 收集时间：{date_str}
> 来源：Behance、Dribbble、Pinterest
> 总计：{sum(len(items) for items in results.values())} 条精选内容

---

## 📊 趋势概览

{trend_summary or "暂无趋势分析"}

---

"""
    
    # 按平台分类输出
    platform_icons = {
        "pinterest": "🎨",
        "dribbble": "🎯",
        "behance": "💎"
    }
    
    for platform, items in results.items():
        icon = platform_icons.get(platform, "📌")
        md += f"""## {icon} {platform.upper()} 精选 ({len(items)}条)

"""
        
        for i, item in enumerate(items, 1):
            title = item.get('title', 'Untitled')[:50]
            url = item.get('url', '')
            score = item.get('score', 0)
            content = item.get('content', '')[:100]
            screenshot_path = screenshots.get(url)
            
            md += f"""### {i}. {title}

- **链接**：{url}
- **相关度**：{score:.1%}
- **描述**：{content}...
"""
            
            if screenshot_path:
                md += f"- **截图**：见下方或附件\n\n"
            else:
                md += f"- **截图**：❌ 截图失败\n\n"
        
        md += "---\n\n"
    
    # 搜索关键词
    md += f"""## 🔍 搜索关键词

在平台搜索这些词可以找到更多：

- `{topic} ui design`
- `{topic} app ui`
- `{topic} dashboard`
- `{topic} mobile`

---

## 📌 相关方向推荐

需要我帮你搜索以下细分主题吗？

1. **{topic} Dashboard** - 仪表盘设计
2. **{topic} Mobile App** - 移动端界面
3. **{topic} Web Design** - 网页设计
4. **{topic} Components** - 组件设计
5. **{topic} Dark Mode** - 暗黑模式

---

*文档由 AI 助手自动生成*
"""
    
    return md

def main():
    if len(sys.argv) < 2:
        print("Usage: python design_collector.py <topic> [max_per_platform]")
        print("Example: python design_collector.py 'healthcare app' 5")
        sys.exit(1)
    
    topic = sys.argv[1]
    max_per_platform = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    # 创建输出目录
    now = datetime.now()
    folder_name = f"{topic.replace(' ', '_')}_{now.strftime('%Y%m%d_%H%M%S')}"
    output_dir = os.path.join(OUTPUT_DIR, folder_name)
    
    # 1. 搜索三个平台
    results = collect_all_platforms(topic, max_per_platform)
    
    # 2. 截图
    screenshots = screenshot_all_results(results, output_dir)
    
    # 3. 生成 Markdown
    markdown = generate_feishu_markdown(topic, results, screenshots)
    
    # 4. 保存到本地
    md_path = os.path.join(output_dir, "report.md")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    print(f"\n✅ 完成！")
    print(f"   文件夹：{output_dir}")
    print(f"   Markdown：{md_path}")
    print(f"   截图数量：{sum(1 for v in screenshots.values() if v)}")
    
    # 5. 输出 JSON 供后续使用
    output_data = {
        "topic": topic,
        "folder": output_dir,
        "markdown_file": md_path,
        "results": results,
        "screenshots": screenshots,
        "summary": {
            "total": sum(len(items) for items in results.values()),
            "screenshots_success": sum(1 for v in screenshots.values() if v),
            "screenshots_failed": sum(1 for v in screenshots.values() if not v)
        }
    }
    
    json_path = os.path.join(output_dir, "data.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"   数据文件：{json_path}")
    
    return output_data

if __name__ == "__main__":
    main()
