---
name: gmail-ai
description: "AI-enhanced Gmail — smart email triage, priority scoring, AI-generated replies, thread summarization, and automated categorization. IMAP/SMTP with OpenRouter-powered intelligence. Use for inbox zero, email management, smart replies, and email automation."
homepage: https://www.agxntsix.ai
---

# 📧 Gmail AI

AI-enhanced Gmail for OpenClaw agents. Fork of gmail v1.0.6 with AI triage, priority scoring, smart replies, and email summarization.

## What's New vs gmail

- **AI triage** — auto-categorize emails (urgent/actionable/FYI/spam)
- **Priority scoring** — 0-100 score based on sender, subject, content
- **Smart replies** — context-aware reply generation in multiple tones
- **Email summarization** — TL;DR for long threads
- **Send email** — compose and send via SMTP

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `GMAIL_ADDRESS` | ✅ | Your Gmail address |
| `GMAIL_APP_PASSWORD` | ✅ | Gmail App Password ([create one](https://myaccount.google.com/apppasswords)) |
| `OPENROUTER_API_KEY` | Optional | For AI triage, replies, and summaries |

## Quick Start

```bash
# Fetch recent unread emails
python3 {baseDir}/scripts/gmail_ai.py inbox --unread --limit 10

# Fetch by label
python3 {baseDir}/scripts/gmail_ai.py inbox --label INBOX --limit 20

# Fetch from specific sender
python3 {baseDir}/scripts/gmail_ai.py inbox --from "boss@company.com"

# AI triage — categorize emails
python3 {baseDir}/scripts/gmail_ai.py triage --limit 20

# Priority scoring
python3 {baseDir}/scripts/gmail_ai.py priority --limit 20

# Summarize an email thread
python3 {baseDir}/scripts/gmail_ai.py summarize <message_id>

# Generate smart reply
python3 {baseDir}/scripts/gmail_ai.py reply <message_id> --tone professional
python3 {baseDir}/scripts/gmail_ai.py reply <message_id> --tone friendly
python3 {baseDir}/scripts/gmail_ai.py reply <message_id> --tone brief

# Send email
python3 {baseDir}/scripts/gmail_ai.py send --to "recipient@example.com" --subject "Hello" --body "Message body"

# Send with CC/BCC
python3 {baseDir}/scripts/gmail_ai.py send --to "a@b.com" --cc "c@d.com" --subject "Hello" --body "Message"
```

## Commands

### `inbox`
Fetch emails from Gmail via IMAP.
- `--unread` — only unread messages
- `--label LABEL` — Gmail label/folder (default: INBOX)
- `--from ADDRESS` — filter by sender
- `--limit N` — max results (default: 10)
- `--since YYYY-MM-DD` — emails since date

### `triage`
AI-powered email categorization (requires `OPENROUTER_API_KEY`).
- Categories: 🔴 Urgent, 🟡 Actionable, 🔵 FYI, ⚪ Spam/Noise
- `--limit N` — number of emails to triage

### `priority`
Score emails 0-100 based on sender importance, subject urgency, and content.
- `--limit N` — number of emails to score
- Factors: known sender, urgency keywords, mentions of you, deadlines

### `summarize <message_id>`
Generate a TL;DR summary of an email or thread.

### `reply <message_id>`
Generate a context-aware reply draft.
- `--tone professional|friendly|brief|formal` — reply style
- `--context TEXT` — additional context for the reply

### `send`
Send email via SMTP.
- `--to ADDRESS` — recipient (required)
- `--subject TEXT` — subject line (required)
- `--body TEXT` — email body (required)
- `--cc ADDRESS` — CC recipient
- `--bcc ADDRESS` — BCC recipient

## Security Notes

- Uses Gmail App Passwords (not OAuth) — simpler setup, works with 2FA
- App Password is NOT your Google password
- Create one at: Google Account → Security → 2-Step Verification → App Passwords
- IMAP must be enabled in Gmail settings

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
