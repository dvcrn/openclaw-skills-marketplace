#!/usr/bin/env python3
"""Fetch and decode ride receipt emails from Gmail via gog into JSONL.

Output: JSONL (one email per line) with:
- provider, gmail_message_id, email_date, subject, from, snippet
- decoded body: text_html (raw HTML from the email)

Note: This intentionally does **not** emit text/plain or any derived fields.

No provider-specific semantic parsing is done here.
"""

import argparse
import base64
import json
import re
import subprocess
from email import policy
from email.parser import BytesParser
from html import unescape
from pathlib import Path

DEFAULT_PROVIDERS = {
    "Uber": 'from:noreply@uber.com subject:("trip with Uber")',
    "Bolt": 'from:(bolt.eu OR receipts-poland@bolt.eu) subject:("Your Bolt ride" OR "Your Bolt trip")',
    "Yandex": 'from:(go@yandex.ru OR taxi.yandex.ru OR noreply@yandex.ru) subject:("electronic ride receipt" OR "Ride report" OR "ride receipt")',
    "Lyft": 'from:(lyftmail.com OR lyft.com) subject:("Your ride with")',
}


def run_json(cmd):
    out = subprocess.check_output(cmd, text=True)
    return json.loads(out)


def add_date_bounds(query: str, after: str | None, before: str | None) -> str:
    q = f"({query})"
    if after:
        y, m, d = after.split("-")
        q += f" after:{y}/{m}/{d}"
    if before:
        y, m, d = before.split("-")
        q += f" before:{y}/{m}/{d}"
    return q


def gmail_search(account: str, query: str, maxn: int):
    return run_json(
        [
            "gog",
            "gmail",
            "messages",
            "search",
            query,
            "--max",
            str(maxn),
            "--account",
            account,
            "--json",
            "--results-only",
        ]
    )


def gmail_get_full(account: str, message_id: str):
    return run_json(
        [
            "gog",
            "gmail",
            "get",
            message_id,
            "--format=full",
            "--account",
            account,
            "--json",
            "--results-only",
            "--select",
            "message.snippet,message.internalDate",
        ]
    )


def gmail_get_raw(account: str, message_id: str):
    return run_json(
        [
            "gog",
            "gmail",
            "get",
            message_id,
            "--format=raw",
            "--account",
            account,
            "--json",
            "--results-only",
        ]
    )


def decode_rfc822(raw_b64url: str):
    raw_bytes = base64.urlsafe_b64decode(raw_b64url + "===")
    return BytesParser(policy=policy.default).parsebytes(raw_bytes)


# NOTE: We intentionally do NOT convert HTML to plain text here.
# The goal is to feed the LLM the raw HTML part by default (no preprocessing).

def decode_part(part) -> str:
    b = part.get_payload(decode=True)
    if not b:
        return ""
    cs = part.get_content_charset() or "utf-8"
    try:
        return b.decode(cs, errors="replace")
    except Exception:
        return b.decode("utf-8", errors="replace")


def collect_html(msg):
    parts = list(msg.walk()) if msg.is_multipart() else [msg]

    htmls = []
    for p in parts:
        if p.get_content_type() == "text/html":
            s = decode_part(p).strip()
            if s:
                htmls.append(s)

    return "\n\n".join(htmls).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--account", required=True)
    ap.add_argument("--after", help="Only include emails after YYYY-MM-DD")
    ap.add_argument("--before", help="Only include emails before YYYY-MM-DD")
    ap.add_argument("--max-per-provider", type=int, default=5000)
    ap.add_argument("--providers", default=",".join(DEFAULT_PROVIDERS.keys()))
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    providers = [p.strip() for p in args.providers.split(",") if p.strip()]

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    n = 0
    with out_path.open("w", encoding="utf-8") as w:
        for prov in providers:
            q0 = DEFAULT_PROVIDERS.get(prov)
            if not q0:
                raise SystemExit(f"Unknown provider: {prov}")
            q = add_date_bounds(q0, args.after, args.before)

            msgs = gmail_search(args.account, q, args.max_per_provider)
            for m in msgs:
                mid = m.get("id")
                if not mid:
                    continue

                full = gmail_get_full(args.account, mid)
                snippet = unescape(full.get("message.snippet", "") or "")

                raw = gmail_get_raw(args.account, mid)
                msg = decode_rfc822(raw["message"]["raw"])

                text_html = collect_html(msg)

                item = {
                    "provider": prov,
                    "gmail_message_id": mid,
                    "email_date": m.get("date"),
                    "subject": m.get("subject"),
                    "from": m.get("from"),
                    "snippet": snippet,
                    "text_html": text_html,
                }
                w.write(json.dumps(item, ensure_ascii=False) + "\n")
                n += 1

    print(f"Wrote {n} emails to {out_path}")


if __name__ == "__main__":
    main()
