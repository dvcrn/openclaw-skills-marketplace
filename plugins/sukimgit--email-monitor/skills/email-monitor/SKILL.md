---
name: email-monitor
description: "Email Monitor v2.0 - Auto email monitoring with business reply templates. Feishu notification for business opportunities."
---

# Email Monitor v2.0

**By Efficiency Lab**

Automatic email monitoring with intelligent business reply templates.

## Features

- Auto email monitoring (every 30 minutes)
- Business opportunity detection
- Auto reply with bilingual templates (Chinese/English)
- Feishu real-time notification
- Spam filtering
- Rate limiting (anti-ban)

## Installation

```bash
pip install requests
cp email_config.example.json email_config.json
python check_emails_complete.py
```

## Configuration

Edit email_config.json with your email credentials and Feishu webhook URL.

## Business Templates (v2.0 New)

3 professional reply templates:

1. Business Inquiry - Triggers: quote/price/cooperation/custom
2. General Consultation - Triggers: consult/inquiry/service
3. Technical Integration - Triggers: API/integration/technical

## Pricing

- Standard: Free (Basic monitoring + auto reply)
- Pro: 350 CNY/month (Multi-email + analytics)
- Custom: 7000-20000 CNY (Private deployment + customization)

## Contact

Efficiency Lab
- Email: 1776480440@qq.com
- Website: https://clawhub.ai

## Changelog

### v2.0.0 (2026-03-08)
- New: Efficiency Lab branding
- New: 3 business reply templates
- New: Auto template selection
- New: Feishu notification optimization

### v1.0.7 (2026-03-05)
- Initial release
