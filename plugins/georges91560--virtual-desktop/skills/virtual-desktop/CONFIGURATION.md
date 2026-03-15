# Virtual Desktop — Configuration Guide

## Why Playwright and not Xvfb + noVNC

The common approach (Xvfb + XFCE + noVNC + systemd) installs services
on the **VPS host** — but your agent lives inside a Docker container
and cannot access host systemd services. It also opens port 6080
to the internet (security risk) and requires root host modifications.

Playwright runs **inside the container** where your agent already lives:

```
VPS Host
└── Docker container (your openclaw container)
    └── Agent
        └── virtual-desktop skill
            └── Playwright headless Chromium
```

No extra ports. No host changes. Screenshots replace the visual feed.

---

## Session Management

Sessions are saved per platform as JSON files containing cookies and
localStorage. Once saved, the agent reuses them without re-authenticating.

| Platform | Session file |
|---|---|
| Google / Gmail / Drive | `/workspace/credentials/sessions/google_session.json` |
| Any platform | `/workspace/credentials/sessions/{platform}_session.json` |

**Sessions contain authentication tokens — never expose or transmit them.**

To reset a session (if expired):
```bash
rm /workspace/credentials/sessions/{platform}_session.json
```

---

## Troubleshooting

**`playwright install` fails**
```bash
pip install playwright --break-system-packages
playwright install chromium --with-deps
```

**Screenshot is black or blank**
→ Page not fully loaded. Add before screenshot:
```python
page.wait_for_load_state("networkidle")
```

**Cloudflare blocks the request**
→ Add realistic user agent + locale to browser context (see Anti-Bot section in SKILL.md)
→ If still blocked: residential proxy required

**Session expired — redirect to login page**
→ Delete the session file and re-authenticate:
```bash
rm /workspace/credentials/sessions/{platform}_session.json
```

**Element not found**
→ Site updated their HTML. Screenshot the page, find the new selector,
update `.learnings/LEARNINGS.md` with the new selector map.

**Container has no display**
→ Normal — Playwright runs headless, no display needed.
→ If you see `DISPLAY` errors: ensure `headless=True` in `launch()`.
