#!/usr/bin/env python3
"""AI-enhanced Gmail integration for OpenClaw agents."""

import argparse
import email
import email.utils
import imaplib
import json
import os
import smtplib
import sys
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


IMAP_SERVER = "imap.gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def get_credentials():
    addr = os.environ.get("GMAIL_ADDRESS")
    pwd = os.environ.get("GMAIL_APP_PASSWORD")
    if not addr or not pwd:
        print("Error: GMAIL_ADDRESS and GMAIL_APP_PASSWORD must be set", file=sys.stderr)
        sys.exit(1)
    return addr, pwd


def llm_request(prompt, system="You are an email assistant."):
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        print("Error: OPENROUTER_API_KEY required for AI features", file=sys.stderr)
        sys.exit(1)
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError
    data = json.dumps({
        "model": "anthropic/claude-haiku-4.5",
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        "max_tokens": 2000,
    }).encode()
    req = Request("https://openrouter.ai/api/v1/chat/completions", data=data, headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json",
    })
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read().decode())["choices"][0]["message"]["content"]
    except HTTPError as e:
        print(f"LLM Error {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)


def decode_mime_header(header):
    if not header:
        return ""
    parts = decode_header(header)
    decoded = []
    for part, charset in parts:
        if isinstance(part, bytes):
            decoded.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            decoded.append(part)
    return " ".join(decoded)


def get_email_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            if ct == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    return payload.decode(charset, errors="replace")
        # Fallback to HTML
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    return payload.decode(charset, errors="replace")
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            return payload.decode(charset, errors="replace")
    return ""


def connect_imap():
    addr, pwd = get_credentials()
    try:
        imap = imaplib.IMAP4_SSL(IMAP_SERVER)
        imap.login(addr, pwd)
        return imap
    except imaplib.IMAP4.error as e:
        print(f"IMAP login failed: {e}", file=sys.stderr)
        sys.exit(1)


def fetch_emails(label="INBOX", unread=False, sender=None, since=None, limit=10):
    imap = connect_imap()
    imap.select(label, readonly=True)

    criteria = []
    if unread:
        criteria.append("UNSEEN")
    if sender:
        criteria.append(f'FROM "{sender}"')
    if since:
        from datetime import datetime
        dt = datetime.strptime(since, "%Y-%m-%d")
        criteria.append(f'SINCE {dt.strftime("%d-%b-%Y")}')
    if not criteria:
        criteria.append("ALL")

    search_str = " ".join(criteria)
    _, msg_nums = imap.search(None, search_str)
    ids = msg_nums[0].split()

    # Get most recent
    ids = ids[-limit:] if len(ids) > limit else ids
    ids.reverse()

    emails = []
    for mid in ids:
        _, msg_data = imap.fetch(mid, "(RFC822)")
        raw = msg_data[0][1]
        msg = email.message_from_bytes(raw)
        emails.append({
            "id": mid.decode(),
            "from": decode_mime_header(msg.get("From", "")),
            "to": decode_mime_header(msg.get("To", "")),
            "subject": decode_mime_header(msg.get("Subject", "")),
            "date": msg.get("Date", ""),
            "body": get_email_body(msg)[:2000],
            "message_id": msg.get("Message-ID", ""),
        })

    imap.logout()
    return emails


def cmd_inbox(args):
    emails = fetch_emails(
        label=args.label, unread=args.unread, sender=getattr(args, "from", None),
        since=args.since, limit=args.limit,
    )
    if not emails:
        print("  No emails found.")
        return
    for e in emails:
        snippet = e["body"][:100].replace("\n", " ").strip()
        print(f"  [{e['id']}] {e['date']}")
        print(f"    From: {e['from']}")
        print(f"    Subject: {e['subject']}")
        print(f"    Preview: {snippet}...")
        print()


def cmd_triage(args):
    emails = fetch_emails(unread=True, limit=args.limit)
    if not emails:
        print("  No emails to triage.")
        return

    email_summaries = []
    for e in emails:
        email_summaries.append({
            "id": e["id"], "from": e["from"], "subject": e["subject"],
            "preview": e["body"][:500],
        })

    prompt = f"""Categorize each email into one of these categories:
🔴 URGENT — needs immediate action (deadlines, emergencies, important people)
🟡 ACTIONABLE — requires a response but not urgent
🔵 FYI — informational, no action needed
⚪ NOISE — newsletters, spam, automated notifications

For each email, output: [category emoji] Subject — brief reason

Emails:
{json.dumps(email_summaries, indent=2)}"""

    result = llm_request(prompt)
    print("  EMAIL TRIAGE")
    print(f"  {'='*50}")
    print(result)


def cmd_priority(args):
    emails = fetch_emails(unread=True, limit=args.limit)
    if not emails:
        print("  No emails to score.")
        return

    email_summaries = [{"id": e["id"], "from": e["from"], "subject": e["subject"],
                        "preview": e["body"][:500]} for e in emails]

    prompt = f"""Score each email from 0-100 for priority. Consider:
- Sender importance (known contacts > unknown, executives > automated)
- Subject urgency (deadline mentions, "urgent", "ASAP")
- Content: mentions of the recipient, action items, questions
- Time sensitivity: calendar invites, expiring offers

Output format per email:
[SCORE] Subject — from Sender — brief reason

Sort by score descending.

Emails:
{json.dumps(email_summaries, indent=2)}"""

    result = llm_request(prompt)
    print("  PRIORITY INBOX")
    print(f"  {'='*50}")
    print(result)


def cmd_summarize(args):
    emails = fetch_emails(limit=50)
    target = None
    for e in emails:
        if e["id"] == args.message_id:
            target = e
            break
    if not target:
        print(f"  Email {args.message_id} not found in recent messages.")
        return

    prompt = f"""Summarize this email concisely:

From: {target['from']}
Subject: {target['subject']}
Date: {target['date']}

Body:
{target['body'][:3000]}

Provide:
1. TL;DR (one sentence)
2. Key points (bullet list)
3. Action items (if any)
4. Response needed? (yes/no + why)"""

    result = llm_request(prompt)
    print(f"  SUMMARY: {target['subject']}")
    print(f"  {'='*50}")
    print(result)


def cmd_reply(args):
    emails = fetch_emails(limit=50)
    target = None
    for e in emails:
        if e["id"] == args.message_id:
            target = e
            break
    if not target:
        print(f"  Email {args.message_id} not found.")
        return

    context = f"\nAdditional context: {args.context}" if args.context else ""

    prompt = f"""Generate a reply to this email in a {args.tone} tone.

Original email:
From: {target['from']}
Subject: {target['subject']}
Body: {target['body'][:2000]}
{context}

Write ONLY the reply body (no subject line, no headers). Make it natural and appropriate for the tone requested."""

    result = llm_request(prompt)
    print(f"  DRAFT REPLY ({args.tone}) to: {target['subject']}")
    print(f"  {'='*50}")
    print(result)


def cmd_send(args):
    addr, pwd = get_credentials()
    msg = MIMEMultipart()
    msg["From"] = addr
    msg["To"] = args.to
    msg["Subject"] = args.subject
    if args.cc:
        msg["Cc"] = args.cc
    if args.bcc:
        msg["Bcc"] = args.bcc
    msg.attach(MIMEText(args.body, "plain"))

    recipients = [args.to]
    if args.cc:
        recipients.append(args.cc)
    if args.bcc:
        recipients.append(args.bcc)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(addr, pwd)
            server.sendmail(addr, recipients, msg.as_string())
        print(f"  Email sent to {args.to} | Subject: {args.subject}")
    except smtplib.SMTPException as e:
        print(f"SMTP Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Gmail AI")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("inbox", help="Fetch emails")
    p.add_argument("--unread", action="store_true")
    p.add_argument("--label", default="INBOX")
    p.add_argument("--from", dest="from_addr")
    p.add_argument("--since")
    p.add_argument("--limit", type=int, default=10)

    p = sub.add_parser("triage", help="AI triage emails")
    p.add_argument("--limit", type=int, default=20)

    p = sub.add_parser("priority", help="Priority score emails")
    p.add_argument("--limit", type=int, default=20)

    p = sub.add_parser("summarize", help="Summarize an email")
    p.add_argument("message_id")

    p = sub.add_parser("reply", help="Generate smart reply")
    p.add_argument("message_id")
    p.add_argument("--tone", choices=["professional", "friendly", "brief", "formal"], default="professional")
    p.add_argument("--context")

    p = sub.add_parser("send", help="Send email")
    p.add_argument("--to", required=True)
    p.add_argument("--subject", required=True)
    p.add_argument("--body", required=True)
    p.add_argument("--cc")
    p.add_argument("--bcc")

    args = parser.parse_args()
    # Fix --from arg name
    if hasattr(args, "from_addr"):
        args.__dict__["from"] = args.from_addr

    cmds = {
        "inbox": cmd_inbox, "triage": cmd_triage, "priority": cmd_priority,
        "summarize": cmd_summarize, "reply": cmd_reply, "send": cmd_send,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
