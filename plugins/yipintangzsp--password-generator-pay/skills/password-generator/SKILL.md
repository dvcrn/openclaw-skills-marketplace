---
name: password-generator
description: "安全密码生成器，支持自定义长度和符号，生成高强度随机密码。"
---

# Password Generator - 密码生成器

生成高强度随机密码，支持自定义长度和符号。

## 使用方式

```bash
# 生成 16 位密码（包含符号）
password-generator 16 --symbols

# 生成 12 位密码（仅字母数字）
password-generator 12

# 查看帮助
password-generator --help
```

## 功能特点

- 🔐 高强度随机密码
- 📏 自定义长度（8-64 位）
- 🔣 可选符号（!@#$%^&*）
- ⚡ 即时生成
- 💰 SkillPay 收费集成（¥0.5/次）

## 示例输出

```
密码：X7#kL9$mN2@pQ5!v
强度：⭐⭐⭐ 强
字符集：字母 + 数字 + 符号
```

## 配置

在 `~/.openclaw/workspace/config/password-generator.json` 配置 SkillPay API Key。
