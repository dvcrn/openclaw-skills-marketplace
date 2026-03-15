# crypto-portfolio-optimizer

加密货币投资组合优化（¥99/月）

## 分类
加密货币/投资管理

## 价格
¥99/月

## 安装

```bash
clawhub install crypto-portfolio-optimizer
```

## 使用

```bash
crypto-portfolio-optimizer [选项]
```

## 配置

1. 创建配置文件 `~/.openclaw/workspace/config/crypto-portfolio-optimizer.json`
2. 添加 SkillPay API Key 和钱包地址:
```json
{
  "skillpay_api_key": "your_api_key_here",
  "price_per_call": 99,
  "wallet_addresses": ["0x..."],
  "chains": ["ethereum", "bsc", "polygon"]
}
```

## 功能

- 多链资产自动追踪
- 投资组合风险分析
- 收益优化建议
- 自动再平衡策略
- 历史收益报告
- SkillPay 集成收费

## 许可证
MIT
