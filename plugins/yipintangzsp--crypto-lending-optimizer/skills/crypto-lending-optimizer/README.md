# crypto-lending-optimizer

加密借贷优化（¥149/月）

## 分类
Web3/借贷

## 价格
¥149/月

## 安装

```bash
clawhub install crypto-lending-optimizer
```

## 使用

```bash
crypto-lending-optimizer [选项]
```

## 配置

1. 创建配置文件 `~/.openclaw/workspace/config/crypto-lending-optimizer.json`
2. 添加 SkillPay API Key:
```json
{
  "skillpay_api_key": "your_api_key_here",
  "price_per_call": 14,
  "platforms": ["Aave", "Compound", "Maker", "dYdX"],
  "collateral_ratio": 150
}
```

## 功能

- 借贷利率对比
- 清算风险监控
- 最优借贷策略
- 抵押品管理
- SkillPay 集成

## 许可证
MIT
