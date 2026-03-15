#!/usr/bin/env python3
"""
Stock Quote CLI - Fetch real-time stock prices and fundamentals
Usage: python quote.py SYMBOL [SYMBOL2 ...] [--json]
"""

import sys
import json
import argparse
from datetime import datetime

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


def fetch_yfinance_data(symbols):
    """Fetch data using yfinance library"""
    results = {}
    
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info
            
            # Get current price
            current_price = info.get('lastPrice') or info.get('regularMarketPrice')
            
            # Build quote data
            quote = {
                'symbol': symbol.upper(),
                'price': float(current_price) if current_price else None,
                'change': None,
                'change_percent': None,
                'previous_close': info.get('previousClose'),
                'open': info.get('open'),
                'day_high': info.get('dayHigh'),
                'day_low': info.get('dayLow'),
                'volume': info.get('volume'),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'week_52_high': info.get('fiftyTwoWeekHigh'),
                'week_52_low': info.get('fiftyTwoWeekLow'),
                'dividend_yield': info.get('dividendYield'),
                'timestamp': datetime.now().isoformat(),
                'source': 'yfinance'
            }
            
            # Calculate change
            if quote['price'] and quote['previous_close']:
                quote['change'] = round(quote['price'] - quote['previous_close'], 2)
                quote['change_percent'] = round(
                    (quote['change'] / quote['previous_close']) * 100, 2
                )
            
            results[symbol.upper()] = quote
            
        except Exception as e:
            results[symbol.upper()] = {
                'symbol': symbol.upper(),
                'error': str(e),
                'source': 'yfinance'
            }
    
    return results


def fetch_web_data(symbols):
    """Fallback: fetch data from Yahoo Finance web pages"""
    results = {}
    
    for symbol in symbols:
        try:
            url = f"https://finance.yahoo.com/quote/{symbol}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                results[symbol.upper()] = {
                    'symbol': symbol.upper(),
                    'error': f'HTTP {response.status_code}',
                    'source': 'web'
                }
                continue
            
            # Simple parsing - in production, use proper HTML parser
            html = response.text
            
            # Extract price (simplified regex approach)
            import re
            price_match = re.search(r'"regularMarketPrice":\s*{"raw":\s*([\d.]+)', html)
            price = float(price_match.group(1)) if price_match else None
            
            results[symbol.upper()] = {
                'symbol': symbol.upper(),
                'price': price,
                'timestamp': datetime.now().isoformat(),
                'source': 'web'
            }
            
        except Exception as e:
            results[symbol.upper()] = {
                'symbol': symbol.upper(),
                'error': str(e),
                'source': 'web'
            }
    
    return results


def format_text_output(quotes):
    """Format quotes as human-readable text"""
    lines = []
    
    for symbol, data in quotes.items():
        if 'error' in data and len(data) == 2:
            lines.append(f"❌ {symbol}: {data['error']}")
            continue
        
        price = data.get('price', 'N/A')
        change = data.get('change')
        change_pct = data.get('change_percent')
        
        if price != 'N/A':
            price_str = f"${price:.2f}"
        else:
            price_str = "N/A"
        
        # Direction indicator
        if change is not None:
            if change > 0:
                direction = "📈"
                change_str = f"+{change:.2f} (+{change_pct:.2f}%)"
            elif change < 0:
                direction = "📉"
                change_str = f"{change:.2f} ({change_pct:.2f}%)"
            else:
                direction = "➡️"
                change_str = "0.00 (0.00%)"
        else:
            direction = "⏸️"
            change_str = "N/A"
        
        lines.append(f"{direction} {symbol}: {price_str} {change_str}")
        
        # Additional info
        if data.get('market_cap'):
            market_cap = data['market_cap']
            if market_cap >= 1e12:
                mc_str = f"${market_cap/1e12:.2f}T"
            elif market_cap >= 1e9:
                mc_str = f"${market_cap/1e9:.2f}B"
            else:
                mc_str = f"${market_cap/1e6:.2f}M"
            lines.append(f"   市值：{mc_str}")
        
        if data.get('pe_ratio'):
            lines.append(f"   PE: {data['pe_ratio']:.2f}")
        
        if data.get('week_52_high') and data.get('week_52_low'):
            high = data['week_52_high']
            low = data['week_52_low']
            if price != 'N/A':
                pct_in_range = ((price - low) / (high - low)) * 100 if high != low else 50
                lines.append(f"   52 周：${low:.2f} - ${high:.2f} (当前位置：{pct_in_range:.1f}%)")
        
        lines.append("")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='Fetch stock quotes')
    parser.add_argument('symbols', nargs='+', help='Stock symbols (e.g., AAPL NVDA TSLA)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--source', choices=['yfinance', 'web', 'auto'], default='auto',
                       help='Data source (default: auto)')
    
    args = parser.parse_args()
    
    # Determine source
    source = args.source
    if source == 'auto':
        source = 'yfinance' if YFINANCE_AVAILABLE else 'web'
    
    # Fetch data
    if source == 'yfinance':
        if not YFINANCE_AVAILABLE:
            print("Error: yfinance not installed. Run: pip install yfinance", file=sys.stderr)
            sys.exit(1)
        quotes = fetch_yfinance_data(args.symbols)
    else:
        if not REQUESTS_AVAILABLE:
            print("Error: requests not installed. Run: pip install requests", file=sys.stderr)
            sys.exit(1)
        quotes = fetch_web_data(args.symbols)
    
    # Output
    if args.json:
        print(json.dumps(quotes, indent=2))
    else:
        print(format_text_output(quotes))


if __name__ == '__main__':
    main()
