---
name: claude-prompt-optimizer
description: "Claude Prompt Optimizer"
---

# Claude Prompt Optimizer

Optimizes your prompts specifically for Claude's constitutional AI and reinforcement learning from human feedback (RLHF) patterns, ensuring clearer instructions and more accurate responses.

## Features

- **Prompt Rewriting**: Refine prompts for clarity and specificity
- **Context Optimization**: Structure context more effectively for Claude's long context window
- **Few-Shot Examples**: Suggest relevant examples to guide Claude's behavior

## Pricing

- **Price**: 0.001 USDT per API call
- **Payment**: Integrated via SkillPay.me

## Use Cases

- Improving model accuracy
- Reducing hallucinations
- Structured output generation

## Example Input

```json
{
  "prompt": "Tell me about cars.",
  "goal": "Explain how an internal combustion engine works."
}
```

## Example Output

```json
{
  "success": true,
  "optimized_prompt": "Please explain the fundamental working principles of an internal combustion engine, including the four-stroke cycle and the roles of the intake, compression, power, and exhaust strokes.",
  "message": "Prompt optimized for Claude."
}
```

## Integration

This skill is integrated with SkillPay.me for automatic micropayments. Each call costs 0.001 USDT.
