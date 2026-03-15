---
name: smart-contract-auditor
description: "AI智能合约安全审计，检测重入攻击、整数溢出、权限问题、未检查返回值等常见漏洞。每次调用收费0.001 USDT。触发词：合约审计、contract audit、智能合约安全、代码审计、solidity审计。"
---

# 智能合约审计

每次调用收费 0.001 USDT。收款钱包: 0x64f15739932c144b54ad12eb05a02ea64f755a53

## 功能

- **漏洞检测**: 重入攻击、整数溢出、权限问题
- **代码模式分析**: tx.origin使用、block.timestamp依赖
- **危险函数检测**: selfdestruct、delegatecall
- **安全评分**: 0-100分综合评分
- **修复建议**: 针对性修复方案

## 使用方法

```bash
# 审计合约文件
python scripts/contract_auditor.py contract.sol

# 直接传入代码
python scripts/contract_auditor.py --code "contract code here"
```

## 检测项目

### 高危漏洞
- 🔴 重入攻击风险 (reentrancy)
- 🔴 自毁函数 (selfdestruct)
- 🔴 未检查的外部调用

### 中危漏洞
- 🟡 tx.origin使用
- 🟡 区块时间依赖
- 🟡 未检查返回值

### 低危问题
- ℹ️ 无限授权风险
- ℹ️ 缺少事件日志

## 输出示例

```
🔍 智能合约审计
━━━━━━━━━━━━━━━━
📊 安全评分: 72/100

检测结果:
  🔴 重入攻击风险 (高)
  🟡 tx.origin使用 (中)
  ℹ️ 未检测到明显漏洞 (信息)

💡 建议使用Slither进行深度审计

✅ 已扣费 0.001 USDT
```

## 修复建议

### 重入攻击
```solidity
// 使用ReentrancyGuard
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract SafeContract is ReentrancyGuard {
    function withdraw() external nonReentrant {
        // ...
    }
}
```

### tx.origin问题
```solidity
// 错误
require(tx.origin == owner);

// 正确
require(msg.sender == owner);
```

## 注意事项

- 此工具提供基础静态分析
- 建议结合Slither、Mythril等专业工具
- 大额项目建议找专业审计公司
