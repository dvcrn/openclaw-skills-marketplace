# Quick Start Guide

Get up and running with G-Prophet API in 5 minutes.

## 1. Get Your API Key (2 minutes)

1. Visit https://www.gprophet.com/settings/api-keys
2. Click "Create New Key"
3. Copy your key (format: `gp_sk_...`)

## 2. Set Up Environment Variable (1 minute)

```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
export GPROPHET_API_KEY="gp_sk_your_key_here"

# Verify it's set
echo $GPROPHET_API_KEY
```

## 3. Make Your First Prediction (2 minutes)

### Using cURL

```bash
curl -X POST "https://www.gprophet.com/api/external/v1/predictions/predict" \
  -H "X-API-Key: $GPROPHET_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "market": "US",
    "days": 7,
    "algorithm": "auto"
  }'
```

### Expected Response

```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "current_price": 185.50,
    "predicted_price": 191.20,
    "change_percent": 3.07,
    "direction": "up",
    "confidence": 0.78,
    "points_consumed": 20
  }
}
```

## Common Operations

### Get Real-Time Quote

```bash
curl "https://www.gprophet.com/api/external/v1/market-data/quote?symbol=AAPL&market=US" \
  -H "X-API-Key: $GPROPHET_API_KEY"
```

**Cost**: 5 points

### Technical Analysis

```bash
curl -X POST "https://www.gprophet.com/api/external/v1/technical/analyze" \
  -H "X-API-Key: $GPROPHET_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "market": "US",
    "indicators": ["rsi", "macd", "bollinger"]
  }'
```

**Cost**: 5 points

### Search for a Stock

```bash
curl "https://www.gprophet.com/api/external/v1/market-data/search?keyword=apple&market=US&limit=5" \
  -H "X-API-Key: $GPROPHET_API_KEY"
```

**Cost**: 5 points

### Deep Analysis (Async)

```bash
# Step 1: Submit analysis task
curl -X POST "https://www.gprophet.com/api/external/v1/analysis/comprehensive" \
  -H "X-API-Key: $GPROPHET_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "market": "US",
    "locale": "en-US"
  }'

# Response: {"data": {"task_id": "task_abc123..."}}

# Step 2: Poll for results (every 5 seconds)
curl "https://www.gprophet.com/api/external/v1/analysis/task/task_abc123" \
  -H "X-API-Key: $GPROPHET_API_KEY"

# When status = "completed", you have your results
```

**Cost**: 150 points

## Supported Markets

| Code | Market | Example Tickers |
|------|--------|-----------------|
| US | US Stocks | AAPL, TSLA, GOOGL |
| CN | China A-shares | 600519, 000001 |
| HK | Hong Kong | 700, 9988 |
| CRYPTO | Cryptocurrency | BTCUSDT, ETHUSDT |

## Pricing Quick Reference

| Operation | Cost |
|-----------|------|
| Stock Prediction | 10-20 points |
| Quote | 5 points |
| Technical Analysis | 5 points |
| Deep Analysis | 150 points |
| Search | 5 points |

## Check Your Balance

```bash
# Visit dashboard
open https://www.gprophet.com/dashboard

# Or use API
curl "https://www.gprophet.com/api/external/v1/account/usage" \
  -H "X-API-Key: $GPROPHET_API_KEY"
```

## Troubleshooting

### "INVALID_API_KEY"
- Check key format starts with `gp_sk_`
- Verify no extra spaces: `echo $GPROPHET_API_KEY`
- Generate new key if needed

### "INSUFFICIENT_POINTS"
- Check balance at https://www.gprophet.com/dashboard
- Purchase more points if needed

### "SYMBOL_NOT_FOUND"
- Use search to find correct ticker
- Verify market code is correct

### More Issues?
See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

## Next Steps

1. **Learn the API**: Read [SKILL.md](./SKILL.md)
2. **Understand costs**: Read [COST_MANAGEMENT.md](./COST_MANAGEMENT.md)
3. **Security best practices**: Read [SECURITY.md](./SECURITY.md)
4. **Solve problems**: Read [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

## Documentation Map

```
Quick Start (you are here)
├── SKILL.md ..................... Complete API reference
├── SECURITY.md .................. Security & credential management
├── COST_MANAGEMENT.md ........... Pricing & budget planning
├── TROUBLESHOOTING.md ........... Common issues & solutions
├── README.md .................... Overview & features
└── IMPROVEMENTS.md .............. Security improvements
```

## Support

- **Documentation**: https://www.gprophet.com/docs
- **Dashboard**: https://www.gprophet.com/dashboard
- **Support Email**: support@gprophet.com
- **Status Page**: https://www.gprophet.com/status

## Tips for Success

1. **Start with quotes** (5 points) before predictions (20 points)
2. **Use environment variables** for API keys, never hardcode them
3. **Monitor your usage** at the dashboard
4. **Set billing alerts** to avoid surprises
5. **Cache results** locally to save points
6. **Use 7-14 day predictions** for best accuracy/cost ratio

---

**Ready to predict?** Start with a simple quote:

```bash
curl "https://www.gprophet.com/api/external/v1/market-data/quote?symbol=AAPL&market=US" \
  -H "X-API-Key: $GPROPHET_API_KEY"
```

Good luck! 📈

