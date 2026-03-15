# Polymarket WebSocket Guide

Complete guide for connecting to Polymarket's real-time data streams.

**Author**: Calvin Lam  
**Last Updated**: 2026-03-03

---

## Table of Contents

1. [Overview](#overview)
2. [Connection Methods](#connection-methods)
3. [Native WebSocket](#native-websocket)
4. [Socket.IO](#socketio)
5. [Async WebSocket](#async-websocket)
6. [Events and Messages](#events-and-messages)
7. [Reconnection Handling](#reconnection-handling)
8. [Best Practices](#best-practices)

---

## Overview

Polymarket provides real-time market data via WebSocket connections.

**WebSocket Endpoint**: `wss://ws-subscriptions.polymarket.com`

### Use Cases

- Real-time price updates
- Live order book changes
- Trade notifications
- Market status updates

### When to Use WebSocket vs Polling

| Scenario | Recommended |
|----------|-------------|
| Real-time updates | WebSocket |
| Multiple markets | WebSocket |
| Infrequent checks | Polling |
| Simple scripts | Polling |
| High-frequency data | WebSocket |

---

## Connection Methods

Three methods available (in order of preference):

1. **Native WebSocket** - Fastest, most reliable
2. **Socket.IO** - Good fallback
3. **Polling** - Slowest, use when others fail

---

## Native WebSocket

### Installation

```bash
pip install websocket-client
```

### Basic Connection

```python
import websocket
import json

def on_message(ws, message):
    """Handle incoming messages"""
    data = json.loads(message)
    print(f"Received: {data}")

def on_error(ws, error):
    """Handle errors"""
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    """Handle connection close"""
    print("Connection closed")

def on_open(ws):
    """Handle connection open"""
    print("Connected!")
    
    # Subscribe to market
    subscribe_msg = {
        "type": "subscribe",
        "market": "your_market_id_here"
    }
    ws.send(json.dumps(subscribe_msg))

# Create connection
ws = websocket.WebSocketApp(
    "wss://ws-subscriptions.polymarket.com",
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
    on_open=on_open
)

# Run
ws.run_forever()
```

### Subscribe to Multiple Markets

```python
def on_open(ws):
    """Subscribe to multiple markets"""
    market_ids = ["market_1", "market_2", "market_3"]
    
    for market_id in market_ids:
        ws.send(json.dumps({
            "type": "subscribe",
            "market": market_id
        }))
        print(f"Subscribed to {market_id}")
```

### Unsubscribe

```python
def unsubscribe(ws, market_id):
    """Unsubscribe from a market"""
    ws.send(json.dumps({
        "type": "unsubscribe",
        "market": market_id
    }))
```

---

## Socket.IO

### Installation

```bash
pip install python-socketio
```

### Basic Connection

```python
import socketio

sio = socketio.Client()

@sio.event
def connect():
    """Handle connection"""
    print("Connected via Socket.IO")
    
    # Subscribe to markets
    sio.emit('subscribe', {
        'markets': ['market_1', 'market_2']
    })

@sio.event
def price_change(data):
    """Handle price updates"""
    print(f"Price update: {data}")

@sio.event
def order_book_update(data):
    """Handle order book updates"""
    print(f"Order book update: {data}")

@sio.event
def disconnect():
    """Handle disconnection"""
    print("Disconnected")

# Connect
sio.connect('wss://ws-subscriptions.polymarket.com')

# Keep running
sio.wait()
```

### Custom Event Handlers

```python
@sio.on('custom_event')
def handle_custom_event(data):
    """Handle custom events"""
    print(f"Custom event: {data}")
```

### Emit Custom Events

```python
# Send custom event
sio.emit('custom_event', {'data': 'value'})
```

---

## Async WebSocket

### Installation

```bash
pip install websockets
```

### Async Connection

```python
import asyncio
import websockets
import json

async def connect_websocket():
    """Connect using async WebSocket"""
    uri = "wss://ws-subscriptions.polymarket.com"
    market_id = "your_market_id_here"
    
    async with websockets.connect(uri) as ws:
        print("Connected!")
        
        # Subscribe
        await ws.send(json.dumps({
            "type": "subscribe",
            "market": market_id
        }))
        
        # Listen for messages
        while True:
            try:
                message = await asyncio.wait_for(
                    ws.recv(),
                    timeout=30.0
                )
                data = json.loads(message)
                print(f"Received: {data}")
                
            except asyncio.TimeoutError:
                # Send keepalive
                await ws.ping()
                
            except websockets.exceptions.ConnectionClosed:
                print("Connection closed")
                break

# Run
asyncio.run(connect_websocket())
```

### Async with Multiple Markets

```python
async def monitor_markets(market_ids):
    """Monitor multiple markets"""
    uri = "wss://ws-subscriptions.polymarket.com"
    
    async with websockets.connect(uri) as ws:
        # Subscribe to all markets
        for market_id in market_ids:
            await ws.send(json.dumps({
                "type": "subscribe",
                "market": market_id
            }))
        
        # Process messages
        async for message in ws:
            data = json.loads(message)
            await process_message(data)

async def process_message(data):
    """Process incoming message"""
    print(f"Processing: {data}")
```

---

## Events and Messages

### Message Types

#### Price Change Event

```json
{
  "type": "price_change",
  "market": "abc123",
  "outcomes": ["Yes", "No"],
  "outcomePrices": ["0.67", "0.33"],
  "timestamp": "2024-03-15T12:34:56Z"
}
```

#### Order Book Update Event

```json
{
  "type": "order_book_update",
  "market": "abc123",
  "bids": [
    {"price": "0.66", "size": "1000"}
  ],
  "asks": [
    {"price": "0.68", "size": "800"}
  ],
  "timestamp": "2024-03-15T12:34:56Z"
}
```

#### Trade Event

```json
{
  "type": "trade",
  "market": "abc123",
  "outcome": "Yes",
  "price": "0.67",
  "size": "100",
  "timestamp": "2024-03-15T12:34:56Z"
}
```

#### Market Status Event

```json
{
  "type": "market_update",
  "market": "abc123",
  "status": "active",
  "timestamp": "2024-03-15T12:34:56Z"
}
```

### Handling Different Message Types

```python
def on_message(ws, message):
    """Route messages to appropriate handlers"""
    data = json.loads(message)
    msg_type = data.get('type')
    
    if msg_type == 'price_change':
        handle_price_change(data)
    elif msg_type == 'order_book_update':
        handle_order_book(data)
    elif msg_type == 'trade':
        handle_trade(data)
    elif msg_type == 'market_update':
        handle_market_update(data)
    else:
        print(f"Unknown message type: {msg_type}")

def handle_price_change(data):
    """Handle price changes"""
    market = data['market']
    prices = data['outcomePrices']
    print(f"Market {market}: {prices}")

def handle_order_book(data):
    """Handle order book updates"""
    market = data['market']
    bids = data['bids']
    asks = data['asks']
    print(f"Order book update for {market}")

def handle_trade(data):
    """Handle trade events"""
    market = data['market']
    outcome = data['outcome']
    price = data['price']
    size = data['size']
    print(f"Trade on {market}: {size}@{price}")

def handle_market_update(data):
    """Handle market status updates"""
    market = data['market']
    status = data['status']
    print(f"Market {market}: {status}")
```

---

## Reconnection Handling

### Basic Reconnection

```python
import websocket
import json
import time

class WebSocketClient:
    """WebSocket client with auto-reconnect"""
    
    def __init__(self, url, market_ids):
        self.url = url
        self.market_ids = market_ids
        self.reconnect_delay = 1
        self.max_reconnect_delay = 60
    
    def connect(self):
        """Connect with auto-reconnect"""
        ws = websocket.WebSocketApp(
            self.url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        ws.run_forever()
    
    def on_open(self, ws):
        """Handle connection open"""
        print("✅ Connected")
        self.reconnect_delay = 1  # Reset on success
        
        # Subscribe to markets
        for market_id in self.market_ids:
            ws.send(json.dumps({
                "type": "subscribe",
                "market": market_id
            }))
    
    def on_message(self, ws, message):
        """Handle messages"""
        data = json.loads(message)
        print(f"📥 {data}")
    
    def on_error(self, ws, error):
        """Handle errors"""
        print(f"❌ Error: {error}")
    
    def on_close(self, ws, *args):
        """Handle connection close"""
        print(f"🔌 Disconnected. Reconnecting in {self.reconnect_delay}s...")
        time.sleep(self.reconnect_delay)
        
        # Exponential backoff
        self.reconnect_delay = min(
            self.reconnect_delay * 2,
            self.max_reconnect_delay
        )
        
        # Reconnect
        self.connect()

# Use
client = WebSocketClient(
    "wss://ws-subscriptions.polymarket.com",
    ["market_1", "market_2"]
)
client.connect()
```

### Async Reconnection

```python
import asyncio
import websockets

class AsyncWebSocketClient:
    """Async WebSocket with reconnection"""
    
    def __init__(self, url, market_ids):
        self.url = url
        self.market_ids = market_ids
        self.reconnect_delay = 1
        self.max_delay = 60
    
    async def connect(self):
        """Connect with reconnection"""
        while True:
            try:
                async with websockets.connect(self.url) as ws:
                    print("✅ Connected")
                    self.reconnect_delay = 1
                    
                    # Subscribe
                    for market_id in self.market_ids:
                        await ws.send(json.dumps({
                            "type": "subscribe",
                            "market": market_id
                        }))
                    
                    # Process messages
                    async for message in ws:
                        await self.handle_message(message)
                        
            except Exception as e:
                print(f"❌ Error: {e}")
                print(f"Reconnecting in {self.reconnect_delay}s...")
                
                await asyncio.sleep(self.reconnect_delay)
                self.reconnect_delay = min(
                    self.reconnect_delay * 2,
                    self.max_delay
                )
    
    async def handle_message(self, message):
        """Handle incoming message"""
        data = json.loads(message)
        print(f"📥 {data}")

# Run
client = AsyncWebSocketClient(
    "wss://ws-subscriptions.polymarket.com",
    ["market_1"]
)
asyncio.run(client.connect())
```

---

## Best Practices

### 1. Use Heartbeats

```python
import threading
import time

def heartbeat(ws, interval=30):
    """Send periodic heartbeats"""
    while True:
        time.sleep(interval)
        try:
            ws.ping()
        except:
            break

# Start heartbeat thread
threading.Thread(
    target=heartbeat,
    args=(ws,),
    daemon=True
).start()
```

### 2. Implement Timeouts

```python
import asyncio

async def connect_with_timeout(timeout=10):
    """Connect with timeout"""
    try:
        ws = await asyncio.wait_for(
            websockets.connect(uri),
            timeout=timeout
        )
        return ws
    except asyncio.TimeoutError:
        print("Connection timeout")
        return None
```

### 3. Handle Message Queues

```python
import queue

message_queue = queue.Queue()

def on_message(ws, message):
    """Queue messages for processing"""
    message_queue.put(message)

def process_messages():
    """Process queued messages"""
    while True:
        try:
            message = message_queue.get(timeout=1)
            data = json.loads(message)
            # Process data
        except queue.Empty:
            continue
```

### 4. Use Connection Pooling

```python
class ConnectionPool:
    """Pool of WebSocket connections"""
    
    def __init__(self, max_connections=5):
        self.connections = []
        self.max_connections = max_connections
    
    def get_connection(self):
        """Get available connection"""
        # Implementation
        pass
    
    def return_connection(self, conn):
        """Return connection to pool"""
        # Implementation
        pass
```

### 5. Monitor Connection Health

```python
import time

class ConnectionMonitor:
    """Monitor connection health"""
    
    def __init__(self):
        self.last_message_time = time.time()
        self.timeout = 60  # seconds
    
    def record_message(self):
        """Record received message"""
        self.last_message_time = time.time()
    
    def is_healthy(self):
        """Check if connection is healthy"""
        return time.time() - self.last_message_time < self.timeout
    
    def check(self):
        """Check and log health"""
        if self.is_healthy():
            print("✅ Connection healthy")
        else:
            print("⚠️ No messages received recently")
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Connection drops | Network issues | Implement reconnection |
| No messages | Not subscribed | Check subscription |
| Slow updates | Network latency | Check connection |
| Rate limited | Too many requests | Reduce subscription rate |

### Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# For websocket-client
websocket.enableTrace(True)
```

---

## Summary

1. **Use Native WebSocket** for best performance
2. **Implement reconnection** with exponential backoff
3. **Handle all message types** appropriately
4. **Use heartbeats** to detect dead connections
5. **Monitor connection health** and log issues

---

**Need REST API details?** See `API_REFERENCE.md`
