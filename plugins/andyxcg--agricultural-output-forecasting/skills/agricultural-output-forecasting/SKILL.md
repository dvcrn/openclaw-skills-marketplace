---
name: agricultural-output-forecasting
description: "Agricultural Product Output Forecasting Based on Big Data. Predicts crop yields and agricultural output using historical data, weather patterns, and market trends. Use when forecasting agricultural production, estimating crop yields, analyzing farming trends, or making data-driven decisions in agriculture."
---

# Agricultural Output Forecasting

> **Version**: 1.0.1  
> **Category**: Agriculture / Analytics  
> **Billing**: SkillPay (1 token per call, ~0.001 USDT)  
> **Free Trial**: 10 free calls per user

A big data-driven agricultural product output forecasting tool that helps farmers, agronomists, and agricultural businesses predict crop yields and production outputs.

## Features

1. **Yield Prediction** - Forecast crop yields based on historical data and current conditions
2. **Weather Impact Analysis** - Factor in weather patterns and climate data
3. **Market Trend Integration** - Consider market prices and demand trends
4. **Multi-Crop Support** - Support for various agricultural products (grains, vegetables, fruits, etc.)
5. **SkillPay Billing** - Pay-per-use monetization (1 token per call, ~0.001 USDT)
6. **Free Trial** - 10 free calls for every new user

## Free Trial

Each user gets **10 free calls** before billing begins. During the trial:
- No payment required
- Full feature access
- Trial status returned in API response

```python
{
    "success": True,
    "trial_mode": True,      # Currently in free trial
    "trial_remaining": 7,    # 7 free calls left
    "balance": None,         # No balance needed in trial
    "forecast": {...}
}
```

After 10 free calls, normal billing applies.

## Quick Start

### Forecast agricultural output:

```python
from scripts.forecast import forecast_output
import os

# Set environment variables (only needed after trial)
os.environ["SKILL_BILLING_API_KEY"] = "your-api-key"
os.environ["SKILL_ID"] = "your-skill-id"

# Forecast wheat yield
result = forecast_output(
    crop_type="wheat",
    area_hectares=100,
    region="North China Plain",
    season="spring",
    user_id="user_123"
)

# Check result
if result["success"]:
    print("预测产量:", result["forecast"])
    if result.get("trial_mode"):
        print(f"免费试用剩余: {result['trial_remaining']} 次")
    else:
        print("剩余余额:", result["balance"])
else:
    print("错误:", result["error"])
    if "paymentUrl" in result:
        print("充值链接:", result["paymentUrl"])
```

### API Usage:

```bash
# Set environment variables (only needed after trial)
export SKILL_BILLING_API_KEY="your-api-key"
export SKILL_ID="your-skill-id"

# Run forecast
python scripts/forecast.py \
  --crop wheat \
  --area 100 \
  --region "North China Plain" \
  --season spring \
  --user-id "user_123"
```

## Environment Variables

This skill requires the following environment variables:

### Required Variables (After Trial)

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `SKILL_BILLING_API_KEY` | Your SkillPay API key for billing | After trial | `skp_abc123...` |
| `SKILL_ID` | Your Skill ID from SkillPay dashboard | After trial | `skill_def456...` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENWEATHER_API_KEY` | OpenWeatherMap API key for weather data | - |
| `WEATHERAPI_KEY` | WeatherAPI key for alternative weather data | - |
| `USDA_API_KEY` | USDA API key for US agricultural data | - |
| `OPENAI_API_KEY` | OpenAI API key for enhanced forecasting | - |
| `CACHE_DURATION_MINUTES` | Cache duration for weather/market data | `60` |
| `MAX_FORECAST_AREA` | Maximum area in hectares per request | `10000` |

See `.env.example` for a complete list of environment variables.

## Configuration

The skill uses SkillPay billing integration:
- Provider: skillpay.me
- Pricing: 1 token per call (~0.001 USDT)
- Chain: BNB Chain
- Free Trial: 10 calls per user
- API Key: Set via `SKILL_BILLING_API_KEY` environment variable
- Skill ID: Set via `SKILL_ID` environment variable
- Minimum deposit: 8 USDT

## Supported Crops

- Grains: wheat, rice, corn, barley, sorghum
- Vegetables: tomato, potato, cabbage, cucumber
- Fruits: apple, orange, grape, peach
- Others: soybean, cotton, sugarcane

## Output Format

Forecast results include:
- Predicted yield (tons/hectare)
- Confidence interval
- Weather impact factor
- Market price prediction
- Risk assessment
- Recommendations

### Response Format

```python
{
    "success": True,
    "trial_mode": False,        # True during free trial
    "trial_remaining": 0,       # Remaining free calls
    "balance": 95.5,            # User balance (None during trial)
    "forecast": {
        "forecast_id": "AGR_20240306120000",
        "crop_type": "wheat",
        "yield_forecast": {...},
        "risk_assessment": {...},
        "recommendations": [...]
    }
}
```

## Security Considerations

### Data Privacy
- Agricultural data is treated as confidential business information
- No personally identifiable information (PII) is collected
- Weather and market data is cached to minimize API calls

### API Key Security
- Never commit API keys to version control
- Use environment variables for all sensitive configuration
- Rotate API keys regularly

## References

- For forecast methodology: see [references/forecast-methodology.md](references/forecast-methodology.md)
- For billing API details: see [references/skillpay-billing.md](references/skillpay-billing.md)
- For full documentation: see [README.md](README.md)
