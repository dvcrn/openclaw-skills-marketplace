# LightningEX API Reference

## Base URL
https://api.lightningex.io

## Authentication
No API key required for public endpoints.

## Endpoints

### 1. Currency List
Get supported currencies and their networks.

```
GET /exchange/currency/list
```

**Response:**
- `currency`: Token ticker (BTC, ETH, etc.)
- `name`: Full name
- `sendStatusAll`/`receiveStatusAll`: Trading availability
- `networkList`: Available networks with fees, confirmations, explorers

### 2. Pair Information
Get trading limits and fees for a pair.

```
GET /exchange/pair/info?send={}&receive={}&sendNetwork={}&receiveNetwork={}
```

**Response:**
- `minimumAmount`/`maximumAmount`: Trade limits
- `networkFee`: Fee in receive currency
- `confirmations`: Required confirmations
- `processingTime`: Estimated time (min-max)

### 3. Exchange Rate
Get current rate (refresh every 20s).

```
GET /exchange/rate?send={}&receive={}&amount={}&sendNetwork={}&receiveNetwork={}
```

**Response:**
- `rate`: Exchange rate
- `sendAmount`/`receiveAmount`: Expected amounts
- `networkFee`: Fee included

### 4. Validate Address
Check if address is valid for currency/network.

```
GET /exchange/address/validate?currency={}&address={}&network={}
```

### 5. Place Order
Create exchange order.

```
POST /exchange/order/place
{
  "send": "BTC",
  "sendNetwork": "BTC",
  "receive": "ETH",
  "receiveNetwork": "ERC20",
  "amount": "0.123",
  "receiveAddress": "0x...",
  "payload": "client-fingerprint-hash"
}
```

**Payload Parameter:**
Client fingerprint for risk assessment. Generated from browser characteristics (userAgent, screen, canvas, WebGL, etc.) using SHA-256 hash.

**Returns:** Order ID string

### 6. Order Status
Get order details (poll every 15s).

```
GET /exchange/order/get?id={orderId}
```

**Status values:**
- `Awaiting Deposit`: Waiting for user deposit
- `Confirming Deposit`: Deposit detected, confirming
- `Exchanging`: Swap in progress
- `Sending`: Sending to user
- `Complete`: Done
- `Failed`/`Refund`: Error states

## Frontend Flow

1. Call `/exchange/currency/list` → Display currency/network selectors
2. User selects currencies → Call `/exchange/pair/info` → Show limits
3. User enters amount → Call `/exchange/rate` every 20s → Update preview
4. User enters address → Call `/exchange/address/validate` → Validate
5. User confirms → Call `/exchange/order/place` → Get order ID
6. Poll `/exchange/order/get` every 15s → Show progress
