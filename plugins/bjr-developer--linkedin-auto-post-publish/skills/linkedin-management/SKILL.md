---
name: linkedin-management
description: "Automates LinkedIn interactions like posting, editing, deleting, and reacting by utilizing browser-captured session cookies and network request structures."
---

# LinkedIn Management Skill

This skill allows agents to automate interactions with LinkedIn by intercepting internal API requests (Voyager and SDUI) and mimicking them using Python's `requests` library.

## When to use this skill
Use this skill when you need to programmatically:
- Create text or image posts on LinkedIn.
- Edit existing posts.
- Delete posts.
- React to posts (Like, Celebrate, Support, Love, Insightful, Funny).
- Comment on posts.

## How it works
LinkedIn uses a combination of GraphQL (Voyager) and Server-Driven UI (SDUI) endpoints. Authentication is primarily handled via cookies (`li_at`, `JSESSIONID`) and headers.

**IMPORTANT**: This skill uses placeholders for all session data. You **must** provide your own `linkedin_cookies.json` and session-specific headers.

### Gathering Cookies & Session Data
To use this skill, you must manually gather:
1.  **Cookies**: Use a Chrome extension (like "Cookie-Editor") or the DevTools Application tab to export `li_at` and `JSESSIONID`. Save them in `linkedin_cookies.json` using the provided template.
2.  **Session Headers**: Use the included `advanced-network-capture` extension to find your `x-li-page-instance` when performing an action on LinkedIn. Update this value in `li_interact.py`.

## Scripts Included

Located in the `scripts/` directory:

### 1. `capture_session.py`
Uses Playwright to open a LinkedIn session, allowing the user to log in and perform actions manually. It captures the cookies and network logs.
**Usage:**
```bash
python scripts/capture_session.py
```

### 2. `li_interact.py`
A comprehensive utility class `LinkedInBot` that handles automated actions.
**Supported actions:** 
- `create_post(text, media_urn=None)`
- `edit_post(share_urn, activity_id, text)`
- `delete_post(activity_id)`
- `react_to_post(activity_id, reaction_type)`
- `create_comment(activity_id, text)`
- `upload_image(image_path)`

**Usage via Python:**
```python
from scripts.li_interact import LinkedInBot

bot = LinkedInBot(cookies_file="linkedin_cookies.json")
bot.create_post("Hello from automated LinkedIn bot!")
```

## Setup Requirements
- Python >= 3.10
- Packages: `requests`, `playwright`
- Cookies: `li_at` and `JSESSIONID` are mandatory.

> [!WARNING]
> Automation on LinkedIn is strictly regulated. Use this skill sparingly and avoid high-frequency automated actions to prevent account suspension.
