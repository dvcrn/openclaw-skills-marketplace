# Cost Management & Quota Guide

## Points System Overview

G-Prophet uses a points-based billing system. Each API call consumes a specific number of points based on the operation type and market.

### Points Pricing Table

| Operation | Market | Points | Notes |
|-----------|--------|--------|-------|
| Stock Prediction | US | 20 | Single prediction |
| Stock Prediction | CN | 10 | China A-shares |
| Stock Prediction | HK | 15 | Hong Kong stocks |
| Stock Prediction | CRYPTO | 20 | Cryptocurrencies |
| Algorithm Compare | Varies | 20-80 | Cost × number of algorithms |
| Quote | All | 5 | Real-time price data |
| History | All | 5 | Historical OHLCV data |
| Search | All | 5 | Symbol search |
| Technical Analysis | All | 5 | Technical indicators |
| Fear & Greed Index | - | 5 | Crypto sentiment |
| Market Overview | All | 5 | Market breadth data |
| Deep Analysis | All | 150 | Multi-agent comprehensive analysis |
| Task Polling | All | 0 | Free (no charge) |

---

## Cost Estimation Examples

### Example 1: Basic Stock Analysis

**Scenario**: Analyze Apple stock (AAPL) with prediction and technical analysis

```
1. Get quote:                    5 points
2. Predict price (7 days):      20 points
3. Technical analysis:           5 points
   ─────────────────────────────
   Total:                       30 points
```

**Estimated cost**: 30 points per analysis

### Example 2: Multi-Algorithm Comparison

**Scenario**: Compare 4 algorithms for Tesla stock

```
1. Compare algorithms (4):      80 points (20 × 4)
   ─────────────────────────────
   Total:                       80 points
```

**Estimated cost**: 80 points per comparison

### Example 3: Comprehensive Market Analysis

**Scenario**: Deep analysis of 5 stocks

```
1. Deep analysis (AAPL):       150 points
2. Deep analysis (MSFT):       150 points
3. Deep analysis (GOOGL):      150 points
4. Deep analysis (TSLA):       150 points
5. Deep analysis (NVDA):       150 points
   ─────────────────────────────
   Total:                      750 points
```

**Estimated cost**: 750 points for comprehensive analysis of 5 stocks

### Example 4: Continuous Monitoring

**Scenario**: Monitor 10 stocks daily with predictions

```
Daily monitoring (10 stocks):
- Quote (10 × 5):              50 points
- Prediction (10 × 20):       200 points
- Technical analysis (10 × 5): 50 points
   ─────────────────────────────
   Daily total:               300 points
   Monthly total:           9,000 points
```

**Estimated cost**: 300 points/day or 9,000 points/month

### Example 5: Mixed Market Analysis

**Scenario**: Analyze stocks across multiple markets

```
1. US stock prediction:         20 points
2. China A-share prediction:    10 points
3. HK stock prediction:         15 points
4. Crypto prediction:           20 points
5. Technical analysis (all):    20 points (5 × 4)
   ─────────────────────────────
   Total:                       85 points
```

**Estimated cost**: 85 points for cross-market analysis

---

## Budget Planning

### Monthly Budget Scenarios

#### Scenario A: Light Usage (Casual Investor)

```
Operations per month:
- 10 predictions:              200 points
- 20 quotes:                   100 points
- 5 technical analyses:         25 points
- 2 deep analyses:             300 points
─────────────────────────────
Monthly budget:                625 points
```

**Recommendation**: 1,000 points/month buffer

#### Scenario B: Active Trading (Day Trader)

```
Operations per month (20 trading days):
- 50 predictions:            1,000 points
- 100 quotes:                  500 points
- 50 technical analyses:       250 points
- 10 deep analyses:          1,500 points
─────────────────────────────
Monthly budget:              3,250 points
```

**Recommendation**: 4,000 points/month buffer

#### Scenario C: Automated Monitoring (Portfolio Manager)

```
Operations per month (20 trading days):
- 200 predictions:           4,000 points
- 400 quotes:                2,000 points
- 200 technical analyses:    1,000 points
- 20 deep analyses:          3,000 points
─────────────────────────────
Monthly budget:             10,000 points
```

**Recommendation**: 12,000 points/month buffer

#### Scenario D: Research & Analysis (Analyst)

```
Operations per month:
- 100 predictions:           2,000 points
- 50 algorithm comparisons:  4,000 points
- 100 technical analyses:      500 points
- 50 deep analyses:          7,500 points
─────────────────────────────
Monthly budget:             14,000 points
```

**Recommendation**: 16,000 points/month buffer

---

## Cost Optimization Strategies

### 1. Use Cheaper Operations First

**Instead of**:
```
Deep analysis (150 points) → Get comprehensive report
```

**Try**:
```
Quote (5 points) → Technical analysis (5 points) → Prediction (20 points)
Total: 30 points (80% savings)
```

### 2. Batch Operations

**Instead of**:
```
Predict AAPL (20 points)
Predict MSFT (20 points)
Predict GOOGL (20 points)
Total: 60 points
```

**Consider**:
```
Compare algorithms for AAPL (80 points for 4 algorithms)
This gives you more insights than 4 separate predictions
```

### 3. Use Appropriate Prediction Periods

**Longer predictions are not more expensive**:
```
Predict 1 day:  20 points
Predict 7 days: 20 points (same cost)
Predict 30 days: 20 points (same cost)
```

**Recommendation**: Use 7-14 day predictions for better accuracy without extra cost

### 4. Leverage Task Polling (Free)

```
1. Submit deep analysis:       150 points
2. Poll task status (10 times): 0 points (free)
   ─────────────────────────────
   Total:                      150 points
```

**Tip**: Polling is free, so don't hesitate to check task status frequently

### 5. Cache Results Locally

```
# Instead of:
Predict AAPL every hour (480 predictions/month = 9,600 points)

# Do:
Predict AAPL once (20 points)
Cache result for 1 hour
Use cached result for subsequent requests
Monthly cost: ~480 points (95% savings)
```

### 6. Use Market-Specific Pricing

**Cheapest to most expensive**:
1. China A-shares: 10 points
2. HK stocks: 15 points
3. US stocks: 20 points
4. Crypto: 20 points

**Tip**: If analyzing multiple markets, prioritize China A-shares for cost savings

---

## Quota Management

### Setting Up Billing Alerts

1. Visit https://www.gprophet.com/dashboard
2. Go to Settings → Billing Alerts
3. Set alert thresholds:
   - Warning: 80% of monthly budget
   - Critical: 95% of monthly budget
   - Hard limit: 100% of monthly budget

### Monitoring Usage

#### Daily Usage Check

```bash
# Check current balance and usage
curl "https://www.gprophet.com/api/external/v1/account/usage" \
  -H "X-API-Key: gp_sk_your_key"
```

#### Weekly Usage Report

Review at: https://www.gprophet.com/dashboard/usage

#### Monthly Budget Review

1. Check total points consumed
2. Identify high-cost operations
3. Adjust strategy for next month
4. Review cost vs. value gained

### Quota Limits

| Limit Type | Value | Notes |
|-----------|-------|-------|
| Requests per second | 10 | Rate limit |
| Requests per minute | 300 | Rate limit |
| Requests per day | 10,000 | Soft limit |
| Concurrent tasks | 5 | Deep analysis tasks |
| Task retention | 7 days | After completion |

---

## Cost Reduction Checklist

- [ ] Use quotes instead of predictions when only price is needed
- [ ] Cache results locally to avoid duplicate calls
- [ ] Use appropriate prediction periods (7-14 days optimal)
- [ ] Batch similar operations together
- [ ] Monitor usage daily
- [ ] Set up billing alerts
- [ ] Review and optimize monthly
- [ ] Use cheaper markets when possible
- [ ] Avoid unnecessary deep analyses
- [ ] Implement request deduplication

---

## Unexpected Charges

### Common Causes

1. **Automated requests**: Scripts running without limits
2. **Duplicate calls**: Same request sent multiple times
3. **Polling too frequently**: Checking task status too often (though polling is free)
4. **Algorithm comparisons**: Using all 6 algorithms instead of 3-4
5. **Deep analysis abuse**: Running deep analysis on every symbol

### Prevention

1. Implement request throttling
2. Add request deduplication
3. Set maximum daily/monthly limits
4. Monitor API logs
5. Use billing alerts

### If You See Unexpected Charges

1. Check your usage logs at https://www.gprophet.com/dashboard
2. Identify the cause
3. Revoke compromised API keys immediately
4. Contact support@gprophet.com with details
5. Request a review of charges

---

## ROI Calculation

### Example: Trading Strategy

**Setup**:
- Monthly cost: 1,000 points
- Average point cost: $0.01 per point
- Monthly cost: $10

**Results**:
- Trades per month: 20
- Average profit per trade: $50
- Monthly profit: $1,000

**ROI**: ($1,000 - $10) / $10 = 9,900% return

---

## Support & Questions

For cost-related questions:
- Email: billing@gprophet.com
- Dashboard: https://www.gprophet.com/dashboard
- Documentation: https://www.gprophet.com/docs

---

**Last Updated**: 2026-03-04

