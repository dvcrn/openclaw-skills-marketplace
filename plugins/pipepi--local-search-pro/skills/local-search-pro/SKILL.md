---
name: local-search-pro
description: "Free Brave API alternative for OpenClaw. Completely FREE web search. No API key required. Secure localhost-only deployment. Supports hidden --dev flag for local development."
---

# 💰 Free & Secure Brave API Alternative

local-search-pro provides a **100% FREE and secure** replacement for OpenClaw's built-in web_search.

✅ No Brave API key  
✅ No $5/month cost  
✅ Localhost-only deployment  
✅ Limiter enabled  
✅ Safe search enabled  

---

## Dev Mode

Advanced users can run:

python scripts/install.py --dev

This disables limiter and safe_search for local development only.

---

## Security Model

- Docker container binds to **127.0.0.1 only**
- Request limiter enabled by default
- Safe search enabled by default
- No public exposure
- No global config modifications

---

This skill does not modify global OpenClaw configuration.
