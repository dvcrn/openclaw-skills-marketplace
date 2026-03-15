#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音视频详情采集 & 结构化解析
对每条视频：
  - 从 desc 文本解析基础字段（时长、播放量、正文、标签、作者、发布时间）
  - 访问视频详情页，拦截 API 获取：粉丝数、点赞/转发/收藏、热门评论
  - 遇到验证码自动滑动处理
  - 输出 douyin_parsed.json
"""
import asyncio, json, re, time, random, urllib.parse, io
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright
from PIL import Image
import numpy as np

import sys

# ── 参数：可通过命令行覆盖 ────────────────────────────────
# 用法：python3 parse_videos.py [工作目录] [detail_limit]
WORK_DIR     = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(".").resolve()
DETAIL_LIMIT = int(sys.argv[2]) if len(sys.argv) > 2 else 50

SAVE_DIR     = WORK_DIR
SESSION_FILE = SAVE_DIR / "douyin_session.json"
RAW_FILE     = SAVE_DIR / "douyin_raw_data.json"
OUT_FILE     = SAVE_DIR / "douyin_parsed.json"

MAX_VIDEOS   = 9999  # 全部处理（由采集结果决定）
COMMENTS_TOP = 5     # 每条视频取前5条热评

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

# ─── 验证码自动处理 ────────────────────────────────────────────────────────

def ease_out_cubic(t):
    return 1 - (1 - t) ** 3

def human_slide_path(distance, steps=65):
    path = []
    overshoot = random.randint(3, 7)
    for i in range(steps):
        t = (i + 1) / steps
        eased = ease_out_cubic(t)
        if t <= 0.85:
            x = int((distance + overshoot) * eased)
        else:
            t2 = (t - 0.85) / 0.15
            x = int(distance + overshoot - overshoot * t2)
        jitter_y = random.randint(-2, 2) if 0.05 < t < 0.9 else 0
        jitter_x = random.randint(-1, 1) if 0.05 < t < 0.8 else 0
        path.append((x + jitter_x, jitter_y))
    path.append((distance, 0))
    return path

def find_gap_by_screenshot(bg_bytes: bytes, sl_bytes: bytes) -> int:
    bg_img = Image.open(io.BytesIO(bg_bytes)).convert("L")
    sl_img = Image.open(io.BytesIO(sl_bytes)).convert("L")
    bg_w, bg_h = bg_img.size
    sl_w, sl_h = sl_img.size

    bg_arr = np.array(bg_img, dtype=float)
    mask_w, mask_h = sl_w + 8, sl_h + 8
    if mask_h < bg_h and mask_w < bg_w:
        fill_col = np.mean(bg_arr[:, mask_w:mask_w+20], axis=1, keepdims=True)
        bg_arr[:mask_h, :mask_w] = fill_col[:mask_h, :]
    sl_arr = np.array(sl_img, dtype=float)

    search_start = sl_w + 12
    search_end   = bg_w - 8

    # 主：模板匹配
    template_x = None
    try:
        from skimage.feature import match_template
        mid_y = bg_h // 2
        half_h = min(sl_h, bg_h // 2)
        y0, y1 = max(0, mid_y - half_h), min(bg_h, mid_y + half_h)
        bg_roi = bg_arr[y0:y1, search_start:]
        sl_roi = sl_arr[:y1-y0, :sl_w]
        if sl_roi.shape[0] < bg_roi.shape[0]:
            sl_roi = np.pad(sl_roi, ((0, bg_roi.shape[0]-sl_roi.shape[0]), (0,0)), mode='edge')
        if bg_roi.shape[0] >= sl_roi.shape[0] and bg_roi.shape[1] >= sl_roi.shape[1]:
            result = match_template(bg_roi, sl_roi)
            ij = np.unravel_index(np.argmax(result), result.shape)
            template_x = int(ij[1]) + search_start
    except Exception:
        pass

    # 辅：Sobel 双峰取左峰
    sobel_corrected = None
    try:
        from scipy.ndimage import sobel as scipy_sobel
        from scipy.signal import find_peaks as sp_peaks
        sx = np.abs(scipy_sobel(bg_arr, axis=1))
        col_sobel = np.mean(sx, axis=0)
        region = col_sobel[search_start:search_end]
        peaks, props = sp_peaks(region, distance=8, prominence=0.5)
        if len(peaks) >= 2:
            top2 = peaks[np.argsort(props["prominences"])[-2:]]
            sobel_corrected = int(np.sort(top2)[0]) + search_start
        elif len(peaks) == 1:
            sobel_corrected = max(int(peaks[0]) + search_start - sl_w, search_start)
        else:
            sobel_corrected = max(int(np.argmax(region)) + search_start - sl_w, search_start)
    except Exception:
        pass

    if template_x is not None and sobel_corrected is not None:
        gap_x = int(template_x * 0.7 + sobel_corrected * 0.3) if abs(template_x - sobel_corrected) <= 25 else template_x
    elif template_x is not None:
        gap_x = template_x
    elif sobel_corrected is not None:
        gap_x = sobel_corrected
    else:
        gap_x = int(bg_w * 0.45)
    return gap_x

async def solve_captcha(page) -> bool:
    """自动处理滑动拼图验证码，最多重试 5 次"""
    for attempt in range(1, 6):
        captcha_frame = None
        for frame in page.frames:
            if "verifycenter" in frame.url or "captcha" in frame.url:
                captcha_frame = frame
                break
        if not captcha_frame:
            return True  # 验证码消失

        log(f"  验证码第{attempt}次尝试...")
        try:
            bg_el  = captcha_frame.locator(".captcha-verify-image").first
            sl_el  = captcha_frame.locator(".captcha-verify-image-slide").first
            btn_el = captcha_frame.locator(".captcha-slider-btn").first
            bg_bb  = await bg_el.bounding_box()
            sl_bb  = await sl_el.bounding_box()
            btn_bb = await btn_el.bounding_box()
            if not btn_bb or not bg_bb or not sl_bb:
                continue

            bg_bytes = await page.screenshot(clip={"x":bg_bb["x"],"y":bg_bb["y"],"width":bg_bb["width"],"height":bg_bb["height"]})
            sl_bytes = await page.screenshot(clip={"x":sl_bb["x"],"y":sl_bb["y"],"width":sl_bb["width"],"height":sl_bb["height"]})
            gap_x = find_gap_by_screenshot(bg_bytes, sl_bytes)

            sl_w_half  = sl_bb["width"] / 2
            btn_w_half = btn_bb["width"] / 2
            slide_distance = (bg_bb["x"] + gap_x + sl_w_half) - (btn_bb["x"] + btn_w_half)
            max_slide = bg_bb["width"] - btn_bb["width"] - 5
            slide_distance = max(min(slide_distance, max_slide), 5)
            log(f"    gap_x={gap_x}  滑动={int(slide_distance)}px")

            cx = btn_bb["x"] + btn_w_half
            cy = btn_bb["y"] + btn_bb["height"] / 2
            await page.mouse.move(cx - 5, cy + random.randint(-2, 2))
            await asyncio.sleep(random.uniform(0.15, 0.3))
            await page.mouse.move(cx, cy)
            await asyncio.sleep(random.uniform(0.08, 0.15))
            await page.mouse.down()
            await asyncio.sleep(random.uniform(0.05, 0.10))

            for dx, dy in human_slide_path(int(slide_distance)):
                await page.mouse.move(cx + dx, cy + dy)
                frac = abs(dx) / max(abs(slide_distance), 1)
                if frac < 0.5:
                    await asyncio.sleep(random.uniform(0.005, 0.008))
                elif frac < 0.85:
                    await asyncio.sleep(random.uniform(0.010, 0.018))
                else:
                    await asyncio.sleep(random.uniform(0.025, 0.045))

            await page.mouse.up()
            await asyncio.sleep(3)

            frames_after = [f for f in page.frames if "verifycenter" in f.url or "captcha" in f.url]
            if not frames_after:
                log("    ✅ 验证通过")
                return True

            # 刷新验证码再试
            try:
                rb = captcha_frame.locator(".vc-captcha-refresh,.captcha-refresh,[class*='refresh']").first
                rbb = await rb.bounding_box()
                if rbb:
                    await page.mouse.click(rbb["x"] + rbb["width"]/2, rbb["y"] + rbb["height"]/2)
                    await asyncio.sleep(1.5)
            except Exception:
                pass
        except Exception as e:
            log(f"    验证码处理异常: {e}")

    return False

# ─── 从 desc 文本解析基础字段 ─────────────────────────────────────────────

def num_str_to_int(s: str) -> int:
    """把 '1.1万' '4.6万' '123' 转成整数"""
    s = s.strip()
    if '万' in s:
        return int(float(s.replace('万', '')) * 10000)
    if '亿' in s:
        return int(float(s.replace('亿', '')) * 100000000)
    try:
        return int(s)
    except:
        return 0

def parse_desc(aweme_id: str, raw_desc: str) -> dict:
    """
    格式示例：
      03:41 1.1万 成长永远比被爱更重要！ #女性成长 #自我成长 @你好周洋帆 9月前
      合集 04:02 107 这是一期... #话题 @作者 14小时前
    """
    text = raw_desc.strip()
    result = {
        "aweme_id"      : aweme_id,
        "video_url"     : f"https://www.douyin.com/video/{aweme_id}",
        "duration"      : "",
        "play_count_raw": "",
        "play_count"    : 0,
        "title"         : "",
        "tags"          : [],
        "author_name"   : "",
        "publish_time"  : "",
        # 详情页补充
        "like_count"    : 0,
        "share_count"   : 0,
        "collect_count" : 0,
        "comment_count" : 0,
        "follower_count": 0,
        "top_comments"  : [],
        "detail_fetched": False,
    }

    # 去掉 "合集" 前缀
    text = re.sub(r'^合集\s*', '', text)

    # 时长 mm:ss 或 hh:mm:ss
    dur_m = re.match(r'^(\d+:\d+(?::\d+)?)\s*', text)
    if dur_m:
        result["duration"] = dur_m.group(1)
        text = text[dur_m.end():]

    # 播放量（紧跟时长后面的数字/万/亿）
    play_m = re.match(r'^([\d.]+[万亿]?)\s+', text)
    if play_m:
        result["play_count_raw"] = play_m.group(1)
        result["play_count"]     = num_str_to_int(play_m.group(1))
        text = text[play_m.end():]

    # 提取所有 hashtag
    tags = re.findall(r'#([^\s#@]+)', text)
    result["tags"] = tags

    # 提取 @作者 (取第一个)
    author_m = re.search(r'@([^\s@]+)', text)
    if author_m:
        result["author_name"] = author_m.group(1)

    # 发布时间（末尾的 "X天前" / "X小时前" / "X月前" / "X年前" / "昨天" 等）
    time_m = re.search(r'(\d+(?:\.\d+)?(?:秒|分钟|小时|天|周|月|年)前|昨天|前天|刚刚)$', text.strip())
    if time_m:
        result["publish_time"] = time_m.group(1)
        text = text[:time_m.start()].strip()

    # 去掉 @xxx 得到正文
    title = re.sub(r'@\S+', '', text)
    title = re.sub(r'#\S+', '', title)
    title = title.strip(' \t\n·-—')
    result["title"] = title

    return result

# ─── 从详情页 API 补充字段 ────────────────────────────────────────────────

async def fetch_detail(page, video: dict, ctx) -> dict:
    """访问单条视频详情页，拦截 API 获取详情数据"""
    aweme_id = video["aweme_id"]
    url = f"https://www.douyin.com/video/{aweme_id}"

    detail_data = {}
    comments_data = []

    async def on_resp(resp):
        u = resp.url
        # 视频详情 API
        if "/aweme/v1/web/aweme/detail/" in u or "/aweme/detail/" in u:
            try:
                body = await resp.json()
                aw = body.get("aweme_detail") or body.get("aweme_list", [{}])[0]
                if aw:
                    st = aw.get("statistics", {})
                    au = aw.get("author", {})
                    detail_data.update({
                        "like_count"    : st.get("digg_count", 0),
                        "share_count"   : st.get("share_count", 0),
                        "collect_count" : st.get("collect_count", 0),
                        "comment_count" : st.get("comment_count", 0),
                        "follower_count": au.get("follower_count", 0),
                        "author_uid"    : au.get("uid", ""),
                        "author_nickname": au.get("nickname", ""),
                    })
            except:
                pass
        # 评论 API
        if "/comment/list/" in u and "douyin.com" in u:
            try:
                body = await resp.json()
                cmts = body.get("comments") or []
                for c in cmts[:COMMENTS_TOP]:
                    user = c.get("user", {})
                    comments_data.append({
                        "text"      : c.get("text", ""),
                        "digg_count": c.get("digg_count", 0),
                        "nickname"  : user.get("nickname", ""),
                    })
            except:
                pass

    page.on("response", on_resp)
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=20000)
        await asyncio.sleep(random.uniform(3, 5))

        # 如果有验证码，自动处理
        title = await page.title()
        if "验证码" in title or "captcha" in page.url.lower():
            log(f"  ⚠ {aweme_id} 遇到验证码，自动处理...")
            ok = await solve_captcha(page)
            if not ok:
                log(f"  ✗ 验证码未通过，跳过 {aweme_id}")
                page.remove_listener("response", on_resp)
                return video
            # 验证通过后等待页面重新加载
            await asyncio.sleep(3)

        # 如果没有从 API 拿到数据，尝试 DOM 解析
        if not detail_data:
            dom_stats = await page.evaluate("""() => {
                const getText = sel => {
                    const el = document.querySelector(sel);
                    return el ? el.innerText.trim() : '';
                };
                // 尝试多种选择器
                const selectors = {
                    like: ['[data-e2e="like-count"]','[class*="like"][class*="count"]','[class*="digg"]'],
                    comment: ['[data-e2e="comment-count"]','[class*="comment"][class*="count"]'],
                    share: ['[data-e2e="share-count"]','[class*="share"][class*="count"]'],
                    collect: ['[data-e2e="collect-count"]','[class*="collect"][class*="count"]'],
                    follower: ['[data-e2e="follow-count"]','[class*="follower"]','[class*="fans"]'],
                };
                const result = {};
                for (const [key, sels] of Object.entries(selectors)) {
                    for (const s of sels) {
                        const el = document.querySelector(s);
                        if (el && el.innerText) {
                            result[key] = el.innerText.trim();
                            break;
                        }
                    }
                }
                // 评论
                const cmtEls = document.querySelectorAll('[class*="comment-item"],[class*="commentItem"]');
                result.comments = Array.from(cmtEls).slice(0, 5).map(el => ({
                    text: (el.querySelector('[class*="text"],[class*="content"]') || el).innerText.slice(0,100),
                    digg: (el.querySelector('[class*="like"],[class*="digg"]') || {innerText:''}).innerText,
                }));
                return result;
            }""")

            def parse_num(s):
                if not s: return 0
                s = str(s).strip()
                if '万' in s: return int(float(s.replace('万',''))*10000)
                try: return int(re.sub(r'[^\d]','',s) or '0')
                except: return 0

            if dom_stats:
                detail_data = {
                    "like_count"    : parse_num(dom_stats.get("like", 0)),
                    "share_count"   : parse_num(dom_stats.get("share", 0)),
                    "collect_count" : parse_num(dom_stats.get("collect", 0)),
                    "comment_count" : parse_num(dom_stats.get("comment", 0)),
                    "follower_count": parse_num(dom_stats.get("follower", 0)),
                }
                for c in dom_stats.get("comments", [])[:COMMENTS_TOP]:
                    comments_data.append({
                        "text"      : c.get("text",""),
                        "digg_count": parse_num(c.get("digg",0)),
                        "nickname"  : "",
                    })

    except Exception as e:
        log(f"  ⚠ {aweme_id} 详情失败: {e}")
    finally:
        page.remove_listener("response", on_resp)

    if detail_data:
        video.update(detail_data)
        video["detail_fetched"] = True
    if comments_data:
        video["top_comments"] = comments_data

    return video


# ─── 主流程 ────────────────────────────────────────────────────────────────

async def main():
    raw = json.loads(RAW_FILE.read_text())
    videos_raw = raw.get("videos", [])
    log(f"加载 {len(videos_raw)} 条原始视频")

    # Step1: 从 desc 文本解析基础字段
    parsed = []
    for v in videos_raw:
        p = parse_desc(v["aweme_id"], v.get("desc",""))
        parsed.append(p)
    log(f"Step1 完成：解析 {len(parsed)} 条基础字段")

    # Step2: 访问详情页补充数据（前 DETAIL_LIMIT 条）
    if not SESSION_FILE.exists():
        log("⚠ 无 session 文件，跳过详情采集")
    else:
        log(f"\nStep2: 访问详情页（最多 {DETAIL_LIMIT} 条）...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                args=["--disable-blink-features=AutomationControlled","--no-sandbox",
                      "--window-size=1440,900","--window-position=0,0"],
            )
            ctx = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                locale="zh-CN",
                viewport={"width":1440,"height":900},
            )
            await ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined});")
            cookies = json.loads(SESSION_FILE.read_text())
            valid = []
            for c in cookies:
                try:
                    clean = {"name":c["name"],"value":c["value"],"domain":c.get("domain",".douyin.com"),"path":c.get("path","/")}
                    if c.get("sameSite") in ["Strict","Lax","None"]: clean["sameSite"] = c["sameSite"]
                    valid.append(clean)
                except: pass
            await ctx.add_cookies(valid)

            page = await ctx.new_page()
            success_count = 0
            for i, video in enumerate(parsed[:DETAIL_LIMIT]):
                log(f"  [{i+1}/{min(DETAIL_LIMIT, len(parsed))}] {video['aweme_id']}  {video['title'][:30]}")
                video = await fetch_detail(page, video, ctx)
                if video.get("detail_fetched"):
                    success_count += 1
                    log(f"    ✓ 赞={video['like_count']:,}  转={video['share_count']:,}  收={video['collect_count']:,}  评={video['comment_count']:,}  粉丝={video['follower_count']:,}")
                    if video.get("top_comments"):
                        for c in video["top_comments"][:2]:
                            log(f"    💬 [{c['digg_count']}赞] {c['text'][:50]}")
                else:
                    log(f"    ✗ 未获取到详情")
                await asyncio.sleep(random.uniform(1.5, 3.0))

            await browser.close()
            log(f"\n详情采集：{success_count}/{min(DETAIL_LIMIT, len(parsed))} 条成功")

    # Step3: 保存结果
    output = {
        "keyword"    : raw.get("keyword","女性成长"),
        "fetch_time" : raw.get("fetch_time",""),
        "parse_time" : datetime.now().isoformat(),
        "total"      : len(parsed),
        "detail_fetched_count": sum(1 for v in parsed if v.get("detail_fetched")),
        "videos"     : parsed,
    }
    OUT_FILE.write_text(json.dumps(output, ensure_ascii=False, indent=2))
    log(f"\n✅ 已保存: {OUT_FILE}  ({OUT_FILE.stat().st_size//1024} KB)")

    # 打印统计摘要
    log("\n" + "="*60)
    log("统计摘要（详情已获取的视频）")
    log("="*60)
    detail_videos = [v for v in parsed if v.get("detail_fetched")]
    if detail_videos:
        total_plays   = sum(v.get("play_count",0) for v in parsed)
        total_likes   = sum(v.get("like_count",0) for v in detail_videos)
        total_shares  = sum(v.get("share_count",0) for v in detail_videos)
        avg_likes     = total_likes // max(len(detail_videos),1)
        top_like      = max(detail_videos, key=lambda v: v.get("like_count",0))
        top_play      = max(parsed, key=lambda v: v.get("play_count",0))
        all_tags      = []
        for v in parsed:
            all_tags.extend(v.get("tags",[]))
        from collections import Counter
        top_tags = Counter(all_tags).most_common(10)
        
        log(f"总播放量（估算）: {total_plays:,}")
        log(f"总点赞数: {total_likes:,}  平均: {avg_likes:,}")
        log(f"总转发数: {total_shares:,}")
        log(f"最高播放: {top_play['play_count_raw']} - {top_play['title'][:40]}")
        log(f"最高点赞: {top_like['like_count']:,} - {top_like['title'][:40]}")
        log(f"\n热门标签 Top10:")
        for tag, cnt in top_tags:
            log(f"  #{tag}  ({cnt}次)")
    
    log("\n前5条完整样本:")
    for i, v in enumerate(parsed[:5], 1):
        log(f"\n[{i}] {v['title'][:60]}")
        log(f"  作者: {v.get('author_nickname') or v['author_name']}  粉丝: {v['follower_count']:,}")
        log(f"  标签: {' '.join('#'+t for t in v['tags'][:5])}")
        log(f"  播放: {v['play_count_raw'] or '-'}  赞: {v['like_count']:,}  转: {v['share_count']:,}  收: {v['collect_count']:,}  评: {v['comment_count']:,}")
        log(f"  发布: {v['publish_time']}  时长: {v['duration']}")
        if v.get("top_comments"):
            log(f"  热评: {v['top_comments'][0]['text'][:60]}")

asyncio.run(main())
