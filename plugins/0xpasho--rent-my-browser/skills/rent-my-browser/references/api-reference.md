# Operator API Reference

All endpoints require `Authorization: Bearer <api_key>` unless noted.
Base URL: `https://api.rentmybrowser.dev`

## Registration (no auth)

```
POST /nodes
{ "wallet_address": "0x...", "node_type": "real" | "headless" }
→ 201 { "account_id": "uuid", "node_id": "uuid", "api_key": "rmb_n_..." }
```

## Heartbeat

Send every 25 seconds. Node goes offline after 60s without heartbeat.

```
POST /nodes/:node_id/heartbeat
{
  "type": "headless" | "real",
  "browser": { "name": "chrome", "version": "124.0.6367.91" },
  "geo": { "country": "US", "region": "California", "city": "San Francisco", "ip_type": "residential" | "datacenter" },
  "capabilities": { "modes": ["simple", "adversarial"], "max_concurrent": 1 }
}
→ 200 { "status": "ok" }
```

Only `type` is required. Other fields are optional but recommended.

## Poll Offers

```
GET /nodes/:node_id/offers
→ 200 {
    "offers": [
      {
        "offer_id": "uuid",
        "task_id": "uuid",
        "goal_summary": "first 100 chars of goal text",
        "mode": "simple" | "adversarial",
        "estimated_steps": 5,
        "payout_per_step": 8,
        "expires_at": "2026-01-15T12:00:15Z"
      }
    ]
  }
```

Offers expire after 15 seconds. The `offers` array may be empty.

## Claim Offer

**Important**: `node_id` is required in the request body.

```
POST /offers/:offer_id/claim
{ "node_id": "your-node-uuid" }
→ 200 {
    "task_id": "uuid",
    "goal": "full text goal from consumer",
    "context": {
      "data": { "name": "John", "email": "john@test.com" },
      "tier": "real",
      "mode": "simple",
      "routing": { "geo": "US", "site": "example.com", ... }
    },
    "tier": "real",
    "mode": "simple",
    "max_budget": 300,
    "estimated_steps": 5
  }
→ 409 { "error": "Offer already claimed or expired" }
```

The 200 response includes the **full task payload**. No need to call `GET /tasks/:id` separately.

## Report Step

```
POST /tasks/:task_id/steps
{
  "step": 1,
  "action": "Navigated to example.com/signup",
  "screenshot": "base64-encoded-png..."  // optional
}
→ 200 {
    "step": 1,
    "action": "Navigated to example.com/signup",
    "screenshot_url": "/uploads/task-id/step_1.png",
    "budget_remaining": 260
  }
→ 400 { "error": "Budget cap reached: step N would cost X credits, max is Y" }
```

Stop execution when `budget_remaining` reaches 0 or you get a 400 budget error.

## Submit Result

```
POST /tasks/:task_id/result
{
  "status": "completed" | "failed",
  "extracted_data": { "confirmation_id": "ABC123" },
  "final_url": "https://example.com/success",
  "files": [{ "name": "report.pdf", "url": "..." }]  // optional
}
→ 200 {
    "task_id": "uuid",
    "status": "completed",
    "steps_executed": 4,
    "actual_cost": 40,
    "max_budget": 300,
    "result": { "screenshots": [...], "extracted_data": {...}, ... },
    "duration_ms": 12400
  }
```

## Pricing

| Tier     | Mode        | Per Step | Operator Gets (80%) |
|----------|-------------|----------|---------------------|
| Headless | Simple      | 5 cr     | 4 cr                |
| Real     | Simple      | 10 cr    | 8 cr                |
| Real     | Adversarial | 15 cr    | 12 cr               |

1 credit = $0.01 USD.
