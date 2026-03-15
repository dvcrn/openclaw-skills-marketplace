from urllib.parse import urlparse
import webbrowser


def _normalize_url(input_text: str) -> str:
    raw = " ".join((input_text or "").split())
    if not raw:
        return "https://www.openclaw.ai"
    if "://" not in raw:
        raw = f"https://{raw}"
    parsed = urlparse(raw)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("Invalid URL input")
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only http/https URLs are allowed")
    return raw


def run(input_text: str):
    url = _normalize_url(input_text)
    opened = webbrowser.open_new(url)
    if not opened:
        return f"Browser open was requested but may have been blocked. URL: {url}"
    return f"Opened browser window: {url}"
