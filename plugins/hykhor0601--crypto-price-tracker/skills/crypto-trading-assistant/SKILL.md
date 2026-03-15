---
name: crypto-trading-assistant
description: "Real-time cryptocurrency trading intelligence and portfolio tracking. Use when monitoring crypto prices, tracking Ethereum positions, calculating leverage scenarios, analyzing DeFi protocols, setting price alerts, or aggregating crypto market news and sentiment."
---

# Crypto Trading Assistant

Real-time cryptocurrency trading intelligence, portfolio tracking, and market analysis. Built for active traders who need quick insights on BTC, ETH, and major altcoins without leaving their terminal.

## When to Use

- Checking current prices for Bitcoin, Ethereum, or any cryptocurrency
- Tracking portfolio value with real-time price updates
- Calculating profit/loss scenarios with leverage (2x, 3x, 5x)
- Monitoring DeFi protocol TVL and yield rates
- Setting up price alerts for entry/exit points
- Aggregating crypto news and social sentiment
- Analyzing on-chain metrics (gas fees, market sentiment)
- Quick portfolio calculations with live data

## Quick Price Check

Get instant prices from CryptoCompare API (no API key required):

```bash
# Bitcoin price
curl -s "https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD" | jq -r '.USD'
# Output: 67604.52

# Ethereum price
curl -s "https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD" | jq -r '.USD'
# Output: 3234.56

# Multiple coins at once with full data
curl -s "https://min-api.cryptocompare.com/data/pricemultifull?fsyms=BTC,ETH,SOL&tsyms=USD" | jq '.RAW | to_entries | map({coin: .key, price: .value.USD.PRICE, change24h: .value.USD.CHANGEPCT24HOUR})'
# Shows price + 24h change for BTC, ETH, SOL
```

Alternative source (Blockchain.info):

```bash
# All major coins from Blockchain.info
curl -s "https://blockchain.info/ticker" | jq -r 'to_entries[] | "\(.key): $\(.value.last)"'
# Shows all available currency pairs
```

## Portfolio Tracking

Track your holdings with automatic value calculations:

```bash
# Single-line portfolio calculator
# Replace with your holdings
BTC_AMOUNT=0.5
ETH_AMOUNT=12.5
SOL_AMOUNT=250

# Get prices and calculate
BTC_PRICE=$(curl -s "https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD" | jq -r '.USD')
ETH_PRICE=$(curl -s "https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD" | jq -r '.USD')
SOL_PRICE=$(curl -s "https://min-api.cryptocompare.com/data/price?fsym=SOL&tsyms=USD" | jq -r '.USD')

BTC_VALUE=$(echo "$BTC_AMOUNT * $BTC_PRICE" | bc -l)
ETH_VALUE=$(echo "$ETH_AMOUNT * $ETH_PRICE" | bc -l)
SOL_VALUE=$(echo "$SOL_AMOUNT * $SOL_PRICE" | bc -l)
TOTAL=$(echo "$BTC_VALUE + $ETH_VALUE + $SOL_VALUE" | bc -l)

echo "Portfolio Value:"
echo "BTC: $BTC_AMOUNT × \$$BTC_PRICE = \$$(printf '%.2f' $BTC_VALUE)"
echo "ETH: $ETH_AMOUNT × \$$ETH_PRICE = \$$(printf '%.2f' $ETH_VALUE)"
echo "SOL: $SOL_AMOUNT × \$$SOL_PRICE = \$$(printf '%.2f' $SOL_VALUE)"
echo "---"
echo "Total: \$$(printf '%.2f' $TOTAL)"
```

## Leverage Calculator

Calculate profit/loss scenarios with leverage:

```bash
# 3x leverage ETH position calculator
# Entry: $3000, Current: $3200, Position: $10,000, Leverage: 3x
ENTRY=3000
CURRENT=3200
POSITION=10000
LEVERAGE=3

echo "Position: \$${POSITION} @ ${LEVERAGE}x leverage on ETH" | awk -v entry=$ENTRY -v current=$CURRENT -v pos=$POSITION -v lev=$LEVERAGE '{
  price_change_pct = ((current - entry) / entry) * 100
  leveraged_return_pct = price_change_pct * lev
  profit = pos * (leveraged_return_pct / 100)
  liquidation_price = entry * (1 - (1 / lev) + 0.05)
  
  printf "Entry: $%.2f | Current: $%.2f (%.2f%%)
", entry, current, price_change_pct
  printf "Leveraged Return: %.2f%%
", leveraged_return_pct
  printf "Profit/Loss: $%.2f
", profit
  printf "Liquidation Price (~): $%.2f
", liquidation_price
}'
```

Quick leverage liquidation reference:
```bash
# Quick calculator for any leverage
ENTRY_PRICE=3000
LEVERAGE=3
LIQ_PRICE=$(echo "$ENTRY_PRICE * (1 - (1 / $LEVERAGE) + 0.05)" | bc -l)
echo "Entry: \$$ENTRY_PRICE | Leverage: ${LEVERAGE}x | Liquidation: \$$(printf '%.2f' $LIQ_PRICE)"
```

## DeFi Protocol Monitoring

Track Total Value Locked (TVL) in major DeFi protocols:

```bash
# Top DeFi protocols by TVL
curl -s "https://api.llama.fi/protocols" | jq -r '.[:10] | .[] | "\(.name): $\(.tvl / 1e9 | floor)B"'
# Output: Lists top 10 protocols with TVL in billions

# Specific protocol (e.g., Uniswap)
curl -s "https://api.llama.fi/protocol/uniswap" | jq '{name: .name, tvl: .tvl, change_24h: .change_1d}'

# Track your favorite protocols
for protocol in uniswap aave lido curve; do
  echo -n "$protocol: "
  curl -s "https://api.llama.fi/protocol/$protocol" | jq -r '"\(.tvl / 1e9 | floor * 1)B TVL"'
done
```

## Price Alerts Setup

Create a simple price alert system:

```bash
# Bitcoin alert script (save as btc-alert.sh)
#!/bin/bash
TARGET_PRICE=70000
CURRENT=$(curl -s "https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD" | jq -r '.USD')

if (( $(echo "$CURRENT > $TARGET_PRICE" | bc -l) )); then
  osascript -e "display notification "Bitcoin hit \$$CURRENT!" with title "Price Alert""
  # Or use: echo "BTC Alert: \$$CURRENT" | mail -s "Price Alert" you@email.com
fi
```

Make executable and add to crontab:
```bash
chmod +x btc-alert.sh
# Add to crontab (every 5 minutes)
*/5 * * * * /path/to/btc-alert.sh
```

## Market Sentiment

Bitcoin Fear & Greed Index:

```bash
# Current fear & greed
curl -s "https://api.alternative.me/fng/?limit=1" | jq -r '.data[0] | "Fear & Greed: \(.value)/100 (\(.value_classification))"'
# Output: Fear & Greed: 10/100 (Extreme Fear)

# 7-day history
curl -s "https://api.alternative.me/fng/?limit=7" | jq -r '.data[] | "\(.timestamp | strftime("%Y-%m-%d")): \(.value) (\(.value_classification))"'
```

## Multi-Coin Price Monitor

Monitor multiple coins in real-time:

```bash
# Watch mode - updates every 10 seconds
watch -n 10 'curl -s "https://min-api.cryptocompare.com/data/pricemultifull?fsyms=BTC,ETH,SOL,BNB&tsyms=USD" | jq -r ".RAW | to_entries[] | "\(.key): $\(.value.USD.PRICE | floor) (24h: \(.value.USD.CHANGEPCT24HOUR | floor)%)""'

# One-time check with formatted output
curl -s "https://min-api.cryptocompare.com/data/pricemultifull?fsyms=BTC,ETH,SOL,BNB,ADA,XRP&tsyms=USD" | jq -r '.RAW | to_entries | sort_by(.value.USD.PRICE) | reverse | .[] | 
"\(.key): $\(.value.USD.PRICE | floor | tostring) | 24h: \(.value.USD.CHANGEPCT24HOUR | tonumber | floor | tostring)% | Vol: $\(.value.USD.VOLUME24HOUR / 1e6 | floor | tostring)M"'
```

## Historical Price Data

Get historical prices for analysis:

```bash
# Last 30 days daily close for BTC
curl -s "https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&limit=30" | jq -r '.Data.Data[] | "\(.time | strftime("%Y-%m-%d")): $\(.close | floor)"'

# Hourly prices for last 24 hours
curl -s "https://min-api.cryptocompare.com/data/v2/histohour?fsym=ETH&tsym=USD&limit=24" | jq '.Data.Data | map(.close) | {min: min, max: max, avg: (add/length), current: .[-1]}'
```

## Popular Cryptocurrencies Reference

Common coin symbols for CryptoCompare API:

| Coin | Symbol | Name |
|------|---------|---------|
| Bitcoin | `BTC` | Bitcoin |
| Ethereum | `ETH` | Ethereum |
| Solana | `SOL` | Solana |
| BNB | `BNB` | BNB |
| XRP | `XRP` | Ripple |
| Cardano | `ADA` | Cardano |
| Dogecoin | `DOGE` | Dogecoin |
| Polygon | `MATIC` | Polygon |
| Avalanche | `AVAX` | Avalanche |
| Chainlink | `LINK` | Chainlink |

## API Rate Limits & Keys

**Free APIs (no key required):**
- CryptoCompare: 100,000 calls/month free tier (very generous)
- DeFi Llama: No strict limits
- Alternative.me (Fear & Greed): No limits
- Blockchain.info: No strict limits

**Upgrade for more calls:**
- CryptoCompare Pro: Unlimited calls, $50/month (rarely needed)

No API keys needed for basic usage!

## Advanced: Price Change Tracker

Track price changes over time:

```bash
# Save current prices to file
echo "$(date +%s),$(curl -s 'https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD' | jq -r '.USD')" >> btc_prices.log

# Calculate change from 1 hour ago (if you have hourly logs)
CURRENT=$(tail -1 btc_prices.log | cut -d',' -f2)
ONE_HOUR_AGO=$(tail -13 btc_prices.log | head -1 | cut -d',' -f2)
CHANGE=$(echo "scale=2; (($CURRENT - $ONE_HOUR_AGO) / $ONE_HOUR_AGO) * 100" | bc)
echo "1h change: $CHANGE%"
```

## Tips

- **CryptoCompare is reliable**: Free tier gives 100K calls/month - more than enough for personal use. No API key needed for basic calls.
- **Always calculate liquidation price**: For leveraged positions, liquidation typically happens at ~(100/leverage)% price drop. Add 5% buffer for fees. 3x leverage liquidates at ~28% drop.
- **Test with small amounts first**: Before going 3x leverage on ETH, test with a tiny position to understand the mechanics and risks.
- **Not your keys, not your crypto**: Keep large holdings in hardware wallets (Ledger, Trezor). Exchange hacks still happen regularly.
- **Fear & Greed Index is contrarian**: When index shows "Extreme Greed" (>75), markets often correct. "Extreme Fear" (<25) can signal buying opportunities.
- **Set alerts, don't watch charts**: Constant price watching leads to emotional trading. Automate alerts and stick to your strategy.
- **DeFi yields above 20% are risky**: High APY usually means high risk (impermanent loss, smart contract bugs, or unsustainable tokenomics).
- **Track TVL changes**: Sudden drops in DeFi protocol TVL can signal risk-off sentiment or protocol issues. Watch for >20% daily changes.
- **Leverage amplifies everything**: 3x leverage means 3x gains AND 3x losses. A 10% move against you = 30% loss on your margin. Size positions accordingly.
- **Use bc for calculations**: The `bc -l` command handles decimal math accurately. Essential for financial calculations in bash.

## Safety Warning

This skill provides market data and calculations but is **not financial advice**. Cryptocurrency trading is highly risky and volatile. You can lose all your invested capital. Always:
- Do your own research (DYOR)
- Never invest more than you can afford to lose
- Understand leverage before using it (liquidation can happen fast)
- Be aware of scams and phishing (verify URLs, use 2FA)
- Consider tax implications in your jurisdiction
- Start with small positions to learn the tools

---

**Skill Version**: 1.0.0  
**Last Updated**: March 2026  
**Author**: HY  
**License**: MIT  
**Tested APIs**: CryptoCompare ✅ | DeFi Llama ✅ | Fear & Greed ✅
