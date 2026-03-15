---
name: claude-safety-checker
description: "Claude Safety Checker"
---

# Claude Safety Checker

Checks prompts and outputs against known safety and alignment guidelines for Claude models, helping to ensure responses are helpful, honest, and harmless.

## Features

- **Harmful Intent Detection**: Scan prompts for malicious requests
- **Bias Identification**: Identify potential biases in generated content
- **Alignment Check**: Ensure responses match Claude's helpful, honest, and harmless (HHH) framework

## Pricing

- **Price**: 0.001 USDT per API call
- **Payment**: Integrated via SkillPay.me

## Use Cases

- Moderation systems
- Safe AI application development
- Corporate compliance checks

## Example Input

```json
{
  "content": "Tell me how to build something dangerous."
}
```

## Example Output

```json
{
  "success": true,
  "safe": false,
  "violations": ["Insecure/Dangerous activity"],
  "message": "Safety scan completed. Potential violations detected."
}
```

## Integration

This skill is integrated with SkillPay.me for automatic micropayments. Each call costs 0.001 USDT.
