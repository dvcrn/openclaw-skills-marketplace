---
name: innotech-polymarket-api
description: "Polymarket API and data access guide. Learn how to connect, find markets, get real-time data via WebSocket, access order books, and build prediction market applications."
---

# Polymarket API & Data Access Guide

**Purpose**: General reference for connecting to and using Polymarket APIs  
**Last Updated**: 2026-03-05

---

## 🎯 What This Skill Covers

This skill teaches you **how to**:

1. ✅ **Connect to Polymarket** - API endpoints, authentication
2. ✅ **Find Markets** - Search, filter, find specific market types
3. ✅ **Get Real-time Data** - WebSocket and Socket.IO usage
4. ✅ **Access Order Books** - Liquidity, bid/ask spreads, depth
5. ✅ **Polling Methods** - When real-time isn't available
6. ✅ **Advanced Market Discovery** - Timestamp-based patterns, recurring markets

**This skill does NOT include**:
- ❌ Specific trading strategies
- ❌ Arbitrage logic
- ❌ Automated trading bots

Use this knowledge to build your own applications!

---

## 📋 Quick Start

### **Step 1: Understanding Polymarket Architecture**

Polymarket has multiple components:

1. **Gamma API** (`https://gamma-api.polymarket.com`)
   - Market information
   - Prices and odds
   - Market metadata
   - **Most reliable for market discovery**

2. **CLOB API** (`https://clob.polymarket.com`)
   - Order books
   - Trade data
   - Market structure

3. **Data API** (`https://data-api.polymarket.com`)
   - User data (requires auth)
   - Historical data

4. **WebSocket** (`wss://ws-subscriptions-clob.polymarket.com`)
   - Real-time price updates
   - Live order book changes
   - Trade notifications
   - **Best for monitoring multiple markets**

### **Step 2: Basic API Call**

```python
import requests

# Get all active markets
response = requests.get("https://gamma-api.polymarket.com/markets")
markets = response.json()

# Find a specific market by slug
response = requests.get(
    "https://gamma-api.polymarket.com/markets",
    params={"slug": "bitcoin-100k-2024"}
)
market = response.json()
```

### **Step 3: Get Real-time Data**

```python
import aiohttp
import asyncio
import json

async def monitor_market():
    async with aiohttp.ClientSession() as session:
        ws = await session.ws_connect(
            "wss://ws-subscriptions-clob.polymarket.com/ws/market"
        )
        
        # Subscribe to market
        await ws.send_json({
            "assets_ids": ["asset_id_1", "asset_id_2"],
            "type": "market",
            "custom_feature_enabled": True
        })
        
        # Listen for updates
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                data = json.loads(msg.data)
                print(f"Update: {data}")

asyncio.run(monitor_market())
```

---

## 🔍 Finding Markets

### **Method 1: Browse All Markets**

```python
import requests

def get_all_active_markets(limit=100, offset=0):
    """Get all active markets"""
    response = requests.get(
        "https://gamma-api.polymarket.com/markets",
        params={
            "active": "true",
            "closed": "false",
            "limit": limit,
            "offset": offset
        }
    )
    return response.json()

# Use
markets = get_all_active_markets(limit=100)
for market in markets:
    print(f"{market['question']}: {market.get('outcomePrices', [])}")
```

### **Method 2: Search by Keyword**

```python
def search_markets(keyword):
    """Search markets by keyword"""
    response = requests.get(
        "https://gamma-api.polymarket.com/markets",
        params={"_s": keyword}
    )
    return response.json()

# Use
bitcoin_markets = search_markets("bitcoin")
```

### **Method 3: Find by Slug Pattern**

```python
def find_market_by_slug(slug):
    """Find market by exact slug"""
    response = requests.get(
        "https://gamma-api.polymarket.com/markets",
        params={"slug": slug}
    )
    markets = response.json()
    return markets[0] if markets else None

# Use
market = find_market_by_slug("bitcoin-100k-2024")
```

---

## 🕐 Advanced: Finding Time-Based Markets

### **Pattern: Recurring Markets**

Some markets follow predictable patterns based on timestamps. For example, Polymarket's **Bitcoin 5-Minute Up/Down** markets follow this pattern:

```
Market Slug: btc-updown-5m-{timestamp}
```

Where `timestamp` is a Unix timestamp rounded to 5-minute intervals (300 seconds).

### **Example: Find 5-Minute Bitcoin Markets**

```python
import time
from datetime import datetime, timezone

def get_current_interval(interval_seconds=300):
    """
    Calculate current 5-minute interval timestamp
    
    Example:
        Current time: 10:43:25 (Unix: 1772591580)
        Interval start: 10:40:00 (Unix: 1772591100)
        Calculation: floor(1772591580 / 300) * 300 = 1772591100
    """
    current_time = int(time.time())
    interval_start = (current_time // interval_seconds) * interval_seconds
    return interval_start

def generate_market_timestamps(num_markets=8):
    """
    Generate N market timestamps: current + next (N-1) intervals
    
    Returns:
        List of Unix timestamps, each 5 minutes apart
    """
    base = get_current_interval()
    return [base + i * 300 for i in range(num_markets)]

def find_5min_bitcoin_markets(num_markets=8):
    """
    Find Bitcoin 5-minute up/down markets
    
    Returns:
        List of market data dicts
    """
    timestamps = generate_market_timestamps(num_markets)
    markets = []
    
    for ts in timestamps:
        slug = f"btc-updown-5m-{ts}"
        
        response = requests.get(
            "https://gamma-api.polymarket.com/markets",
            params={"slug": slug}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data:
                market = data[0]
                
                # Check if active and not closed
                if market.get('active') and not market.get('closed'):
                    markets.append(market)
                    print(f"✅ Found: {slug}")
    
    return markets

# Use
markets = find_5min_bitcoin_markets(num_markets=8)
print(f"Found {len(markets)} active markets")
```

---

## 🎯 Asset IDs and Token IDs

### **Understanding Asset IDs**

Each market outcome (e.g., "UP" and "DOWN") has a unique **asset ID** (also called **token ID**). These IDs are required for:
- WebSocket subscriptions
- Order book queries
- Trading operations

### **Getting Asset IDs**

**Method 1: From `clobTokenIds` Field** (Recommended)

```python
import json

def get_asset_ids(market):
    """
    Get asset IDs from clobTokenIds field
    
    Note: clobTokenIds is a JSON string, not an array
    """
    clob_token_ids_str = market.get('clobTokenIds')
    
    if clob_token_ids_str:
        try:
            asset_ids = json.loads(clob_token_ids_str)
            return asset_ids  # List of 2 asset IDs
        except json.JSONDecodeError:
            print(f"Failed to parse clobTokenIds: {clob_token_ids_str}")
    
    return []

# Use
market = find_market_by_slug("btc-updown-5m-1772618700")
asset_ids = get_asset_ids(market)
print(f"Asset IDs: {asset_ids}")
# Output: ['12345...', '67890...']
```

**Method 2: From `tokens` Field** (Legacy)

```python
def get_asset_ids_legacy(market):
    """Get asset IDs from tokens array (old method)"""
    tokens = market.get('tokens', [])
    return [t.get('token_id') for t in tokens if t.get('token_id')]
```

**Important**:
- ✅ Use `clobTokenIds` first (newer, more reliable)
- ⚠️ Fall back to `tokens` only if `clobTokenIds` is missing
- 🔑 Asset IDs are required for WebSocket subscriptions

---

## 📊 Order Books and Liquidity

### **Understanding Order Books**

An order book contains:
- **Bids**: Buy orders (people wanting to buy)
- **Asks**: Sell orders (people wanting to sell)
- **Size**: Amount available at each price level
- **Liquidity**: Total amount available for trading

### **Getting Order Book Data**

**Via WebSocket** (Real-time)

```python
import aiohttp
import asyncio
import json

async def monitor_orderbook(asset_ids):
    """
    Monitor order book updates via WebSocket
    
    Args:
        asset_ids: List of asset IDs to monitor
    """
    async with aiohttp.ClientSession() as session:
        ws = await session.ws_connect(
            "wss://ws-subscriptions-clob.polymarket.com/ws/market"
        )
        
        # Subscribe
        await ws.send_json({
            "assets_ids": asset_ids,
            "type": "market",
            "custom_feature_enabled": True
        })
        
        # Listen for order book updates
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                    
                    if data.get('event_type') == 'book':
                        book = data.get('book', {})
                        asset_id = data.get('asset_id')
                        
                        # Process order book
                        bids = book.get('bids', [])
                        asks = book.get('asks', [])
                        
                        print(f"\n📊 Order Book for {asset_id[:20]}...")
                        print(f"Best Bid: {bids[0].get('price') if bids else 'N/A'}")
                        print(f"Best Ask: {asks[0].get('price') if asks else 'N/A'}")
                        
                        # Calculate liquidity
                        total_liquidity = sum(float(b.get('size', 0)) for b in bids)
                        total_liquidity += sum(float(a.get('size', 0)) for a in asks)
                        print(f"Total Liquidity: ${total_liquidity:.2f}")
                        
                except json.JSONDecodeError:
                    pass

# Use
asset_ids = ["asset_id_1", "asset_id_2"]
asyncio.run(monitor_orderbook(asset_ids))
```

### **Calculating Liquidity**

```python
def calculate_liquidity(book):
    """
    Calculate total liquidity from order book
    
    Liquidity = sum of all bid sizes + sum of all ask sizes
    
    Returns:
        Total liquidity in USD
    """
    total = 0.0
    
    # Sum all bid sizes (buy orders)
    for bid in book.get('bids', []):
        total += float(bid.get('size', 0))
    
    # Sum all ask sizes (sell orders)
    for ask in book.get('asks', []):
        total += float(ask.get('size', 0))
    
    return total

def format_liquidity(liquidity):
    """Format liquidity for display"""
    if liquidity >= 10000:
        return f"${liquidity/1000:.1f}K"
    elif liquidity >= 1000:
        return f"${liquidity/1000:.2f}K"
    else:
        return f"${liquidity:.0f}"

# Use
book = {
    'bids': [
        {'price': '0.45', 'size': '1000'},
        {'price': '0.44', 'size': '500'}
    ],
    'asks': [
        {'price': '0.46', 'size': '800'},
        {'price': '0.47', 'size': '300'}
    ]
}

liquidity = calculate_liquidity(book)
print(f"Liquidity: {format_liquidity(liquidity)}")
# Output: Liquidity: $2.60K
```

---

## 🔄 Real-time Data with WebSocket

### **Connection Methods**

Polymarket supports **3 connection methods** (in order of preference):

1. **Native WebSocket** (Fastest, most reliable) ✅
2. **Socket.IO** (Good fallback)
3. **Polling** (Slowest, use when others fail)

### **Method 1: Native WebSocket (Recommended)**

**Endpoint**: `wss://ws-subscriptions-clob.polymarket.com/ws/market`

```python
import aiohttp
import asyncio
import json
import time

class PolymarketWebSocket:
    """Real-time market data via WebSocket"""
    
    def __init__(self):
        self.ws = None
        self.session = None
        self.last_ping = 0
    
    async def connect(self):
        """Connect to WebSocket"""
        self.session = aiohttp.ClientSession()
        self.ws = await self.session.ws_connect(
            "wss://ws-subscriptions-clob.polymarket.com/ws/market",
            heartbeat=None,
            timeout=aiohttp.ClientWSTimeout(ws_close=30.0)
        )
        print("✅ Connected to WebSocket")
    
    async def subscribe(self, asset_ids):
        """Subscribe to market updates"""
        msg = {
            "assets_ids": asset_ids,
            "type": "market",
            "custom_feature_enabled": True
        }
        await self.ws.send_json(msg)
        print(f"✅ Subscribed to {len(asset_ids)} assets")
    
    async def unsubscribe(self, asset_ids):
        """Unsubscribe from market updates"""
        msg = {
            "assets_ids": asset_ids,
            "type": "unsubscribe"
        }
        await self.ws.send_json(msg)
        print(f"✅ Unsubscribed from {len(asset_ids)} assets")
    
    async def send_heartbeat(self):
        """Send PING every 10 seconds to keep connection alive"""
        if time.time() - self.last_ping >= 10:
            await self.ws.send_str("PING")
            self.last_ping = time.time()
    
    async def listen(self, callback):
        """Listen for updates with callback"""
        try:
            async for msg in self.ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    if msg.data == "PONG":
                        continue  # Heartbeat response
                    
                    try:
                        data = json.loads(msg.data)
                        await callback(data)
                    except json.JSONDecodeError:
                        pass
                
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print(f"❌ WebSocket error: {self.ws.exception()}")
                    break
                
                # Send heartbeat
                await self.send_heartbeat()
        
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def close(self):
        """Close connection"""
        if self.ws:
            await self.ws.close()
        if self.session:
            await self.session.close()

# Example usage
async def main():
    ws = PolymarketWebSocket()
    await ws.connect()
    
    asset_ids = ["asset_id_1", "asset_id_2"]
    await ws.subscribe(asset_ids)
    
    async def handle_update(data):
        event_type = data.get('event_type')
        asset_id = data.get('asset_id')
        
        if event_type == 'book':
            book = data.get('book', {})
            bids = book.get('bids', [])
            asks = book.get('asks', [])
            
            if bids and asks:
                print(f"Best Bid: {bids[0].get('price')}, Best Ask: {asks[0].get('price')}")
        
        elif event_type == 'best_bid_ask':
            print(f"Best Bid: {data.get('best_bid')}, Best Ask: {data.get('best_ask')}")
    
    await ws.listen(handle_update)
    await ws.close()

asyncio.run(main())
```

### **WebSocket Event Types**

| Event Type | Description | Data |
|------------|-------------|------|
| `book` | Full order book snapshot | `book.bids`, `book.asks` |
| `best_bid_ask` | Best bid/ask update | `best_bid`, `best_ask` |
| `price_change` | Price change notification | `price`, `asset_id` |
| `last_trade_price` | Last trade price | `price`, `size` |

### **Method 2: Socket.IO**

```python
import socketio

sio = socketio.Client()

@sio.event
def connect():
    print("Connected!")
    sio.emit('subscribe', {'markets': ['market_id_1', 'market_id_2']})

@sio.event
def price_change(data):
    print(f"Price update: {data}")

@sio.event
def disconnect():
    print("Disconnected")

# Connect
sio.connect('wss://ws-subscriptions.polymarket.com')
sio.wait()
```

### **Method 3: Polling (Fallback)**

When WebSocket/Socket.IO not available:

```python
import requests
import time

def poll_market_prices(market_id, interval=5):
    """
    Poll market prices at regular intervals
    
    Args:
        market_id: Market to poll
        interval: Seconds between polls (minimum 5)
    """
    while True:
        response = requests.get(
            f"https://gamma-api.polymarket.com/markets/{market_id}"
        )
        market = response.json()
        
        prices = market.get('outcomePrices', [])
        print(f"Prices: {prices}")
        
        time.sleep(max(5, interval))  # Minimum 5 seconds

# Use
poll_market_prices("market_id_here", interval=10)
```

---

## 📊 Market Data Structure

### **Market Object**

```json
{
  "id": "abc123",
  "slug": "bitcoin-100k-2024",
  "question": "Will Bitcoin reach $100K by end of 2024?",
  "description": "...",
  "outcomes": ["Yes", "No"],
  "outcomePrices": ["0.67", "0.33"],
  "volume": "1234567.89",
  "active": true,
  "closed": false,
  "expirationDate": "2024-12-31T23:59:59Z",
  "createdAt": "2024-01-01T00:00:00Z",
  "clobTokenIds": "[\"token1\", \"token2\"]",
  "tokens": []
}
```

**Important Fields**:
- `clobTokenIds`: JSON string of asset IDs (use this!)
- `outcomes`: May be array or JSON string
- `outcomePrices`: Current prices
- `active`: Market is live
- `closed`: Market has ended

---

## 🎓 Common Use Cases

### **Use Case 1: Monitor Multiple Markets**

```python
import requests
import time

def track_markets(market_ids, interval=10):
    """Track multiple markets simultaneously"""
    while True:
        for market_id in market_ids:
            response = requests.get(
                f"https://gamma-api.polymarket.com/markets/{market_id}"
            )
            market = response.json()
            
            question = market.get('question', 'N/A')
            prices = market.get('outcomePrices', [])
            
            print(f"{question}: {prices}")
        
        time.sleep(interval)

# Use
market_ids = ["id1", "id2", "id3"]
track_markets(market_ids, interval=10)
```

### **Use Case 2: Price Alert System**

```python
def price_alert(market_id, target_price, outcome_index=0):
    """Alert when price reaches target"""
    while True:
        response = requests.get(
            f"https://gamma-api.polymarket.com/markets/{market_id}"
        )
        market = response.json()
        prices = market.get('outcomePrices', [])
        
        if prices:
            current_price = float(prices[outcome_index])
            
            if current_price >= target_price:
                print(f"🎯 PRICE ALERT: {current_price} (target: {target_price})")
                break
        
        time.sleep(10)

# Use
price_alert("market_id_here", target_price=0.50, outcome_index=0)
```

### **Use Case 3: Market Scanner**

```python
def scan_for_arbitrage(min_profit=0.02):
    """
    Scan for arbitrage opportunities (UP + DOWN < 1.0)
    
    Note: This is for educational purposes only!
    """
    response = requests.get(
        "https://gamma-api.polymarket.com/markets",
        params={"active": "true", "limit": 100}
    )
    markets = response.json()
    
    opportunities = []
    
    for market in markets:
        prices = market.get('outcomePrices', [])
        
        if len(prices) == 2:
            total = float(prices[0]) + float(prices[1])
            profit = 1.0 - total
            
            if profit >= min_profit:
                opportunities.append({
                    'question': market.get('question'),
                    'total': total,
                    'profit': profit,
                    'profit_pct': profit * 100
                })
    
    return opportunities

# Use
opps = scan_for_arbitrage(min_profit=0.02)
for opp in opps:
    print(f"{opp['question']}: {opp['profit_pct']:.2f}% profit")
```

---

## 📚 API Reference

### **Gamma API Endpoints**

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/markets` | GET | Get all markets | No |
| `/markets/{id}` | GET | Get market by ID | No |
| `/markets?slug={slug}` | GET | Get market by slug | No |
| `/markets?_s={term}` | GET | Search markets | No |

### **WebSocket Events**

| Event | Direction | Description | Data Structure |
|-------|-----------|-------------|----------------|
| `connect` | Client → Server | Connect to WebSocket | - |
| `subscribe` | Client → Server | Subscribe to market updates | - |
| `unsubscribe` | Client → Server | Unsubscribe from updates | - |
| `book` | Server → Client | **Full order book** | `bids[]`, `asks[]` at TOP LEVEL |
| `best_bid_ask` | Server → Client | Best bid/ask prices | `best_bid`, `best_ask` |
| `price_change` | Server → Client | Price notification | Less detailed |
| `last_trade_price` | Server → Client | Last trade price | Trade notification |

---

## 🔧 CRITICAL: WebSocket Data Structure (2026-03-05)

### **⚠️ IMPORTANT: Book Event Structure**

**The `book` event has a specific structure that is easy to get wrong:**

#### **❌ WRONG (Common Mistake):**
```python
# This will return empty arrays!
event = {'event_type': 'book', 'bids': [...], 'asks': [...]}
book = event.get('book', {})  # ❌ Returns {} (empty dict)
bids = book.get('bids', [])   # ❌ Returns [] (empty array)
asks = book.get('asks', [])   # ❌ Returns [] (empty array)
```

#### **✅ CORRECT (How to Read):**
```python
# bids and asks are at the TOP LEVEL, not under 'book' key!
event = {'event_type': 'book', 'bids': [...], 'asks': [...]}
bids = event.get('bids', [])  # ✅ Direct access
asks = event.get('asks', [])  # ✅ Direct access
```

### **Full Example: Handling Book Events**

```python
async def handle_message(data):
    event_type = data.get('event_type')
    asset_id = data.get('asset_id', 'unknown')
    
    if event_type == 'book':
        # ✅ CORRECT: Read bids/asks from top level
        bids = data.get('bids', [])
        asks = data.get('asks', [])
        
        if len(bids) == 0 and len(asks) == 0:
            # Empty book - no liquidity
            return
        
        # Get best bid/ask with sizes
        if bids and asks:
            best_bid = float(bids[0].get('price', 0))
            best_ask = float(asks[0].get('price', 0))
            best_bid_size = float(bids[0].get('size', 0))
            best_ask_size = float(asks[0].get('size', 0))
            
            print(f"Best Bid: {best_bid:.4f} (${best_bid_size:,.0f})")
            print(f"Best Ask: {best_ask:.4f} (${best_ask_size:,.0f})")
            
            # Calculate total liquidity
            total_liquidity = sum(float(b.get('size', 0)) for b in bids)
            total_liquidity += sum(float(a.get('size', 0)) for a in asks)
            print(f"Total Liquidity: ${total_liquidity:,.0f}")
    
    elif event_type == 'best_bid_ask':
        # Only has prices, no sizes
        best_bid = float(data.get('best_bid', 0))
        best_ask = float(data.get('best_ask', 0))
        print(f"Best Bid: {best_bid:.4f}, Best Ask: {best_ask:.4f}")
```

---

## 💰 Real-Time Liquidity Tracking

### **Understanding Order Book Data**

Each bid/ask contains:
```python
{
  'price': '0.4550',  # Price level
  'size': '7270'      # Size available at this price (in $)
}
```

### **Calculate Total Liquidity**

```python
def calculate_liquidity(bids, asks):
    """
    Calculate total liquidity from order book
    
    Returns:
        Total dollar amount available for trading
    """
    total = 0.0
    
    # Sum all bid sizes (buy orders available)
    for bid in bids:
        total += float(bid.get('size', 0))
    
    # Sum all ask sizes (sell orders available)
    for ask in asks:
        total += float(ask.get('size', 0))
    
    return total

def format_liquidity(liquidity):
    """Format liquidity for display"""
    if liquidity >= 10000:
        return f"${liquidity/1000:.1f}K"
    elif liquidity >= 1000:
        return f"${liquidity/1000:.2f}K"
    else:
        return f"${liquidity:.0f}"

# Example
bids = [{'price': '0.45', 'size': '10000'}, {'price': '0.44', 'size': '5000'}]
asks = [{'price': '0.46', 'size': '8000'}, {'price': '0.47', 'size': '3000'}]

liquidity = calculate_liquidity(bids, asks)
print(format_liquidity(liquidity))  # Output: $26.0K
```

---

## 🎯 Multi-Cryptocurrency Monitoring

### **Pattern for 5-Minute Markets**

Different cryptocurrencies follow the same timestamp pattern:

```python
# Supported cryptocurrencies
CRYPTOS = ['btc', 'eth', 'sol', 'xrp']

# Market slug pattern
slug = f"{crypto}-updown-5m-{timestamp}"

# Examples:
# btc-updown-5m-1772699400
# eth-updown-5m-1772699400
# sol-updown-5m-1772699400
# xrp-updown-5m-1772699400
```

### **Monitoring Multiple Cryptos**

```python
import time

def generate_market_timestamps(num_markets=8):
    """Generate timestamps for current + next 7 intervals"""
    current_time = int(time.time())
    base = (current_time // 300) * 300  # 5-minute intervals
    return [base + i * 300 for i in range(num_markets)]

async def fetch_all_crypto_markets():
    """Fetch markets for all cryptocurrencies"""
    timestamps = generate_market_timestamps()
    
    for crypto in ['btc', 'eth', 'sol', 'xrp']:
        print(f"\n🔍 {crypto.upper()} Markets:")
        
        for ts in timestamps:
            slug = f"{crypto}-updown-5m-{ts}"
            
            response = requests.get(
                "https://gamma-api.polymarket.com/markets",
                params={"slug": slug}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    print(f"  ✅ {slug}")
```

---

## 📊 Display Best Practices

### **Clean Output Pattern**

```python
# ❌ Don't: Log every book update
if event_type == 'book':
    print(f"📖 BOOK event: {len(bids)} bids, {len(asks)} asks")  # Too noisy!

# ✅ Do: Only show actionable information
if total_cost < 1.0:  # Arbitrage opportunity
    print("="*80)
    print(f"💰 {crypto} ARBITRAGE OPPORTUNITY! 💰")
    print("="*80)
    print(f"Market: {question}")
    print(f"Time: {time_str}")
    print(f"🔗 {market_url}")
    print("-"*80)
    print(f"UP:    Ask {up_ask:.4f} (${up_ask_size:,.0f}) | Bid {up_bid:.4f} (${up_bid_size:,.0f})")
    print(f"DOWN:  Ask {down_ask:.4f} (${down_ask_size:,.0f}) | Bid {down_bid:.4f} (${down_bid_size:,.0f})")
    print("-"*80)
    print(f"Total: {total_cost:.4f} (UP + DOWN)")
    print(f"Profit: {profit_pct:.2f}%")
    print("="*80)
```

### **Information to Show**

| Data | Show? | Why |
|------|-------|-----|
| Best Ask Price | ✅ | Price to buy |
| Best Bid Price | ✅ | Price to sell |
| Ask Size | ✅ | How much available to buy |
| Bid Size | ✅ | How much available to sell |
| Spread | ✅ | Trading cost indicator |
| Total Liquidity | ⚠️ Optional | Can calculate from sizes |
| Every book update | ❌ | Too noisy |

---

## ⚠️ Important Notes

### **Rate Limits**
- Gamma API: ~100 requests/minute
- WebSocket: No limit (but don't spam subscriptions)
- **Best Practice**: Use WebSocket for real-time, not polling

### **Best Practices**

1. ✅ **Use WebSocket for real-time data** (preferred)
2. ✅ **Use `clobTokenIds` for asset IDs** (not `tokens`)
3. ✅ **Implement exponential backoff** on errors
4. ✅ **Cache responses** when possible
5. ✅ **Use polling intervals >= 5 seconds**
6. ✅ **Send PING every 10 seconds** to keep WebSocket alive
7. ✅ **Handle disconnections gracefully**

### **Error Handling**

```python
import time

def safe_api_call(url, max_retries=3):
    """Make API call with retry logic"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise

# Use
data = safe_api_call("https://gamma-api.polymarket.com/markets")
```

---

## 🎓 Advanced Topics

### **Time-Based Market Patterns**

Many markets follow predictable patterns:
- **5-minute intervals**: Bitcoin Up/Down markets
- **Daily intervals**: "Will X happen today?"
- **Weekly intervals**: "Will X happen this week?"

**Implementation**:
```python
def generate_interval_timestamps(interval_seconds, num_intervals):
    """Generate timestamps for time-based markets"""
    current = int(time.time())
    base = (current // interval_seconds) * interval_seconds
    return [base + i * interval_seconds for i in range(num_intervals)]

# Generate 8 5-minute intervals
timestamps = generate_interval_timestamps(300, 8)
```

### **Market Rotation**

For markets that rotate (like 5-minute markets):

```python
async def rotate_markets(manager, websocket):
    """Rotate markets at regular intervals"""
    while True:
        await asyncio.sleep(300)  # 5 minutes
        
        # Unsubscribe from old markets
        old_asset_ids = manager.get_all_asset_ids()
        await websocket.unsubscribe(old_asset_ids)
        
        # Generate new timestamps
        new_timestamps = manager.generate_market_timestamps()
        
        # Fetch new markets
        new_markets = []
        for ts in new_timestamps:
            market = await manager.fetch_market_by_timestamp(ts)
            if market:
                new_markets.append(market)
        
        # Subscribe to new markets
        new_asset_ids = manager.get_all_asset_ids()
        await websocket.subscribe(new_asset_ids)
```

---

## 📖 Further Reading

- **API Documentation**: Check `references/API_REFERENCE.md`
- **WebSocket Guide**: Check `references/WEBSOCKET_GUIDE.md`
- **Examples**: Check `examples/` directory

---

## 🎯 Summary

This skill teaches you **how to access Polymarket data**:

1. ✅ **Connect**: Gamma API, CLOB API, WebSocket
2. ✅ **Find Markets**: Browse, search, pattern-based discovery
3. ✅ **Asset IDs**: Use `clobTokenIds` field
4. ✅ **Real-time Data**: WebSocket (preferred) or Socket.IO
5. ✅ **Order Books**: Liquidity, bid/ask spreads
6. ✅ **Polling**: Fallback when real-time unavailable
7. ✅ **Time-Based Markets**: Pattern discovery, rotation

**Use this knowledge to build your own applications!**

---

**Note**: This is a **general reference guide**. For specific trading strategies, build separate programs using these APIs.

---

## 📝 Version History

- **v1.2.0 (2026-03-05 22:20)**:
  - ✅ **CRITICAL FIX**: WebSocket book event structure (bids/asks at top level)
  - ✅ Added real-time liquidity tracking with sizes
  - ✅ Added multi-cryptocurrency monitoring (BTC, ETH, SOL, XRP)
  - ✅ Added clean output best practices
  - ✅ Added detailed display patterns with sizes
  - ✅ Fixed common mistake in reading book events

- **v1.1.0 (2026-03-05)**:
  - ✅ Added time-based market discovery (5-minute pattern)
  - ✅ Added WebSocket real-time data guide
  - ✅ Added order book and liquidity tracking
  - ✅ Added `clobTokenIds` field documentation
  - ✅ Added market rotation examples
  - ✅ Improved error handling examples

- **v1.0.0 (2026-03-03)**:
  - Initial release
  - Basic API connectivity
  - Market search and discovery
  - WebSocket basics
