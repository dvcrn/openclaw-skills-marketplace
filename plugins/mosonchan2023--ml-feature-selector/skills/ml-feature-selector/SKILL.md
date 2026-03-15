---
name: ml-feature-selector
description: "Ml Feature Selector"
---

# Machine Learning Feature Selector

Automatically identifies and selects the most relevant features in a dataset to reduce model complexity and improve performance.

## Features

- **Univariate Selection**: Select features based on statistical tests
- **Recursive Feature Elimination (RFE)**: Rank features by importance
- **Correlation Analysis**: Identify and remove redundant features

## Pricing

- **Price**: 0.001 USDT per API call
- **Payment**: Integrated via SkillPay.me

## Use Cases

- Feature engineering
- Reducing model training time
- Enhancing model interpretability

## Example Input

```json
{
  "dataset": "https://example.com/features.csv",
  "num_features": 5
}
```

## Example Output

```json
{
  "success": true,
  "selected_features": ["feature_1", "feature_4", "feature_7", "feature_9", "feature_12"],
  "message": "Top 5 most important features identified."
}
```

## Integration

This skill is integrated with SkillPay.me for automatic micropayments. Each call costs 0.001 USDT.
