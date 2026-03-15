#!/usr/bin/env python3
"""
ClawSavings Deal Refresh Script

Refreshes the deal layer in discounts.json by scraping current voucher prices.

Usage:
    python refresh_deals.py --source poalim_wonder
    python refresh_deals.py --source htzone_pro2
    python refresh_deals.py --source htzone_club --category supermarkets
    python refresh_deals.py --all
    python refresh_deals.py --status

Requirements:
    pip install playwright
    playwright install chromium

HTZone Club login (optional — needed only for htzone_club):
    export HTZONE_EMAIL=your@email.com
    export HTZONE_PASSWORD=yourpassword

Sources without login:
    - poalim_wonder   : public JS page, no login needed
    - htzone_pro2     : public webview pages, no login needed
"""

import argparse
import json
import os
import re
import sys
from datetime import date, datetime
from pathlib import Path

KB_PATH = Path(__file__).parent.parent / "discounts.json"
TODAY = date.today().isoformat()


# ─── KB helpers ──────────────────────────────────────────────────────────────

def load_kb():
    with open(KB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_kb(kb):
    with open(KB_PATH, "w", encoding="utf-8") as f:
        json.dump(kb, f, ensure_ascii=False, indent=2)
    print(f"✅ KB saved → {KB_PATH}")


def mark_source(kb, category, source_id, deals, updated_count):
    """Update a source's deals + cached_at in the KB."""
    src = kb["categories"][category]["sources"].get(source_id)
    if src is None:
        print(f"   ⚠️  {category}/{source_id} not found in KB — skipping")
        return
    src["deals"] = deals
    src["cached_at"] = TODAY
    print(f"   ✅ {category}/{source_id}: {updated_count} deals updated")


# ─── Playwright bootstrap ────────────────────────────────────────────────────

def get_browser(p, headless=True):
    """Launch Chromium. Falls back to headed mode if headless fails."""
    try:
        return p.chromium.launch(headless=headless)
    except Exception as e:
        print(f"   ⚠️  Headless launch failed ({e}), trying headed mode...")
        return p.chromium.launch(headless=False)


def scroll_to_bottom(page, pause_ms=800, max_scrolls=30):
    """Scroll page to bottom to trigger lazy-loaded content."""
    prev_height = 0
    for _ in range(max_scrolls):
        try:
            page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight || document.body.scrollHeight)")
            page.wait_for_timeout(pause_ms)
            new_height = page.evaluate("document.documentElement.scrollHeight || document.body.scrollHeight")
            if new_height == prev_height:
                break
            prev_height = new_height
        except Exception:
            break


def parse_shekel(text):
    """Extract integer shekel amount from text like '₪259' or '259.00₪'."""
    if not text:
        return None
    m = re.search(r'(\d+(?:\.\d+)?)', text.replace(",", ""))
    return int(float(m.group(1))) if m else None


def parse_points(text):
    """Extract integer points from text like '+ 50 נקודות'."""
    if not text:
        return 0
    m = re.search(r'(\d+)\s*נקודות', text)
    return int(m.group(1)) if m else 0


# ─── Poalim Wonder scraper ───────────────────────────────────────────────────

WONDER_PAGES = {
    "Shopping": "https://www.bankhapoalim.co.il/he/Poalim-Wonder/Shopping",
    "Fun":      "https://www.bankhapoalim.co.il/he/Poalim-Wonder/Fun",
}

# Maps Hebrew store name patterns → (category, source_key)
WONDER_STORE_MAP = {
    "שוק העיר":      ("supermarkets",       "poalim_wonder"),
    "ויקטורי":       ("supermarkets",       "poalim_wonder"),
    "קרפור":         ("supermarkets",       "poalim_wonder"),
    "רמי לוי":       ("supermarkets",       "poalim_wonder"),
    "נוי השדה":      ("supermarkets",       "poalim_wonder"),
    "קשת טעמים":     ("supermarkets",       "poalim_wonder"),
    "וולט":          ("delivery",           "poalim_wonder"),
    "קסטרו":         ("fashion",            "poalim_wonder"),
    "SOHO":          ("fashion",            "poalim_wonder"),
    "כיתן":          ("fashion",            "poalim_wonder"),
    "גולף קידס":     ("fashion",            "poalim_wonder"),
    "אינטימה":       ("fashion",            "poalim_wonder"),
    "ורדינון":       ("fashion",            "poalim_wonder"),
    "סלטם":          ("home_kitchen",       "poalim_wonder"),
    "מגה ספורט":     ("gym_sports",         "poalim_wonder"),
    "MEGA SPORT":    ("gym_sports",         "poalim_wonder"),
    "סנו":           ("household_products", "poalim_wonder"),
    "SOLTAM":        ("home_kitchen",       "poalim_wonder"),
    "סולטם":         ("home_kitchen",       "poalim_wonder"),
    "KITAN":         ("fashion",            "poalim_wonder"),
    "כיתן":          ("fashion",            "poalim_wonder"),
    "GOLF KIDS":     ("fashion",            "poalim_wonder"),
    "INTIMA":        ("fashion",            "poalim_wonder"),
    "GiftZone":      ("gifts_gift_cards",   "poalim_wonder"),
    "LOVE GIFT CARD":("gifts_gift_cards",   "poalim_wonder"),
    "DREAM CARD":    ("gifts_gift_cards",   "poalim_wonder"),
    "Gifta":         ("gifts_gift_cards",   "poalim_wonder"),
    "מקדונלד":       ("restaurants",        "poalim_wonder"),
    "פלאנט":         ("entertainment",      "poalim_wonder"),
    # Fun page additions
    "מיי בייבי":     ("kids_baby",          "poalim_wonder"),
    "קיפצובה":       ("entertainment",      "poalim_wonder"),
    "מיני ישראל":    ("entertainment",      "poalim_wonder"),
    "ספארי":         ("entertainment",      "poalim_wonder"),
    "ספארק":         ("entertainment",      "poalim_wonder"),
    "סקיי ג'אמפ":    ("entertainment",      "poalim_wonder"),
    "GRAVITY PARK":  ("entertainment",      "poalim_wonder"),
    "אייסמול":       ("entertainment",      "poalim_wonder"),
}


def scrape_wonder_page(page, url, page_name):
    """Scrape all deal cards from a Poalim Wonder sub-page."""
    print(f"   🌐 Loading Wonder/{page_name}...")
    page.goto(url, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(3000)  # Drupal JS hydration
    scroll_to_bottom(page)

    deals_raw = []

    # Strategy 1: find deal card containers
    # Wonder renders cards with store name + price text
    # Try multiple selector patterns — adjust if site HTML changes
    card_selectors = [
        "[class*='product-card']",
        "[class*='benefit-card']",
        "[class*='deal-card']",
        "[class*='wonder-item']",
        "[class*='voucher']",
        "article",
        ".card",
    ]

    # Verified selector (2026-03-07): Poalim Wonder uses Drupal "team-member" template
    # Primary: div.team-member.with-img (each card = one deal)
    # Fallback: generic selectors, then full-text parse
    WONDER_CARD_SELECTORS = [
        "div.team-member.with-img",   # verified ✅
        "div.team-member",
    ] + card_selectors

    cards = []
    for sel in WONDER_CARD_SELECTORS:
        found = page.query_selector_all(sel)
        if len(found) > 3:
            print(f"   📦 Found {len(found)} cards with selector: {sel}")
            cards = found
            break

    if not cards:
        # Fallback: scrape full text and parse line by line
        print("   ⚠️  No card selector matched — falling back to text scrape")
        return _parse_wonder_text(page.inner_text("body"))

    for card in cards:
        # Try to extract store name and subtitle separately for cleaner parsing
        subtitle_el = card.query_selector("div.team-member-subtitle, .team-member-subtitle")
        if subtitle_el:
            # Get store name = full card text minus the subtitle
            full_text = card.inner_text().strip()
            subtitle_text = subtitle_el.inner_text().strip()
            store_name = full_text.replace(subtitle_text, "").strip().splitlines()[0].strip()
            deal = _parse_wonder_card_text(f"{store_name}\n{subtitle_text}")
        else:
            deal = _parse_wonder_card_text(card.inner_text())
        if deal:
            deals_raw.append(deal)

    print(f"   📊 Scraped {len(deals_raw)} raw deals from {page_name}")
    return deals_raw


def _parse_wonder_card_text(text):
    """
    Parse a Wonder deal card's text block.
    Examples:
        'שוק העיר\nשובר בשווי 300₪\nתמורת 255.00₪ + 50 נקודות'
        'מגה ספורט\nשובר בשווי 250₪\nתמורת 199.00₪ + 25 נקודות'
        'מיי בייבי ירכא...\nכרטיס נטען על סך 150 ₪\nתמורת 75.00 ₪ + 15 נקודות'
    """
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    if len(lines) < 2:
        return None

    store = lines[0]

    # Find face value: "שווי X ₪" or "X ₪"
    face_value = None
    price = None
    points = 0
    description = None

    for line in lines[1:]:
        # Price line: "תמורת Y₪ + Z נקודות" or "Y ₪"
        if "תמורת" in line or re.match(r"^\d", line):
            price = parse_shekel(line)
            points = parse_points(line)
        # Face value line: "שווי X" or "בשווי X" or "X ₪"
        elif "שווי" in line or "בשווי" in line:
            face_value = parse_shekel(line)
            if not description:
                description = line
        elif not description and len(line) > 5:
            description = line

    if price is None:
        return None

    effective_pct = round((1 - price / face_value) * 100, 1) if face_value and face_value > 0 else None

    return {
        "store": store,
        "description": description,
        "face_value": face_value,
        "price": price,
        "extra_points": points,
        "effective_pct": effective_pct,
    }


def _parse_wonder_text(full_text):
    """Fallback: parse Wonder page full text, looking for price patterns."""
    deals = []
    lines = [l.strip() for l in full_text.splitlines() if l.strip()]

    i = 0
    while i < len(lines):
        line = lines[i]
        # A store name precedes a "שווי X" or "תמורת Y" line
        if i + 1 < len(lines):
            next_line = lines[i + 1]
            if ("שווי" in next_line or "תמורת" in next_line) and len(line) > 2:
                # Collect up to 3 more lines for context
                block = "\n".join(lines[i:i+4])
                deal = _parse_wonder_card_text(block)
                if deal and deal.get("price"):
                    deals.append(deal)
                    i += 3
                    continue
        i += 1
    return deals


def _group_wonder_deals(deals_raw):
    """
    Group scraped deals by (category, source) for KB update.
    Returns: {(category, source): [deal, ...]}
    """
    grouped = {}
    unmatched = []

    for deal in deals_raw:
        store = deal.get("store", "")
        matched = None
        for pattern, (cat, src) in WONDER_STORE_MAP.items():
            if pattern in store:
                matched = (cat, src)
                break
        if matched:
            grouped.setdefault(matched, []).append(deal)
        else:
            unmatched.append(store)

    if unmatched:
        print(f"   ℹ️  Unmatched stores (not in KB map): {unmatched}")

    return grouped


def refresh_poalim_wonder(kb, category=None):
    """Scrape all public Poalim Wonder pages (no login required)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ playwright not installed. Run: pip install playwright && playwright install chromium")
        return False

    print("🔄 Refreshing Poalim Wonder (public pages, no login)...")

    all_deals_raw = []
    with sync_playwright() as p:
        browser = get_browser(p)
        ctx = browser.new_context(
            locale="he-IL",
            extra_http_headers={"Accept-Language": "he-IL,he;q=0.9,en;q=0.8"}
        )
        page = ctx.new_page()

        pages_to_scrape = {"Shopping": WONDER_PAGES["Shopping"], "Fun": WONDER_PAGES["Fun"]}
        if category:
            # If category specified, only scrape Shopping (Fun is leisure only)
            pages_to_scrape = {"Shopping": WONDER_PAGES["Shopping"]}

        for page_name, url in pages_to_scrape.items():
            try:
                raw = scrape_wonder_page(page, url, page_name)
                all_deals_raw.extend(raw)
            except Exception as e:
                print(f"   ⚠️  Failed to scrape Wonder/{page_name}: {e}")

        browser.close()

    if not all_deals_raw:
        print("   ❌ No deals scraped — selectors may need updating")
        return False

    grouped = _group_wonder_deals(all_deals_raw)
    updated = 0

    for (cat, src), deals in grouped.items():
        if category and cat != category:
            continue
        mark_source(kb, cat, src, deals, len(deals))
        updated += len(deals)

    save_kb(kb)
    print(f"\n✅ Poalim Wonder: {updated} deals across {len(grouped)} categories updated")
    return True


# ─── HTZone PRO² webview scraper ─────────────────────────────────────────────

def scrape_htzone_webview_page(page, url, store_name):
    """
    Scrape an HTZone webview page for all price tiers.

    Verified page formats (live, 2026-03-07):
      Format A (3-tier): "300 ₪ מחיר רגיל  279 ₪ חבר htz  259 ₪ מחיר PRO²"
        → face_value=300, club_price=279 (7%), pro2_price=259 (13.7%)
      Format B (PRO²-only): "מחיר רגיל 200 ₪ / חבר htz 200 ₪ / כ.א PRO: 180 ₪"
        → face_value=200, club_price=200 (no club discount), pro2_price=180 (10%)

    Returns dict with all three price tiers + effective discount %.
    """
    print(f"   🌐 Loading HTZone webview for {store_name}...")
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=15000)
        page.wait_for_timeout(2000)
    except Exception as e:
        print(f"   ⚠️  Timeout/error for {store_name}: {e}")
        return None

    text = page.inner_text("body")

    face_value = None
    club_price = None
    pro2_price = None

    # ── Format A: inline summary line ────────────────────────────────────────
    # "300 ₪ מחיר רגיל 279 ₪ חבר htz 259 ₪ מחיר PRO²"
    m = re.search(
        r'(\d+)\s*₪\s*מחיר רגיל\s+(\d+)\s*₪\s*חבר htz\s+(\d+)\s*₪\s*מחיר PRO',
        text
    )
    if m:
        face_value  = int(m.group(1))
        club_price  = int(m.group(2))
        pro2_price  = int(m.group(3))

    # ── Format B: table rows / כ.א PRO: ─────────────────────────────────────
    if not face_value:
        # Face value from "מחיר רגיל\n\nX ₪" or "בשווי X ₪"
        for pat in [r'מחיר רגיל\s+(\d+)', r'בשווי\s+(\d+)\s*₪', r'בשווי (\d+)']:
            m = re.search(pat, text)
            if m:
                face_value = int(m.group(1))
                break

        # Club price from "חבר htz\n\nX ₪"
        m = re.search(r'חבר htz\s+(\d+)', text, re.IGNORECASE)
        if m:
            club_price = int(m.group(1))

        # PRO² price
        for pat in [
            r'כ\.א\s+PRO[²2]?\s*:\s*(\d+)',
            r'(\d+)\s*₪\s*\n?\s*מחיר PRO',
            r'מחיר PRO[²2]?\s+(\d+)',
        ]:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                pro2_price = int(m.group(1))
                break

    if not face_value:
        print(f"   ⚠️  Could not extract any prices for {store_name}")
        return None

    # If club_price == face_value → no club member discount
    has_club_discount = club_price is not None and club_price < face_value
    club_eff_pct = round((1 - club_price / face_value) * 100, 1) if has_club_discount else None
    pro2_eff_pct = round((1 - pro2_price / face_value) * 100, 1) if pro2_price else None

    tiers = []
    if has_club_discount:
        tiers.append(f"club ₪{club_price} ({club_eff_pct}%)")
    if pro2_price:
        tiers.append(f"PRO² ₪{pro2_price} ({pro2_eff_pct}%)")
    print(f"   ✅ {store_name}: ₪{face_value} → {' / '.join(tiers) or 'no discount found'}")

    return {
        "face_value":      face_value,
        "club_price":      club_price if has_club_discount else None,
        "club_eff_pct":    club_eff_pct,
        "pro2_price":      pro2_price,
        "pro2_eff_pct":    pro2_eff_pct,
    }


# Keep old name as alias for backward compat
scrape_htzone_pro2_page = scrape_htzone_webview_page


def refresh_htzone_pro2(kb, category=None):
    """
    Refresh HTZone webview deals (public, no login).
    Scrapes all three price tiers per store:
      - htzone_pro2  → PRO² member price
      - htzone_club  → regular HTZ club member price (if discounted vs face value)
    Only refreshes deals with cached_at=null or price=null.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ playwright not installed. Run: pip install playwright && playwright install chromium")
        return False

    print("🔄 Refreshing HTZone webview deals (public, no login)...")
    print("   ℹ️  Captures all 3 tiers: face value / club member price / PRO² price")

    # Collect all stale PRO² deals with a webview_url
    to_refresh = []  # [(cat_id, deal_obj)]
    for cat_id, cat_data in kb["categories"].items():
        if category and cat_id != category:
            continue
        src = cat_data.get("sources", {}).get("htzone_pro2")
        if not src:
            continue
        for deal in src.get("deals", []):
            if deal.get("webview_url") and (
                deal.get("cached_at") is None or deal.get("price") is None
            ):
                to_refresh.append((cat_id, deal))

    if not to_refresh:
        print("   ✅ All HTZone webview deals are fresh — nothing to do")
        return True

    print(f"   📋 {len(to_refresh)} deals need refresh")
    updated_pro2 = 0
    updated_club = 0

    with sync_playwright() as p:
        browser = get_browser(p)
        ctx = browser.new_context(locale="he-IL")
        page = ctx.new_page()

        for cat_id, deal in to_refresh:
            result = scrape_htzone_webview_page(page, deal["webview_url"], deal["store"])
            if not result:
                continue

            # ── Update htzone_pro2 deal ───────────────────────────────────
            deal["face_value"]   = result["face_value"]
            deal["price"]        = result["pro2_price"]
            deal["effective_pct"]= result["pro2_eff_pct"]
            deal["cached_at"]    = TODAY
            updated_pro2 += 1

            # ── Also update htzone_club if store has a club discount ──────
            if result["club_price"] is not None:
                club_src = kb["categories"][cat_id]["sources"].get("htzone_club")
                if club_src is not None:
                    # Find or create the deal entry in htzone_club
                    club_deals = club_src.setdefault("deals", [])
                    existing = next((d for d in club_deals if d.get("store") == deal["store"]), None)
                    club_deal = {
                        "store":         deal["store"],
                        "face_value":    result["face_value"],
                        "price":         result["club_price"],
                        "effective_pct": result["club_eff_pct"],
                        "cached_at":     TODAY,
                        "notes":         "scraped from HTZone webview",
                    }
                    if existing:
                        existing.update(club_deal)
                    else:
                        club_deals.append(club_deal)
                    updated_club += 1

        browser.close()

    # Update source-level cached_at for htzone_pro2
    for cat_id, cat_data in kb["categories"].items():
        src = cat_data.get("sources", {}).get("htzone_pro2")
        if src:
            deal_dates = [d.get("cached_at") for d in src.get("deals", []) if d.get("cached_at")]
            if deal_dates:
                src["cached_at"] = max(deal_dates)

    save_kb(kb)
    print(f"\n✅ HTZone webview: {updated_pro2} PRO² deals + {updated_club} club deals refreshed")
    return updated_pro2 > 0


# ─── HTZone Club scraper (requires login) ────────────────────────────────────

HTZONE_CLUB_CATEGORY_URLS = {
    "supermarkets":       "https://www.htzone.co.il/sale/1147",
    "restaurants":        "https://www.htzone.co.il/sale/1148",
    "entertainment":      "https://www.htzone.co.il/sale/1149",
    "fashion":            "https://www.htzone.co.il/sale/1150",
    "pharma":             "https://www.htzone.co.il/sale/1152",
    "electronics":        "https://www.htzone.co.il/sale/1153",
    "home_kitchen":       "https://www.htzone.co.il/sale/1154",
    "gym_sports":         "https://www.htzone.co.il/sale/1155",
    "kids_baby":          "https://www.htzone.co.il/sale/1156",
    "office_stationery":  "https://www.htzone.co.il/sale/1147",
}


def htzone_login(page):
    """Login to HTZone. Credentials from env vars."""
    email = os.environ.get("HTZONE_EMAIL")
    password = os.environ.get("HTZONE_PASSWORD")

    if not email or not password:
        raise EnvironmentError(
            "Set HTZONE_EMAIL and HTZONE_PASSWORD env vars to scrape HTZone Club deals"
        )

    print("   🔐 Logging in to HTZone...")
    page.goto("https://www.htzone.co.il/login", wait_until="networkidle")

    # Fill login form — selectors may need adjustment if site changes
    page.fill("input[type='email'], input[name='email'], #email", email)
    page.fill("input[type='password'], input[name='password'], #password", password)
    page.click("button[type='submit'], .login-btn, #login-submit")
    page.wait_for_load_state("networkidle")

    # Verify login succeeded
    if "login" in page.url.lower() or page.query_selector(".login-error"):
        raise RuntimeError("HTZone login failed — check credentials")

    print("   ✅ Logged in")


def scrape_htzone_club_page(page, url, cat_id):
    """
    Scrape HTZone Club voucher page for a category.
    Returns list of deal dicts.
    """
    page.goto(url, wait_until="networkidle", timeout=30000)
    scroll_to_bottom(page)

    deals = []
    # Try common product card selectors
    for sel in ["[class*='product-item']", "[class*='product-card']", ".item", "article"]:
        cards = page.query_selector_all(sel)
        if len(cards) > 2:
            break

    for card in cards:
        text = card.inner_text()
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        if len(lines) < 2:
            continue

        store = lines[0]
        # Look for "שובר בשווי X ₪" and price
        face_value = None
        price = None
        for line in lines[1:]:
            if "שווי" in line or "בשווי" in line:
                face_value = parse_shekel(line)
            if re.match(r'^\d', line) and "₪" in line:
                price = parse_shekel(line)

        if store and price:
            effective_pct = round((1 - price / face_value) * 100, 1) if face_value else None
            deals.append({
                "store": store,
                "face_value": face_value,
                "price": price,
                "effective_pct": effective_pct,
            })

    print(f"   📦 {cat_id}: scraped {len(deals)} deals")
    return deals


def refresh_htzone_club(kb, category=None):
    """
    Refresh HTZone Club voucher deals (requires login).
    Set HTZONE_EMAIL + HTZONE_PASSWORD env vars before running.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ playwright not installed. Run: pip install playwright && playwright install chromium")
        return False

    email = os.environ.get("HTZONE_EMAIL")
    if not email:
        print("❌ HTZone Club requires login. Set HTZONE_EMAIL + HTZONE_PASSWORD env vars.")
        print("   Skipping htzone_club refresh.")
        return False

    print("🔄 Refreshing HTZone Club deals (requires login)...")

    cats_to_scrape = (
        {category: HTZONE_CLUB_CATEGORY_URLS[category]}
        if category and category in HTZONE_CLUB_CATEGORY_URLS
        else HTZONE_CLUB_CATEGORY_URLS
    )

    updated_cats = 0
    with sync_playwright() as p:
        browser = get_browser(p, headless=False)  # headed — easier for login
        ctx = browser.new_context(locale="he-IL")
        page = ctx.new_page()

        try:
            htzone_login(page)
        except Exception as e:
            print(f"   ❌ Login failed: {e}")
            browser.close()
            return False

        for cat_id, url in cats_to_scrape.items():
            if cat_id not in kb["categories"]:
                continue
            if "htzone_club" not in kb["categories"][cat_id]["sources"]:
                continue
            try:
                deals = scrape_htzone_club_page(page, url, cat_id)
                if deals:
                    mark_source(kb, cat_id, "htzone_club", deals, len(deals))
                    updated_cats += 1
            except Exception as e:
                print(f"   ⚠️  Failed to scrape {cat_id}: {e}")

        browser.close()

    save_kb(kb)
    print(f"\n✅ HTZone Club: {updated_cats} categories updated")
    return updated_cats > 0


# ─── Cache status ────────────────────────────────────────────────────────────

def check_staleness(kb):
    print("📊 Cache Status Report")
    print("=" * 50)

    today = date.today()
    ttl_days = kb.get("meta", {}).get("cache_ttl_days", 30)
    stale, fresh, never = [], [], []

    for cat_id, cat_data in kb.get("categories", {}).items():
        for src_id, src_data in cat_data.get("sources", {}).items():
            if "cached_at" not in src_data:
                continue
            cached_at = src_data.get("cached_at")
            if cached_at is None:
                never.append((cat_id, src_id))
            else:
                try:
                    age = (today - datetime.strptime(cached_at, "%Y-%m-%d").date()).days
                    (stale if age > ttl_days else fresh).append((cat_id, src_id, age))
                except ValueError:
                    stale.append((cat_id, src_id, f"bad date: {cached_at}"))

    if never:
        print(f"\n🔴 NEVER CACHED ({len(never)}):")
        for cat, src in sorted(never):
            print(f"   {cat}/{src}")
    if stale:
        print(f"\n🟡 STALE ({len(stale)}):")
        for cat, src, age in sorted(stale):
            print(f"   {cat}/{src}: {age} days")
    if fresh:
        print(f"\n🟢 FRESH ({len(fresh)}):")
        for cat, src, age in sorted(fresh):
            print(f"   {cat}/{src}: {age}d")

    return len(never) + len(stale)


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Refresh ClawSavings deal data",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--source",
        choices=["poalim_wonder", "htzone_pro2", "htzone_club", "all"],
        help=(
            "poalim_wonder  — public, no login needed\n"
            "htzone_pro2    — public webview pages, no login needed\n"
            "htzone_club    — requires HTZONE_EMAIL + HTZONE_PASSWORD\n"
            "all            — run all three"
        ),
    )
    parser.add_argument("--category", help="Limit to a specific category (e.g. supermarkets)")
    parser.add_argument("--status", action="store_true", help="Show cache staleness report")
    parser.add_argument("--headed", action="store_true", help="Run browser in headed (visible) mode")

    args = parser.parse_args()

    if not KB_PATH.exists():
        print(f"❌ KB not found at {KB_PATH}")
        sys.exit(1)

    kb = load_kb()

    if args.status or not args.source:
        stale_count = check_staleness(kb)
        if args.status:
            sys.exit(0 if stale_count == 0 else 1)
        print("\nRun with --source <source> to refresh. Run with --source all to refresh everything.")
        return

    refreshers = {
        "poalim_wonder": refresh_poalim_wonder,
        "htzone_pro2":   refresh_htzone_pro2,
        "htzone_club":   refresh_htzone_club,
    }

    if args.source == "all":
        for name, fn in refreshers.items():
            print(f"\n{'─'*50}")
            fn(kb, args.category)
    else:
        refreshers[args.source](kb, args.category)


if __name__ == "__main__":
    main()
