---
name: didi
description: "Browser-assisted Didi ride helper for manual ride-hailing workflows. Use when the user wants help checking ride estimates, reviewing available ride types, logging in manually, viewing trip status, or preparing a manual Didi booking flow. Keep login manual and do not complete payment automatically."
---

# Didi Ride Helper

Use this skill for browser-assisted, manual Didi workflows.

## Supported Help

- log in with a user-controlled QR flow
- check ride estimates between two locations
- review supported ride types
- inspect current trip status
- review past trip history when available
- check available coupons when available

## Typical Commands

```bash
python didi.py login
python didi.py estimate "Guomao" "Tiananmen"
python didi.py call "Guomao" "Tiananmen"
python didi.py call "Guomao" "Tiananmen" --type premier
python didi.py status
python didi.py history
python didi.py coupon
```

## Safety Boundaries

- Keep login manual.
- Do not request or store account passwords in plain text.
- Do not perform hidden background actions outside the user's current instruction.
- Do not automatically complete payment.

## Dependencies

- Python 3.8+
- Playwright
- Chromium browser
