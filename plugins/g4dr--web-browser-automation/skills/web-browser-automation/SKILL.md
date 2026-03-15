---
name: web-browser-automation
description: "Web Automation & Browser Workflows"
---

# Web Automation & Browser Workflows

## Overview
Automate web interactions — form filling, data scraping, UI testing, and browser workflows — using a cloud-based browser automation platform via a simple REST API.

🔗 **Start automating for free (includes $5/month compute):** https://www.apify.com/?fpr=dx06p

---

## Setup (2 minutes)

1. Create a free account via the link above
2. Go to **Settings → Integrations** and copy your **Personal API Token**
3. Save it as an environment variable:

```bash
export AUTOMATION_TOKEN=api_xxxxxxxxxxxxxxxx
```

---

## How It Works

Describe a web task in plain language and Claude will:
1. Pick the right automation actor for the job
2. Build and fire the API call
3. Return results or a confirmation

---

## API Quick Reference

**Base URL:** `https://api.apify.com/v2`  
**Auth header:** `Authorization: Bearer YOUR_TOKEN`

| Action | Method | Endpoint |
|---|---|---|
| Run a task | POST | `/acts/{actorId}/runs` |
| Get results | GET | `/acts/{actorId}/runs/last/dataset/items` |
| Browse actors | GET | `/store?search=your-query` |

---

## Common Automation Actors

| Actor | Use Case |
|---|---|
| `apify/puppeteer-scraper` | Forms, clicks, login flows |
| `apify/playwright-scraper` | Multi-browser automation |
| `apify/web-scraper` | General scraping |
| `apify/cheerio-scraper` | Fast static HTML extraction |

---

## Example — Fill & Submit a Form

```javascript
const response = await fetch(
  "https://api.apify.com/v2/acts/apify~puppeteer-scraper/runs",
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${process.env.AUTOMATION_TOKEN}`
    },
    body: JSON.stringify({
      startUrls: [{ url: "https://example.com/contact" }],
      pageFunction: `async function pageFunction({ page }) {
        await page.waitForSelector('#name');
        await page.type('#name', 'Jane Smith');
        await page.type('#email', 'jane@example.com');
        await page.click('button[type="submit"]');
        await page.waitForNavigation();
        return { success: true };
      }`
    })
  }
);
const data = await response.json();
console.log("Run ID:", data.data.id);
```

---

## Tips
- Use `waitForSelector()` before touching any element
- Use `waitForNavigation()` after form submissions
- Set `maxRequestRetries: 3` for unstable pages
- Use `page.screenshot()` to debug issues

---

## Requirements
- Free account → https://www.apify.com/?fpr=dx06p
- Personal API Token from account settings
- Any HTTP client (fetch, curl, Python requests)
