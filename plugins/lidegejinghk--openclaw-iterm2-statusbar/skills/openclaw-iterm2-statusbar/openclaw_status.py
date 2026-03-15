#!/usr/bin/env python3
"""
OpenClaw Cost Status Bar for iTerm2
显示 session 费用和上下文用量

安装：已放在 AutoLaunch 目录，重启 iTerm2 自动加载
启用：Preferences → Profiles → Session → Status Bar → Configure → 添加 "OpenClaw" 组件
"""

import iterm2
import asyncio
import json
import re
import urllib.request
import urllib.error
import plistlib
import os

GATEWAY_URL = "http://127.0.0.1:18789"
PLIST_PATH = os.path.expanduser("~/Library/LaunchAgents/ai.openclaw.gateway.plist")


def get_token():
    token = os.environ.get("OPENCLAW_GATEWAY_TOKEN")
    if token:
        return token
    try:
        with open(PLIST_PATH, "rb") as f:
            plist = plistlib.load(f)
            return plist.get("EnvironmentVariables", {}).get("OPENCLAW_GATEWAY_TOKEN", "")
    except Exception:
        return ""


def get_reserve_tokens():
    try:
        config_path = os.path.expanduser("~/.openclaw/openclaw.json")
        with open(config_path) as f:
            config = json.load(f)
        return (
            config.get("agents", {})
            .get("defaults", {})
            .get("compaction", {})
            .get("reserveTokensFloor", 24000)
        )
    except Exception:
        return 24000


def usage_color(pct, threshold_pct):
    """根据用量占阈值的比例返回颜色 emoji"""
    if pct >= threshold_pct:
        return "🔴"
    elif pct >= int(threshold_pct * 0.8):
        return "🟠"
    elif pct >= 50:
        return "🟡"
    else:
        return "🟢"


def fetch_session_cost(token, session_key):
    try:
        payload = json.dumps({"tool": "session_status", "sessionKey": session_key}).encode()
        req = urllib.request.Request(
            f"{GATEWAY_URL}/tools/invoke",
            data=payload,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
        text = data.get("result", {}).get("details", {}).get("statusText", "")
        m = re.search(r"💵 Cost: \$([0-9.]+)", text)
        return float(m.group(1)) if m else 0.0
    except Exception:
        return 0.0


def fetch_status():
    token = get_token()
    if not token:
        return "⚠️ no token"
    try:
        # 当前 main session 状态
        payload = json.dumps({"tool": "session_status", "sessionKey": "main"}).encode()
        req = urllib.request.Request(
            f"{GATEWAY_URL}/tools/invoke",
            data=payload,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())

        text = data.get("result", {}).get("details", {}).get("statusText", "")
        cost_m = re.search(r"💵 Cost: \$([0-9.]+)", text)
        ctx = re.search(r"📚 Context: (\S+)/(\S+) \((\d+)%\)", text)
        model_m = re.search(r"🧠 Model: (\S+/\S+)", text)
        main_cost = float(cost_m.group(1)) if cost_m else 0.0
        model_name = model_m.group(1) if model_m else "?"

        # 所有 session 总费用
        sl_payload = json.dumps({"tool": "sessions_list", "args": {"limit": 20}, "sessionKey": "main"}).encode()
        req2 = urllib.request.Request(
            f"{GATEWAY_URL}/tools/invoke",
            data=sl_payload,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req2, timeout=5) as resp2:
            sl_data = json.loads(resp2.read().decode())

        sessions = sl_data.get("result", {}).get("details", {}).get("sessions", [])
        total_cost = main_cost
        for s in sessions:
            key = s.get("key", "")
            if key and key != "agent:main:main":
                total_cost += fetch_session_cost(token, key)

        # 上下文 + 压缩阈值
        if ctx:
            used, total_str, pct = ctx.group(1), ctx.group(2), ctx.group(3)
            pct_int = int(pct)
            try:
                total_tokens = int(float(total_str.rstrip("k")) * 1000)
                reserve = get_reserve_tokens()
                threshold_pct = int((total_tokens - reserve) / total_tokens * 100)
                color = usage_color(pct_int, threshold_pct)
                ctx_str = f"{color} {used}/{total_str} ({pct}%)"
                threshold_str = f"⚡{threshold_pct}%"
            except Exception:
                ctx_str = f"{used}/{total_str} ({pct}%)"
                threshold_str = "⚡?"
        else:
            ctx_str = "?"
            threshold_str = "⚡?"

        return f"[{model_name}] 🤖 main  |  💵 ${main_cost:.4f} (total ${total_cost:.4f})  |  {ctx_str}  |  {threshold_str}"

    except urllib.error.URLError:
        return "⚠️ offline"
    except Exception:
        return "⚠️ err"


async def main(connection):
    component = iterm2.StatusBarComponent(
        short_description="OpenClaw",
        detailed_description="OpenClaw session cost and context usage",
        knobs=[],
        exemplar="[model/name] 🤖 main | 💵 $0.0000 (total $0.0000) | 🟢 10k/200k (5%) | ⚡88%",
        update_cadence=30,
        identifier="ai.openclaw.cost-status",
    )

    @iterm2.StatusBarRPC
    async def cost_coroutine(knobs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, fetch_status)

    await component.async_register(connection, cost_coroutine)


iterm2.run_forever(main)
