#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音登录 & 保存 Session
用法：python3 douyin_login.py [工作目录]

执行后：
  1. 打开抖音首页（Chromium）
  2. 用户手动扫码登录（或已有账号点击登录）
  3. 检测到登录成功后，自动保存 cookies 到 douyin_session.json
"""
import asyncio, json, sys
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

WORK_DIR     = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(".").resolve()
SESSION_FILE = WORK_DIR / "douyin_session.json"

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

async def login():
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox",
                  "--window-size=1440,900", "--window-position=0,0"],
        )
        ctx = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="zh-CN",
            viewport={"width": 1440, "height": 900},
        )
        await ctx.add_init_script(
            "Object.defineProperty(navigator,'webdriver',{get:()=>undefined});"
        )
        page = await ctx.new_page()

        log("导航到抖音首页...")
        await page.goto("https://www.douyin.com", wait_until="domcontentloaded", timeout=30000)
        log("请在浏览器中扫码/点击登录。等待登录成功（最多 120 秒）...")

        # 轮询检测登录状态：cookie 中出现 passport_csrf_token 或 sessionid
        for i in range(120):
            await asyncio.sleep(1)
            cookies = await ctx.cookies()
            cookie_names = {c["name"] for c in cookies}
            if "passport_csrf_token" in cookie_names or "sessionid" in cookie_names:
                log(f"✅ 检测到登录成功（{i+1}s）")
                break
        else:
            log("⚠ 超时，请检查是否已登录")

        cookies = await ctx.cookies()
        SESSION_FILE.write_text(json.dumps(cookies, ensure_ascii=False, indent=2))
        log(f"✅ Session 已保存到 {SESSION_FILE}（共 {len(cookies)} 个 cookie）")

        await browser.close()

asyncio.run(login())
