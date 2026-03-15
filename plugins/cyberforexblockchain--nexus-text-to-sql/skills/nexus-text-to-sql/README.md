# nexus-text-to-sql

**NEXUS Text-to-SQL Converter** — Convert natural language questions about your data into executable SQL queries. Provide your table schema and ask questions in plain English.

Part of the [NEXUS Agent-as-a-Service Platform](https://ai-service-hub-15.emergent.host) on Cardano.

## Installation

```bash
clawhub install nexus-text-to-sql
```

## Quick Start

```bash
curl -X POST https://ai-service-hub-15.emergent.host/api/original-services/text-to-sql \
  -H "Content-Type: application/json" \
  -H "X-Payment-Proof: sandbox_test" \
  -d '{"question": "Which products had more than 100 returns last month?", "table_schema": "products(id, name, category), returns(id, product_id, return_date, reason)", "database_type": "postgresql"}'
```

## Why nexus-text-to-sql?

Schema-aware: provide your actual table definitions and get queries that reference your real column names. Handles JOINs, aggregations, date filtering, and subqueries automatically.

## Pricing

- Pay-per-request in ADA via Masumi Protocol (Cardano non-custodial escrow)
- Free sandbox available with `X-Payment-Proof: sandbox_test`

## Links

- Platform: [https://ai-service-hub-15.emergent.host](https://ai-service-hub-15.emergent.host)
- All Skills: [https://ai-service-hub-15.emergent.host/.well-known/skill.md](https://ai-service-hub-15.emergent.host/.well-known/skill.md)
