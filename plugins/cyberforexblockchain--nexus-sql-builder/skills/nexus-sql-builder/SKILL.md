---
name: nexus-sql-builder
description: "Describe your data query in natural language and get optimized, production-ready SQL with proper JOINs, window functions, CTEs, and index recommendations. Supports PostgreSQL, MySQL, SQLite, and SQL S"
---

# NEXUS SQL Architect

> Cardano-native AI service for autonomous agents | NEXUS AaaS Platform

## When to use

Your agent needs to query databases but works with natural language input. Provide a description like 'find top customers by revenue last quarter' and get executable SQL with performance optimization hints. Handles complex multi-table JOINs, aggregations, and subqueries.

## What makes this different

Dialect-aware: generates syntax specific to your database (PostgreSQL arrays, MySQL LIMIT, SQL Server TOP). Includes query execution plan analysis, index creation suggestions, and warns about potential N+1 query patterns. Handles CTEs, window functions, and recursive queries.

## Steps

1. Prepare your input as a JSON payload.
2. POST to the NEXUS API with `X-Payment-Proof` header.
3. Parse the structured JSON response.

### API Call

```bash
curl -X POST https://ai-service-hub-15.emergent.host/api/original-services/sql-builder \
  -H "Content-Type: application/json" \
  -H "X-Payment-Proof: sandbox_test" \
  -d '{"description": "Find top 10 customers by total spend in last 90 days with their most recent order date", "dialect": "postgresql", "tables": "customers, orders, order_items"}'
```

**Endpoint:** `https://ai-service-hub-15.emergent.host/api/original-services/sql-builder`
**Method:** POST
**Headers:**
- `Content-Type: application/json`
- `X-Payment-Proof: <masumi_payment_id>` (use `sandbox_test` for free sandbox)

## External Endpoints

| URL | Method | Data Sent |
|-----|--------|-----------|
| `https://ai-service-hub-15.emergent.host/api/original-services/sql-builder` | POST | Input parameters as JSON body |

## Security & Privacy

All requests encrypted via HTTPS/TLS to `https://ai-service-hub-15.emergent.host`. No data stored permanently — processed in memory and discarded. Payment verification via Masumi Protocol on Cardano (non-custodial escrow). No filesystem or shell permissions required.

## Model Invocation Note

This skill calls the NEXUS AI service API which uses large language models to process requests server-side. You may opt out by not installing this skill.

## Trust Statement

By installing this skill, input data is transmitted to NEXUS (https://ai-service-hub-15.emergent.host) for AI processing. All payments non-custodial via Cardano. Visit https://ai-service-hub-15.emergent.host for documentation and terms.
