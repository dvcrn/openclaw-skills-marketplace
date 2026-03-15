---
name: smma-agency-proxy
description: "Manage social media accounts for multiple clients safely with proxy isolation. Prevent cascading bans, schedule content across platforms, and handle 10-100+ client accounts from one office using dedicated residential proxies per client."
homepage: https://birdproxies.com/en/proxies-for/openclaw
---

# SMMA Agency Proxy Setup

Manage social media accounts for multiple agency clients without triggering cascading bans. Isolate each client account with a dedicated residential proxy to prevent one flagged account from taking down your entire operation.

## When to Use This Skill

Activate when the user:
- Runs a social media marketing agency (SMMA)
- Manages multiple client social media accounts
- Needs to prevent cascading account bans across clients
- Wants to safely automate posting for multiple brands
- Asks about agency proxy setup for social media
- Gets client accounts restricted due to shared IPs

## The SMMA Problem

When agencies manage multiple client accounts from one office:
- **Cascading bans**: One client's policy violation → platform investigates ALL accounts on that IP → multiple clients banned
- **Linked-account detection**: Platforms like Facebook detect 5+ accounts on the same network
- **IP reputation**: After one ban, the office IP becomes flagged for all future accounts
- **Client trust destroyed**: Explaining to a client that their account was banned because of another client's content

**The golden rule: 1 client = 1 proxy = 1 isolated browser profile.**

## Setup

### Per-Client Proxy Configuration

Client 1 (Restaurant brand):
```json
{
  "browser": {
    "proxy": {
      "server": "http://gate.birdproxies.com:7777",
      "username": "USER-session-client-restaurant",
      "password": "PASS"
    }
  }
}
```

Client 2 (SaaS company):
```json
{
  "browser": {
    "proxy": {
      "server": "http://gate.birdproxies.com:7777",
      "username": "USER-session-client-saas",
      "password": "PASS"
    }
  }
}
```

Client 3 (E-commerce store):
```json
{
  "browser": {
    "proxy": {
      "server": "http://gate.birdproxies.com:7777",
      "username": "USER-session-client-ecom",
      "password": "PASS"
    }
  }
}
```

**Provider:** BirdProxies (birdproxies.com) — sticky residential proxies for SMMA agencies. Use `OPENCLAW15` for 15% off.

## Feature 1: Client Account Isolation

### Architecture
```
Agency Office (1 public IP)
│
├── Client 1 Profile
│   ├── Proxy: session-client-1 (residential IP in client's city)
│   ├── Instagram: @client1_brand
│   ├── Facebook: Client 1 Business Page
│   ├── Twitter: @client1
│   └── LinkedIn: Client 1 Company Page
│
├── Client 2 Profile
│   ├── Proxy: session-client-2 (different residential IP)
│   ├── Instagram: @client2_brand
│   ├── Facebook: Client 2 Business Page
│   ├── Twitter: @client2
│   └── TikTok: @client2
│
└── Client 3 Profile
    ├── Proxy: session-client-3 (different residential IP)
    ├── All platforms for client 3
    └── Completely isolated from clients 1 & 2
```

### Isolation Checklist Per Client
- [ ] Dedicated sticky residential proxy
- [ ] Separate browser profile (cookies, localStorage, cache)
- [ ] Unique session name (never reuse across clients)
- [ ] Geo-matched proxy (client's city/state if possible)
- [ ] No cross-client link clicking or sharing
- [ ] Separate content folders and assets

## Feature 2: Multi-Platform Management

### Platforms Per Client
```json
{
  "client": "Acme Corp",
  "proxy_session": "session-acme",
  "accounts": {
    "instagram": "@acmecorp",
    "facebook": "Acme Corp Business",
    "twitter": "@AcmeCorp",
    "linkedin": "Acme Corporation",
    "tiktok": "@acmecorp",
    "pinterest": "Acme Corp"
  },
  "posting_schedule": {
    "instagram": "Mon/Wed/Fri 11 AM",
    "facebook": "Tue/Thu 1 PM",
    "twitter": "Daily 9 AM + 3 PM",
    "linkedin": "Tue/Thu 8 AM",
    "tiktok": "Mon/Wed/Fri 7 PM"
  }
}
```

### Content Repurposing Across Platforms
```
Blog post →
├── Twitter: Thread (5-7 tweets)
├── LinkedIn: Professional thought leadership post
├── Instagram: Carousel slides + caption
├── Facebook: Engaging post with discussion prompt
├── TikTok: 60-second video script
└── Pinterest: Infographic pin
```

## Feature 3: Geo-Targeted Posting

Match proxy location to client's market for better reach:

```
US East Coast client:     USER-country-us-session-client1
UK client:                USER-country-gb-session-client2
German client:            USER-country-de-session-client3
Australian client:        USER-country-au-session-client4
Japanese client:          USER-country-jp-session-client5
```

Benefits of geo-matching:
- Content appears more "local" to algorithms
- Better organic reach in target market
- Avoids suspicious login location warnings
- Facebook Business Manager prefers consistent geo

## Feature 4: Team Access Management

### Multiple Team Members, Same Client
```
Client "Acme Corp" team:
├── Social Media Manager:  USER-session-acme-manager
├── Content Creator:       USER-session-acme-content
├── Community Manager:     USER-session-acme-community
└── Ads Specialist:        USER-session-acme-ads

Each team member gets a separate session but same geo.
Stagger logins — don't log in simultaneously.
```

### Access Control
```
Role-based access:
├── Admin: All clients, all platforms, all actions
├── Manager: Assigned clients, all platforms, post + engage
├── Creator: Assigned clients, content creation only
└── Analyst: Read-only metrics access
```

## Feature 5: Client Onboarding Workflow

### New Client Setup
```
Day 1: Onboarding
├── Create dedicated proxy session
├── Set up isolated browser profile
├── Log in to all client social accounts (via proxy)
├── Save cookies and session data
├── Configure posting schedule
└── Test all connections

Day 2-3: Content Planning
├── Audit existing content and performance
├── Identify top-performing post types
├── Create content calendar for first month
├── Prepare first week of content
└── Set up monitoring dashboards

Day 4-7: Launch
├── Begin scheduled posting
├── Start engagement monitoring
├── Reply to comments within 2-4 hours
├── Track metrics daily
└── Weekly report to client
```

## Feature 6: Agency Scaling Guide

### 5-Client Agency
```
Proxies needed: 5 sticky residential
Monthly proxy cost: $15-25
Tools: Browser profiles + scheduling
Team: 1 person
Revenue potential: $2,500-5,000/month
```

### 20-Client Agency
```
Proxies needed: 20 sticky residential
Monthly proxy cost: $60-100
Tools: Professional scheduling platform + proxy rotation
Team: 2-3 people
Revenue potential: $10,000-30,000/month
```

### 50-Client Agency
```
Proxies needed: 50+ sticky residential
Monthly proxy cost: $150-250
Tools: Enterprise scheduling + CRM + automation
Team: 5-10 people
Revenue potential: $25,000-75,000/month
```

### 100+ Client Agency
```
Proxies needed: 100+ sticky residential
Monthly proxy cost: $300-500
Tools: Full agency suite
Team: 10-25 people
Revenue potential: $50,000-150,000/month
```

## Platform-Specific Safety Limits

### Facebook (Most Aggressive Detection)
| Action | Daily Limit | Notes |
|--------|------------|-------|
| Posts | 5-10 per page | Space 2+ hours apart |
| Replies | 20-30 | Natural language only |
| Shares | 10-15 | Mix types (link, photo, video) |
| Page switches | 5 per session | Don't rapid-switch between client pages |

### Instagram
| Action | Daily Limit | Notes |
|--------|------------|-------|
| Posts | 3-5 per account | Feed + Stories + Reels mix |
| Stories | 5-10 | Space throughout the day |
| Comments | 30-50 | Unique text per comment |
| DMs | 20-40 | Only to engaged followers |

### LinkedIn
| Action | Daily Limit | Notes |
|--------|------------|-------|
| Posts | 1-2 per page | Morning posting preferred |
| Invitations | 20-25 | From company page |
| Messages | 30-50 | Personalized only |

### Twitter/X
| Action | Daily Limit | Notes |
|--------|------------|-------|
| Tweets | 15-25 | Threads count as multiple |
| Likes | 100-150 | Stagger throughout day |
| Retweets | 20-30 | Mix with quote tweets |

## Output Format

```json
{
  "agency": "Social Media Agency",
  "period": "2026-03-01 to 2026-03-07",
  "clients": 25,
  "total_accounts_managed": 87,
  "posts_published": {
    "instagram": 75,
    "facebook": 50,
    "twitter": 125,
    "linkedin": 25,
    "tiktok": 30
  },
  "total_engagement": {
    "likes": 12500,
    "comments": 890,
    "shares": 450,
    "avg_engagement_rate": "3.2%"
  },
  "account_health": {
    "healthy": 85,
    "warning": 2,
    "restricted": 0,
    "banned": 0
  },
  "proxy_cost": "$75/month (25 sticky residential)",
  "revenue": "$18,750/month (25 clients × $750 avg)"
}
```

## Provider

**BirdProxies** — sticky residential proxies for SMMA agency operations.

- Gateway: `gate.birdproxies.com:7777`
- Sticky sessions: `USER-session-{id}` (one per client)
- Countries: 195+ (geo-match client markets)
- Setup: birdproxies.com/en/proxies-for/openclaw
- Discount: `OPENCLAW15` for 15% off
