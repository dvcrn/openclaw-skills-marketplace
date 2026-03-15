---
name: tianmao
description: "Tianmao"
---

# Tianmao (天猫) Skill

Simple browser launcher for Tmall.com (天猫) e-commerce platform.

## Description

This skill helps users quickly open the Tmall (天猫) website in their browser. It's designed to be a simple, no-frills utility that guides users to the correct Tmall URLs (tmall.com or tianmao.com) and lets them browse, shop, and complete transactions independently.

## Commands

### Open Tmall Homepage
```bash
tianmao open
```
Opens the main Tmall homepage (https://www.tmall.com) in your default browser.

### Open Tianmao (Alternative Domain)
```bash
tianmao tianmao
```
Opens the alternative domain (https://www.tianmao.com) which redirects to Tmall.

### Search on Tmall (Optional)
```bash
tianmao search "运动鞋"
```
(Optional) Opens Tmall search results for the given query. This requires more complex browser automation and may be added in future versions.

## Features

- **Simple Launch**: Just opens the browser to Tmall – no complex setup
- **Dual Domain Support**: Supports both tmall.com and tianmao.com URLs
- **User Control**: After opening the browser, users complete all shopping independently
- **No Data Collection**: Does not store any user data, cookies, or browsing history
- **Cross‑Platform**: Works on macOS, Linux, and Windows (via OpenClaw browser tool)

## Technical Implementation

### Core Implementation
The skill uses OpenClaw's built‑in `browser` tool to open the target URL. No external dependencies are required.

**Example agent usage:**
```javascript
browser({action: 'open', url: 'https://www.tmall.com', profile: 'chrome'})
```

### Script Implementation (Optional)
A standalone CLI script can be created for convenience:

```bash
#!/bin/bash
# bin/tianmao
openclaw browser open --url https://www.tmall.com
```

### Integration with Existing E‑commerce Skills
This skill is intentionally minimal. For advanced features (product search, price tracking, login automation), consider using the `taobao` or `alibaba` skills which offer full‑featured automation.

## File Structure

```
~/.openclaw/workspace/skills/tianmao/
├── SKILL.md               # This documentation
├── README.md              # Quick start guide (optional)
├── bin/
│   └── tianmao            # Main executable script
├── examples/
│   └── basic-usage.md     # Example usage scenarios
└── references/
    └── tmall-urls.md      # Reference: official Tmall URLs
```

## Installation & Usage

### As an OpenClaw Agent
When the `tianmao` skill is installed, agents can invoke it directly:
```
Open Tmall for me → triggers tianmao open
```

### As a Standalone CLI
If the `bin/tianmao` script is made executable and added to `PATH`:
```bash
tianmao open
```

## Privacy & Security

- **No Authentication**: This skill does not handle login or authentication
- **No Data Storage**: No cookies, browsing history, or personal data is stored
- **Browser‑Only**: All interaction happens in the user's own browser session
- **Transparent**: Users see exactly what URL is opened and can verify it's the legitimate Tmall site

## Why This Skill Exists

Many users know they want to shop on "天猫" but may not remember the exact URL (tmall.com vs tianmao.com). This skill provides a quick, reliable way to get to the right starting point, then steps out of the way so users can shop normally.

## Future Enhancements (Optional)

If the skill evolves beyond the simple version:
1. **Search Integration**: Open Tmall with a pre‑filled search query
2. **Category Shortcuts**: Open specific category pages (e.g., electronics, clothing)
3. **Deals Page**: Open the current promotion/deals page
4. **Mobile‑Optimized**: Open the mobile‑friendly version (m.tmall.com)

---

**Maintainer**: OpenClaw Skills Team  
**Version**: 1.0.0 (Simple Browser Launcher)  
**Last Updated**: 2026‑03‑10