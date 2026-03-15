---
name: nexus-text-to-sql
description: "Schema-aware natural language database querying. Provide your CREATE TABLE definitions, ask questions in English, get executable SQL with JOINs, aggregations, and performance annotations."
---

# NEXUS Schema-Aware SQL Generator

> Turn data questions into executable queries using your actual table definitions

## The Problem This Solves

Agents working with databases need to construct SQL queries dynamically. Generic LLM prompting produces SQL with hallucinated column names. This service takes your real schema as input and generates queries that reference your actual tables and columns.

## When to use

Your agent has access to a database schema and receives natural language questions from users or other agents. Instead of maintaining a library of pre-written queries, feed the question and schema to this service and get back executable, optimized SQL.

## How it works

1. Agent provides table definitions (CREATE TABLE statements or simplified column lists)
2. Agent provides the natural language question
3. Service returns: executable SQL + English explanation + performance notes

### Three-input API call

```bash
curl -X POST https://ai-service-hub-15.emergent.host/api/original-services/text-to-sql \
  -H "Content-Type: application/json" \
  -H "X-Payment-Proof: sandbox_test" \
  -d '{
    "question": "Which products had more than 100 returns last month?",
    "table_schema": "products(id, name, category, price), returns(id, product_id, return_date, reason, refund_amount)",
    "database_type": "postgresql"
  }'
```

## What you get back

```json
{
  "sql": "SELECT p.name, p.category, COUNT(r.id) as return_count ...",
  "explanation": "Joins products with returns, filters by last 30 days, groups by product, filters groups with HAVING > 100",
  "performance_notes": "Consider index on returns(product_id, return_date)"
}
```

## External Endpoints

| URL | Method |
|-----|--------|
| `https://ai-service-hub-15.emergent.host/api/original-services/text-to-sql` | POST |

## Security & Privacy

Table schemas and questions are encrypted via HTTPS/TLS. No data is stored — processed in memory and discarded immediately. Your actual database is never accessed; only the schema definition and question are processed. Payment via Masumi Protocol on Cardano.

## Model Invocation Note

Uses server-side LLM processing to parse schemas and generate SQL. Opt out by not installing.

## Trust Statement

Schema definitions are transmitted to NEXUS for query generation. No database connections are made. All payments non-custodial via Cardano. Visit https://ai-service-hub-15.emergent.host for terms.
