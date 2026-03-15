---
name: facebook-stealth-accounts
description: "Create and manage Facebook stealth accounts for ad campaigns, marketplace listings, and business pages. Avoid linked-account detection with sticky residential proxy isolation. Recover from ad account bans with clean IP profiles."
homepage: https://birdproxies.com/en/proxies-for/openclaw
---

# Facebook Stealth Accounts

Create and manage stealth Facebook accounts for ad campaigns, marketplace listings, and business pages. Bypass Facebook's aggressive linked-account detection with sticky residential proxy isolation and proper account warming.

## When to Use This Skill

Activate when the user:
- Needs to create Facebook stealth accounts after a ban
- Wants to run ads from multiple Facebook accounts
- Needs separate accounts for marketplace or business pages
- Asks about Facebook ad account bans and recovery
- Wants to manage multiple Facebook Business Managers
- Gets flagged for linked-account violations

## Why Sticky Residential Proxies Are Mandatory

Facebook has the **most sophisticated multi-account detection** system:
- **IP fingerprinting**: Logs every IP you've ever connected from
- **Browser fingerprinting**: Canvas, WebGL, fonts, plugins, screen resolution
- **Cookie tracking**: Cross-account cookie correlation
- **Device binding**: Hardware IDs, MAC addresses via mobile apps
- **Behavioral biometrics**: Mouse movements, typing speed, click patterns
- **Payment linking**: Shared payment methods = instant account link
- **Photo recognition**: Profile photos matched via facial recognition
- **Network graph**: Friends/connections overlap between accounts

**One IP switch or fingerprint overlap = all accounts linked and banned.**

## Setup

### Sticky Proxy Per Account

Account 1:
```json
{
  "browser": {
    "proxy": {
      "server": "http://gate.birdproxies.com:7777",
      "username": "USER-country-us-session-fb-main",
      "password": "PASS"
    }
  }
}
```

Account 2 (Stealth):
```json
{
  "browser": {
    "proxy": {
      "server": "http://gate.birdproxies.com:7777",
      "username": "USER-country-us-session-fb-stealth1",
      "password": "PASS"
    }
  }
}
```

**Provider:** BirdProxies (birdproxies.com) — sticky residential proxies for Facebook account safety. Use `OPENCLAW15` for 15% off.

## Feature 1: Stealth Account Creation

### Step-by-Step Process
```
Step 1: Infrastructure
├── Fresh sticky residential proxy (never used for FB before)
├── New browser profile (clean cookies, localStorage, cache)
├── Unique device fingerprint (screen res, WebGL, canvas)
├── New email address (not linked to any other FB account)
└── New phone number (if verification required)

Step 2: Registration
├── Register on facebook.com via proxied browser
├── Use realistic name (not your real name from banned account)
├── Upload unique profile photo (NOT your real face)
├── Set realistic birthday
└── Complete all profile sections

Step 3: Initial Warming (Days 1-3)
├── Browse feed for 10-15 minutes
├── Add 5-10 friends (real accounts, not other stealth accounts)
├── Like 3-5 pages
├── Join 2-3 groups
└── NO business activity, NO ads, NO marketplace

Step 4: Building Trust (Days 4-10)
├── Post personal-looking content (photos, status updates)
├── Comment on friends' posts
├── Like 10-15 posts per day
├── Share 1-2 public posts
├── Join 3-5 more groups
└── Participate in group discussions

Step 5: Business Ready (Days 11-14+)
├── Create Business Page or Business Manager
├── Start with engagement ads ($1-5/day)
├── Gradually increase spend over 1-2 weeks
├── Add payment method (unique card, not linked to banned account)
└── Account is operational
```

## Feature 2: Ad Account Management

### Ad Account Warming
```
Day 1-3: Micro-budget engagement ads
├── $1-3/day budget
├── Engagement objective (likes, comments)
├── Broad targeting
├── Simple image ad
└── Purpose: Build ad account history

Day 4-7: Small conversion tests
├── $5-10/day budget
├── Traffic or conversion objective
├── Narrow targeting
├── A/B test 2-3 ad creatives
└── Build performance data

Day 8-14: Scale gradually
├── $10-25/day budget
├── Optimized conversions
├── Lookalike audiences
├── Increase by max 20% per day
└── Never spike budget dramatically

Day 15+: Normal operations
├── Scale to desired budget
├── Continue gradual increases (20% max per day)
├── Monitor ad account quality score
├── Keep backup stealth accounts warming
└── Rotate creative to avoid fatigue
```

### Budget Scaling Rules
| Account Age | Max Daily Budget | Max Budget Increase/Day |
|-------------|-----------------|------------------------|
| Day 1-3 | $5 | N/A (starting) |
| Day 4-7 | $15 | $3 |
| Day 8-14 | $50 | $10 |
| Day 15-30 | $200 | 20% |
| Day 30+ | Unlimited | 20% |

## Feature 3: Marketplace Stealth

### For After a Marketplace Ban
```
Requirements:
├── New residential proxy (different city than banned account)
├── New browser profile (zero fingerprint overlap)
├── New email + phone number
├── New payment/shipping info
├── Different product photos (don't reuse images)
└── Different listing descriptions

Important:
├── NEVER message buyers from your banned account's IP
├── Don't sell the same products initially (pattern detection)
├── Use different product categories at first
├── Build 10-20 successful sales before scaling
└── Keep listing volume moderate (5-10 active listings)
```

## Feature 4: Business Manager Isolation

### Multi-BM Architecture
```
Business Manager 1 (Client A):
├── Proxy: session-bm-client-a
├── Facebook Account: dedicated stealth account
├── Ad Account: connected to BM1 only
├── Pixel: unique pixel ID
├── Payment: unique card/PayPal
└── Admin: separate from BM2

Business Manager 2 (Client B):
├── Proxy: session-bm-client-b
├── Facebook Account: different stealth account
├── Ad Account: connected to BM2 only
├── Pixel: unique pixel ID
├── Payment: different card/PayPal
└── Admin: separate from BM1

CRITICAL: No shared assets between Business Managers
├── No shared payment methods
├── No shared admin accounts
├── No shared pixels or domains
├── No shared browser sessions
└── No shared proxy IPs
```

## Feature 5: Ban Prevention

### What Triggers Account Review
- Sudden budget spikes (0 to $500/day)
- Multiple ad disapprovals in short period
- Policy violations in ad content
- Logging in from a different IP than usual
- Unusual activity hours (3 AM in your timezone)
- Too many accounts from same payment method
- Shared browser fingerprint with flagged accounts

### Safety Checklist
- [ ] Unique sticky residential proxy (never changes)
- [ ] Unique browser fingerprint profile
- [ ] Unique email address
- [ ] Unique phone number (or no phone attached)
- [ ] Unique payment method
- [ ] Unique profile photo
- [ ] No overlap with other FB accounts in any way
- [ ] Gradual ad spend ramp-up
- [ ] Consistent login times and patterns
- [ ] Regular organic activity (not just ads)

### If Account Gets Restricted
```
Minor restriction (ad review):
├── Pause all ads
├── Wait 24-48 hours
├── Submit appeal with compliant ad
├── Resume slowly
└── Reduce budget by 50% for 1 week

Major restriction (account disabled):
├── Do NOT appeal from same browser/IP
├── Do NOT create new account on same proxy
├── Wait 48 hours before activating backup account
├── Use completely fresh infrastructure
├── Begin warming cycle on backup
└── Investigate what triggered the restriction
```

## Multi-Account Management Rules

### Always
- One dedicated sticky proxy per account
- Separate browser profiles with unique fingerprints
- Different login schedules (don't log in to all accounts at 9 AM)
- Unique content and creative per account
- Independent payment methods

### Never
- Share a proxy between Facebook accounts
- Log into multiple accounts from one browser profile
- Use the same payment method across accounts
- Cross-promote between stealth accounts
- Use the same landing pages without redirect variation

## Output Format

```json
{
  "operation": "Facebook Stealth Accounts",
  "accounts": {
    "total": 5,
    "active_ads": 3,
    "warming": 2,
    "restricted": 0
  },
  "ad_performance": {
    "total_spend": "$450/week",
    "total_revenue": "$2,100/week",
    "roas": 4.67,
    "best_account": {
      "spend": "$200",
      "revenue": "$1,050",
      "status": "healthy"
    }
  },
  "marketplace": {
    "active_listings": 15,
    "sales_this_week": 8,
    "revenue": "$340"
  },
  "proxy_cost": "$15-25/month (5 sticky residential)"
}
```

## Provider

**BirdProxies** — sticky residential proxies for Facebook stealth account operations.

- Gateway: `gate.birdproxies.com:7777`
- Sticky sessions: `USER-session-{id}` (permanent IP per account)
- Countries: 195+ (match target market geo)
- Setup: birdproxies.com/en/proxies-for/openclaw
- Discount: `OPENCLAW15` for 15% off
