#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from browser_session import (
    DEFAULT_COOKIE_FILE,
    DEFAULT_RAW_COOKIE_FILE,
    normalize_cookie_records,
    save_cookie_records,
)
from suno_auth import (
    SunoAuthError,
    authenticate_session,
    build_browser_session,
    format_cookie_summary,
    parse_cookie_source,
    save_cookie_header,
)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Receive Suno cookies from the local browser extension and save a normalized auth header."
    )
    parser.add_argument("--host", default="127.0.0.1", help="Bind host")
    parser.add_argument("--port", default=8765, type=int, help="Bind port")
    parser.add_argument("--path", default="/suno/cookies", help="POST path")
    parser.add_argument(
        "--cookie-file",
        default=str(DEFAULT_COOKIE_FILE),
        help="Destination for the normalized Suno cookie header",
    )
    parser.add_argument(
        "--raw-cookie-file",
        default=str(DEFAULT_RAW_COOKIE_FILE),
        help="Destination for the raw Suno cookie JSON export",
    )
    parser.add_argument(
        "--skip-validate",
        action="store_true",
        help="Store cookies without Clerk or Suno validation",
    )
    parser.add_argument(
        "--keep-running",
        action="store_true",
        help="Keep the receiver alive after the first successful import",
    )
    return parser.parse_args()


class CookieImportHandler(BaseHTTPRequestHandler):
    server_version = "SunoCookieReceiver/1.0"

    def do_POST(self) -> None:
        if self.path != self.server.import_path:
            self._send_json(
                HTTPStatus.NOT_FOUND,
                {"ok": False, "error": f"Use POST {self.server.import_path}"},
            )
            return

        length = int(self.headers.get("Content-Length", "0"))
        payload_bytes = self.rfile.read(length)
        try:
            payload = json.loads(payload_bytes.decode("utf-8"))
        except json.JSONDecodeError as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
            return

        try:
            raw_cookie_records = normalize_cookie_records(payload)
            bundle = parse_cookie_source(json.dumps(payload))
            session_info = None
            if not self.server.skip_validate:
                session = build_browser_session(bundle.header)
                session_info = authenticate_session(session, require_billing=True)
            save_cookie_header(self.server.cookie_file, bundle.header)
            save_cookie_records(self.server.raw_cookie_file, raw_cookie_records)
        except SunoAuthError as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
            return

        response = {
            "ok": True,
            "cookie_file": str(self.server.cookie_file),
            "raw_cookie_file": str(self.server.raw_cookie_file),
            "cookie_names": list(bundle.cookies.keys()),
            "cookie_summary": format_cookie_summary(bundle.cookies),
        }
        if session_info is not None:
            response["session_id"] = session_info.session_id
            response["credits_left"] = session_info.credits_left
        self._send_json(HTTPStatus.OK, response)

        if not self.server.keep_running:
            threading.Thread(target=self.server.shutdown, daemon=True).start()

    def log_message(self, fmt: str, *args) -> None:
        return

    def _send_json(self, status: HTTPStatus, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=True).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class CookieImportServer(ThreadingHTTPServer):
    def __init__(
        self,
        server_address,
        handler,
        *,
        cookie_file: Path,
        raw_cookie_file: Path,
        import_path: str,
        skip_validate: bool,
        keep_running: bool,
    ) -> None:
        super().__init__(server_address, handler)
        self.cookie_file = cookie_file
        self.raw_cookie_file = raw_cookie_file
        self.import_path = import_path
        self.skip_validate = skip_validate
        self.keep_running = keep_running


def main() -> int:
    args = parse_args()
    cookie_file = Path(args.cookie_file).expanduser().resolve()
    raw_cookie_file = Path(args.raw_cookie_file).expanduser().resolve()
    cookie_file.parent.mkdir(parents=True, exist_ok=True)
    raw_cookie_file.parent.mkdir(parents=True, exist_ok=True)

    server = CookieImportServer(
        (args.host, args.port),
        CookieImportHandler,
        cookie_file=cookie_file,
        raw_cookie_file=raw_cookie_file,
        import_path=args.path,
        skip_validate=args.skip_validate,
        keep_running=args.keep_running,
    )

    print(f"Listening on http://{args.host}:{args.port}{args.path}")
    print("Set the extension URL to this address and click export.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
