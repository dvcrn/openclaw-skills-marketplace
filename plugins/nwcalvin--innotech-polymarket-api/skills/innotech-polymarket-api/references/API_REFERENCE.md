# Polymarket API Reference

Complete reference for Polymarket API endpoints, parameters, and responses.

**Author**: Calvin Lam  
**Last Updated**: 2026-03-03

---

## Table of Contents

1. [Gamma API](#gamma-api)
2. [Data API](#data-api)
3. [Response Formats](#response-formats)
4. [Error Handling](#error-handling)
5. [Rate Limits](#rate-limits)

---

## Gamma API

**Base URL**: `https://gamma-api.polymarket.com`

The Gamma API is the primary public API for accessing market data. No authentication required.

### Endpoints

#### GET /markets

List all markets with optional filtering.

**Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | 100 | Number of results to return |
| `offset` | int | 0 | Pagination offset |
| `active` | bool | - | Filter by active status |
| `closed` | bool | - | Filter by closed status |
| `slug` | string | - | Filter by URL slug |
| `_s` | string | - | Search term |
| `tag` | string | - | Filter by tag |
| `order` | string | - | Sort order |

**Example Request**:

```python
import requests

# Get all active markets
response = requests.get(
    "https://gamma-api.polymarket.com/markets",
    params={
        "active": "true",
        "limit": 100,
        "offset": 0
    }
)
markets = response.json()
```

**Response**:

```json
[
  {
    "id": "abc123",
    "slug": "bitcoin-100k-2024",
    "question": "Will Bitcoin reach $100K by end of 2024?",
    "description": "Market description...",
    "outcomes": ["Yes", "No"],
    "outcomePrices": ["0.67", "0.33"],
    "volume": "1234567.89",
    "active": true,
    "closed": false,
    "expirationDate": "2024-12-31T23:59:59Z",
    "createdAt": "2024-01-01T00:00:00Z"
  }
]
```

---

#### GET /markets/{id}

Get a specific market by ID.

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Market ID |

**Example Request**:

```python
market_id = "abc123"
response = requests.get(
    f"https://gamma-api.polymarket.com/markets/{market_id}"
)
market = response.json()
```

**Response**: Single market object (same structure as above)

---

#### GET /markets/{id}/price

Get current prices for a market.

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Market ID |

**Example Request**:

```python
market_id = "abc123"
response = requests.get(
    f"https://gamma-api.polymarket.com/markets/{market_id}/price"
)
prices = response.json()
```

**Response**:

```json
{
  "market": "abc123",
  "outcomes": ["Yes", "No"],
  "outcomePrices": ["0.67", "0.33"],
  "volume": "1234567.89",
  "timestamp": "2024-03-15T12:34:56Z"
}
```

---

#### GET /markets?slug={slug}

Get market by URL slug.

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `slug` | string | Market URL slug |

**Example Request**:

```python
slug = "bitcoin-100k-2024"
response = requests.get(
    "https://gamma-api.polymarket.com/markets",
    params={"slug": slug}
)
market = response.json()[0]  # Returns array
```

---

#### GET /markets?_s={search_term}

Search markets by keyword.

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `_s` | string | Search term |

**Example Request**:

```python
search_term = "bitcoin"
response = requests.get(
    "https://gamma-api.polymarket.com/markets",
    params={"_s": search_term}
)
markets = response.json()
```

---

## Data API

**Base URL**: `https://data-api.polymarket.com`

The Data API provides detailed market data including order books and trade history.

### Endpoints

#### GET /orderbook/{id}

Get order book for a market.

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Market ID |

**Example Request**:

```python
market_id = "abc123"
response = requests.get(
    f"https://data-api.polymarket.com/orderbook/{market_id}"
)
orderbook = response.json()
```

**Response**:

```json
{
  "market": "abc123",
  "bids": [
    {"price": "0.66", "size": "1000"},
    {"price": "0.65", "size": "500"}
  ],
  "asks": [
    {"price": "0.68", "size": "800"},
    {"price": "0.69", "size": "300"}
  ],
  "timestamp": "2024-03-15T12:34:56Z"
}
```

**Field Descriptions**:

| Field | Description |
|-------|-------------|
| `bids` | Array of buy orders (highest price first) |
| `asks` | Array of sell orders (lowest price first) |
| `price` | Order price (0.0 to 1.0) |
| `size` | Order size in dollars |

---

#### GET /trades/{id}

Get trade history for a market.

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Market ID |

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | int | Number of trades to return |
| `before` | string | Trade ID for pagination |

**Example Request**:

```python
market_id = "abc123"
response = requests.get(
    f"https://data-api.polymarket.com/trades/{market_id}",
    params={"limit": 50}
)
trades = response.json()
```

**Response**:

```json
[
  {
    "id": "trade123",
    "market": "abc123",
    "outcome": "Yes",
    "price": "0.67",
    "size": "100",
    "timestamp": "2024-03-15T12:34:56Z"
  }
]
```

---

## Response Formats

### Market Object

```json
{
  "id": "string - unique identifier",
  "slug": "string - URL-friendly identifier",
  "question": "string - market question",
  "description": "string - detailed description",
  "outcomes": ["Yes", "No"] - possible outcomes,
  "outcomePrices": ["0.67", "0.33"] - current prices,
  "volume": "1234567.89" - trading volume in USD,
  "active": true - whether market is active,
  "closed": false - whether market is closed,
  "expirationDate": "2024-12-31T23:59:59Z" - when market expires,
  "createdAt": "2024-01-01T00:00:00Z" - when market was created
}
```

### Price Object

```json
{
  "market": "string - market ID",
  "outcomes": ["Yes", "No"] - outcome labels,
  "outcomePrices": ["0.67", "0.33"] - prices as strings,
  "volume": "1234567.89" - total volume,
  "timestamp": "2024-03-15T12:34:56Z" - last update time
}
```

### Order Book Object

```json
{
  "market": "string - market ID",
  "bids": [
    {"price": "0.66", "size": "1000"}
  ],
  "asks": [
    {"price": "0.68", "size": "800"}
  ],
  "timestamp": "2024-03-15T12:34:56Z"
}
```

### Trade Object

```json
{
  "id": "string - trade ID",
  "market": "string - market ID",
  "outcome": "string - outcome traded",
  "price": "0.67" - trade price,
  "size": "100" - trade size in USD,
  "timestamp": "2024-03-15T12:34:56Z"
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process response |
| 400 | Bad Request | Check parameters |
| 404 | Not Found | Verify market ID |
| 429 | Rate Limited | Implement backoff |
| 500 | Server Error | Retry with backoff |

### Error Response

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {}
}
```

### Handling Errors

```python
import requests
import time

def safe_api_call(url, max_retries=3):
    """Make API call with error handling"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 429:
                # Rate limited - wait and retry
                wait_time = 2 ** attempt
                print(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise
    
    return None
```

---

## Rate Limits

### Gamma API

- **Limit**: ~100 requests per minute
- **Headers**: Check `X-RateLimit-Remaining` header
- **Best Practice**: Use polling intervals >= 5 seconds

### Data API

- **Limit**: ~50 requests per minute
- **Best Practice**: Cache responses when possible

### WebSocket

- **Limit**: No hard limit on subscriptions
- **Best Practice**: Don't spam subscriptions, batch if needed

---

## Best Practices

### 1. Use Connection Pooling

```python
import requests
from requests.adapters import HTTPAdapter

session = requests.Session()
adapter = HTTPAdapter(pool_connections=10, pool_maxsize=10)
session.mount('https://', adapter)
```

### 2. Implement Caching

```python
import time

cache = {}

def get_market_cached(market_id, ttl=60):
    """Get market with caching"""
    cache_key = f"market_{market_id}"
    
    if cache_key in cache:
        data, timestamp = cache[cache_key]
        if time.time() - timestamp < ttl:
            return data
    
    response = requests.get(
        f"https://gamma-api.polymarket.com/markets/{market_id}"
    )
    data = response.json()
    cache[cache_key] = (data, time.time())
    return data
```

### 3. Use Exponential Backoff

```python
def backoff_request(url, max_retries=5):
    """Request with exponential backoff"""
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            if i < max_retries - 1:
                wait = min(2 ** i, 60)  # Cap at 60 seconds
                time.sleep(wait)
            else:
                raise
```

---

## Notes

- All prices are returned as strings (parse with `float()`)
- Timestamps are ISO 8601 format
- Most endpoints are public (no auth required)
- Auth is only needed for user-specific endpoints (positions, orders)

---

**Need WebSocket details?** See `WEBSOCKET_GUIDE.md`
