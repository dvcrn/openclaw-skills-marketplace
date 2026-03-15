---
name: ai-refactoring-assistant
description: "AI-powered refactoring assistant - get code improvement suggestions, refactoring patterns, and best practices. Each call charges 0.001 USDT via SkillPay."
homepage: https://github.com/moson/ai-refactoring-assistant
---

# AI Refactoring Assistant

## 功能

AI-powered refactoring assistant that helps developers improve code quality through intelligent suggestions and refactoring patterns.

### 核心功能

- **Code Improvement Suggestions**: Get specific suggestions to improve your code
- **Refactoring Patterns**: Apply proven refactoring patterns
- **Design Patterns**: Recommend appropriate design patterns
- **Code Smell Detection**: Identify code smells and anti-patterns
- **Complexity Reduction**: Simplify complex code logic
- **Best Practices**: Apply language-specific best practices

## 使用方法

```json
{
  "action": "refactor",
  "code": "function processUserData(users) { ... }",
  "language": "javascript",
  "focus": "readability"
}
```

## 输出示例

```json
{
  "success": true,
  "suggestions": [
    {
      "type": "extract-function",
      "original": "processUserData",
      "reason": "Function does too many things",
      "refactored": "validateUser + transformUser + saveUser"
    }
  ],
  "complexity": "reduced from O(n^2) to O(n)"
}
```

## 价格

每次调用: 0.001 USDT

## 常见问题

**Q: 支持哪些语言？**
A: JavaScript, Python, Java, Go, Rust, C++ 等主流语言。

**Q: 重构是自动执行吗？**
A: 提供建议，你需要手动应用或确认自动应用。

**Q: 重构后代码会破坏原有功能吗？**
A: 建议都是等价变换，不会改变代码行为。
