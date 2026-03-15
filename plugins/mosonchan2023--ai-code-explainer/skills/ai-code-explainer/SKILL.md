---
name: ai-code-explainer
description: "AI-powered code explainer that explains any code in plain English. Each call charges 0.001 USDT via SkillPay."
homepage: https://github.com/moson/ai-code-explainer
---

# AI Code Explainer

## 功能

AI-powered code explanation tool that helps developers understand any code snippet in plain English.

### 核心功能

- **Plain English Explanation**: Understand code without reading line by line
- **Function Flow Analysis**: Trace how data flows through functions
- **Algorithm Explanation**: Understand complex algorithms
- **Documentation Generation**: Auto-generate code comments
- **Time Complexity Analysis**: Know the performance implications
- **Dependency Analysis**: Understand external dependencies

## 支持的语言

- JavaScript / TypeScript
- Python
- Java
- Go
- Rust
- C/C++
- Ruby
- PHP
- SQL
- HTML/CSS

## 使用方法

```json
{
  "action": "explain",
  "code": "function fibonacci(n) { return n <= 1 ? n : fibonacci(n-1) + fibonacci(n-2); }",
  "language": "javascript",
  "detail_level": "detailed"
}
```

## 输出示例

```json
{
  "success": true,
  "explanation": "This is a recursive function that calculates the nth Fibonacci number...",
  "complexity": "O(2^n) - exponential time complexity",
  "use_cases": ["Mathematical calculations", "Interview preparation"],
  "alternatives": "Consider using memoization for better performance"
}
```

## 价格

每次调用: 0.001 USDT

## 常见问题

**Q: 能解释多长的代码？**
A: 建议每次不超过 500 行代码 for best results.

**Q: 支持注释生成吗？**
A: 是的，设置 detail_level 为 "with-comments" 获取带注释的代码。

**Q: 能分析算法复杂度吗？**
A: 是的，会自动分析时间复杂度和空间复杂度。
