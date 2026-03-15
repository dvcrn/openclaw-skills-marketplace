#!/usr/bin/env python3
"""
APIClaw Natural Language Client
Main entry point for natural language queries to APIClaw API v2.
"""

import os
import sys
import argparse
import json
import re

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.apiclaw_nlu import parse_query, translate_to_api_call
from scripts.apiclaw_client import APIClawClient


def load_env_file():
    """Load environment variables from .env file (without external dependencies)."""
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_file = os.path.join(skill_dir, '.env')
    
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    
    return env_file


def save_api_key(api_key, env_file):
    """Save API key to .env file."""
    try:
        with open(env_file, 'w') as f:
            f.write("# APIClaw API Key\n")
            f.write("# Get your API key from: https://APIClaw.io\n")
            f.write(f"APICLAW_API_KEY={api_key}\n")
        os.chmod(env_file, 0o600)  # Restrict permissions
        return True
    except Exception as e:
        print(f"Error saving API key: {e}")
        return False


def check_and_setup_key(query):
    """Check if query contains API key setup request and auto-configure."""
    # Pattern: "my api key is xxx" or "api key: xxx" or "key is xxx"
    patterns = [
        r'(?:my\s+)?api\w*\s+key\s+(?:is\s+)?[:=]?\s*([a-zA-Z0-9_-]+)',
        r'(?:my\s+)?key\s+(?:is\s+)?[:=]?\s*([a-zA-Z0-9_-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            api_key = match.group(1)
            # Validate key format (should start with common prefixes)
            if len(api_key) > 10:  # Basic length check
                return api_key
    return None


def main():
    parser = argparse.ArgumentParser(
        description="APIClaw Natural Language Interface - Query Amazon product data in plain English or Chinese"
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Natural language query (e.g., 'find wireless headphones under $50')"
    )
    parser.add_argument(
        "--setup",
        metavar="API_KEY",
        help="Setup API key (one-time configuration)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the API call without executing it"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--format",
        choices=["json", "table", "compact"],
        default="compact",
        help="Output format (default: compact)"
    )
    
    args = parser.parse_args()
    
    # Load .env file
    env_file = load_env_file()
    
    # Check if query contains API key (for automatic setup)
    if args.query:
        auto_key = check_and_setup_key(args.query)
        if auto_key:
            if save_api_key(auto_key, env_file):
                # Reload env to get the new key
                load_env_file()
                print("✅ APIClaw credentials saved securely.")
                print("Ready to research Amazon products!")
                print("\nYou can now start querying. For example:")
                print('  "find wireless headphones under $50"')
                print('  "analyze market for kitchen gadgets"')
            else:
                print("❌ Failed to save API key.")
            return
    
    # Handle explicit setup mode
    if args.setup:
        if save_api_key(args.setup, env_file):
            print("✅ APIClaw credentials saved securely.")
            print("Ready to research Amazon products!")
            print("\nExample usage:")
            print('  python scripts/apiclaw_nl.py "find wireless headphones under $50"')
        else:
            print("❌ Failed to save API key.")
            sys.exit(1)
        return
    
    # Get API key from environment variable (loaded from .env file)
    api_key = os.environ.get("APICLAW_API_KEY")
    if not api_key:
        print("🔑 API Key Required")
        print("\nTo use Amazon Product Research, you need an APIClaw.io API key.")
        print("\n1. Visit https://APIClaw.io to register and get your key")
        print("2. Then provide your key to activate this skill")
        print("\nOnce you have your key, just say: \"My APIClaw key is sk-xxxxxx\"")
        sys.exit(1)
    
    client = APIClawClient(api_key)
    
    if args.interactive:
        run_interactive(client, args)
    elif args.query:
        run_single_query(client, args.query, args)
    else:
        parser.print_help()
        sys.exit(1)


def run_interactive(client, args):
    """Run in interactive mode."""
    print("🦅 APIClaw Natural Language Interface (v2)")
    print("Type your query in English or Chinese, or 'quit' to exit")
    print("Examples:")
    print("  - find wireless headphones under $50")
    print("  - show me details for ASIN B08N5WRWNW")
    print("  - analyze market for electronics")
    print("  - 查找蓝牙耳机")
    print()
    
    while True:
        try:
            query = input("> ").strip()
            if query.lower() in ["quit", "exit", "q", "退出"]:
                break
            if not query:
                continue
            
            run_single_query(client, query, args)
            print()
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            break


def run_single_query(client, query, args):
    """Run a single query."""
    # Parse natural language to intent and parameters
    intent, params = parse_query(query)
    
    # Translate to API call specification
    api_spec = translate_to_api_call(intent, params)
    
    if args.dry_run:
        print(f"Intent: {intent}")
        print(f"Parameters: {json.dumps(params, indent=2, ensure_ascii=False)}")
        print(f"API Call: {api_spec['method']} {api_spec['endpoint']}")
        print(f"Request Body: {json.dumps(api_spec['body'], indent=2, ensure_ascii=False)}")
        return
    
    # Execute API call
    try:
        result = client.execute(api_spec)
        
        if result.get("success"):
            display_results(result, api_spec["endpoint"], args.format)
        else:
            error = result.get("error", {})
            error_code = error.get("code", "")
            error_message = error.get("message", "Unknown error")
            
            # Check for quota exhausted error
            if error_code == "QUOTA_EXHAUSTED":
                print(error_message)
            else:
                print(f"Error: {error_message}")
                if error_code:
                    print(f"Code: {error_code}")
                
    except Exception as e:
        print(f"Error executing query: {e}")


def display_results(result, endpoint, format_type="compact"):
    """Display API results in the specified format."""
    data = result.get("data", [])
    meta = result.get("meta", {})
    
    if not data:
        print("No results found.")
        return
    
    if format_type == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return
    
    # Compact/table format
    if "/categories" in endpoint:
        display_categories(data, meta)
    elif "/markets/search" in endpoint:
        display_markets(data, meta)
    elif "/products/competitor-lookup" in endpoint or "/products/search" in endpoint:
        display_products(data, meta)
    elif "/realtime/product" in endpoint:
        display_realtime_product(data)
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))


def display_categories(data, meta):
    """Display category results."""
    print(f"Found {meta.get('total', len(data))} categories")
    print()
    
    for cat in data[:20]:  # Limit to 20
        path = " > ".join(cat.get("categoryPath", []))
        print(f"  {path}")
        print(f"    ID: {cat.get('categoryId', 'N/A')}")
        print(f"    Products: {cat.get('productCount', 'N/A')}")
        print(f"    Level: {cat.get('level', 'N/A')}")
        if cat.get("hasChildren"):
            print(f"    Has subcategories: Yes")
        print()


def display_markets(data, meta):
    """Display market search results."""
    total = meta.get("total", len(data))
    page = meta.get("page", 1)
    page_size = meta.get("pageSize", 20)
    
    print(f"Found {total} markets (Page {page}, showing {len(data)} results)")
    print()
    
    for market in data[:10]:  # Limit to 10 for compact display
        categories = " > ".join(market.get("categories", []))
        print(f"  📊 {categories}")
        print(f"     SKUs: {market.get('totalSkuCount', 'N/A')} total, {market.get('sampleSkuCount', 'N/A')} sampled")
        print(f"     Avg Price: ${market.get('sampleAvgPrice', 'N/A'):.2f}" if market.get('sampleAvgPrice') else "     Avg Price: N/A")
        print(f"     Monthly Sales: {market.get('sampleAvgMonthlySales', 'N/A'):.0f} units" if market.get('sampleAvgMonthlySales') else "     Monthly Sales: N/A")
        print(f"     Monthly Revenue: ${market.get('sampleAvgMonthlyRevenue', 'N/A'):,.2f}" if market.get('sampleAvgMonthlyRevenue') else "     Monthly Revenue: N/A")
        print(f"     Rating: {market.get('sampleAvgRating', 'N/A'):.1f}★" if market.get('sampleAvgRating') else "     Rating: N/A")
        print(f"     New Products: {market.get('sampleNewSkuRate', 0)*100:.1f}%" if market.get('sampleNewSkuRate') else "")
        print()


def display_products(data, meta):
    """Display product search results."""
    total = meta.get("total", len(data))
    page = meta.get("page", 1)
    
    print(f"Found {total} products (Page {page}, showing {len(data)} results)")
    print()
    
    for product in data[:10]:  # Limit to 10 for compact display
        title = product.get("title", "N/A")[:60] + "..." if len(product.get("title", "")) > 60 else product.get("title", "N/A")
        asin = product.get("asin", "N/A")
        brand = product.get("brand", "N/A")
        
        print(f"  📦 {title}")
        print(f"     ASIN: {asin} | Brand: {brand}")
        
        price = product.get("price")
        if price:
            print(f"     Price: ${price:.2f}", end="")
        
        sales = product.get("salesMonthly")
        if sales:
            print(f" | Sales: {sales}/month", end="")
        
        revenue = product.get("salesRevenue")
        if revenue:
            print(f" | Revenue: ${revenue:,.2f}", end="")
        
        rating = product.get("rating")
        if rating:
            print(f" | Rating: {rating:.1f}★", end="")
        
        review_count = product.get("reviewCount")
        if review_count:
            print(f" ({review_count} reviews)", end="")
        
        print()
        
        bsr = product.get("bsrRank")
        if bsr:
            print(f"     BSR: #{bsr} in {product.get('bsrCategory', 'N/A')}")
        
        badges = []
        if product.get("isBestSeller"):
            badges.append("🏆 Best Seller")
        if product.get("isAmazonChoice"):
            badges.append("✓ Amazon's Choice")
        if product.get("isNewRelease"):
            badges.append("🆕 New Release")
        
        if badges:
            print(f"     {' | '.join(badges)}")
        
        print()


def display_realtime_product(data):
    """Display realtime product details."""
    if isinstance(data, list) and len(data) > 0:
        product = data[0]
    else:
        product = data
    
    print(f"📦 {product.get('title', 'N/A')}")
    print(f"   ASIN: {product.get('asin', 'N/A')}")
    print(f"   Brand: {product.get('brand', 'N/A')}")
    
    rating = product.get('rating')
    rating_count = product.get('ratingCount')
    if rating and rating_count:
        print(f"   Rating: {rating:.1f}★ ({rating_count} ratings)")
    
    categories = product.get('categories', [])
    if categories:
        print(f"   Categories: {' > '.join(categories)}")
    
    features = product.get('features', [])
    if features:
        print("\n   Key Features:")
        for feature in features[:5]:
            print(f"   • {feature}")
    
    description = product.get('description', '')
    if description:
        desc = description[:200] + "..." if len(description) > 200 else description
        print(f"\n   Description: {desc}")


if __name__ == "__main__":
    main()
