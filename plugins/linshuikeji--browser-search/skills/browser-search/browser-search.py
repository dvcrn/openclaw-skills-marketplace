#!/usr/bin/env python3
"""
Browser Search 技能
使用本地浏览器进行自动化搜索和内容提取

支持搜索引擎：Bing, Google, Baidu, DuckDuckGo
无需 API 配置，直接使用本地浏览器
"""

import os
import sys
import json
import time
import urllib.parse
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# 配置
DEFAULT_TIMEOUT = 30000  # 30 秒超时
DEFAULT_MAX_RESULTS = 10
SUPPORTED_ENGINES = ["bing", "google", "baidu", "duckduckgo"]

class BrowserSearch:
    def __init__(self):
        self.engine = "bing"
        self.search_url = ""
        self.query_selector = "h2"  # 使用 h2 作为主要选择器
        self.output_file: Optional[str] = None
        self.results: List[Dict] = []
        
    def set_engine(self, engine: str) -> None:
        """设置搜索引擎"""
        if engine not in SUPPORTED_ENGINES:
            print(f"⚠️ 不支持的搜索引擎：{engine}")
            print(f"支持的引擎：{', '.join(SUPPORTED_ENGINES)}")
            return
        self.engine = engine
        configs = {
            "bing": "https://www.bing.com/search?q={query}",
            "google": "https://www.google.com/search?q={query}",
            "baidu": "https://www.baidu.com/s?wd={query}",
            "duckduckgo": "https://duckduckgo.com/?q={query}"
        }
        self.search_url = configs.get(engine, configs["bing"])
    
    def search(self, query: str, max_results: int = DEFAULT_MAX_RESULTS, timeout: int = DEFAULT_TIMEOUT, output_file: Optional[str] = None) -> Dict:
        """执行搜索"""
        # 清洗搜索词：去掉多余空格和特殊字符
        clean_query = " ".join(query.split())
        
        self.results = []
        self.output_file = output_file
        
        try:
            with sync_playwright() as p:
                # 启动浏览器
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    viewport={"width": 1280, "height": 720},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                page = context.new_page()
                
                # 构建搜索 URL（正确编码空格）
                encoded_query = urllib.parse.quote(clean_query, safe="+")
                search_url = self.search_url.format(query=encoded_query)
                
                print(f"\n🔍 正在搜索：{clean_query}")
                print(f"🌐 搜索引擎：{self.engine}")
                print(f"📍 搜索 URL: {search_url}")
                
                # 打开搜索页面
                try:
                    page.goto(search_url, wait_until="domcontentloaded", timeout=timeout)
                    time.sleep(2)  # 等待内容加载
                except Exception as goto_error:
                    print(f"❌ 打开页面失败：{str(goto_error)[:100]}")
                    return {"error": "page_open_failed", "message": str(goto_error)}
                
                # 获取页面快照（用于调试）
                page_snapshot = page.content()
                
                # 提取搜索结果
                results = page.query_selector_all(self.query_selector)
                
                print(f"\n📊 找到 {len(results)} 个搜索结果")
                
                if len(results) == 0:
                    print("⚠️ 没有找到结果，尝试备用选择器...")
                    # 尝试其他选择器
                    alt_selectors = ["h3 a", "h2 a", "li a", "a"]
                    for selector in alt_selectors:
                        try:
                            alt_results = page.query_selector_all(selector)
                            if len(alt_results) > 0:
                                print(f"✓ 使用备用选择器 '{selector}' 找到了 {len(alt_results)} 个结果")
                                results = alt_results
                                break
                        except:
                            continue
                
                # 提取结果详情
                extracted_count = 0
                for result in results[:max_results]:
                    try:
                        # 获取标题和链接
                        heading = result.query_selector("h2")
                        link = result.query_selector("h2 a") or result.query_selector("a")
                        
                        if link:
                            title = link.text_content().strip()
                            url = link.get_attribute("href")
                            
                            if title and url:
                                # 尝试获取摘要
                                snippet = ""
                                try:
                                    snippet_elem = result.query_selector("p") or result.query_selector_all("p")[0]
                                    if snippet_elem:
                                        snippet = snippet_elem.text_content().strip()[:200]
                                except:
                                    pass
                                
                                self.results.append({
                                    "title": title,
                                    "url": url,
                                    "snippet": snippet,
                                    "engine": self.engine
                                })
                                extracted_count += 1
                                print(f"  ✓ 提取：{title[:60]}...")
                                
                    except Exception as e:
                        print(f"  ⚠️ 跳过：{str(e)[:50]}")
                        continue
                
                print(f"\n📝 成功提取 {extracted_count} 条结果")
                
                # 关闭浏览器
                browser.close()
                
                # 生成结果
                response = {
                    "query": clean_query,
                    "engine": self.engine,
                    "count": len(self.results),
                    "results": self.results
                }
                
                # 保存到文件（如果指定）
                if self.output_file:
                    try:
                        with open(self.output_file, 'w', encoding='utf-8') as f:
                            json.dump(response, f, ensure_ascii=False, indent=2)
                        print(f"\n💾 结果已保存到：{self.output_file}")
                    except Exception as e:
                        print(f"❌ 保存文件失败：{str(e)}")
                
                return response
                
        except PlaywrightTimeout:
            print("\n⚠️ 浏览器超时，请稍后重试或重启网关")
            return {
                "error": "timeout",
                "message": "搜索超时",
                "results": []
            }
        except Exception as e:
            print(f"\n❌ 搜索错误：{str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "error": str(e),
                "results": []
            }

def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("🔎 Browser Search - 浏览器自动化搜索")
        print("\n用法：browser-search.py \"搜索词\" [选项]")
        print("\n选项:")
        print(f"  --engine <{', '.join(SUPPORTED_ENGINES)}>  搜索引擎（默认：bing）")
        print("  --output <file>                           输出文件（JSON 格式）")
        print("  --max <n>                                 结果数量（默认：10）")
        print("  --help                                    显示帮助")
        sys.exit(1)
    
    # 解析参数
    args = sys.argv[1:]
    engine = "bing"
    output_file = None
    max_results = DEFAULT_MAX_RESULTS
    
    i = 0
    while i < len(args):
        if args[i] == "--engine" and i + 1 < len(args):
            engine = args[i + 1]
            i += 2
        elif args[i] == "--output" and i + 1 < len(args):
            output_file = args[i + 1]
            i += 2
        elif args[i] == "--max" and i + 1 < len(args):
            try:
                max_results = int(args[i + 1])
                i += 2
            except ValueError:
                print(f"❌ 无效的 --max 参数：{args[i + 1]}")
                sys.exit(1)
        elif args[i] == "--help":
            main()
            sys.exit(0)
        else:
            # 搜索词：收集所有非选项参数
            query_parts = []
            while i < len(args) and not (args[i].startswith("--")):
                query_parts.append(args[i])
                i += 1
            query = " ".join(query_parts)
            break
    
    if not query:
        print("❌ 需要提供搜索词")
        sys.exit(1)
    
    # 执行搜索
    search_engine = BrowserSearch()
    search_engine.set_engine(engine)
    search_engine.output_file = output_file
    
    response = search_engine.search(query, max_results=max_results)
    
    # 输出结果
    print("\n" + "=" * 70)
    print(f"搜索结果 ({response.get('count', 0)} 条)")
    print("=" * 70)
    
    if "error" in response:
        print(f"❌ 错误：{response['error']}")
        if "message" in response:
            print(f"详情：{response['message']}")
    else:
        for i, result in enumerate(response["results"], 1):
            print(f"\n{i}. {result['title']}")
            print(f"   🔗 {result['url']}")
            if result['snippet']:
                print(f"   📝 {result['snippet'][:150]}...")
    
    print("\n" + "=" * 70)
    print(f"📊 共提取 {len(response.get('results', []))} 条结果")

if __name__ == "__main__":
    main()
