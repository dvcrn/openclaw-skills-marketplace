---
name: ai-performance-optimizer
description: "Ai Performance Optimizer"
---

# AI Performance Optimizer

Analyzes code for performance bottlenecks and provides suggestions for optimization (e.g., algorithmic improvements, caching, database indexing).

## Features

- **Complexity Analysis**: Estimate time/space complexity
- **Hotspot Identification**: Find inefficient code paths
- **Optimization Strategies**: Get concrete improvement tips

## Pricing

- **Price**: 0.001 USDT per API call
- **Payment**: Integrated via SkillPay.me

## Use Cases

- Latency reduction
- Resource usage optimization
- Code review enhancement

## Example Input

```json
{
  "code": "function find(arr, val) { for(let i=0; i<arr.length; i++) if(arr[i] === val) return i; }",
  "context": "Searching in large sorted arrays."
}
```

## Example Output

```json
{
  "success": true,
  "suggestions": [
    {
      "improvement": "Binary Search",
      "reason": "Since the array is sorted, O(log n) is better than O(n).",
      "example": "..."
    }
  ],
  "message": "Performance analysis completed."
}
```

## Integration

This skill is integrated with SkillPay.me for automatic micropayments. Each call costs 0.001 USDT.
