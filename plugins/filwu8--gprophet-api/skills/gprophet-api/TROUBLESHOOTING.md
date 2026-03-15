# Troubleshooting Guide

## Common Issues & Solutions

### Authentication Issues

#### "INVALID_API_KEY" or "INVALID_KEY_FORMAT"

**Problem**: API key is rejected or malformed

**Solutions**:
1. Verify key format starts with `gp_sk_`
2. Check for extra spaces or line breaks in the key
3. Ensure the key is correctly set in environment variable:
   ```bash
   echo $GPROPHET_API_KEY  # Should show: gp_sk_...
   ```
4. Generate a new key at https://www.gprophet.com/settings/api-keys

#### "API_KEY_DISABLED" or "API_KEY_EXPIRED"

**Problem**: Your API key has been disabled or expired

**Solutions**:
1. Check your account status at https://www.gprophet.com/dashboard
2. Generate a new API key
3. Update your environment variable with the new key
4. Contact support@gprophet.com if you believe this is an error

#### "INSUFFICIENT_SCOPE"

**Problem**: Your API key lacks permission for this operation

**Solutions**:
1. Check your API key permissions at https://www.gprophet.com/settings/api-keys
2. Create a new key with broader permissions if needed
3. Contact support@gprophet.com for permission upgrades

---

### Billing & Points Issues

#### "INSUFFICIENT_POINTS"

**Problem**: Your account doesn't have enough points for the operation

**Solutions**:
1. Check your point balance at https://www.gprophet.com/dashboard
2. Purchase more points if needed
3. Review recent usage to identify high-cost operations
4. Consider using cheaper operations (e.g., quote instead of deep analysis)

**Cost Reference**:
- Stock prediction: 10-20 points (varies by market)
- Technical analysis: 5 points
- Market data: 5 points
- Deep analysis: 150 points

#### "POINTS_DEDUCTION_FAILED"

**Problem**: System failed to deduct points despite sufficient balance

**Solutions**:
1. Wait a few seconds and retry
2. Check your account status at https://www.gprophet.com/dashboard
3. If issue persists, contact support@gprophet.com

---

### Data & Symbol Issues

#### "SYMBOL_NOT_FOUND"

**Problem**: The stock/crypto ticker is not recognized

**Solutions**:
1. Verify the ticker symbol is correct:
   - US stocks: AAPL, TSLA, GOOGL (uppercase)
   - China A-shares: 6-digit code (600519, 000001)
   - HK stocks: Numeric code (700, 9988)
   - Crypto: Trading pair (BTCUSDT, ETHUSDT)

2. Use the search function to find the correct symbol:
   ```bash
   /gprophet search "apple" US
   ```

3. Check market code is correct:
   - US: US stocks
   - CN: China A-shares
   - HK: Hong Kong stocks
   - CRYPTO: Cryptocurrencies

#### "INVALID_MARKET"

**Problem**: Market code is not recognized

**Solutions**:
1. Use only valid market codes: `US`, `CN`, `HK`, `CRYPTO`
2. Check for typos (case-sensitive)
3. Verify the symbol exists in the specified market

#### "NO_DATA"

**Problem**: Unable to retrieve data for the requested symbol

**Solutions**:
1. Verify the symbol is active and trading
2. Try a different time period (for historical data)
3. Check if the market is open (some markets have trading hours)
4. Try again in a few moments (data may be updating)

---

### Performance & Timeout Issues

#### Prediction Takes Too Long

**Problem**: Stock prediction is slow or times out

**Solutions**:
1. This is normal for complex algorithms (5-30 seconds typical)
2. Try a simpler algorithm:
   ```bash
   /gprophet predict AAPL US 7 --algorithm lstm
   ```
3. Reduce prediction days (1-7 days is faster than 20-30)
4. Check your network connection
5. If consistently timing out, contact support@gprophet.com

#### Deep Analysis Hangs

**Problem**: Deep analysis task never completes

**Solutions**:
1. Deep analysis typically takes 30-120 seconds
2. Ensure you're polling the task status regularly:
   ```bash
   /gprophet task <task_id>  # Poll every 5 seconds
   ```
3. Maximum wait time is 5 minutes; if not completed by then, the task has failed
4. Check the error message for details
5. Try again with a different symbol

---

### Data Quality Issues

#### Prediction Confidence is Very Low

**Problem**: Prediction confidence is below 50%

**Causes**:
- Insufficient historical data
- High market volatility
- Unusual trading patterns
- Illiquid stocks

**Solutions**:
1. Try a longer prediction period (7-14 days instead of 1-3)
2. Use ensemble algorithm for more robust predictions
3. Combine with technical analysis for confirmation
4. Consider the market conditions (earnings, news, etc.)

#### Data Quality Score is Low

**Problem**: Data quality score in prediction response is below 70%

**Causes**:
- Missing historical data
- Data anomalies detected
- Insufficient trading history

**Solutions**:
1. Use a more established stock with longer trading history
2. Try a different time period
3. Check for recent corporate actions (splits, mergers)
4. Contact support if the issue persists

---

### Integration Issues

#### MCP Tool Not Found

**Problem**: MCP tool is not available in your agent

**Solutions**:
1. Verify the skill is installed in your OpenClaw workspace
2. Check the tool name matches exactly (case-sensitive)
3. Restart your agent or IDE
4. Verify your API key is configured

#### Tool Returns Empty Results

**Problem**: Tool executes but returns no data

**Solutions**:
1. Check the `success` field in the response
2. If `success: false`, check the `error.code` for details
3. Verify all required parameters are provided
4. Check your API key has sufficient permissions

---

### Network & Connectivity Issues

#### "Connection Refused" or "Network Timeout"

**Problem**: Cannot connect to G-Prophet API

**Solutions**:
1. Verify your internet connection
2. Check if https://www.gprophet.com is accessible
3. Verify firewall/proxy settings allow HTTPS to www.gprophet.com:443
4. Check G-Prophet status page: https://www.gprophet.com/status
5. Try again in a few moments (may be temporary outage)

#### SSL Certificate Error

**Problem**: "SSL certificate verification failed"

**Solutions**:
1. Verify your system time is correct
2. Update your SSL certificates
3. Do NOT disable SSL verification (security risk)
4. Contact support@gprophet.com if issue persists

---

### Account & Billing Issues

#### Unexpected Point Consumption

**Problem**: Points are being consumed faster than expected

**Solutions**:
1. Review your usage logs at https://www.gprophet.com/dashboard
2. Check for automated or repeated calls
3. Verify no one else has access to your API key
4. If compromised, revoke the key immediately
5. Contact support@gprophet.com to review charges

#### Cannot Access Dashboard

**Problem**: Cannot log in to https://www.gprophet.com/dashboard

**Solutions**:
1. Verify your account credentials
2. Check if your account is active
3. Try resetting your password
4. Clear browser cache and cookies
5. Contact support@gprophet.com

---

## Getting Help

### Before Contacting Support

1. Check this troubleshooting guide
2. Review the error code in the response
3. Verify your API key and permissions
4. Check your account balance and status
5. Review the API documentation at https://www.gprophet.com/docs

### Contact Support

- **Email**: support@gprophet.com
- **Security Issues**: security@gprophet.com
- **Status Page**: https://www.gprophet.com/status
- **Documentation**: https://www.gprophet.com/docs

### Provide This Information

When contacting support, include:
1. Error code and full error message
2. The operation you were attempting
3. Your API key ID (not the full key)
4. Timestamp of the issue
5. Any relevant logs or screenshots

---

## FAQ

### Q: How much does each prediction cost?

**A**: Costs vary by market:
- US stocks: 20 points
- China A-shares: 10 points
- HK stocks: 15 points
- Crypto: 20 points

### Q: Can I use the same API key in multiple places?

**A**: Yes, but we recommend using separate keys for different applications for security and monitoring purposes.

### Q: How often should I rotate my API key?

**A**: We recommend rotating every 90 days, or immediately if you suspect compromise.

### Q: What's the maximum prediction period?

**A**: 30 days. Longer predictions are less accurate.

### Q: Can I get historical predictions?

**A**: No, predictions are generated in real-time based on current data.

### Q: Is there a free tier?

**A**: Check https://www.gprophet.com/pricing for current pricing and trial options.

### Q: Can I use this for automated trading?

**A**: This skill provides predictions for informational purposes. You must implement your own trading logic and risk management.

---

**Last Updated**: 2026-03-04

