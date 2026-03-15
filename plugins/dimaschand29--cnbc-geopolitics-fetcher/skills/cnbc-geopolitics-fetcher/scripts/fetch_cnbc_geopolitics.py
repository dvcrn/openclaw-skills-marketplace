#!/usr/bin/env python3
"""
CNBC Geopolitics Fetcher - Enhanced Fact Extraction
Fetches geopolitical news from CNBC and extracts real facts from article content.
"""

import argparse
import json
import re
import sys
from html import unescape
from bs4 import BeautifulSoup

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    import urllib.request
    HAS_REQUESTS = False


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--webhook', type=str)
    parser.add_argument('--count', type=int, default=5)
    parser.add_argument('--config', type=str)
    parser.add_argument('--output', type=str)
    return parser.parse_args()


def load_webhook_from_config(config_path):
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'https://discord\.com/api/webhooks/\S+', content)
            return match.group(0) if match else None
    except FileNotFoundError:
        return None


def http_get(url, headers=None):
    headers = headers or {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    if HAS_REQUESTS:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.text
    else:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode('utf-8')


def http_post_json(url, data):
    json_data = json.dumps(data).encode('utf-8')
    headers = {'Content-Type': 'application/json'}
    if HAS_REQUESTS:
        resp = requests.post(url, data=json_data, headers=headers, timeout=30)
        if resp.status_code >= 400:
            raise Exception(f"Discord error {resp.status_code}: {resp.text[:200]}")
        # Discord returns 204 No Content on success - empty body is normal
        if resp.status_code == 204:
            return {'status': 'ok'}
        try:
            return resp.json()
        except json.JSONDecodeError:
            return {'status': 'ok'}
    else:
        req = urllib.request.Request(url, data=json_data, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode('utf-8')
            if not body:
                return {'status': 'ok'}
            return json.loads(body)


def extract_articles_from_html(html):
    """Extract article URLs from CNBC HTML."""
    articles = []
    
    # Pattern: CNBC article URLs with year
    pattern = r'href="(https://www\.cnbc\.com/(\d{4})/[^"]+)"'
    matches = re.findall(pattern, html, re.IGNORECASE)
    
    for m in matches:
        url = m[0]
        # Skip non-article pages
        if any(x in url.lower() for x in ['/video/', '/premium/', '/pro/', 'tag/', 'section/', 'live']):
            continue
        
        articles.append({'url': url, 'title': 'pending', 'year': m[1]})
    
    # Dedupe
    seen = set()
    unique = []
    for a in articles:
        if a['url'] not in seen:
            seen.add(a['url'])
            unique.append(a)
    
    return unique[:25]


def fetch_article_details(url):
    """Fetch article and extract real content."""
    try:
        html = http_get(url)
        return extract_real_facts(html, url)
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return None


def extract_real_facts(html, url):
    """Extract actual facts from article content using BeautifulSoup."""
    metadata = {'url': url, 'title': '', 'market_impact': '', 'hard_facts': []}
    
    # Parse HTML with BeautifulSoup
    try:
        soup = BeautifulSoup(html, 'html.parser')
    except Exception:
        # Fallback to regex if BS4 fails
        return extract_facts_regex(html, url)
    
    # Extract title
    og_title = soup.find('meta', property='og:title')
    if og_title and og_title.get('content'):
        metadata['title'] = clean_title(unescape(og_title['content']))
    
    # Extract article body - CNBC uses specific classes
    article_body = soup.find('div', class_='ArticleBody-wrapper') or soup.find('div', class_='article-body') or soup.find('article')
    
    if not article_body:
        # Fallback: get all paragraph text
        paragraphs = soup.find_all('p')
        full_text = ' '.join(p.get_text() for p in paragraphs[:20])
    else:
        full_text = article_body.get_text(separator=' ', strip=True)
    
    # Extract description for fallback
    og_desc = soup.find('meta', property='og:description')
    description = unescape(og_desc['content']) if og_desc and og_desc.get('content') else ''
    
    # Now extract REAL facts from the text
    metadata['hard_facts'] = extract_facts_from_text(full_text, description)
    metadata['market_impact'] = extract_market_impact(full_text)
    
    if not metadata['title']:
        metadata['title'] = url.split('/')[-1].replace('-', ' ').title()
    
    return metadata


def extract_facts_from_text(text, description=''):
    """Extract 3 real hard facts from article text."""
    facts = []
    combined = (description + ' ' + text) if description else text
    
    # 1. Find quoted statements (people saying things)
    # Pattern: "quote" said/states/announced
    quote_patterns = [
        r'"([^"]{20,200})"\s*(?:said|says|stated|announced|declared|told|warned)',
        r'(?:according to|per|source says)\s+([^.\n]{20,150})',
    ]
    
    for pattern in quote_patterns:
        matches = re.findall(pattern, combined, re.IGNORECASE)
        if matches:
            facts.append(f"Official: {matches[0][:120]}")
            break
    
    # 2. Find specific actions (military, diplomatic, economic)
    action_keywords = {
        'fired': 'military action',
        'launched': 'military/diplomatic action',
        'deployed': 'military movement',
        'sanctions': 'economic action',
        'troops': 'military deployment',
        'missile': 'military action',
        'summit': 'diplomatic event',
        'talks': 'diplomatic engagement',
        'strike': 'military action',
        'attack': 'military action',
        'agreement': 'diplomatic outcome',
        'deal': 'economic/diplomatic outcome',
    }
    
    for keyword, action_type in action_keywords.items():
        pattern = rf'{keyword}[^.\n]{{20,150}}'
        match = re.search(pattern, combined, re.IGNORECASE)
        if match:
            facts.append(f"{action_type.title()}: {match.group(0)[:120]}")
            break
    
    # 3. Find numerical statistics with context
    # Look for numbers with units (million, billion, percent, etc.)
    stat_pattern = r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(million|billion|percent|%|thousand|missiles|troops|vehicles)?'
    stats = re.findall(stat_pattern, combined, re.IGNORECASE)
    
    if stats:
        # Find context around the biggest number
        for stat in stats[:3]:
            num, unit = stat
            # Get surrounding context
            context_pattern = rf'[^.\n]{{0,30}}{num}[^.\n]{{0,50}}'
            context = re.search(context_pattern, combined, re.IGNORECASE)
            if context:
                facts.append(f"Data: {context.group(0)[:120]}")
                break
    
    # 4. Find dates/deadlines
    date_pattern = r'(?:by|before|after|until|deadline)\s+([^.\n]{10,80})'
    date_match = re.search(date_pattern, combined, re.IGNORECASE)
    if date_match and len(facts) < 3:
        facts.append(f"Timeline: {date_match.group(1)[:100]}")
    
    # 5. Find location-specific info
    location_pattern = r'(?:in|at|from)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)(?:[^.\n]{0,50})'
    loc_matches = re.findall(location_pattern, combined)
    if loc_matches and len(facts) < 3:
        facts.append(f"Location: {loc_matches[0]} referenced")
    
    # Ensure we have at least 3 meaningful facts
    while len(facts) < 3:
        if description:
            # Use description as fallback but make it specific
            desc_facts = re.split(r'[.!?]', description)
            for df in desc_facts:
                if len(df) > 20:
                    facts.append(f"Context: {df[:120]}")
                    break
        else:
            # Last resort: summarize topic from URL
            url_slug = url.split('/')[-1].replace('-', ' ')
            facts.append(f"Topic: {url_slug[:100]}")
    
    return facts[:5]


def extract_facts_regex(html, url):
    """Fallback fact extraction without BeautifulSoup."""
    metadata = {'url': url, 'title': '', 'market_impact': '', 'hard_facts': []}
    
    # Title from og:title
    title_match = re.search(r'<meta[^>]*property="og:title"[^>]*content="([^"]+)"', html, re.IGNORECASE)
    if title_match:
        metadata['title'] = clean_title(unescape(title_match.group(1)))
    
    # Get text content (strip HTML tags)
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text)
    
    metadata['hard_facts'] = extract_facts_from_text(text)
    metadata['market_impact'] = extract_market_impact(text)
    
    return metadata


def extract_market_impact(text):
    """Extract market impact data from text."""
    impacts = []
    
    # Oil/Energy
    oil_match = re.search(r'(?:oil|crude|WTI|Brent)[^.\n]*(?:\$?\d+\.?\d*|barrel)', text, re.IGNORECASE)
    if oil_match:
        impacts.append(f"Energy: {oil_match.group(0)[:60]}")
    
    # Stocks
    stock_match = re.search(r'(S&P[^.\n]*|NASDAQ[^.\n]*|Dow[^.\n]*|Stoxx[^.\n]*)', text, re.IGNORECASE)
    if stock_match:
        impacts.append(f"Stocks: {stock_match.group(1)[:50]}")
    
    # Currency
    curr_match = re.search(r'(dollar[^.\n]*|EUR/USD[^.\n]*|currency[^.\n]*)', text, re.IGNORECASE)
    if curr_match:
        impacts.append(f"Currency: {curr_match.group(1)[:50]}")
    
    return '; '.join(impacts[:3]) if impacts else 'Market impact detailed in article'


def clean_title(title):
    """Remove editorial adjectives."""
    editorial = ['stunning', 'grim', 'worrisome', 'shocking', 'breaking', 'major', 'huge', 'massive', 'critical', 'urgent', 'dramatic', 'surprising']
    for word in editorial:
        title = re.sub(rf'\b{word}\b', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\s+', ' ', title).strip()
    title = re.sub(r'&x27;', "'", title)
    title = re.sub(r'&quot;', '"', title)
    title = re.sub(r'&amp;', '&', title)
    return title


def format_briefing(articles):
    """Format briefing for Discord (max 2000 chars)."""
    output = []
    total_chars = 0
    max_chars = 1900
    
    for article in articles:
        if not article.get('title'):
            continue
        
        title = article['title'][:70] + ('...' if len(article['title']) > 70 else '')
        market = article.get('market_impact', 'See article')
        if len(market) > 60:
            market = market[:57] + '...'
        
        facts = article.get('hard_facts', ['No facts extracted'])[:3]
        facts_text = ''
        for f in facts:
            f_clean = f[:110] + ('...' if len(f) > 110 else '')
            facts_text += f"  - {f_clean}\n"
        
        entry = f"""---
**{title}**
- URL: {article['url']}
- Market: {market}
- Facts:
{facts_text}---
"""
        
        if total_chars + len(entry) > max_chars:
            break
        
        output.append(entry)
        total_chars += len(entry)
    
    return '\n'.join(output) if output else 'No articles found'


def post_to_discord(webhook_url, content):
    if len(content) > 2000:
        content = content[:1995] + '...'
    
    payload = {'content': content, 'username': 'Geopolitical Intel'}
    
    try:
        http_post_json(webhook_url, payload)
        return True, 'Posted'
    except Exception as e:
        return False, str(e)[:150]


def main():
    args = parse_args()
    
    webhook_url = args.webhook or load_webhook_from_config(args.config)
    if not webhook_url:
        print('Error: No webhook URL', file=sys.stderr)
        sys.exit(1)
    
    print('Fetching CNBC geopolitical news...', file=sys.stderr)
    
    # Fetch from multiple sections
    sections = [
        'https://www.cnbc.com/world/',
        'https://www.cnbc.com/',
        'https://www.cnbc.com/finance/',
    ]
    
    all_candidates = []
    for section in sections:
        try:
            html = http_get(section)
            candidates = extract_articles_from_html(html)
            all_candidates.extend(candidates)
        except Exception as e:
            print(f'Section error: {e}', file=sys.stderr)
    
    # Filter for geopolitical topics
    geo_keywords = ['iran', 'china', 'russia', 'north korea', 'ukraine', 'israel', 
                    'middle east', 'tariff', 'sanctions', 'defense', 'military',
                    'foreign policy', 'trade', 'oil', 'energy', 'nato', 'putin', 'trump']
    
    geo_articles = []
    for c in all_candidates:
        title_lower = c.get('title', '').lower()
        url_lower = c.get('url', '').lower()
        if any(kw in title_lower or kw in url_lower for kw in geo_keywords):
            geo_articles.append(c)
    
    print(f'Found {len(geo_articles)} geopolitical articles', file=sys.stderr)
    
    # Fetch details with real fact extraction
    articles = []
    for candidate in geo_articles[:15]:
        if len(articles) >= args.count:
            break
        details = fetch_article_details(candidate['url'])
        if details and details.get('title'):
            articles.append(details)
            print(f'Extracted: {details["title"][:50]}', file=sys.stderr)
    
    briefing = format_briefing(articles)
    print('\n' + briefing, file=sys.stdout)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(briefing)
    
    success, msg = post_to_discord(webhook_url, briefing)
    print(f'Discord: {msg}', file=sys.stderr)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
