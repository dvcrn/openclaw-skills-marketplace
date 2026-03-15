# crypto-sentiment-analyzer

加密情绪分析（¥149/月）

## 分类
Web3/情绪分析

## 价格
¥149/月

## 安装

```bash
clawhub install crypto-sentiment-analyzer
```

## 使用

```bash
crypto-sentiment-analyzer [选项]
```

## 配置

1. 创建配置文件 `~/.openclaw/workspace/config/crypto-sentiment-analyzer.json`
2. 添加 SkillPay API Key:
```json
{
  "skillpay_api_key": "your_api_key_here",
  "price_per_call": 14,
  "sources": ["Twitter", "Reddit", "Telegram"],
  "tracked_assets": ["BTC", "ETH", "SOL"]
}
```

## 功能

- 社交媒体情绪监控
- 情绪指数计算
- 趋势预警
- 情绪与价格关联
- SkillPay 集成

## 许可证
MIT
