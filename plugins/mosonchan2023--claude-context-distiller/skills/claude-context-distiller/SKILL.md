---
name: claude-context-distiller
description: "Claude Context Distiller"
---

# Claude Context Distiller

Distills large volumes of text into the most essential information, maximizing the value of Claude's context window while minimizing noise.

## Features

- **Text Distillation**: Extract key concepts and facts
- **Redundancy Removal**: Eliminate repetitive information
- **Structure Transformation**: Convert raw text into concise, Claude-friendly formats (e.g., Markdown, XML)

## Pricing

- **Price**: 0.001 USDT per API call
- **Payment**: Integrated via SkillPay.me

## Use Cases

- Summarizing large documents
- Preparing data for long-context queries
- Cleaning up noisy datasets

## Example Input

```json
{
  "text": "Extremely long document text...",
  "focus": "technical architecture"
}
```

## Example Output

```json
{
  "success": true,
  "distilled_text": "Key architecture details: ...",
  "compression_ratio": "75%",
  "message": "Context distilled successfully."
}
```

## Integration

This skill is integrated with SkillPay.me for automatic micropayments. Each call costs 0.001 USDT.
