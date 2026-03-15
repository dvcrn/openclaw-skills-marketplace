#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

CREDENTIALS_HEADER = "CADUCEUSMAIL_CREDENTIALS_V1"
ALLOWED_KEYS = {
    "ENTRA_TENANT_ID",
    "ENTRA_CLIENT_ID",
    "ENTRA_CLIENT_SECRET",
    "EXCHANGE_DEFAULT_MAILBOX",
    "EXCHANGE_ORGANIZATION",
    "ORGANIZATION_DOMAIN",
    "CLOUDFLARE_API_TOKEN",
    "CLOUDFLARE_ZONE_ID",
    "CF_API_TOKEN",
    "CF_ZONE_ID",
}
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key and value and key not in os.environ:
            os.environ[key] = value.strip('"').strip("'")


def load_credentials() -> None:
    creds_dir = Path(os.environ.get("CADUCEUSMAIL_CREDENTIALS_DIR", str(ROOT / "credentials"))).expanduser()
    for name in ("entra.txt", "cloudflare.txt"):
        path = creds_dir / name
        if not path.exists():
            continue
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        header_seen = False
        for raw in lines:
            line = raw.strip()
            if not line:
                continue
            if not header_seen:
                if line != CREDENTIALS_HEADER:
                    raise SystemExit(f"invalid credentials file: {path}")
                header_seen = True
                continue
            if line.startswith("#"):
                continue
            if "=" not in line:
                raise SystemExit(f"invalid line in credentials file: {path}")
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if key in ALLOWED_KEYS and key not in os.environ:
                os.environ[key] = value


def load_defaults() -> None:
    load_credentials()
    load_env_file(Path(os.environ.get("CADUCEUSMAIL_ENV_FILE", str(Path.home() / ".caduceusmail" / ".env"))))


def token() -> str:
    tenant = os.environ.get("ENTRA_TENANT_ID", "").strip()
    client = os.environ.get("ENTRA_CLIENT_ID", "").strip()
    secret = os.environ.get("ENTRA_CLIENT_SECRET", "").strip()
    if not tenant or not client or not secret:
        raise SystemExit("missing ENTRA_TENANT_ID, ENTRA_CLIENT_ID, or ENTRA_CLIENT_SECRET")
    body = urllib.parse.urlencode({
        "client_id": client,
        "client_secret": secret,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials",
    }).encode("utf-8")
    req = urllib.request.Request(
        f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token",
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return str(data["access_token"])


def send_message(from_alias: str, mailbox: str, to_email: str, subject: str, body: str, dry_run: bool = False) -> dict[str, Any]:
    if not EMAIL_RE.fullmatch(from_alias):
        raise SystemExit(f"invalid --from address: {from_alias}")
    if not EMAIL_RE.fullmatch(mailbox):
        raise SystemExit(f"invalid --mailbox address: {mailbox}")
    if not EMAIL_RE.fullmatch(to_email):
        raise SystemExit(f"invalid --to address: {to_email}")

    payload = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "Text",
                "content": body,
            },
            "toRecipients": [
                {"emailAddress": {"address": to_email}},
            ],
            "from": {
                "emailAddress": {"address": from_alias},
            },
        },
        "saveToSentItems": True,
    }
    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "endpoint": f"https://graph.microsoft.com/v1.0/users/{mailbox}/sendMail",
            "payload": payload,
        }

    req = urllib.request.Request(
        f"https://graph.microsoft.com/v1.0/users/{urllib.parse.quote(mailbox)}/sendMail",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token()}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            status = getattr(resp, "status", 202)
            return {"ok": status in {200, 202}, "status": status, "mailbox": mailbox, "from": from_alias, "to": to_email}
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="replace")
        return {"ok": False, "status": exc.code, "error": body_text, "mailbox": mailbox, "from": from_alias, "to": to_email}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="☤CaduceusMail Graph sendMail helper")
    sub = parser.add_subparsers(dest="command", required=True)
    send = sub.add_parser("send")
    send.add_argument("--from", dest="from_alias", required=True)
    send.add_argument("--mailbox", required=True)
    send.add_argument("--to", required=True)
    send.add_argument("--subject", required=True)
    send.add_argument("--body", required=True)
    send.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    load_defaults()
    if args.command == "send":
        result = send_message(args.from_alias, args.mailbox, args.to, args.subject, args.body, dry_run=args.dry_run)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0 if result.get("ok") else 1
    print(json.dumps({"ok": False, "error": "unsupported command"}))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
