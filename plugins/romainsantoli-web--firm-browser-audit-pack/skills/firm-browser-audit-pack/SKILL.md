---
name: firm-browser-audit-pack
description: "Browser automation security audit pack. Validates Playwright/Puppeteer headless configuration for dangerous arguments. 1 audit tool."
---

# firm-browser-audit-pack

> ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.

## Purpose

Audits browser automation configurations for security risks. Detects 13 dangerous
Chrome/Chromium arguments (--no-sandbox, --disable-web-security, etc.) in Playwright
and Puppeteer configs with severity-based classification.

## Tools (1)

| Tool | Description | Severity |
|------|-------------|----------|
| `openclaw_browser_context_check` | Headless browser config security audit | CRITICAL (--no-sandbox), HIGH (others) |

## Usage

```yaml
skills:
  - firm-browser-audit-pack

# Audit browser configuration:
openclaw_browser_context_check config_path=/path/to/config.json
```

## Requirements

- `mcp-openclaw-extensions >= 3.0.0`
