#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音视频数据采集（参数化版本）
用法：
  python3 collect_videos.py [关键词] [采集数量] [工作目录]

示例：
  python3 collect_videos.py 女性成长 100 /tmp/douyin_output
  python3 collect_videos.py 职场提升 50 .

依赖：douyin_session.json 已存在于工作目录（先跑 douyin_login.py 获取）
"""

import asyncio, json, time, random, urllib.parse, sys
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

# ── 参数：可通过命令行覆盖 ────────────────────────────────
KEYWORD      = sys.argv[1] if len(sys.argv) > 1 else "女性成长"
TOTAL        = int(sys.argv[2]) if len(sys.argv) > 2 else 100
WORK_DIR     = Path(sys.argv[3]).resolve() if len(sys.argv) > 3 else Path(".").resolve()

SAVE_DIR     = WORK_DIR
SESSION_FILE = SAVE_DIR / "douyin_session.json"
RAW_FILE     = SAVE_DIR / "douyin_raw_data.json"

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

async def collect_videos(ctx, page):
    enc_kw = urllib.parse.quote(KEYWORD)
    collected = []
    fresh = []

    async def on_resp(resp):
        url = resp.url
        if "search/item" in url and "douyin.com" in url:
            try:
                body  = await resp.json()
                items = body.get("aweme_list") or []
                nil   = body.get("search_nil_info", {}).get("search_nil_type", "ok")
                hm    = body.get("has_more", 0)
                log(f"  ↳ API 返回: {len(items)} 条  nil={nil}  has_more={hm}")
                if items:
                    fresh.extend(items)
            except Exception as e:
                log(f"  ↳ API 解析错误: {e}")

    page.on("response", on_resp)

    for batch_no in range(1, 11):
        log(f"\n── 第 {batch_no}/10 批 ──────────────────")
        fresh.clear()

        if batch_no == 1:
            log(f"导航到搜索页: {KEYWORD}")
            await page.goto(
                f"https://www.douyin.com/search/{enc_kw}?type=video",
                wait_until="domcontentloaded", timeout=30000,
            )
            await asyncio.sleep(8)
        else:
            # 滚动加载更多
            log("滚动加载更多...")
            for _ in range(8):
                await page.evaluate("window.scrollBy(0, window.innerHeight * 1.5)")
                await asyncio.sleep(1.0)
            await asyncio.sleep(3)

        if fresh:
            # 去重
            exist_ids = {v.get("aweme_id","") for v in collected}
            new_items = [v for v in fresh if v.get("aweme_id","") not in exist_ids]
            collected.extend(new_items)
            log(f"  ✓ 新增 {len(new_items)} 条（原始 {len(fresh)} 条）  累计 {len(collected)} 条")
        else:
            log("  ⚠ 本批无 API 数据，尝试 DOM 解析...")
            dom_items = await scrape_dom(page)
            exist_ids = {v.get("aweme_id","") for v in collected}
            new_items = [v for v in dom_items if v.get("aweme_id","") not in exist_ids]
            if new_items:
                collected.extend(new_items)
                log(f"  DOM 补充 {len(new_items)} 条  累计 {len(collected)} 条")
            else:
                log(f"  无新数据（DOM也为空）")
                if batch_no >= 4:
                    log("  连续无数据，提前结束")
                    break

        if len(collected) >= TOTAL:
            log(f"\n✅ 已达到 {TOTAL} 条目标，停止采集")
            break

        await asyncio.sleep(random.uniform(2.0, 4.0))

    return collected[:TOTAL]


async def scrape_dom(page):
    """备用：从DOM解析视频卡片"""
    try:
        return await page.evaluate("""() => {
            const result = [];
            const cards = document.querySelectorAll(
                '[data-e2e="search-video-item"], [class*="videoCard"], [class*="VideoCard"], [class*="searchCard"]'
            );
            cards.forEach(card => {
                const a   = card.querySelector('a[href*="/video/"]');
                const id  = a ? (a.href.match(/\\/video\\/(\\d+)/) || [])[1] || '' : '';
                const txt = card.querySelector('[class*="desc"], [class*="title"], [class*="content"]');
                const lik = card.querySelector('[class*="like"], [class*="digg"]');
                const aut = card.querySelector('[class*="author"], [class*="nickname"]');
                if (id) {
                    result.push({
                        aweme_id   : id,
                        desc       : txt ? txt.innerText.trim() : '',
                        author     : { nickname: aut ? aut.innerText.trim() : '' },
                        statistics : { digg_count: lik ? lik.innerText.trim() : '0' },
                        _source    : 'dom',
                    });
                }
            });
            return result;
        }""")
    except:
        return []


async def main():
    if not SESSION_FILE.exists():
        log("❌ 找不到 session 文件，请先运行 douyin_qr_v6.py 完成登录")
        return

    log("=" * 60)
    log(f"抖音「{KEYWORD}」视频数据采集")
    log("=" * 60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled","--no-sandbox","--window-size=1440,900"],
        )
        ctx = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="zh-CN",
            viewport={"width":1440,"height":900},
        )
        await ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined});")

        # 加载 session cookies
        cookies = json.loads(SESSION_FILE.read_text())
        valid_cookies = []
        for c in cookies:
            try:
                # 只保留有效字段
                clean = {
                    "name": c["name"],
                    "value": c["value"],
                    "domain": c.get("domain", ".douyin.com"),
                    "path": c.get("path", "/"),
                }
                if c.get("httpOnly") is not None:
                    clean["httpOnly"] = c["httpOnly"]
                if c.get("secure") is not None:
                    clean["secure"] = c["secure"]
                if c.get("sameSite") in ["Strict","Lax","None"]:
                    clean["sameSite"] = c["sameSite"]
                valid_cookies.append(clean)
            except:
                pass
        
        await ctx.add_cookies(valid_cookies)
        log(f"已加载 {len(valid_cookies)} 个 cookies")

        page = await ctx.new_page()
        
        # 访问主页验证登录
        log("验证登录状态...")
        await page.goto("https://www.douyin.com/", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)
        
        cks = await ctx.cookies(["https://www.douyin.com"])
        sid = next((c for c in cks if c["name"] == "sessionid" and c["value"]), None)
        if sid:
            log(f"✅ 登录有效: sessionid={sid['value'][:20]}...")
        else:
            log("⚠ 未检测到 sessionid，但继续尝试...")

        # 采集视频
        videos = await collect_videos(ctx, page)
        
        await browser.close()

    log(f"\n{'='*60}")
    log(f"采集完成：共 {len(videos)} 条视频")

    if videos:
        # 保存原始数据
        out = {
            "keyword"    : KEYWORD,
            "fetch_time" : datetime.now().isoformat(),
            "total"      : len(videos),
            "source"     : "real_api",
            "videos"     : videos,
        }
        RAW_FILE.write_text(json.dumps(out, ensure_ascii=False, indent=2))
        log(f"✅ 原始数据已保存: {RAW_FILE}")

        # 打印示例
        log("\n示例数据（前3条）:")
        for i, v in enumerate(videos[:3], 1):
            log(f"\n  [{i}] {v.get('desc','')[:60]}")
            a = v.get("author", {})
            log(f"      作者: {a.get('nickname','?')}  粉丝: {a.get('follower_count',0):,}")
            s = v.get("statistics", {})
            log(f"      点赞: {s.get('digg_count',0):,}  评论: {s.get('comment_count',0):,}  转发: {s.get('share_count',0):,}  收藏: {s.get('collect_count',0):,}")
            tags = [t.get("title","") for t in v.get("text_extra",[]) if t.get("type") == 1]
            log(f"      标签: {tags[:5]}")
    else:
        log("⚠ 未获取到视频数据")

    return videos

if __name__ == "__main__":
    asyncio.run(main())
