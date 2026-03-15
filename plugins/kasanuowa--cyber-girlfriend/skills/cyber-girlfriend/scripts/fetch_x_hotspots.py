#!/usr/bin/env python3
import argparse
import asyncio
import json
import time
from pathlib import Path

import browser_cookie3
from playwright.async_api import async_playwright


TREND_MARKERS = {
    "global trending",
    "trending",
    "热点",
    "热搜",
    "趋势",
}

NEWS_MARKERS = {
    "today’s news",
    "today's news",
    "news",
    "新闻",
}

STOP_MARKERS = {
    "who to follow",
    "you might like",
    "relevant people",
    "关注推荐",
    "你可能喜欢",
}

NEWS_META_MARKERS = ("news", "posts", "trending now", "新闻", "帖子", "热议")


def load_cookies(domain_name: str):
    jar = browser_cookie3.chrome(domain_name=domain_name)
    cookies = []
    for cookie in jar:
        if domain_name not in cookie.domain and "twitter.com" not in cookie.domain:
            continue
        cookies.append(
            {
                "name": cookie.name,
                "value": cookie.value,
                "domain": cookie.domain,
                "path": cookie.path or "/",
                "expires": float(cookie.expires) if cookie.expires and cookie.expires > 0 else -1,
                "httpOnly": False,
                "secure": bool(cookie.secure),
                "sameSite": "Lax",
            }
        )
    return cookies


def normalize(line: str) -> str:
    return " ".join(line.strip().lower().split())


def is_stop_line(line: str) -> bool:
    lowered = normalize(line)
    return any(marker in lowered for marker in STOP_MARKERS)


def looks_like_news_meta(line: str) -> bool:
    lowered = normalize(line)
    return any(marker in lowered for marker in NEWS_META_MARKERS)


def parse_ranked_trends(lines: list[str], limit: int):
    trends = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.isdigit():
            i += 1
            continue
        rank = int(line)
        if rank <= 0 or rank > 50 or i + 3 >= len(lines):
            i += 1
            continue
        category = lines[i + 2]
        title = lines[i + 3]
        if any(not text or is_stop_line(text) for text in [category, title]):
            i += 1
            continue
        detail = ""
        if i + 4 < len(lines):
            maybe_detail = lines[i + 4]
            if "Trending with" in maybe_detail or "posts" in maybe_detail or "帖子" in maybe_detail:
                detail = maybe_detail
        trends.append(
            {
                "rank": rank,
                "category": category,
                "title": title,
                "detail": detail,
            }
        )
        i += 4
        if len(trends) >= limit:
            break
    return trends


def parse_news_pairs(lines: list[str], limit: int):
    news = []
    i = 0
    max_items = max(2, min(5, limit // 2 or 2))
    while i + 1 < len(lines) and len(news) < max_items:
        line = lines[i]
        meta = lines[i + 1]
        if not is_stop_line(line) and looks_like_news_meta(meta):
            news.append({"headline": line, "meta": meta})
            i += 2
            continue
        i += 1
    return news


def parse_body_text(body_text: str, limit: int):
    lines = [line.strip() for line in body_text.splitlines() if line.strip()]
    trends = []
    news = []
    in_trends = False
    in_news = False

    i = 0
    while i < len(lines):
        line = lines[i]
        lowered = normalize(line)
        if lowered in TREND_MARKERS:
            in_trends = True
            in_news = False
            i += 1
            continue
        if lowered in NEWS_MARKERS:
            in_trends = False
            in_news = True
            i += 1
            continue
        if is_stop_line(line):
            break

        if in_trends and line.isdigit() and i + 3 < len(lines):
            category = lines[i + 2]
            title = lines[i + 3]
            detail = ""
            if i + 4 < len(lines):
                maybe_detail = lines[i + 4]
                if "Trending with" in maybe_detail or "posts" in maybe_detail:
                    detail = maybe_detail
            trends.append(
                {
                    "rank": int(line),
                    "category": category,
                    "title": title,
                    "detail": detail,
                }
            )
            i += 1
            continue

        if in_news and i + 1 < len(lines):
            meta = lines[i + 1]
            if "News" in meta or "posts" in meta or "Trending now" in meta:
                news.append({"headline": line, "meta": meta})
                i += 2
                continue

        i += 1

    if not trends:
        trends = parse_ranked_trends(lines, limit)
    if not news:
        news = parse_news_pairs(lines, limit)

    return trends[:limit], news[: max(2, min(5, limit // 2 or 2))]


async def fetch_hotspots(chrome_path: str, trending_url: str, domain_name: str, limit: int):
    cookies = load_cookies(domain_name)
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True, executable_path=chrome_path)
        context = await browser.new_context(
            viewport={"width": 1440, "height": 2200},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
        )
        await context.add_cookies(cookies)
        page = await context.new_page()
        await page.goto(trending_url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)
        body_text = await page.locator("body").inner_text(timeout=30000)
        title = await page.title()
        current_url = page.url
        await browser.close()

    trends, news = parse_body_text(body_text, limit)
    highlights = []
    for item in trends[:3]:
        extra = f" {item['detail']}" if item["detail"] else ""
        highlights.append(f"{item['title']} ({item['category']}){extra}".strip())
    for item in news[:2]:
        highlights.append(f"{item['headline']} [{item['meta']}]")

    return {
        "fetched_at": int(time.time()),
        "source": "x-trending",
        "url": current_url,
        "title": title,
        "trends": trends,
        "news": news,
        "highlights": highlights[:5],
    }


def main():
    parser = argparse.ArgumentParser(description="Fetch hotspot topics from a signed-in X trending page.")
    parser.add_argument("--chrome-path", required=True)
    parser.add_argument("--trending-url", default="https://x.com/explore/tabs/trending")
    parser.add_argument("--domain-name", default="x.com")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    result = asyncio.run(
        fetch_hotspots(
            chrome_path=args.chrome_path,
            trending_url=args.trending_url,
            domain_name=args.domain_name,
            limit=args.limit,
        )
    )
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
