#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
精准版：在浏览器中实时截图+图像匹配+自动滑动
核心改进：
1. 截图即屏幕坐标（无需缩放）
2. 用模板匹配找缺口
3. 在完整滑动过程中截图验证
"""
import asyncio, json, io, math, random
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright
from PIL import Image
import numpy as np

SESSION_FILE = Path("/Users/hhao/WorkBuddy/20260313220324/douyin_session.json")
SAVE_DIR = Path("/Users/hhao/WorkBuddy/20260313220324")


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def ease_out_cubic(t):
    """快去慢停，更像真人拖动"""
    return 1 - (1 - t) ** 3


def human_slide_path(distance, steps=65):
    """
    生成仿真滑动路径：
    - ease-out 曲线（快启动，慢到位）
    - Y 轴轻微抖动
    - 到达终点前略微过冲，再回拉
    """
    path = []
    overshoot = random.randint(3, 7)   # 过冲距离

    for i in range(steps):
        t = (i + 1) / steps
        eased = ease_out_cubic(t)

        # 前 85%：滑向目标+过冲；后 15%：轻微回拉
        if t <= 0.85:
            x = int((distance + overshoot) * eased)
        else:
            # 线性回拉到正确位置
            t2 = (t - 0.85) / 0.15
            x = int(distance + overshoot - overshoot * t2)

        jitter_y = random.randint(-2, 2) if 0.05 < t < 0.9 else 0
        jitter_x = random.randint(-1, 1) if 0.05 < t < 0.8 else 0
        path.append((x + jitter_x, jitter_y))

    path.append((distance, 0))
    return path


def find_gap_by_screenshot(bg_bytes: bytes, sl_bytes: bytes) -> int:
    """
    找缺口左边缘的 x 坐标（相对于背景图左侧，屏幕坐标）

    根据实测分析：
      - 模板匹配（黄）最准，直接给出缺口左边缘
      - Sobel（蓝）次之，但检测到的是缺口右边缘，需减去缺口宽修正
      - 最终 = 模板匹配为主，Sobel修正值为辅（加权平均）

    返回：gap_x（缺口左边缘相对背景图左侧的 px 距离）
    """
    bg_img = Image.open(io.BytesIO(bg_bytes)).convert("L")
    sl_img = Image.open(io.BytesIO(sl_bytes)).convert("L")

    bg_w, bg_h = bg_img.size
    sl_w, sl_h = sl_img.size
    log(f"  背景截图: {bg_w}x{bg_h}  滑块截图: {sl_w}x{sl_h}")

    # 遮掉背景图左上角叠加的滑块区域，用周边像素填充
    bg_arr = np.array(bg_img, dtype=float)
    mask_w = sl_w + 8
    mask_h = sl_h + 8
    if mask_h < bg_h and mask_w < bg_w:
        fill_col = np.mean(bg_arr[:, mask_w:mask_w + 20], axis=1, keepdims=True)
        bg_arr[:mask_h, :mask_w] = fill_col[:mask_h, :]

    sl_arr = np.array(sl_img, dtype=float)

    search_start = sl_w + 12
    search_end   = bg_w - 8

    # ── 方法1（主）：模板匹配 ─────────────────────────────
    # 用滑块图在背景图中部做模板匹配，找缺口左边缘
    template_x = None
    try:
        from skimage.feature import match_template

        # 取背景图中部高度带（缺口与滑块图等高）
        mid_y  = bg_h // 2
        half_h = min(sl_h, bg_h // 2)
        y0 = max(0, mid_y - half_h)
        y1 = min(bg_h, mid_y + half_h)

        bg_roi = bg_arr[y0:y1, search_start:]
        sl_roi = sl_arr[:y1 - y0, :sl_w]

        # 如果 sl_roi 行数不足，补齐
        if sl_roi.shape[0] < bg_roi.shape[0]:
            pad = bg_roi.shape[0] - sl_roi.shape[0]
            sl_roi = np.pad(sl_roi, ((0, pad), (0, 0)), mode='edge')

        if bg_roi.shape[0] >= sl_roi.shape[0] and bg_roi.shape[1] >= sl_roi.shape[1]:
            result = match_template(bg_roi, sl_roi)
            ij = np.unravel_index(np.argmax(result), result.shape)
            template_x = int(ij[1]) + search_start
            conf = float(result.max())
            log(f"  模板匹配（主）: gap_x={template_x}px  confidence={conf:.3f}")
        else:
            log(f"  模板匹配跳过：bg_roi={bg_roi.shape} sl_roi={sl_roi.shape}")
    except Exception as e:
        log(f"  模板匹配失败: {e}")

    # ── 方法2（辅）：Sobel 双峰，取左峰再减缺口宽修正 ────
    sobel_corrected = None
    try:
        from scipy.ndimage import sobel as scipy_sobel
        from scipy.signal import find_peaks as sp_peaks

        sx = np.abs(scipy_sobel(bg_arr, axis=1))
        col_sobel = np.mean(sx, axis=0)
        region = col_sobel[search_start:search_end]

        peaks, props = sp_peaks(region, distance=8, prominence=0.5)
        if len(peaks) >= 2:
            # 取最大两个峰
            top2 = peaks[np.argsort(props["prominences"])[-2:]]
            top2_sorted = np.sort(top2)
            left_peak  = int(top2_sorted[0]) + search_start
            right_peak = int(top2_sorted[1]) + search_start
            gap_width = right_peak - left_peak
            log(f"  Sobel双峰: left={left_peak}px  right={right_peak}px  gap_width={gap_width}px")
            # Sobel 检测到的是边缘中心，左峰即缺口左边缘——直接用
            sobel_corrected = left_peak
        elif len(peaks) == 1:
            raw = int(peaks[0]) + search_start
            # 单峰可能是右边缘，减去 sl_w 修正
            sobel_corrected = max(raw - sl_w, search_start)
            log(f"  Sobel单峰修正: {raw} - {sl_w} = {sobel_corrected}px")
        else:
            raw = int(np.argmax(region)) + search_start
            sobel_corrected = max(raw - sl_w, search_start)
            log(f"  Sobel最大值修正: {raw} → {sobel_corrected}px")
    except Exception as e:
        log(f"  Sobel失败: {e}")

    # ── 最终决策 ─────────────────────────────────────────
    if template_x is not None and sobel_corrected is not None:
        diff = abs(template_x - sobel_corrected)
        if diff <= 25:
            # 两者接近，加权：模板匹配占 70%，Sobel 占 30%
            gap_x = int(template_x * 0.7 + sobel_corrected * 0.3)
            log(f"  两者接近(diff={diff}px)，加权: gap_x={gap_x}px")
        else:
            # 差异大，优先模板匹配
            gap_x = template_x
            log(f"  差异较大(diff={diff}px)，采用模板匹配: gap_x={gap_x}px")
    elif template_x is not None:
        gap_x = template_x
    elif sobel_corrected is not None:
        gap_x = sobel_corrected
    else:
        gap_x = int(bg_w * 0.45)
        log(f"  全部失败，使用默认: gap_x={gap_x}px")

    log(f"  最终 gap_x={gap_x}px")
    return gap_x


async def solve_captcha_precise(page, captcha_frame) -> bool:
    """精准版验证码求解"""
    log("  获取验证码元素...")

    bg_el  = captcha_frame.locator(".captcha-verify-image").first
    sl_el  = captcha_frame.locator(".captcha-verify-image-slide").first
    btn_el = captcha_frame.locator(".captcha-slider-btn").first

    bg_bb  = await bg_el.bounding_box()
    sl_bb  = await sl_el.bounding_box()
    btn_bb = await btn_el.bounding_box()

    if not btn_bb or not bg_bb:
        log("  无法获取元素 bbox")
        return False

    log(f"  背景: {int(bg_bb['width'])}x{int(bg_bb['height'])} @ ({int(bg_bb['x'])},{int(bg_bb['y'])})")
    log(f"  滑块图: {int(sl_bb['width'])}x{int(sl_bb['height'])} @ ({int(sl_bb['x'])},{int(sl_bb['y'])})")
    log(f"  滑块btn: {int(btn_bb['width'])}x{int(btn_bb['height'])} @ ({int(btn_bb['x'])},{int(btn_bb['y'])})")

    # 截取背景图（屏幕坐标直接截取）
    bg_clip = {"x": bg_bb["x"], "y": bg_bb["y"], "width": bg_bb["width"], "height": bg_bb["height"]}
    sl_clip = {"x": sl_bb["x"], "y": sl_bb["y"], "width": sl_bb["width"], "height": sl_bb["height"]}

    bg_bytes = await page.screenshot(clip=bg_clip)
    sl_bytes = await page.screenshot(clip=sl_clip)

    # 保存截图用于调试
    ts = datetime.now().strftime("%H%M%S")
    Image.open(io.BytesIO(bg_bytes)).save(str(SAVE_DIR / f"debug_bg_{ts}.png"))
    log(f"  截图已保存: debug_bg_{ts}.png")

    # 计算滑动距离（屏幕坐标）
    gap_x = find_gap_by_screenshot(bg_bytes, sl_bytes)

    # 坐标说明：
    #   bg_bb["x"]  = 背景图在主页面的左边缘 x
    #   btn_bb["x"] = 滑块btn在主页面的左边缘 x（初始位置）
    #   gap_x       = 缺口左边缘相对于背景图左侧的偏移量（截图坐标=屏幕距离）
    #
    # 我们希望：让滑块中心对准缺口中心
    #   缺口中心绝对 x = bg_bb["x"] + gap_x + sl_bb["width"] / 2
    #   滑块中心绝对 x（初始）= btn_bb["x"] + btn_bb["width"] / 2
    #   需要滑动 = 缺口中心 - 滑块中心（初始）
    sl_w_half = sl_bb["width"] / 2
    btn_w_half = btn_bb["width"] / 2
    gap_center_abs = bg_bb["x"] + gap_x + sl_w_half
    btn_center_abs = btn_bb["x"] + btn_w_half
    slide_distance = gap_center_abs - btn_center_abs
    log(f"  gap_x={gap_x}  缺口中心={int(gap_center_abs)}  btn中心={int(btn_center_abs)}  滑动={int(slide_distance)}px")

    # 限制范围
    max_slide = bg_bb["width"] - btn_bb["width"] - 5
    slide_distance = max(min(slide_distance, max_slide), 5)
    log(f"  最终滑动距离: {int(slide_distance)}px (max={int(max_slide)}px)")

    # 滑块中心点
    cx = btn_bb["x"] + btn_bb["width"] / 2
    cy = btn_bb["y"] + btn_bb["height"] / 2

    # 移动到滑块上
    await page.mouse.move(cx - 5, cy + random.randint(-3, 3))
    await asyncio.sleep(random.uniform(0.15, 0.3))
    await page.mouse.move(cx, cy)
    await asyncio.sleep(random.uniform(0.08, 0.18))
    await page.mouse.down()
    await asyncio.sleep(random.uniform(0.05, 0.12))

    # 沿路径滑动
    path = human_slide_path(int(slide_distance), steps=65)
    for dx, dy in path:
        tx = cx + dx
        ty = cy + dy
        await page.mouse.move(tx, ty)
        frac = abs(dx) / max(abs(slide_distance), 1)
        if frac < 0.5:
            await asyncio.sleep(random.uniform(0.005, 0.008))
        elif frac < 0.85:
            await asyncio.sleep(random.uniform(0.010, 0.018))
        else:
            await asyncio.sleep(random.uniform(0.025, 0.045))

    await page.mouse.move(cx + slide_distance + random.randint(-1, 1), cy + random.randint(-1, 1))
    await asyncio.sleep(random.uniform(0.08, 0.15))
    await page.mouse.up()

    log("  滑动完成，等待结果...")
    await asyncio.sleep(3)

    title = await page.title()
    url_now = page.url
    log(f"  结果: title={title}  url={url_now[:60]}")

    if "验证码" not in title and "captcha" not in url_now.lower():
        return True
    frames_after = [f for f in page.frames if "verifycenter" in f.url or "captcha" in f.url]
    if not frames_after:
        return True
    return False


async def test_captcha():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False, slow_mo=10,
            args=["--disable-blink-features=AutomationControlled","--no-sandbox",
                  "--window-size=1440,900","--window-position=0,0"],
        )
        ctx = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="zh-CN", viewport={"width":1440,"height":900},
        )
        await ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined});")
        cookies = json.loads(SESSION_FILE.read_text())
        valid = []
        for c in cookies:
            try:
                cl = {"name":c["name"],"value":c["value"],"domain":c.get("domain",".douyin.com"),"path":c.get("path","/")}
                if c.get("sameSite") in ["Strict","Lax","None"]: cl["sameSite"] = c["sameSite"]
                valid.append(cl)
            except: pass
        await ctx.add_cookies(valid)

        page = await ctx.new_page()
        log("访问视频详情页...")
        await page.goto("https://www.douyin.com/video/7509445758202940707",
                        wait_until="domcontentloaded", timeout=20000)
        await asyncio.sleep(5)

        title = await page.title()
        log(f"Title: {title}")

        if "验证码" not in title:
            log("无验证码，直接成功")
            await browser.close()
            return

        for attempt in range(1, 7):
            log(f"\n=== 第 {attempt}/6 次尝试 ===")

            captcha_frame = None
            for frame in page.frames:
                if "verifycenter" in frame.url or "captcha" in frame.url:
                    captcha_frame = frame
                    break

            if not captcha_frame:
                log("验证码 iframe 消失！成功！")
                break

            ok = await solve_captcha_precise(page, captcha_frame)
            if ok:
                log("✅ 验证通过！")
                await page.screenshot(path=str(SAVE_DIR / "captcha_success.png"))
                break

            await asyncio.sleep(2)
            # 刷新验证码（点击刷新按钮）
            try:
                refresh_btn = captcha_frame.locator(".vc-captcha-refresh").first
                refresh_bb = await refresh_btn.bounding_box()
                if refresh_bb:
                    rx = refresh_bb["x"] + refresh_bb["width"] / 2
                    ry = refresh_bb["y"] + refresh_bb["height"] / 2
                    await page.mouse.click(rx, ry)
                    log(f"  点击刷新按钮 ({int(rx)},{int(ry)})")
                    await asyncio.sleep(1.5)
            except:
                pass
        else:
            log("❌ 6次均未通过")

        await asyncio.sleep(3)
        await browser.close()

asyncio.run(test_captcha())
