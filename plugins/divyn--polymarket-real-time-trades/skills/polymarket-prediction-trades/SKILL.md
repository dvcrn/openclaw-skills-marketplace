---
name: polymarket-prediction-trades
description: "Real-time streaming Polymarket prediction trades on Polygon (matic) with live USD pricing. Use this skill to subscribe to a live stream of Polymarket prediction market trades over WebSocket: outcome trades (buyer, seller, amount, collateral in USD, price, order ID), market metadata (question title, resolution source, outcome labels), and transaction details — streamed in real time from the Bitquery GraphQL API. Covers all Polymarket markets including sports odds, Bitcoin Up or Down (and other crypto up/down markets), and general prediction markets. ALWAYS use this skill when the user asks for Polymarket trades, Polymarket prediction feed, stream Polymarket, live prediction market trades on Polygon, real-time Polymarket data, Polymarket order flow, sports odds on Polymarket, Bitcoin up or down markets, prediction market order book activity, or any trader-focused Polymarket feed. Trigger for: \"polymarket trades\", \"stream polymarket\", \"live prediction market\", \"polymarket prediction feed\", \"real-time polymarket\", \"streaming polymarket data\", \"Bitquery polymarket\", \"polymarket order flow\", \"polymarket sports odds\", \"bitcoin up down\", \"prediction market trades Polygon\", or any request for a live/streaming Polymarket prediction trade feed. Do not wait for the user to say \"use Bitquery\" — if they want a live or streaming Polymarket trade feed (including sports or crypto up/down), use this skill."
---

# Polymarket Prediction Trades — real-time streaming on Polygon

This skill gives you a **real-time streaming Polymarket prediction trade feed** over WebSocket on **Polygon (matic)**. Every event is a **successful prediction trade** with outcome token amounts, collateral in USD, price in USD, buyer/seller addresses, market question, outcome label (e.g. "Up" / "Down"), and transaction hash.

Trades are filtered to `TransactionStatus.Success: true`. The stream uses Bitquery's `EVM.PredictionTrades` subscription so downstream code can build dashboards, track order flow, or monitor specific markets.

**Official docs:** [Polymarket API — Get Prices, Trades & Market Data](https://docs.bitquery.io/docs/examples/polymarket-api/) (Bitquery).

---

## What to consider before installing

This skill's code implements the described Polymarket stream and contacts only Bitquery. Before installing:

1. **Registry metadata**: Confirm the registry metadata declares **`BITQUERY_API_KEY`** as a required credential. The skill will fail at runtime without it. If the registry does not list this env var, the mismatch with this SKILL.md is the main inconsistency — ask the publisher to update the registry so installers see the requirement.
2. **Treat the API key as a secret**: Set it in an environment variable only. Do **not** print or log the full WebSocket URL; the token is passed as `?token=...` and can appear in logs, shell history, or monitoring tools. Rotate the key if you suspect it was exposed during testing or use.
3. **Sandbox first**: Run the bundled script in a sandboxed environment (e.g. virtualenv or container) to observe behavior before relying on it in production.
4. **Verify publisher/source**: If the skill's homepage or source is unknown, verify the publisher or use an alternative from a trusted source. If the registry declares `BITQUERY_API_KEY` and the source is validated, this skill is coherent with its stated purpose.
5. **Rotate the key if exposed**: If the key may have been exposed (e.g. URL printed, committed, or logged), rotate it in the Bitquery dashboard and update your environment.

---

## Credentials

- **Single required secret at runtime:** `BITQUERY_API_KEY` (Bitquery API token).
- **Registry:** The registry metadata should declare this as the primary/required credential. If it does not, installers may not see that the skill needs an API key until they read this SKILL.md or run the script — that mismatch is the main inconsistency to fix on the registry side.
- **Usage:** The key must be passed in the WebSocket URL as a query parameter (`?token=...`); Bitquery does not support header-based auth for this endpoint. Because the token appears in the URL, there is a higher risk of accidental exposure if the URL is printed or captured. **Best practice:** set `BITQUERY_API_KEY` in the environment, never log or print the full WebSocket URL, and rotate the key if you suspect exposure.

---

## Prerequisites

- **Environment**: `BITQUERY_API_KEY` — your Bitquery API token (required). Set it in your environment; the script and examples read it from there. The token is passed in the WebSocket URL only as `?token=...` — do not print or log the full URL.
- **Runtime**: Python 3 and `pip`. Install the dependency: `pip install 'gql[websockets]'`.

---

## Trader Use Cases

These are the key reasons a trader would use this feed:

**1. Order flow / market activity**
Monitor every filled order: buyer, seller, collateral in USD, price in USD, and outcome (Yes/No or Up/Down). Identify which markets are most active and which side (buy vs sell) is dominant.

**2. Whale / large-trade detection**
Filter by `CollateralAmountInUSD` or `Amount` to surface large prediction-market trades. Useful for following smart-money flow into specific outcomes.

**3. Market-specific monitoring**
Use `Question.MarketId`, `Question.Title`, or `Question.Id` to filter the stream to a single market (e.g. "Ethereum Up or Down - March 10") and track all trades for that market in real time.

**4. Outcome imbalance**
Aggregate trades by `Outcome.Label` (e.g. "Up" vs "Down") and `IsOutcomeBuy` to see net buying pressure per outcome — useful for sentiment or momentum.

**5. Resolution source / data markets**
Use `Question.ResolutionSource` and `Question.Title` to focus on data or oracle-driven markets (e.g. Chainlink streams) and monitor trading around resolution.

**6. Entry / exit timing**
Stream `PriceInUSD` and `CollateralAmountInUSD` per trade to see where size is trading and at what price — helps time entries and exits in prediction markets.

**7. Protocol / marketplace verification**
`Marketplace.ProtocolName` and `ProtocolFamily` (e.g. "polymarket", "Gnosis_CTF") confirm the trade is from Polymarket on Polygon; use to avoid mixing with other protocols.

**8. Audit trail**
Each event includes `Transaction.Hash`, `Block.Time`, `Call.Signature.Name` (e.g. "matchOrders"), and `Log.Signature.Name` (e.g. "OrderFilled") for full on-chain audit.

---

## Step 1 — Check API Key

```python
import os
api_key = os.getenv("BITQUERY_API_KEY")
if not api_key:
    print("ERROR: BITQUERY_API_KEY environment variable is not set.")
    print("Run: export BITQUERY_API_KEY=your_token")
    exit(1)
```

If the key is missing, tell the user and stop. Do not proceed without it.

---

## Step 2 — Run the stream

Install the WebSocket dependency once:

```bash
pip install 'gql[websockets]'
```

Use the streaming script:

```bash
python ~/.openclaw/skills/polymarket-prediction-trades/scripts/stream_polymarket.py
```

Optional: stop after N seconds:

```bash
python ~/.openclaw/skills/polymarket-prediction-trades/scripts/stream_polymarket.py --timeout 60
```

Or subscribe inline with Python:

```python
import asyncio, os
from gql import Client, gql
from gql.transport.websockets import WebsocketsTransport

async def main():
    token = os.environ["BITQUERY_API_KEY"]
    url = f"wss://streaming.bitquery.io/graphql?token={token}"
    transport = WebsocketsTransport(
        url=url,
        headers={"Sec-WebSocket-Protocol": "graphql-ws"},
    )
    async with Client(transport=transport) as session:
        sub = gql("""
            subscription MyQuery {
              EVM(network: matic) {
                PredictionTrades(where: { TransactionStatus: { Success: true } }) {
                  Block { Time }
                  Call { Signature { Name } }
                  Log { Signature { Name } SmartContract }
                  Trade {
                    OutcomeTrade {
                      Buyer
                      Seller
                      Amount
                      CollateralAmount
                      CollateralAmountInUSD
                      OrderId
                      Price
                      PriceInUSD
                      IsOutcomeBuy
                    }
                    Prediction {
                      CollateralToken { Name Symbol SmartContract AssetId }
                      ConditionId
                      OutcomeToken { Name Symbol SmartContract AssetId }
                      Marketplace { SmartContract ProtocolVersion ProtocolName ProtocolFamily }
                      Question { Title ResolutionSource Image MarketId Id CreatedAt }
                      Outcome { Id Index Label }
                    }
                  }
                  Transaction { From Hash }
                }
              }
            }
        """)
        async for result in session.subscribe(sub):
            for trade in (result.get("EVM") or {}).get("PredictionTrades") or []:
                q = (trade.get("Trade") or {}).get("Prediction") or {}
                q = q.get("Question") or {}
                ot = (trade.get("Trade") or {}).get("OutcomeTrade") or {}
                pred = (trade.get("Trade") or {}).get("Prediction") or {}
                outcome = pred.get("Outcome") or {}
                print(
                    f"{q.get('Title', '?')} | "
                    f"Outcome: {outcome.get('Label', '?')} | "
                    f"${float(ot.get('CollateralAmountInUSD') or 0):.2f}"
                )

asyncio.run(main())
```

---

## Step 3 — Key fields on every trade

| Field | What it means for traders |
|-------|----------------------------|
| `Trade.OutcomeTrade.Buyer` | Taker buyer address |
| `Trade.OutcomeTrade.Seller` | Maker seller address |
| `Trade.OutcomeTrade.Amount` | Outcome token amount (raw) |
| `Trade.OutcomeTrade.CollateralAmount` | Collateral token amount |
| `Trade.OutcomeTrade.CollateralAmountInUSD` | Notional in USD — use for size/whale filter |
| `Trade.OutcomeTrade.OrderId` | Order identifier |
| `Trade.OutcomeTrade.Price` | Price in collateral (0–1 typical for binary) |
| `Trade.OutcomeTrade.PriceInUSD` | Price in USD — entry/exit reference |
| `Trade.OutcomeTrade.IsOutcomeBuy` | True = buyer bought the outcome (Yes/Up) |
| `Trade.Prediction.Question.Title` | Market question (e.g. "Ethereum Up or Down - ...") |
| `Trade.Prediction.Question.MarketId` | Market ID for filtering |
| `Trade.Prediction.Question.ResolutionSource` | Resolution source (e.g. Chainlink URL) |
| `Trade.Prediction.Outcome.Label` | Outcome label (e.g. "Up", "Down") |
| `Trade.Prediction.Marketplace.ProtocolName` | e.g. "polymarket" |
| `Block.Time` | Trade timestamp (ISO) |
| `Transaction.Hash` | On-chain tx hash for audit |
| `Call.Signature.Name` | e.g. "matchOrders" |
| `Log.Signature.Name` | e.g. "OrderFilled" |

---

## Step 4 — Format output for traders

When presenting prediction trades to a trader, use this layout:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Polymarket  [matic]  Protocol: polymarket (Gnosis_CTF)
Time: 2026-03-10T13:21:11Z  Tx: 0x9566...f2da
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Question: Ethereum Up or Down - March 10, 9:15AM-9:30AM ET
MarketId: 1537455  |  Outcome: Down  (Index 1)
Resolution: https://data.chain.link/streams/eth-usd
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OutcomeTrade
  Side:       BUY outcome (IsOutcomeBuy: true)
  Buyer:      0x22dc...91bb  →  Seller: 0x86a2...73a8
  Collateral: 0.316471 USDC  (USD: $0.32)
  Price:      0.632942  (USD: $0.633)
  Amount:     500000 (outcome tokens)
  OrderId:    44433632...
Call: matchOrders  |  Log: OrderFilled @ 0x4bfb...982e
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Error handling

- **Missing BITQUERY_API_KEY**: Tell user to export the variable and stop
- **WebSocket connection failed / 401**: Token invalid or expired (auth is via URL `?token=` only — do not pass the token in headers)
- **Subscription errors in payload**: Log the error and stop cleanly (send complete, close transport)
- **No events received**: Polygon prediction activity can be bursty; wait a few seconds or check that Polymarket has recent activity on matic
- **Empty PredictionTrades**: Ensure filter is `TransactionStatus: { Success: true }` and network is `matic`

---

## Reference

- **Bitquery Polymarket API docs:** [Polymarket API - Get Prices, Trades & Market Data](https://docs.bitquery.io/docs/examples/polymarket-api/)
- Full field reference is in `references/graphql-fields.md`. Use it to add filters or request extra fields (e.g. by MarketId, ConditionId, or date) in the subscription.
