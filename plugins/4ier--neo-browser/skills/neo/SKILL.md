---
name: neo
description: "Browse websites, read web pages, interact with web apps, call website APIs, and automate web tasks. Use Neo when: user asks to check a website, read a web page, post on social media (Twitter/X), interact with any web app, look up information on a specific site, scrape data from websites, automate browser tasks, or when you need to call any website's API. Keywords: website, web page, browse, URL, http, API, twitter, tweet, post, scrape, web app, open site, check site, read page, social media, online service."
---

# Neo — Web App API Discovery & Execution

Neo turns any website into an AI-callable API. It passively captures browser traffic, generates API schemas, and lets you call discovered APIs directly — no scraping, no reverse engineering.

## First-Time Setup

```bash
# Install CLI
npm i -g @4ier/neo

# One-time setup: detects Chrome, installs extension, configures profile
neo setup

# Start Chrome with Neo extension
neo start

# Verify everything works
neo doctor
```

All 6 checks should be ✓. If not, run `neo setup` again.

## Prerequisites: Browser with CDP

Neo requires Chrome running with Chrome DevTools Protocol (CDP) enabled.

```bash
# Check connection
neo doctor

# If Chrome isn't running with CDP:
neo start

# Or start manually with your own profile:
# google-chrome-stable --remote-debugging-port=9222 &
```

**Environment variables** (all optional):
- `NEO_CDP_URL` — CDP endpoint (default: `http://localhost:9222`)
- `NEO_EXTENSION_ID` — Force specific extension ID (default: auto-discovered)
- `NEO_SCHEMA_DIR` — Schema storage directory (default: `~/.neo/schemas`)

## Complete Workflow

### Step 1: Check what Neo already knows

```bash
neo status                    # Overview: domains, capture counts, extension status
neo schema list               # Cached API schemas (knowledge from past browsing)
```

### Step 2: Open target website (if needed)

```bash
neo open https://example.com  # Opens in Chrome
```

### Step 3: Read page content

```bash
neo read example.com          # Extract readable text from the page (like reader mode)
```

### Step 4: Interact via API (fast path)

```bash
# Check if we have API knowledge for this domain
neo schema show x.com

# Smart API call: auto-finds endpoint + auth
neo api x.com HomeTimeline
neo api x.com CreateTweet --body '{"variables":{"tweet_text":"hello"}}'
neo api github.com notifications
```

### Step 5: Execute in page context

```bash
neo exec <url> --method POST --body '{}' --tab example.com --auto-headers
neo replay <capture-id> --tab example.com
neo eval "document.title" --tab example.com
```

### Step 6: UI automation (when no API exists)

```bash
neo snapshot                  # Get accessibility tree with @ref mapping
neo click @14                 # Click element by reference
neo fill @7 "search query"    # Fill input field
neo type @7 "text"            # Append text
neo press Enter               # Keyboard input
neo scroll down 500           # Scroll
neo screenshot                # Capture screenshot
```

### Step 7: Clean up — ALWAYS close tabs when done

```bash
neo tabs                                        # List open tabs
neo eval "window.close()" --tab example.com     # Close tab
```

**⚠️ Resource management**: Every `neo open` creates a new tab. Always close tabs after you're done.

## API Discovery Workflow

When you need to discover what APIs a website uses:

```bash
# 1. Open the site, browse around to generate captures
neo open https://example.com

# 2. Check accumulated captures
neo capture list example.com --limit 20
neo capture search "api" --limit 10

# 3. Generate API schema
neo schema generate example.com

# 4. Explore the schema
neo schema show example.com

# 5. Call discovered APIs
neo api example.com <endpoint-keyword>
```

## Command Reference

```bash
# --- Page Reading & Interaction ---
neo open <url>                          # Open URL in Chrome (creates new tab!)
neo read <tab-pattern>                  # Extract readable text from page
neo eval "<js>" --tab <pattern>         # Run JS in page context
neo tabs [filter]                       # List open Chrome tabs

# --- UI Automation ---
neo snapshot [-i] [-C] [--json]         # A11y tree with @ref mapping
neo click @ref [--new-tab]              # Click element
neo fill @ref "text"                    # Clear + fill input
neo type @ref "text"                    # Append text to input
neo press <key>                         # Keyboard key (Ctrl+a, Enter, etc.)
neo hover @ref                          # Hover
neo scroll <dir> [px] [--selector css]  # Scroll
neo select @ref "value"                 # Select dropdown
neo screenshot [path] [--full]          # Capture screenshot
neo get text @ref | url | title         # Extract info
neo wait @ref | --load | <ms>           # Wait for element/load/time

# --- Capture & Traffic ---
neo status                              # Overview
neo capture list [domain] [--limit N]   # Recent captures
neo capture search <query>              # Search by URL pattern
neo capture domains                     # Domains with counts
neo capture detail <id>                 # Full capture details
neo capture stats <domain>              # Statistics breakdown

# --- Schema (API Knowledge) ---
neo schema generate <domain>            # Generate from captures
neo schema show <domain>                # Human-readable
neo schema list                         # All cached schemas
neo schema search <query>               # Search endpoints
neo schema openapi <domain>             # Export OpenAPI 3.0

# --- API Execution ---
neo api <domain> <keyword> [--body '{}']  # Smart call (schema + auto-auth)
neo exec <url> [--method POST] [--body] [--tab pattern] [--auto-headers]
neo replay <id> [--tab pattern]         # Replay captured call

# --- Analysis ---
neo flows <domain>                      # API call sequence patterns
neo deps <domain>                       # Data flow dependencies
neo suggest <domain>                    # AI capability analysis

# --- Setup & Diagnostics ---
neo setup                               # First-time setup (Chrome + extension)
neo start                               # Launch Chrome with Neo extension
neo doctor                              # Health check
neo version                             # Version
```

## Decision Tree

```
User wants to interact with a website
  │
  ├─ Just read content? → neo read <domain>
  │
  ├─ Need to call an API?
  │   ├─ neo schema show <domain> → schema exists? → neo api <domain> <keyword>
  │   └─ No schema? → neo open <url> → browse → neo schema generate <domain>
  │
  ├─ Need to fill forms / click buttons?
  │   └─ neo snapshot → neo click/fill/type @ref
  │
  └─ Complex multi-step interaction?
      └─ Combine: neo open → neo snapshot → neo click/fill → neo read → close tab
```

## Key Rules

1. **Always check CDP first**: Run `neo doctor` to verify Chrome is reachable
2. **Close tabs after use**: `neo eval "window.close()" --tab <pattern>`
3. **Check schema before API calls**: `neo schema show <domain>` — use cached knowledge
4. **API > UI automation**: If an API exists, use `neo api`/`neo exec` instead of snapshot+click
5. **Per-domain capture cap**: 500 entries, auto-cleanup. Don't worry about storage.
6. **Auth is automatic**: API calls run in browser context, inheriting cookies/session/CSRF
