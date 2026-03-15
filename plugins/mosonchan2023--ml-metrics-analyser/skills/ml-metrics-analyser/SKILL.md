---
name: ml-metrics-analyser
description: "Ml Metrics Analyser"
---

# Machine Learning Metrics Analyser

Calculates and analyzes common performance metrics for machine learning models, helping you evaluate model quality and generalization.

## Features

- **Classification Metrics**: Accuracy, Precision, Recall, F1-Score
- **Regression Metrics**: RMSE, MAE, R-Squared
- **Confusion Matrix**: Visualize model performance on individual classes

## Pricing

- **Price**: 0.001 USDT per API call
- **Payment**: Integrated via SkillPay.me

## Use Cases

- Evaluating model performance
- Comparing different algorithms
- Monitoring model drift

## Example Input

```json
{
  "y_true": [1, 0, 1, 1],
  "y_pred": [1, 0, 0, 1]
}
```

## Example Output

```json
{
  "success": true,
  "accuracy": 0.75,
  "f1_score": 0.8,
  "message": "Performance metrics calculated successfully."
}
```

## Integration

This skill is integrated with SkillPay.me for automatic micropayments. Each call costs 0.001 USDT.
