from __future__ import annotations

import json
import re
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import requests

CLERK_JS_VERSION = "4.73.2"
CLERK_CLIENT_URL = (
    f"https://clerk.suno.com/v1/client?_clerk_js_version={CLERK_JS_VERSION}"
)
CLERK_TOKEN_URL = (
    "https://clerk.suno.com/v1/client/sessions/"
    "{session_id}/tokens?_clerk_js_version="
    f"{CLERK_JS_VERSION}"
)
SUNO_BILLING_URL = "https://studio-api.prod.suno.com/api/billing/info/"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
)

ALLOWED_COOKIE_PREFIXES = ("__client", "__client_uat", "__session")
ALLOWED_COOKIE_NAMES = {
    "clerk_active_context",
    "_clerk_db_jwt",
    "__clerk_db_jwt",
}


class SunoAuthError(RuntimeError):
    pass


@dataclass
class CookieBundle:
    header: str
    cookies: OrderedDict[str, str]
    source_kind: str


@dataclass
class SunoSessionInfo:
    session_id: str
    jwt: str
    billing: dict | None = None

    @property
    def credits_left(self) -> int | None:
        if not self.billing:
            return None
        return self.billing.get("total_credits_left") or self.billing.get("credits")


def load_cookie_bundle(path: Path) -> CookieBundle:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise SunoAuthError(f"Cookie source is empty: {path}")
    bundle = parse_cookie_source(text)
    return CookieBundle(header=bundle.header, cookies=bundle.cookies, source_kind=bundle.source_kind)


def parse_cookie_source(text: str) -> CookieBundle:
    stripped = text.strip()
    if not stripped:
        raise SunoAuthError("Cookie source is empty.")

    cookie_pairs: list[tuple[str, str]]
    source_kind: str

    if _looks_like_json(stripped):
        cookie_pairs = _parse_json_cookie_source(stripped)
        source_kind = "json"
    elif _looks_like_netscape_cookie_export(stripped):
        cookie_pairs = _parse_netscape_cookie_export(stripped)
        source_kind = "netscape"
    else:
        cookie_pairs = _parse_cookie_header(stripped)
        source_kind = "header"

    cookies = _filter_auth_cookies(cookie_pairs)
    has_client = any(_is_client_cookie_name(name) for name in cookies)
    has_session = "__session" in cookies or any(name.startswith("__session_") for name in cookies)
    if not has_client:
        raise SunoAuthError("Missing Clerk client cookie (__client or suffixed variant).")
    if not has_session:
        raise SunoAuthError("Missing Suno session cookie (__session or suffixed variant).")

    header = "; ".join(f"{name}={value}" for name, value in cookies.items())
    return CookieBundle(header=header, cookies=cookies, source_kind=source_kind)


def save_cookie_header(path: Path, cookie_header: str) -> None:
    path.write_text(cookie_header.strip() + "\n", encoding="utf-8")
    path.chmod(0o600)


def build_browser_session(cookie_header: str) -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "Accept": "application/json",
            "Cookie": cookie_header,
            "User-Agent": DEFAULT_USER_AGENT,
        }
    )
    return session


def authenticate_session(
    session: requests.Session,
    *,
    require_billing: bool = True,
    timeout: int = 20,
) -> SunoSessionInfo:
    try:
        client_response = session.get(CLERK_CLIENT_URL, timeout=timeout)
    except requests.RequestException as exc:
        raise SunoAuthError(f"Clerk client request failed: {exc}") from exc

    client_data = _parse_json_response(client_response, "Clerk client probe")
    response_data = client_data.get("response") or {}
    if not response_data:
        detail = _extract_error_detail(client_data) or _truncate(client_response.text)
        raise SunoAuthError(
            "Clerk did not return an active session. Export fresh Suno cookies and try again. "
            f"Detail: {detail}"
        )

    session_id = (
        response_data.get("last_active_session_id")
        or _first_session_id(response_data.get("sessions"))
        or _extract_session_id_from_cookie_header(session.headers.get("Cookie", ""))
    )
    if not session_id:
        raise SunoAuthError("Unable to determine the active Clerk session id.")

    try:
        token_response = session.post(
            CLERK_TOKEN_URL.format(session_id=session_id),
            timeout=timeout,
        )
    except requests.RequestException as exc:
        raise SunoAuthError(f"Clerk token renewal failed: {exc}") from exc

    token_data = _parse_json_response(token_response, "Clerk token renewal")
    jwt = token_data.get("jwt")
    if not jwt:
        detail = _extract_error_detail(token_data) or _truncate(token_response.text)
        raise SunoAuthError(
            "Suno rejected the current Clerk session during token renewal. "
            "The saved cookies are stale or incomplete. "
            f"Detail: {detail}"
        )

    session.headers["Authorization"] = f"Bearer {jwt}"

    billing = None
    if require_billing:
        try:
            billing_response = session.get(SUNO_BILLING_URL, timeout=timeout)
        except requests.RequestException as exc:
            raise SunoAuthError(f"Suno billing probe failed: {exc}") from exc
        billing = _parse_json_response(billing_response, "Suno billing probe")

    return SunoSessionInfo(session_id=session_id, jwt=jwt, billing=billing)


def format_cookie_summary(cookies: OrderedDict[str, str]) -> str:
    return ", ".join(cookies.keys())


def _looks_like_json(text: str) -> bool:
    return text.startswith("{") or text.startswith("[")


def _looks_like_netscape_cookie_export(text: str) -> bool:
    if text.startswith("# Netscape HTTP Cookie File"):
        return True
    return any(line.count("\t") >= 6 for line in text.splitlines() if line and not line.startswith("#"))


def _parse_json_cookie_source(text: str) -> list[tuple[str, str]]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SunoAuthError(f"Cookie JSON could not be parsed: {exc}") from exc

    cookies = payload.get("cookies") if isinstance(payload, dict) else payload
    if not isinstance(cookies, list):
        raise SunoAuthError("Cookie JSON must contain a list under `cookies`.")

    pairs: list[tuple[str, str]] = []
    for item in cookies:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "").strip()
        value = str(item.get("value") or "").strip()
        if name and value:
            pairs.append((name, value))
    if not pairs:
        raise SunoAuthError("Cookie JSON contained no usable cookies.")
    return pairs


def _parse_netscape_cookie_export(text: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = raw_line.split("\t")
        if len(parts) < 7:
            continue
        name = parts[-2].strip()
        value = parts[-1].strip()
        if name and value:
            pairs.append((name, value))
    if not pairs:
        raise SunoAuthError("Netscape cookie export contained no usable cookies.")
    return pairs


def _parse_cookie_header(text: str) -> list[tuple[str, str]]:
    header = text.strip()
    if header.lower().startswith("cookie:"):
        header = header.split(":", 1)[1].strip()

    pairs: list[tuple[str, str]] = []
    for chunk in header.split(";"):
        piece = chunk.strip()
        if not piece or "=" not in piece:
            continue
        name, value = piece.split("=", 1)
        name = name.strip()
        value = value.strip()
        if name and value:
            pairs.append((name, value))
    if not pairs:
        raise SunoAuthError("Raw cookie header contained no usable cookies.")
    return pairs


def _filter_auth_cookies(cookie_pairs: Iterable[tuple[str, str]]) -> OrderedDict[str, str]:
    cookies: OrderedDict[str, str] = OrderedDict()
    for name, value in cookie_pairs:
        if not value:
            continue
        if name in ALLOWED_COOKIE_NAMES or name.startswith(ALLOWED_COOKIE_PREFIXES):
            cookies[name] = value
    if not cookies:
        raise SunoAuthError(
            "No Suno or Clerk auth cookies were found. "
            "Expected cookies like __client, __session or clerk_active_context."
        )

    ordered_names = sorted(cookies.keys(), key=_cookie_sort_key)
    ordered = OrderedDict((name, cookies[name]) for name in ordered_names)
    return ordered


def _cookie_sort_key(name: str) -> tuple[int, str]:
    priority = {
        "__client": 0,
        "__client_uat": 1,
        "__session": 2,
        "clerk_active_context": 50,
        "_clerk_db_jwt": 60,
        "__clerk_db_jwt": 61,
    }.get(name)
    if priority is not None:
        return (priority, name)
    if name.startswith("__client_"):
        return (10, name)
    if name.startswith("__client_uat_"):
        return (11, name)
    if name.startswith("__session_"):
        return (12, name)
    return (100, name)


def _is_client_cookie_name(name: str) -> bool:
    if name == "__client":
        return True
    return name.startswith("__client_") and not name.startswith("__client_uat")


def _parse_json_response(response: requests.Response, label: str) -> dict:
    if response.status_code >= 400:
        detail = _truncate(response.text)
        raise SunoAuthError(f"{label} failed with HTTP {response.status_code}: {detail}")
    try:
        data = response.json()
    except ValueError as exc:
        raise SunoAuthError(f"{label} returned invalid JSON.") from exc
    if not isinstance(data, dict):
        raise SunoAuthError(f"{label} returned an unexpected response shape.")
    return data


def _extract_session_id_from_cookie_header(cookie_header: str) -> str | None:
    match = re.search(r"clerk_active_context=(session_[A-Za-z0-9]+)", cookie_header)
    if match:
        return match.group(1)
    return None


def _first_session_id(sessions: object) -> str | None:
    if not isinstance(sessions, list):
        return None
    for session in sessions:
        if isinstance(session, dict) and session.get("id"):
            return str(session["id"])
    return None


def _extract_error_detail(data: dict) -> str | None:
    if data.get("error"):
        return str(data["error"])
    errors = data.get("errors")
    if isinstance(errors, list) and errors:
        first = errors[0]
        if isinstance(first, dict):
            message = first.get("message") or first.get("long_message")
            if message:
                return str(message)
        return str(first)
    if data.get("message"):
        return str(data["message"])
    return None


def _truncate(value: str, limit: int = 180) -> str:
    text = " ".join(value.split())
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."
