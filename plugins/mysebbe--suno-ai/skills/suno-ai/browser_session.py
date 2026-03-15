from __future__ import annotations

import json
import os
import shutil
import sqlite3
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import requests
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from playwright.sync_api import sync_playwright
from pyvirtualdisplay import Display

from suno_auth import SunoAuthError

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_COOKIE_FILE = Path.home() / ".suno" / "suno_cookie.txt"
DEFAULT_RAW_COOKIE_FILE = Path.home() / ".suno" / "cookies.json"
DEFAULT_PROFILE_DIR = Path.home() / ".suno" / "chrome_gui_profile"
DEFAULT_DEBUG_DIR = Path.home() / ".suno" / "debug"
DEFAULT_LIVE_CHROMIUM_COOKIE_DB = (
    Path.home() / "snap" / "chromium" / "common" / "chromium" / "Default" / "Cookies"
)
ALLOWED_BROWSER_COOKIE_PREFIXES = ("__client", "__client_uat", "__session")
ALLOWED_BROWSER_COOKIE_NAMES = {
    "_u",
    "clerk_active_context",
    "has_logged_in_before",
    "sessionid",
    "ssr_bucket",
    "suno_device_id",
}
SAMESITE_MAP = {
    "lax": "Lax",
    "strict": "Strict",
    "none": "None",
    1: "Lax",
    2: "Strict",
    3: "None",
}


@dataclass
class BrowserRuntime:
    playwright_cm: object
    playwright: object
    context: object
    page: object
    display: object | None
    profile_dir: Path
    raw_cookie_file: Path

    def close(self) -> None:
        try:
            self.context.close()
        finally:
            try:
                self.playwright.stop()
            finally:
                if self.display is not None:
                    self.display.stop()


def ensure_parent_dir(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def save_cookie_records(path: Path, cookies: list[dict]) -> None:
    target = ensure_parent_dir(path.expanduser().resolve())
    target.write_text(json.dumps(cookies, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    target.chmod(0o600)


def load_cookie_records(path: Path) -> list[dict]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SunoAuthError(f"Cookie JSON not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SunoAuthError(f"Cookie JSON could not be parsed: {exc}") from exc
    return normalize_cookie_records(payload)


def normalize_cookie_records(payload: object) -> list[dict]:
    if isinstance(payload, dict):
        items = payload.get("cookies")
    else:
        items = payload

    if not isinstance(items, list):
        raise SunoAuthError("Cookie JSON must be a list or an object with a `cookies` list.")

    records: list[dict] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "").strip()
        value = str(item.get("value") or "").strip()
        domain = str(item.get("domain") or item.get("host_key") or "").strip()
        path = str(item.get("path") or "/").strip() or "/"
        if (
            not name
            or not value
            or not domain
            or not _is_suno_domain(domain)
            or not _is_allowed_browser_cookie(name)
            or _has_invalid_cookie_value(value)
        ):
            continue

        record = {
            "name": name,
            "value": value,
            "domain": domain,
            "path": path,
        }
        expires = _normalize_cookie_expiry(
            item.get("expires"),
            item.get("expirationDate"),
            item.get("expires_utc"),
        )
        if expires is not None:
            record["expires"] = expires

        if item.get("httpOnly") is not None:
            record["httpOnly"] = bool(item.get("httpOnly"))
        elif item.get("is_httponly") is not None:
            record["httpOnly"] = bool(item.get("is_httponly"))

        if item.get("secure") is not None:
            record["secure"] = bool(item.get("secure"))
        elif item.get("is_secure") is not None:
            record["secure"] = bool(item.get("is_secure"))

        same_site = _normalize_same_site(item.get("sameSite", item.get("samesite")))
        if same_site is not None:
            record["sameSite"] = same_site

        records.append(record)

    if not records:
        raise SunoAuthError("No usable Suno cookies were found in the JSON export.")

    deduped: dict[tuple[str, str, str], dict] = {}
    for record in records:
        key = (record["domain"], record["path"], record["name"])
        deduped[key] = record
    return list(deduped.values())


def export_live_chromium_suno_cookies(
    db_path: Path = DEFAULT_LIVE_CHROMIUM_COOKIE_DB,
) -> list[dict]:
    source_db = db_path.expanduser().resolve()
    if not source_db.exists():
        raise SunoAuthError(f"Live Chromium cookie DB not found: {source_db}")

    connection: sqlite3.Connection | None = None
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as handle:
        temp_db_path = Path(handle.name)
    try:
        shutil.copy2(source_db, temp_db_path)
        connection = sqlite3.connect(str(temp_db_path))
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """
            SELECT host_key, name, value, encrypted_value, path, expires_utc,
                   is_secure, is_httponly, samesite
            FROM cookies
            WHERE host_key LIKE '%suno.com%'
            """
        ).fetchall()
    finally:
        try:
            if connection is not None:
                connection.close()
        except Exception:
            pass
        temp_db_path.unlink(missing_ok=True)

    if not rows:
        raise SunoAuthError("No Suno cookies were found in the live Chromium profile.")

    cookies: list[dict] = []
    for row in rows:
        host = str(row["host_key"])
        if not _is_suno_domain(host):
            continue
        value = row["value"] or _decrypt_chromium_cookie(row["encrypted_value"])
        if not value:
            continue
        record = {
            "name": row["name"],
            "value": value,
            "domain": host,
            "path": row["path"] or "/",
            "secure": bool(row["is_secure"]),
            "httpOnly": bool(row["is_httponly"]),
        }
        expires = _normalize_cookie_expiry(row["expires_utc"])
        if expires is not None:
            record["expires"] = expires
        same_site = _normalize_same_site(row["samesite"])
        if same_site is not None:
            record["sameSite"] = same_site
        cookies.append(record)

    if not cookies:
        raise SunoAuthError("Live Chromium export did not produce any usable Suno cookies.")
    return normalize_cookie_records(cookies)


def launch_browser_runtime(
    *,
    raw_cookie_file: Path = DEFAULT_RAW_COOKIE_FILE,
    profile_dir: Path = DEFAULT_PROFILE_DIR,
) -> BrowserRuntime:
    raw_cookie_file = raw_cookie_file.expanduser().resolve()
    profile_dir = profile_dir.expanduser().resolve()
    raw_cookie_file.parent.mkdir(parents=True, exist_ok=True)
    profile_dir.mkdir(parents=True, exist_ok=True)

    display = _setup_virtual_display_if_needed()
    playwright_cm = sync_playwright()
    playwright = playwright_cm.start()
    context = playwright.chromium.launch_persistent_context(
        str(profile_dir),
        headless=False,
        viewport={"width": 1440, "height": 960},
        accept_downloads=True,
        ignore_default_args=["--enable-automation"],
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage",
        ],
    )
    context.add_init_script(
        """
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        if (!window.chrome) {
          window.chrome = {};
        }
        if (!window.chrome.runtime) {
          window.chrome.runtime = {};
        }
        """
    )
    page = context.pages[0] if context.pages else context.new_page()
    return BrowserRuntime(
        playwright_cm=playwright_cm,
        playwright=playwright,
        context=context,
        page=page,
        display=display,
        profile_dir=profile_dir,
        raw_cookie_file=raw_cookie_file,
    )


def ensure_logged_in_browser(
    runtime: BrowserRuntime,
    *,
    import_cookie_file: Path | None = None,
    allow_live_browser_export: bool = True,
) -> str:
    if is_logged_in(runtime.page):
        persist_context_cookies(runtime.context, runtime.raw_cookie_file)
        return "persistent-profile"

    cookie_sources: list[tuple[str, list[dict]]] = []
    candidate = import_cookie_file.expanduser().resolve() if import_cookie_file else runtime.raw_cookie_file
    if candidate.exists():
        cookie_sources.append((str(candidate), load_cookie_records(candidate)))
    if allow_live_browser_export:
        try:
            live_cookies = export_live_chromium_suno_cookies()
        except SunoAuthError:
            live_cookies = []
        if live_cookies:
            cookie_sources.append(("live-chromium", live_cookies))

    if not cookie_sources:
        raise SunoAuthError(
            "No Suno cookie source is available. "
            "Export cookies with the extension or keep a logged-in Chromium session open."
        )

    last_error: Exception | None = None
    for source_name, cookies in cookie_sources:
        try:
            runtime.context.clear_cookies()
            runtime.context.add_cookies(cookies)
            runtime.page.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=60000)
            runtime.page.wait_for_timeout(4000)
            if is_logged_in(runtime.page):
                persist_context_cookies(runtime.context, runtime.raw_cookie_file)
                return source_name
        except Exception as exc:
            last_error = exc

    if last_error is not None:
        raise SunoAuthError(f"Unable to establish a logged-in Suno browser session: {last_error}") from last_error
    raise SunoAuthError("Unable to establish a logged-in Suno browser session from the available cookies.")


def persist_context_cookies(context: object, raw_cookie_file: Path) -> None:
    cookies = [
        cookie
        for cookie in context.cookies()
        if _is_suno_domain(str(cookie.get("domain") or ""))
    ]
    if cookies:
        save_cookie_records(raw_cookie_file, cookies)


def is_logged_in(page: object) -> bool:
    page.goto("https://suno.com/sign-in", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(3000)
    parsed = urlparse(page.url)
    return "suno.com" in parsed.netloc and "sign-in" not in parsed.path


def fetch_clerk_token(page: object) -> str:
    try:
        page.wait_for_function(
            "() => Boolean(window.Clerk && window.Clerk.session)",
            timeout=20000,
        )
    except Exception as exc:
        raise SunoAuthError("Clerk session is not available in the Suno browser context.") from exc

    token = page.evaluate(
        """
        async () => {
          if (!window.Clerk || !window.Clerk.session) {
            return null;
          }
          return await window.Clerk.session.getToken();
        }
        """
    )
    if not token:
        raise SunoAuthError("Failed to obtain a Suno Clerk token from the browser session.")
    return token


def fetch_billing_from_browser(page: object) -> dict:
    token = fetch_clerk_token(page)
    response = requests.get(
        "https://studio-api.prod.suno.com/api/billing/info/",
        headers={
            "Authorization": f"Bearer {token}",
            "Origin": "https://suno.com",
            "Referer": "https://suno.com/",
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def _setup_virtual_display_if_needed() -> object | None:
    if os.environ.get("DISPLAY") or os.name != "posix":
        return None
    display = Display(visible=0, size=(1440, 960))
    display.start()
    return display


def _is_suno_domain(domain: str) -> bool:
    host = domain.lstrip(".").lower()
    return host == "suno.com" or host.endswith(".suno.com")


def _is_allowed_browser_cookie(name: str) -> bool:
    return name in ALLOWED_BROWSER_COOKIE_NAMES or name.startswith(ALLOWED_BROWSER_COOKIE_PREFIXES)


def _has_invalid_cookie_value(value: str) -> bool:
    return any(ord(char) < 0x20 or ord(char) == 0x7F for char in value)


def _normalize_same_site(value: object) -> str | None:
    if value is None or value == "" or value == 0 or value == -1:
        return None
    if isinstance(value, str):
        mapped = SAMESITE_MAP.get(value.strip().lower())
        return mapped
    return SAMESITE_MAP.get(value)


def _normalize_cookie_expiry(*values: object) -> int | None:
    for value in values:
        if value in (None, "", 0):
            continue
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if number > 10_000_000_000:
            unix_seconds = (number / 1_000_000) - 11_644_473_600
            if unix_seconds > 0:
                return int(unix_seconds)
            continue
        if number > 0:
            return int(number)
    return None


def _decrypt_chromium_cookie(encrypted: bytes) -> str:
    if not encrypted:
        return ""
    blob = bytes(encrypted)
    if blob.startswith((b"v10", b"v11")):
        key = PBKDF2(b"peanuts", b"saltysalt", dkLen=16, count=1)
        cipher = AES.new(key, AES.MODE_CBC, iv=b" " * 16)
        decrypted = cipher.decrypt(blob[3:])
        pad = decrypted[-1]
        if 1 <= pad <= 16:
            decrypted = decrypted[:-pad]
        if len(decrypted) > 32 and _looks_like_cookie_bytes(decrypted[32:]):
            decrypted = decrypted[32:]
        return decrypted.decode("utf-8", errors="ignore")
    return blob.decode("utf-8", errors="ignore")


def _looks_like_cookie_bytes(value: bytes) -> bool:
    if not value:
        return False
    printable = sum(1 for byte in value if 32 <= byte < 127)
    return printable / len(value) > 0.9
