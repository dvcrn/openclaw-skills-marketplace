---
name: token-contract-scanner
description: "Token Contract Scanner"
---

# 代币合约检测器 - 合约风险分析

## 概述
专注于智能合约代码层面的安全检测，识别 honeypot、rug pull 等常见骗局特征。

## 定价
- **按次收费：** ¥9/次
- **包月订阅：** ¥199/月（无限次）

## 功能特性
- 🐯 Honeypot 检测
- 🔓 权限分析
- 💸 交易税费检查
- 🚫 黑名单/白名单检测
- ⚠️ 风险等级评估

## 使用方式
```bash
# 基础检测
/contract-scan "合约地址"

# 深度分析
/contract-scan "0x..." --deep

# 特定链
/contract-scan "0x..." --chain BSC
/contract-scan "0x..." --chain ETH
/contract-scan "0x..." --chain SOL

# 批量扫描
/contract-scan "地址列表" --batch
```

## 输出格式
```markdown
## 🕵️ 代币合约检测报告

### 🚨 风险等级：高风险

### 📋 合约信息
- 地址：0x1234...5678
- 链：BSC
- 创建时间：2026-03-01
- 是否开源：是

### ⚠️ 风险项
- [🚨] 发现 honeypot 特征
- [⚠️] 所有者可修改交易税
- [⚠️] 可暂停交易
- [⚠️] 有黑名单功能

### ✅ 安全项
- [✓] 代码已开源
- [✓] LP 已燃烧

### 💡 结论
**不建议投资** - 发现多个高风险特征

### 🔍 详细分析
- 买入税：5%
- 卖出税：99% ⚠️
- 最大交易：无限制
- 所有者权限：过高
```

## 技术实现
- 合约代码反编译
- 字节码分析
- 常见漏洞模式匹配
- 多链支持
