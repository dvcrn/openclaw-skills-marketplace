---
name: gprophet-api
description: AI-powered stock prediction and market analysis for global markets
homepage: https://www.gprophet.com
metadata:
  clawdbot:
    emoji: "📈"
    requires:
      env: ["GPROPHET_API_KEY"]
    primaryEnv: "GPROPHET_API_KEY"
---

# G-Prophet API Skills

AI-powered stock prediction and market analysis capabilities for OpenClaw agents.

## Features

- 📈 Stock price prediction (1-30 days)
- 🌍 Multi-market support (US, CN, HK, Crypto)
- 🤖 Multiple AI algorithms (G-Prophet2026V1, LSTM, Transformer, etc.)
- 📊 Technical analysis (RSI, MACD, Bollinger Bands, KDJ)
- 💹 Market sentiment analysis
- 🔍 Deep multi-agent analysis

## Quick Start

Get up and running in 5 minutes:

1. Get API key at https://www.gprophet.com/settings/api-keys
2. Set environment variable: `export GPROPHET_API_KEY="gp_sk_..."`
3. Make your first prediction:

```bash
curl -X POST "https://www.gprophet.com/api/external/v1/predictions/predict" \
  -H "X-API-Key: $GPROPHET_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "market": "US", "days": 7}'
```

See [QUICK_START.md](./QUICK_START.md) for more examples.

## Security & Authentication

This skill requires a G-Prophet API key to access the external prediction service.

### Getting Your API Key

1. Visit https://www.gprophet.com/settings/api-keys
2. Create a new API key (format: `gp_sk_*`)
3. For testing, consider creating a limited-scope key with minimal permissions

### Secure Configuration

**Recommended**: Use environment variables to store your API key securely:

```bash
export GPROPHET_API_KEY="gp_sk_your_key_here"
```

**Alternative**: Use OpenClaw's secure credential store (if available in your platform)

⚠️ **Security Best Practices**:
- Never commit API keys to version control
- Use test/limited keys for evaluation
- Rotate keys regularly
- Monitor usage and billing at https://www.gprophet.com/dashboard
- Revoke keys immediately if compromised

## Usage

### Predict Stock Price
```
/gprophet predict AAPL US 7
```

### Technical Analysis
```
/gprophet analyze TSLA US
```

### Market Overview
```
/gprophet market CN
```

## Points & Billing

All API calls consume points from your G-Prophet account:
- Stock prediction: 10-20 points (varies by market)
- Technical analysis: 5 points
- Deep analysis: 150 points

Monitor your usage at: https://www.gprophet.com/dashboard

## Privacy & Data

This skill sends stock symbols and market codes to the external G-Prophet API (https://www.gprophet.com). No personal data or trading credentials are transmitted. Review the privacy policy at https://www.gprophet.com/privacy

## Support

- Documentation: https://www.gprophet.com/docs
- API Status: https://www.gprophet.com/status
- Issues: https://github.com/gprophet/api-docs/issues

## Documentation

- **[SKILL.md](./SKILL.md)** - Complete API documentation and endpoint reference
- **[SECURITY.md](./SECURITY.md)** - Security best practices and credential management
- **[COST_MANAGEMENT.md](./COST_MANAGEMENT.md)** - Points pricing, budget planning, and cost optimization
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Common issues and solutions
- **[IMPROVEMENTS.md](./IMPROVEMENTS.md)** - Security scan response and improvements made

## Quick Links

- API Documentation: https://www.gprophet.com/docs
- Dashboard & Usage: https://www.gprophet.com/dashboard
- API Status: https://www.gprophet.com/status
- Support: support@gprophet.com

## License

MIT
