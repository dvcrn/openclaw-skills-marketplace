---
name: claude-token-counter
description: "Claude Token Counter"
---

# Claude Token Counter

Accurately estimates the number of tokens in a given text based on Claude's tokenizer (approximate, as Claude's actual tokenizer is proprietary).

## Features

- **Token Estimation**: Get a close approximation of token usage
- **Pricing Calculator**: Estimate API costs based on current Claude pricing
- **Chunking Advice**: Get suggestions on how to split text if it exceeds context limits

## Pricing

- **Price**: 0.001 USDT per API call
- **Payment**: Integrated via SkillPay.me

## Use Cases

- Budget management
- Context window management
- API call optimization

## Example Input

```json
{
  "text": "Hello, how are you today?",
  "model": "claude-3-5-sonnet-20241022"
}
```

## Example Output

```json
{
  "success": true,
  "estimated_tokens": 7,
  "estimated_cost": 0.000021,
  "message": "Token estimation completed."
}
```

## Integration

This skill is integrated with SkillPay.me for automatic micropayments. Each call costs 0.001 USDT.
