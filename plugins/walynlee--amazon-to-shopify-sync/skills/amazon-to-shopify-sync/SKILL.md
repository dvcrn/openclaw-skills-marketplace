---
name: amazon-to-shopify-sync
description: "amazon-to-shopify-sync"
---

# Amazon to Shopify Sync Skill 🦞

## Description
Extract product data from Amazon (multilingual) and synchronize it directly to Shopify via REST Admin API with automatic token renewal.

## Core Logic
- **Automatic Token Renewal**: Triggers `client_credentials` grant before every sync to bypass the 24h token expiry.
- **Multilingual Support**: Extracted French content is rewritten into high-conversion English Body HTML.
- **API Mapping**: Targets `dinoho.myshopify.com` for authentication and `dinoho.cn` for store data.

## Configuration
- **Grant URL**: `https://dinoho.myshopify.com/admin/oauth/access_token`
- **Product API**: `https://dinoho.myshopify.com/admin/api/2024-01/products.json`
- **Keys**: Client ID (32-char) & Secret Key (Managed in environment/scripts).

## Usage
Trigger this skill when the user provides an Amazon URL (e.g. Amazon.fr, .de, .uk) for automated Shopify listing.
