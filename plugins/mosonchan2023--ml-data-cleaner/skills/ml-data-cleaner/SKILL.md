---
name: ml-data-cleaner
description: "Ml Data Cleaner"
---

# Machine Learning Data Cleaner

Cleans and preprocesses datasets to prepare them for machine learning, including handling missing values, scaling features, and encoding categorical variables.

## Features

- **Missing Value Imputation**: Automatically fill in or remove missing data
- **Feature Scaling**: Normalize or standardize numeric features
- **Category Encoding**: Convert text categories to numeric representations

## Pricing

- **Price**: 0.001 USDT per API call
- **Payment**: Integrated via SkillPay.me

## Use Cases

- Preparing raw data for ML models
- Automating ETL pipelines
- Improving model performance through cleaner data

## Example Input

```json
{
  "data": [{"age": 25, "city": "NY"}, {"age": null, "city": "SF"}],
  "impute_strategy": "mean"
}
```

## Example Output

```json
{
  "success": true,
  "cleaned_data": [{"age": 25, "city": "NY"}, {"age": 25, "city": "SF"}],
  "message": "Data cleaning and preprocessing complete."
}
```

## Integration

This skill is integrated with SkillPay.me for automatic micropayments. Each call costs 0.001 USDT.
