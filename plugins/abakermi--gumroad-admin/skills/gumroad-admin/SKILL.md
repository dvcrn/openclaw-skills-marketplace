---
name: gumroad-admin
description: "Gumroad Admin CLI. Check sales, products, and manage discounts."
---

# Gumroad Admin

Manage your Gumroad store from OpenClaw.

## Setup

1. Get your Access Token from Gumroad (Settings > Advanced > Applications).
2. Set it: `export GUMROAD_ACCESS_TOKEN="your_token"`

## Commands

### Sales
```bash
gumroad-admin sales --day today
gumroad-admin sales --last 30
```

### Products
```bash
gumroad-admin products
```

### Discounts
```bash
gumroad-admin discounts create --product <id> --code "TWITTER20" --amount 20 --type percent
```
