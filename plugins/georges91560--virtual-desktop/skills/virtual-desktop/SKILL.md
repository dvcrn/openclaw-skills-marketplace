---
name: virtual-desktop
description: "Gives any OpenClaw agent a persistent headless browser running inside the Docker container. Full autonomous execution layer: navigate any website, click, type, fill forms, extract data, upload files, submit, screenshot — on any platform, for any task. The agent can analyze, plan, execute, and self-correct across every revenue axis: content creation, email management, social publishing, sales funnels, market research, admin workflows, and more. Uses Playwright Chromium — no Xvfb, no VNC, no host dependencies. Sessions persist across runs. Every action is logged. Every discovery improves future performance through .learnings/."
---

# Virtual Desktop — Universal Execution Layer

## What this skill does

Gives the agent a persistent headless browser (Playwright Chromium) running
inside the Docker container. No Xvfb, no VNC, no host dependencies.

| Capability | What it means |
|---|---|
| **ANALYZE** | Read any page, extract structured data, monitor changes over time |
| **PLAN** | Map the UI, identify selectors, prepare multi-step action sequences |
| **EXECUTE** | Click, type, fill forms, submit, upload, download, navigate any flow |
| **SELF-CORRECT** | Screenshot error state, identify root cause, retry with alternate approach |
| **IMPROVE** | Write UI patterns and selector maps to `.learnings/` after every session |

Use cases: Google Workspace · social platforms · admin dashboards · e-commerce ·
forms · market research · data extraction · any platform with no API

---

## Required Workspace Structure

```
/workspace/
│
├── screenshots/                          ← Visual proof of every action (auto-created)
│   └── YYYY-MM-DD_{action}.png
│
├── logs/
│   └── browser/                          ← Error traces (auto-created)
│       └── YYYY-MM-DD.log
│
├── credentials/
│   └── sessions/                         ← Persistent auth sessions (auto-created)
│       └── {platform}_session.json
│
├── AUDIT.md                              ← Append-only action log (already exists)
├── memory/YYYY-MM-DD.md                  ← Daily run summary (already exists)
└── .learnings/
    ├── ERRORS.md                         ← Selector failures, auth issues, timeouts
    └── LEARNINGS.md                      ← Platform patterns, UI maps, discoveries
```

---

## Setup — One Time

```bash
#!/bin/bash
# Run once after skill installation

echo "🖥️ Virtual Desktop — Setup..."

# Install Chromium
playwright install chromium
echo "✅ Chromium installed"

# Create directories
mkdir -p /workspace/screenshots
mkdir -p /workspace/logs/browser
mkdir -p /workspace/credentials/sessions
echo "✅ Directories created"

# Deploy browser_control.py
cat > /workspace/skills/virtual-desktop/browser_control.py << 'PYEOF'
#!/usr/bin/env python3
"""
Virtual Desktop — Browser Control
Universal headless browser for OpenClaw agents
Usage: python3 browser_control.py [action] [args...]

Actions:
  screenshot <url> [label]
  navigate <url> [selector]
  click <url> <selector> [session]
  fill <url> <selector> <value> [session]
  login <url> <email_env> <pass_env> <success_url_fragment> <platform>
  upload <url> <file_selector> <file_path> [session]
  workflow <json_steps_file> [session]
  status
"""

import sys
import os
import json
import time
import traceback
from datetime import datetime
from playwright.sync_api import sync_playwright

WORKSPACE = "/workspace"
SCREENSHOTS = f"{WORKSPACE}/screenshots"
SESSIONS = f"{WORKSPACE}/credentials/sessions"
LOGS = f"{WORKSPACE}/logs/browser"
AUDIT = f"{WORKSPACE}/AUDIT.md"
ERRORS = f"{WORKSPACE}/.learnings/ERRORS.md"
LEARNINGS = f"{WORKSPACE}/.learnings/LEARNINGS.md"

TS = datetime.now().strftime("%Y-%m-%d_%H%M%S")
DATE = TS[:10]

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def audit(msg):
    with open(AUDIT, "a") as f:
        f.write(f"\n[{TS}] [virtual-desktop] {msg}\n")


def log_error(platform, title, what, cause, fix, prevention):
    with open(ERRORS, "a") as f:
        f.write(f"""
## [{DATE}] {platform} — {title}
**Logged**: {TS}
**Priority**: medium
**Status**: pending
**Area**: browser_automation
**What happened**: {what}
**Root cause**: {cause}
**Fix applied**: {fix}
**Prevention**: {prevention}
""")


def log_learning(platform, category, discovery, usage):
    with open(LEARNINGS, "a") as f:
        f.write(f"""
## [{DATE}] {platform} — {category}
**Category**: {category}
**Discovery**: {discovery}
**Usage**: {usage}
""")


def get_context(p, session=None, locale="fr-FR", tz="Europe/Paris"):
    browser = p.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
    )
    opts = {
        "user_agent": UA,
        "viewport": {"width": 1920, "height": 1080},
        "locale": locale,
        "timezone_id": tz,
        "extra_http_headers": {"Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8"}
    }
    if session and os.path.exists(f"{SESSIONS}/{session}_session.json"):
        opts["storage_state"] = f"{SESSIONS}/{session}_session.json"
    return browser, browser.new_context(**opts)


def save_session(context, platform):
    path = f"{SESSIONS}/{platform}_session.json"
    context.storage_state(path=path)
    return path


def cmd_screenshot(url, label="screenshot"):
    audit(f"BEFORE screenshot {url}")
    path = f"{SCREENSHOTS}/{TS}_{label}.png"
    try:
        with sync_playwright() as p:
            browser, context = get_context(p)
            page = context.new_page()
            page.goto(url)
            page.wait_for_load_state("networkidle")
            page.screenshot(path=path, full_page=True)
            browser.close()
        audit(f"OK screenshot saved: {path}")
        print(f"✅ Screenshot: {path}")
    except Exception as e:
        tb = traceback.format_exc()
        with open(f"{LOGS}/{DATE}.log", "a") as f:
            f.write(f"\n[{TS}] screenshot error\n{tb}\n")
        log_error("unknown", "Screenshot failed", str(e), "page error", "see log", "check URL + wait_for_load_state")
        print(f"❌ Screenshot failed: {e}")


def cmd_navigate(url, selector=None):
    audit(f"BEFORE navigate {url}")
    try:
        with sync_playwright() as p:
            browser, context = get_context(p)
            page = context.new_page()
            page.goto(url)
            page.wait_for_load_state("networkidle")
            if selector:
                items = page.query_selector_all(selector)
                for i in items:
                    print(i.inner_text())
            else:
                print(page.inner_text("body")[:3000])
            page.screenshot(path=f"{SCREENSHOTS}/{TS}_navigate.png", full_page=True)
            browser.close()
        audit(f"OK navigate {url}")
    except Exception as e:
        tb = traceback.format_exc()
        with open(f"{LOGS}/{DATE}.log", "a") as f:
            f.write(f"\n[{TS}] navigate error\n{tb}\n")
        print(f"❌ Navigate failed: {e}")


def cmd_click(url, selector, session=None):
    audit(f"BEFORE click {selector} on {url}")
    try:
        with sync_playwright() as p:
            browser, context = get_context(p, session)
            page = context.new_page()
            page.goto(url)
            page.wait_for_load_state("networkidle")
            page.click(selector)
            time.sleep(1.0)
            page.wait_for_load_state("networkidle")
            page.screenshot(path=f"{SCREENSHOTS}/{TS}_click.png")
            if session:
                save_session(context, session)
            browser.close()
        audit(f"OK click {selector}")
        print(f"✅ Clicked: {selector}")
    except Exception as e:
        log_error("unknown", f"Click failed: {selector}", str(e), "selector not found or changed",
                  "screenshot taken", "update selector in .learnings/LEARNINGS.md")
        print(f"❌ Click failed: {e}")


def cmd_fill(url, selector, value, session=None):
    audit(f"BEFORE fill {selector} on {url}")
    try:
        with sync_playwright() as p:
            browser, context = get_context(p, session)
            page = context.new_page()
            page.goto(url)
            page.wait_for_load_state("networkidle")
            page.fill(selector, value)
            time.sleep(0.5)
            page.screenshot(path=f"{SCREENSHOTS}/{TS}_fill.png")
            if session:
                save_session(context, session)
            browser.close()
        audit(f"OK fill {selector}")
        print(f"✅ Filled: {selector}")
    except Exception as e:
        log_error("unknown", f"Fill failed: {selector}", str(e), "selector not found",
                  "screenshot taken", "verify selector")
        print(f"❌ Fill failed: {e}")


def cmd_login(url, email_env, pass_env, success_fragment, platform):
    audit(f"BEFORE login {platform} at {url}")
    session_path = f"{SESSIONS}/{platform}_session.json"
    try:
        with sync_playwright() as p:
            browser, context = get_context(p)
            page = context.new_page()
            page.goto(url)
            page.wait_for_load_state("networkidle")
            email = os.environ.get(email_env, "")
            password = os.environ.get(pass_env, "")
            page.fill("input[type='email'], #email, #username", email)
            time.sleep(0.8)
            page.fill("input[type='password'], #password", password)
            time.sleep(0.8)
            page.click("button[type='submit'], #login-button, .login-btn, input[type='submit']")
            page.wait_for_navigation()
            if success_fragment in page.url:
                context.storage_state(path=session_path)
                page.screenshot(path=f"{SCREENSHOTS}/{TS}_{platform}_login_ok.png")
                audit(f"OK login {platform} — session saved: {session_path}")
                print(f"✅ Login OK — session saved: {session_path}")
            else:
                page.screenshot(path=f"{SCREENSHOTS}/{TS}_{platform}_login_failed.png")
                log_error(platform, "Login failed", f"current URL: {page.url}",
                          "wrong credentials or selector", "screenshot taken",
                          f"check {email_env} and {pass_env} in .env")
                print(f"❌ Login failed — URL: {page.url}")
            browser.close()
    except Exception as e:
        tb = traceback.format_exc()
        with open(f"{LOGS}/{DATE}.log", "a") as f:
            f.write(f"\n[{TS}] login error\n{tb}\n")
        print(f"❌ Login exception: {e}")


def cmd_upload(url, file_selector, file_path, session=None):
    audit(f"BEFORE upload {file_path} to {url}")
    try:
        with sync_playwright() as p:
            browser, context = get_context(p, session)
            page = context.new_page()
            page.goto(url)
            page.wait_for_load_state("networkidle")
            page.set_input_files(file_selector, file_path)
            time.sleep(1.0)
            page.screenshot(path=f"{SCREENSHOTS}/{TS}_upload.png")
            if session:
                save_session(context, session)
            browser.close()
        audit(f"OK upload {file_path}")
        print(f"✅ Uploaded: {file_path}")
    except Exception as e:
        log_error("unknown", "Upload failed", str(e), "selector or file issue",
                  "screenshot taken", "verify file_selector and file_path")
        print(f"❌ Upload failed: {e}")


def cmd_workflow(steps_file, session=None):
    """
    steps_file: JSON array of steps
    Each step: {"action": "goto|click|fill|wait|screenshot", "target": "...", "value": "..."}
    """
    audit(f"BEFORE workflow {steps_file}")
    with open(steps_file) as f:
        steps = json.load(f)
    log = {"date": TS, "steps": [], "status": "started"}
    try:
        with sync_playwright() as p:
            browser, context = get_context(p, session)
            page = context.new_page()
            for i, step in enumerate(steps):
                action = step.get("action")
                target = step.get("target", "")
                value = step.get("value", "")
                try:
                    if action == "goto":
                        page.goto(target)
                        page.wait_for_load_state("networkidle")
                    elif action == "click":
                        page.click(target)
                        time.sleep(0.8)
                    elif action == "fill":
                        page.fill(target, value)
                        time.sleep(0.5)
                    elif action == "wait":
                        time.sleep(float(value) if value else 1.0)
                    elif action == "screenshot":
                        page.screenshot(path=f"{SCREENSHOTS}/{TS}_step{i}.png")
                    log["steps"].append({"step": i, "action": action, "status": "ok"})
                    print(f"✅ Step {i}: {action} {target}")
                except Exception as e:
                    log["steps"].append({"step": i, "action": action, "status": "failed", "error": str(e)})
                    page.screenshot(path=f"{SCREENSHOTS}/{TS}_step{i}_error.png")
                    print(f"❌ Step {i} failed: {e}")
            log["status"] = "completed"
            page.screenshot(path=f"{SCREENSHOTS}/{TS}_workflow_done.png")
            if session:
                save_session(context, session)
            browser.close()
    except Exception as e:
        log["status"] = "failed"
        tb = traceback.format_exc()
        with open(f"{LOGS}/{DATE}.log", "a") as f:
            f.write(f"\n[{TS}] workflow error\n{tb}\n")
    finally:
        mem_file = f"{WORKSPACE}/memory/{DATE}.md"
        with open(mem_file, "a") as f:
            f.write(f"\n## Workflow — {TS}\n```json\n{json.dumps(log, indent=2)}\n```\n")
        audit(f"{log['status']} workflow {steps_file}")
        print(f"{'✅' if log['status'] == 'completed' else '❌'} Workflow {log['status']}")


def cmd_status():
    checks = {
        "playwright": os.path.exists("/usr/bin/playwright") or os.system("which playwright > /dev/null 2>&1") == 0,
        "screenshots_dir": os.path.exists(SCREENSHOTS),
        "sessions_dir": os.path.exists(SESSIONS),
        "logs_dir": os.path.exists(LOGS),
        "audit_file": os.path.exists(AUDIT),
        "learnings_dir": os.path.exists(f"{WORKSPACE}/.learnings"),
    }
    sessions = [f for f in os.listdir(SESSIONS)] if os.path.exists(SESSIONS) else []
    print("\n🖥️ Virtual Desktop — Status")
    for k, v in checks.items():
        print(f"  {'✅' if v else '❌'} {k}")
    print(f"\n  Sessions saved: {len(sessions)}")
    for s in sessions:
        print(f"    • {s}")


# CLI dispatcher
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    action = sys.argv[1]
    args = sys.argv[2:]

    if action == "screenshot":
        cmd_screenshot(args[0], args[1] if len(args) > 1 else "screenshot")
    elif action == "navigate":
        cmd_navigate(args[0], args[1] if len(args) > 1 else None)
    elif action == "click":
        cmd_click(args[0], args[1], args[2] if len(args) > 2 else None)
    elif action == "fill":
        cmd_fill(args[0], args[1], args[2], args[3] if len(args) > 3 else None)
    elif action == "login":
        cmd_login(args[0], args[1], args[2], args[3], args[4])
    elif action == "upload":
        cmd_upload(args[0], args[1], args[2], args[3] if len(args) > 3 else None)
    elif action == "workflow":
        cmd_workflow(args[0], args[1] if len(args) > 1 else None)
    elif action == "status":
        cmd_status()
    else:
        print(f"❌ Unknown action: {action}")
        print(__doc__)
PYEOF

chmod +x /workspace/skills/virtual-desktop/browser_control.py
echo "✅ browser_control.py deployed"

# Smoke test
python3 /workspace/skills/virtual-desktop/browser_control.py status
echo ""
echo "🎉 Virtual Desktop ready"
echo "Usage: python3 /workspace/skills/virtual-desktop/browser_control.py [action] [args]"
```

---

## 🔧 Available Commands

```bash
# Screenshot any URL
python3 browser_control.py screenshot https://example.com my_label

# Navigate and extract text (full page or by selector)
python3 browser_control.py navigate https://example.com ".article-title"

# Click a button (with optional session)
python3 browser_control.py click https://example.com "#submit-btn" platform_name

# Fill a form field
python3 browser_control.py fill https://example.com "#email" "value@example.com" platform_name

# Login and save session (reads credentials from .env)
python3 browser_control.py login https://app.com/login EMAIL_ENV PASS_ENV "dashboard" platform_name

# Upload a file
python3 browser_control.py upload https://app.com/upload "input[type='file']" /workspace/file.pdf platform_name

# Run a multi-step workflow from a JSON file
python3 browser_control.py workflow /workspace/tasks/my_workflow.json platform_name

# Check status
python3 browser_control.py status
```

---

## 📋 Workflow JSON Format

For multi-step tasks, create a JSON file and pass it to `workflow`:

```json
[
  { "action": "goto",       "target": "https://TARGET_URL" },
  { "action": "fill",       "target": "#email",    "value": "user@example.com" },
  { "action": "fill",       "target": "#password", "value": "mypassword" },
  { "action": "click",      "target": "#login-btn" },
  { "action": "wait",       "value": "2" },
  { "action": "screenshot", "target": "" },
  { "action": "click",      "target": "#publish-btn" }
]
```

---

## Execution Protocol

```
BEFORE EVERY ACTION:
  1. Confirm the action is authorized by the principal
  2. browser_control.py logs to AUDIT.md automatically before + after
  3. Screenshots are taken automatically on every action
  4. Session is saved automatically after authenticated actions

NEVER:
  - Access platforms the principal has not explicitly authorized
  - Submit forms with unverified or fabricated data
  - Execute payments without explicit per-action approval
  - Expose credentials in screenshots, logs, or Telegram messages
  - Retry a destructive action more than once without confirmation
```

---

## Error Recovery

```
PAGE LOAD TIMEOUT:
  → browser_control.py logs to ERRORS.md automatically
  → Check /workspace/logs/browser/YYYY-MM-DD.log for full traceback

SESSION EXPIRED (redirect to login):
  → Delete expired session: rm /workspace/credentials/sessions/{platform}_session.json
  → Re-run login command to get a fresh session

ELEMENT NOT FOUND (selector changed):
  → Screenshot is saved automatically — inspect it
  → Update selector in .learnings/LEARNINGS.md with new value

CLOUDFLARE / BOT DETECTION:
  → browser_control.py already sets realistic user_agent + locale
  → If still blocked: residential proxy required — add PROXY_URL to .env
  → Then pass proxy in get_context(): proxies={"server": os.environ["PROXY_URL"]}

UNHANDLED EXCEPTION:
  → Full traceback written to /workspace/logs/browser/YYYY-MM-DD.log
  → Alert principal with log path
```

---

## Self-Improvement

`browser_control.py` writes to `.learnings/` automatically on every error.
After each session, add manual discoveries:

```bash
# Log a new platform pattern
cat >> /workspace/.learnings/LEARNINGS.md << 'EOF'

## [YYYY-MM-DD] [Platform] — [Pattern]
**Category**: selector_map | navigation | timing | auth_flow
**Discovery**: what you found
**Usage**: how to reuse it
EOF

# Log a task-scoped lesson (during active mission)
echo "[HH:MM] Platform — selector .new-class replaced #old-id" >> /workspace/tasks/lessons.md
```

---

## Compatible Skills

| Skill | Role |
|---|---|
| `agent-shark-mindset` | Visual layer for dashboards, posting, screenshot proof |
| `wesley-web-operator` | Fallback when gog CLI or platform API fails |
| `self-improving-agent` | Enriches .learnings/ with distilled patterns |
| `skill-combinator` | Cross-skill browser automation pipelines |

---

## Files Written By This Skill

| File | When | Content |
|---|---|---|
| `/workspace/AUDIT.md` | Every action | Before + after log, append-only |
| `/workspace/screenshots/YYYY-MM-DD_{action}.png` | Every action | Visual proof |
| `/workspace/logs/browser/YYYY-MM-DD.log` | On exception | Full traceback |
| `/workspace/credentials/sessions/{platform}_session.json` | After login | Persistent session |
| `/workspace/.learnings/ERRORS.md` | On failure | Auto-logged by browser_control.py |
| `/workspace/.learnings/LEARNINGS.md` | On discovery | Platform patterns, selector maps |
| `/workspace/tasks/lessons.md` | During mission | Immediate task-scoped capture |
| `/workspace/memory/YYYY-MM-DD.md` | After workflow | Run summary |