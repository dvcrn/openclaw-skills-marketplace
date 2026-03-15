# GAQL (Google Ads Query Language) Examples

## Common Query Patterns

### Campaign Performance (Last 30 Days)
```sql
SELECT
    campaign.id,
    campaign.name,
    campaign.status,
    metrics.impressions,
    metrics.clicks,
    metrics.cost_micros,
    metrics.conversions,
    metrics.conversions_value
FROM campaign
WHERE segments.date DURING LAST_30_DAYS
```

### Ad Group Performance
```sql
SELECT
    ad_group.id,
    ad_group.name,
    ad_group.status,
    campaign.name,
    metrics.impressions,
    metrics.clicks,
    metrics.cost_micros,
    metrics.ctr,
    metrics.average_cpc
FROM ad_group
WHERE segments.date DURING LAST_30_DAYS
```

### Keyword Performance
```sql
SELECT
    ad_group_criterion.criterion_id,
    ad_group_criterion.keyword.text,
    ad_group_criterion.keyword.match_type,
    metrics.impressions,
    metrics.clicks,
    metrics.cost_micros,
    metrics.conversions,
    metrics.quality_score
FROM keyword_view
WHERE segments.date DURING LAST_30_DAYS
```

### Search Terms Report
```sql
SELECT
    search_term_view.search_term,
    search_term_view.status,
    campaign.name,
    metrics.impressions,
    metrics.clicks,
    metrics.cost_micros,
    metrics.conversions
FROM search_term_view
WHERE segments.date DURING LAST_30_DAYS
```

### Geographic Performance
```sql
SELECT
    geographic_view.country_criterion_id,
    geographic_view.location_name,
    metrics.impressions,
    metrics.clicks,
    metrics.cost_micros,
    metrics.conversions
FROM geographic_view
WHERE segments.date DURING LAST_30_DAYS
```

### Device Performance
```sql
SELECT
    segments.device,
    metrics.impressions,
    metrics.clicks,
    metrics.cost_micros,
    metrics.conversions,
    metrics.conversions_value
FROM campaign
WHERE segments.date DURING LAST_30_DAYS
```

### Daily Performance Trend
```sql
SELECT
    segments.date,
    metrics.impressions,
    metrics.clicks,
    metrics.cost_micros,
    metrics.conversions
FROM campaign
WHERE segments.date DURING LAST_30_DAYS
ORDER BY segments.date DESC
```

### Account Budget Information
```sql
SELECT
    customer.id,
    customer.descriptive_name,
    customer.status,
    customer.currency_code,
    customer.time_zone
FROM customer
```

## Date Ranges

- `TODAY`
- `YESTERDAY`
- `LAST_7_DAYS`
- `LAST_30_DAYS`
- `LAST_MONTH`
- `THIS_MONTH`
- `CUSTOM_DATE_RANGE` (requires start_date and end_date)

## Status Filters

```sql
WHERE campaign.status = 'ENABLED'
WHERE campaign.status IN ('ENABLED', 'PAUSED')
WHERE ad_group.status != 'REMOVED'
```

## Cost Calculations

Cost is returned in micros (1/1,000,000 of the currency unit):
- Divide by 1,000,000 to get actual currency amount
- Example: 5000000 micros = $5.00 USD

## Common Metrics

- `metrics.impressions` - Number of times ads were shown
- `metrics.clicks` - Number of clicks on ads
- `metrics.cost_micros` - Total cost in micros
- `metrics.conversions` - Number of conversions
- `metrics.conversions_value` - Total conversion value
- `metrics.ctr` - Click-through rate
- `metrics.average_cpc` - Average cost per click
- `metrics.quality_score` - Quality score (for keywords)
