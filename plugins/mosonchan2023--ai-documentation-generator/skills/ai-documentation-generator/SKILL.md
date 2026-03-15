---
name: ai-documentation-generator
description: "Ai Documentation Generator"
---

# AI Documentation Generator

Automatically generates high-quality documentation (Markdown, JSDoc, etc.) from source code, including function descriptions, parameter details, and examples.

## Features

- **Multi-format Output**: Generate Markdown, HTML, or JSDoc
- **Context-Aware**: Understands function logic for better descriptions
- **Example Generation**: Creates usage examples automatically

## Pricing

- **Price**: 0.001 USDT per API call
- **Payment**: Integrated via SkillPay.me

## Use Cases

- API documentation
- Developer portals
- Code maintenance

## Example Input

```json
{
  "code": "async function chargeUser(userId, amount) { ... }",
  "format": "markdown"
}
```

## Example Output

```json
{
  "success": true,
  "documentation": "### chargeUser\n\nCharges a user a specific amount.\n\n**Parameters:**\n- `userId`: The unique ID of the user.\n- `amount`: The amount to charge.",
  "message": "Documentation generated successfully."
}
```

## Integration

This skill is integrated with SkillPay.me for automatic micropayments. Each call costs 0.001 USDT.
