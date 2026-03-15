#!/usr/bin/env python3
"""
Outlook 邮件读取脚本 - Token 模式
复用 owa_calendar.py 的 Bearer Token 缓存（~/.outlook/token.json）
调用 OWA REST API 读取邮件
"""
import json, time, sys, argparse, requests, re, subprocess
from pathlib import Path
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).parent
OUTLOOK_DIR = Path.home() / ".outlook"
with open(OUTLOOK_DIR / "config.json") as f:
    cfg = json.load(f)

COOKIE_FILE = OUTLOOK_DIR / "cookies.json"
TOKEN_FILE = OUTLOOK_DIR / "token.json"
TOKEN_TTL = 3600


def load_cached_token():
    if not TOKEN_FILE.exists():
        return None
    with open(TOKEN_FILE) as f:
        data = json.load(f)
    if time.time() - data.get("saved_at", 0) < TOKEN_TTL:
        return data.get("bearer")
    return None


def run_login_and_notify():
    STATUS_FILE = OUTLOOK_DIR / "login_status.txt"
    login_script = BASE_DIR / "login.py"
    STATUS_FILE.write_text("")
    proc = subprocess.Popen(
        [sys.executable, str(login_script)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print("[AUTH] Cookie 已过期，正在自动重新登录...", flush=True)
    notified_number = False
    for _ in range(150):
        time.sleep(2)
        try:
            content = STATUS_FILE.read_text()
        except:
            content = ""
        if not notified_number:
            m = re.search(r'\[NUMBER:(\d+)\]', content)
            if m:
                print(f"[MFA] 请在 Microsoft Authenticator 上选择数字：【{m.group(1)}】", flush=True)
                notified_number = True
        if "[DONE]" in content:
            proc.wait()
            print("[AUTH] 登录成功，继续执行...", flush=True)
            return
    proc.kill()
    print("[AUTH_FAILED] 登录超时，请手动运行 login.py", flush=True)
    sys.exit(1)


def fetch_token_via_playwright():
    if not COOKIE_FILE.exists():
        run_login_and_notify()

    with open(COOKIE_FILE) as f:
        saved_cookies = json.load(f)

    owa_token = None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        ctx.add_cookies(saved_cookies)

        def handle_request(req):
            nonlocal owa_token
            if owa_token:
                return
            auth = req.headers.get("authorization", "")
            if auth.startswith("Bearer ") and "outlook.office.com" in req.url:
                owa_token = auth[7:]

        ctx.on("request", handle_request)
        page = ctx.new_page()
        page.goto("https://outlook.office.com/mail/", timeout=30000)
        page.wait_for_load_state("load", timeout=20000)
        time.sleep(10)

        if "login.microsoftonline.com" in page.url:
            browser.close()
            run_login_and_notify()
            return fetch_token_via_playwright()

        browser.close()

    if not owa_token:
        print("[AUTH_FAILED] 未能获取 Bearer Token，请重新运行 login.py", file=sys.stderr)
        sys.exit(1)

    TOKEN_FILE.parent.mkdir(exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        json.dump({"bearer": owa_token, "saved_at": time.time()}, f)

    return owa_token


def get_token():
    token = load_cached_token()
    if token:
        return token
    return fetch_token_via_playwright()


def fetch_mail_api(token, folder="Inbox", limit=20, unread_only=False, search=None, since=None):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }
    params = {
        "$select": "Subject,From,ReceivedDateTime,IsRead,BodyPreview,HasAttachments,Importance",
        "$top": limit,
    }
    if not search:
        params["$orderby"] = "ReceivedDateTime desc"

    filters = []
    if unread_only:
        filters.append("IsRead eq false")
    if since:
        filters.append(f"ReceivedDateTime ge {since}")
    if filters:
        params["$filter"] = " and ".join(filters)

    if search:
        params["$search"] = f'"{search}"'

    url = f"https://outlook.office.com/api/v2.0/me/MailFolders/{folder}/Messages"
    resp = requests.get(url, headers=headers, params=params, timeout=15)

    if resp.status_code == 401:
        return None, "token_expired"
    if not resp.ok:
        return None, f"api_error:{resp.status_code}:{resp.text[:300]}"
    return resp.json().get("value", []), None


def parse_mails(raw_mails):
    mails = []
    for m in raw_mails:
        received = m.get("ReceivedDateTime", "")[:16].replace("T", " ")
        sender = m.get("From", {}).get("EmailAddress", {})
        mails.append({
            "subject": m.get("Subject", "（无主题）"),
            "from_name": sender.get("Name", ""),
            "from_email": sender.get("Address", ""),
            "received": received,
            "is_read": m.get("IsRead", True),
            "has_attachment": m.get("HasAttachments", False),
            "importance": m.get("Importance", "Normal"),
            "preview": m.get("BodyPreview", "")[:100],
        })
    return mails


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--unread", action="store_true", help="只看未读邮件")
    parser.add_argument("--today", action="store_true", help="今天收到的邮件")
    parser.add_argument("--limit", type=int, default=20, help="最多返回条数（默认20）")
    parser.add_argument("--search", type=str, help="搜索主题或发件人关键词")
    parser.add_argument("--folder", type=str, default="Inbox", help="邮件文件夹（默认Inbox）")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    args = parser.parse_args()

    since = None
    if args.today:
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        since = today.strftime("%Y-%m-%dT%H:%M:%SZ")

    token = get_token()
    raw_mails, err = fetch_mail_api(
        token,
        folder=args.folder,
        limit=args.limit,
        unread_only=args.unread,
        search=args.search,
        since=since,
    )

    if err == "token_expired":
        if TOKEN_FILE.exists():
            TOKEN_FILE.unlink()
        token = fetch_token_via_playwright()
        raw_mails, err = fetch_mail_api(
            token,
            folder=args.folder,
            limit=args.limit,
            unread_only=args.unread,
            search=args.search,
            since=since,
        )

    if err:
        print(f"[ERROR] {err}", file=sys.stderr)
        sys.exit(1)

    mails = parse_mails(raw_mails)

    if args.json:
        print(json.dumps(mails, ensure_ascii=False, indent=2))
    else:
        label = "未读邮件" if args.unread else "邮件"
        print(f"\n📬 {args.folder} {label}（共 {len(mails)} 封）\n")
        for m in mails:
            read_icon = "⚪" if m["is_read"] else "🔵"
            attach_icon = "📎" if m["has_attachment"] else "  "
            imp_icon = "🔴" if m["importance"] == "High" else "  "
            # UTC+8
            try:
                dt = datetime.strptime(m["received"], "%Y-%m-%d %H:%M")
                dt_local = dt + timedelta(hours=8)
                received_str = dt_local.strftime("%m-%d %H:%M")
            except:
                received_str = m["received"]
            print(f"{read_icon}{attach_icon}{imp_icon} {received_str} | {m['from_name'] or m['from_email']}")
            print(f"   主题: {m['subject']}")
            if m["preview"]:
                print(f"   摘要: {m['preview']}")
            print()


if __name__ == "__main__":
    main()
