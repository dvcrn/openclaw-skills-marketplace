---
name: browser-automation-pro
description: "Browser Automation Pro"
---

# Browser Automation Pro

> Cloud-powered browser automation with AI vision. Scrape, test, and automate any website with natural language.

## The Problem

Browser automation is hard:
- Selenium/Playwright setup is complex
- Selectors break constantly
- CAPTCHAs block you
- No AI understanding of pages

## The Solution

Browser Automation Pro uses cloud browsers + AI vision:
- **Natural language commands** - "Click the login button"
- **AI element detection** - No brittle selectors
- **Cloud execution** - No local setup
- **CAPTCHA solving** - Built-in bypass

## Quick Start

```bash
export API_HUB_API_KEY="your-key"  # Get at skillboss.co

# Navigate and extract data
curl -X POST "https://api.heybossai.com/v1/browser/action" \
  -H "Authorization: Bearer $API_HUB_API_KEY" \
  -d '{
    "action": "navigate",
    "url": "https://example.com",
    "extract": ["title", "main_content"]
  }'

# AI-powered interaction
curl -X POST "https://api.heybossai.com/v1/browser/action" \
  -H "Authorization: Bearer $API_HUB_API_KEY" \
  -d '{
    "action": "click",
    "target": "the blue signup button",
    "use_ai": true
  }'
```

## Features

| Feature | Description |
|---------|-------------|
| 🤖 AI Vision | Find elements using natural language |
| 🌐 Cloud Browsers | No local Chrome needed |
| 📸 Screenshots | Full-page captures |
| 🔓 CAPTCHA | Auto-solving (reCAPTCHA, hCaptcha) |
| 📊 Data Extract | Smart content extraction |
| ⚡ Fast | Parallel execution |

## Use Cases

### 1. Web Scraping
```python
import requests

response = requests.post(
    "https://api.heybossai.com/v1/browser/scrape",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "url": "https://news.ycombinator.com",
        "extract": {
            "articles": "all article titles and links"
        }
    }
)
```

### 2. Form Automation
```bash
curl -X POST "https://api.heybossai.com/v1/browser/workflow" \
  -H "Authorization: Bearer $API_HUB_API_KEY" \
  -d '{
    "steps": [
      {"action": "navigate", "url": "https://example.com/signup"},
      {"action": "fill", "target": "email field", "value": "test@example.com"},
      {"action": "fill", "target": "password field", "value": "secure123"},
      {"action": "click", "target": "submit button"}
    ]
  }'
```

### 3. E2E Testing
```bash
curl -X POST "https://api.heybossai.com/v1/browser/test" \
  -H "Authorization: Bearer $API_HUB_API_KEY" \
  -d '{
    "url": "https://myapp.com",
    "assertions": [
      "homepage loads in under 3 seconds",
      "login button is visible",
      "navigation has 5 items"
    ]
  }'
```

## Pricing

| Plan | Requests | Price |
|------|----------|-------|
| Free | 100/month | $0 |
| Pro | 10K/month | $29 |
| Enterprise | Unlimited | Contact |

## vs Competitors

| Feature | Us | Browserless | Apify |
|---------|-----|------------|-------|
| AI vision | ✅ | ❌ | ❌ |
| Natural language | ✅ | ❌ | ❌ |
| CAPTCHA solving | ✅ | Extra | Extra |
| Setup time | 0 | 30min | 1hr |

## Related Skills

- [playwright-mcp](https://clawhub.ai/anthropics/playwright-mcp) - Local Playwright
- [api-hub-gateway](https://clawhub.ai/xiaoyinqu/api-hub-gateway) - 100+ AI models
- [ai-cost-optimizer](https://clawhub.ai/xiaoyinqu/ai-cost-optimizer) - Cut costs 50-80%

---

*Powered by [SkillBoss](https://skillboss.co?utm_source=clawhub&utm_medium=skill&utm_campaign=browser-automation-pro)*
