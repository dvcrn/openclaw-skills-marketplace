#!/usr/bin/env python3
"""
2fun.live 网盘资源搜索

API: POST https://www.2fun.live/api/pan/search
    { kw: "关键词", res: "merge" }

限速: 60次/分钟（按IP）

Usage:
  python3 search.py "流浪地球2"
  python3 search.py "权游 第四季" --types aliyun quark
  python3 search.py "流浪地球2" --json
"""

import sys
import json
import os
import urllib.request
import urllib.parse
import argparse

API_BASE_URL = os.getenv("API_URL", "https://www.2fun.live").rstrip("/")
SEARCH_API_URL = os.getenv("PAN_SEARCH_API_URL", "https://s.2fun.live/api/search").rstrip("/")
SEARCH_API_ORIGIN = "{uri.scheme}://{uri.netloc}".format(uri=urllib.parse.urlparse(SEARCH_API_URL))

# 云盘显示名称及优先级（用户友好度）
DRIVE_PRIORITY = ["aliyun", "quark", "115", "baidu", "pikpak", "uc", "xunlei", "123", "tianyi", "mobile", "magnet", "ed2k", "other"]

DRIVE_NAMES = {
    "115": "115网盘",
    "quark": "夸克网盘",
    "baidu": "百度网盘",
    "aliyun": "阿里云盘",
    "tianyi": "天翼云盘",
    "uc": "UC网盘",
    "mobile": "移动云盘",
    "pikpak": "PikPak",
    "xunlei": "迅雷云盘",
    "123": "123网盘",
    "magnet": "磁力链接",
    "ed2k": "ED2K",
    "other": "其他",
}

DRIVE_EMOJI = {
    "aliyun": "☁️",
    "quark": "⚡",
    "baidu": "🔵",
    "115": "🔷",
    "pikpak": "🟣",
    "magnet": "🧲",
    "ed2k": "🔗",
}


def search(
    keyword: str,
    cloud_types: list = None,
    refresh: bool = False,
    page: int = 1,
    page_size: int = None,
) -> dict:
    page = max(1, int(page or 1))
    page_size = max(1, min(100, int(page_size or 20)))
    use_paged_results = bool(cloud_types) or page > 1 or page_size is not None
    headers = {
        "Referer": f"{SEARCH_API_ORIGIN}/",
        "User-Agent": "Mozilla/5.0",
    }

    if SEARCH_API_URL.endswith("/api/search"):
        query = {
            "q": keyword,
            "page": page,
            "pageSize": page_size,
        }
        if cloud_types:
            query["cloud"] = ",".join(cloud_types)

        url = f"{SEARCH_API_URL}?{urllib.parse.urlencode(query)}"
        req = urllib.request.Request(url, headers=headers, method="GET")
    else:
        payload = {"kw": keyword, "res": "results" if use_paged_results else "merge"}
        if cloud_types:
            payload["cloud_types"] = cloud_types
        if refresh:
            payload["refresh"] = True
        if use_paged_results:
            payload["page"] = page
            payload["page_size"] = page_size

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            SEARCH_API_URL,
            data=data,
            headers={
                **headers,
                "Content-Type": "application/json",
            },
            method="POST",
        )

    resp = urllib.request.urlopen(req, timeout=30)
    raw = json.loads(resp.read().decode("utf-8"))
    return normalize_result(raw, keyword, page, page_size)


def normalize_result(raw: dict, keyword: str, page: int, page_size: int) -> dict:
    if "merged_by_type" in raw:
        return raw

    if "total_count" in raw and "results" in raw:
        return raw

    if "total" in raw and "results" in raw:
        results = []
        drive_counts = {}

        for item in raw.get("results", []):
            drive_type = item.get("netdiskType", "other")
            normalized_item = {
                "type": drive_type,
                "url": item.get("url", ""),
                "note": item.get("title", ""),
                "datetime": item.get("createdAt", ""),
                "source": item.get("source", "PanSou"),
            }
            results.append(normalized_item)
            drive_counts[drive_type] = drive_counts.get(drive_type, 0) + 1

        total = int(raw.get("total", len(results)) or 0)
        total_pages = max(1, (total + page_size - 1) // page_size) if total > 0 else 1

        return {
            "keyword": raw.get("query", keyword),
            "total_count": total,
            "results": results,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_more": page < total_pages,
            "drive_counts": drive_counts,
            "from_cache": raw.get("fromCache", raw.get("from_cache", False)),
            "cache_status": raw.get("cacheStatus", raw.get("cache_status")),
            "stale": raw.get("stale", False),
        }

    return raw


def format_results(result: dict, max_per_type: int = 3) -> str:
    keyword = result.get("keyword", "")
    total = result.get("total_count", 0)
    duration = result.get("search_duration", 0)
    from_cache = result.get("from_cache", False)
    cache_tag = "（缓存）" if from_cache else ""

    if total == 0:
        return f"❌ 未找到「{keyword}」的网盘资源"

    if "results" in result:
        page = result.get("page", 1)
        total_pages = result.get("total_pages", 1)
        drive_counts = result.get("drive_counts", {})
        results = result.get("results", [])

        lines = [f"🔍 **{keyword}** — 共 {total} 条结果，第 {page}/{max(total_pages, 1)} 页 ({duration}ms{cache_tag})\n"]

        grouped = {}
        for item in results:
            drive_type = item.get("type", "other")
            grouped.setdefault(drive_type, []).append(item)

        ordered_types = [t for t in DRIVE_PRIORITY if t in grouped and grouped[t]]
        for t in grouped:
            if t not in ordered_types and grouped[t]:
                ordered_types.append(t)

        for drive_type in ordered_types:
            links = grouped[drive_type]
            name = DRIVE_NAMES.get(drive_type, drive_type)
            emoji = DRIVE_EMOJI.get(drive_type, "📁")
            count_label = drive_counts.get(drive_type, len(links))
            lines.append(f"**{emoji} {name}** ({count_label} 个，当前页 {len(links)} 条)")

            for lnk in links[:max_per_type]:
                url = lnk.get("url", "")
                pwd = lnk.get("password", "")
                note = lnk.get("note", "")
                date = lnk.get("datetime", "")
                restricted = lnk.get("_restricted", False)

                if restricted:
                    lines.append("  🔒 需登录查看完整链接")
                    continue

                line = f"  `{url}`"
                if pwd:
                    line += f"  密码: `{pwd}`"
                if note:
                    line += f"  {note}"
                if date:
                    line += f"  ({date[:10]})"
                lines.append(line)
            lines.append("")

        if page < total_pages:
            lines.append(f"➡️ 还有更多结果，继续翻到第 {page + 1} 页查看")
            lines.append("")

        lines.append(f"🌐 完整搜索：<{SEARCH_API_ORIGIN}/pan?kw={urllib.parse.quote(keyword)}>")
        return "\n".join(lines)

    by_type = result.get("merged_by_type", {})
    lines = [f"🔍 **{keyword}** — 共 {total} 条结果 ({duration}ms{cache_tag})\n"]

    # 按优先级排列云盘
    ordered_types = [t for t in DRIVE_PRIORITY if t in by_type and by_type[t]]
    # 加上优先级里没有的类型
    for t in by_type:
        if t not in ordered_types and by_type[t]:
            ordered_types.append(t)

    for drive_type in ordered_types:
        links = by_type[drive_type]
        if not links:
            continue
        name = DRIVE_NAMES.get(drive_type, drive_type)
        emoji = DRIVE_EMOJI.get(drive_type, "📁")
        lines.append(f"**{emoji} {name}** ({len(links)} 个)")
        for lnk in links[:max_per_type]:
            url = lnk.get("url", "")
            pwd = lnk.get("password", "")
            note = lnk.get("note", "")
            date = lnk.get("datetime", "")
            restricted = lnk.get("_restricted", False)

            if restricted:
                lines.append("  🔒 需登录查看完整链接")
                continue

            line = f"  `{url}`"
            if pwd:
                line += f"  密码: `{pwd}`"
            if note:
                line += f"  {note}"
            if date:
                line += f"  ({date[:10]})"
            lines.append(line)

        if len(links) > max_per_type:
            lines.append(f"  … 还有 {len(links) - max_per_type} 个，去 2fun.live 查看全部")
        lines.append("")

    lines.append(f"🌐 完整搜索：<{SEARCH_API_ORIGIN}/pan?kw={urllib.parse.quote(keyword)}>")
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="2fun.live 网盘资源搜索")
    parser.add_argument("keyword", help="搜索关键词")
    parser.add_argument("--types", nargs="+", help="限定云盘类型 (aliyun/quark/baidu/...)")
    parser.add_argument("--page", type=int, default=1, help="结果页码（默认1）")
    parser.add_argument("--page-size", type=int, help="每页结果数（默认20，启用服务端分页）")
    parser.add_argument("--max", type=int, default=3, help="每种类型最多显示条数")
    parser.add_argument("--refresh", action="store_true", help="强制刷新缓存")
    parser.add_argument("--json", dest="as_json", action="store_true", help="输出原始 JSON")
    args = parser.parse_args()

    try:
        result = search(
            args.keyword,
            cloud_types=args.types,
            refresh=args.refresh,
            page=args.page,
            page_size=args.page_size,
        )
        if args.as_json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(format_results(result, max_per_type=args.max))
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if "RATE_LIMIT" in body:
            print("❌ 搜索过于频繁，稍等一分钟再试")
        else:
            print(f"❌ API 错误 {e.code}: {body[:200]}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 搜索失败: {e}")
        sys.exit(1)
