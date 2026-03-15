---
name: dogeye-data
description: "DogEye Data"
---

# DogEye Data Skill

实时加密货币市场数据查询 Skill v1.2.0

## 功能

查询多维度市场数据：
- 大单交易流向
- 大单逐笔明细
- 资金流分析
- 清算地图
- 持仓量
- 多空比
- 资金费率
- 大单墙
- RSI 热力图
- 市场深度 (多交易所聚合)
- 灰度持仓
- ETF 数据
- 恐惧贪婪指数

## 安装

```bash
openclaw skills install dogeye-data
```

## 配置

可选：设置默认用户ID（用于计费）
```bash
export DOGEYE_USER_ID="your_user_id"
```

## 使用

### 查询大单交易
```bash
/dogeye block-trades BTC
```

### 查询大单逐笔明细
```bash
/dogeye block-trades-list BTC --market contra
```

### 查询资金流
```bash
/dogeye fund-flow ETH --period 1D
```

### 查询清算地图
```bash
/dogeye liq-map BTC --exchange Binance
```

### 查询持仓量
```bash
/dogeye oi BTC
```

### 查询多空比
```bash
/dogeye long-short BTC
```

### 查询资金费率
```bash
/dogeye funding BTC
```

### 查询大单墙
```bash
/dogeye order-walls BTC
```

### 查询 RSI 热力图
```bash
/dogeye rsi-heatmap --coins BTC,ETH,SOL --timeframe 1H
```

### 查询市场深度
```bash
/dogeye market-depth BTC
```

### 查询灰度持仓
```bash
/dogeye grayscale BTC
```

### 查询 ETF 数据
```bash
/dogeye etf btc
```

### 查询恐惧贪婪指数
```bash
/dogeye fear-greed
```

### 查询配额
```bash
/dogeye quota
```

## 计费

- 每日免费额度：100 次调用
- 超出后调用 SkillPay 真实扣费

## 价格

| 数据类型 | 单价 |
|---------|------|
| 大单交易 | 0.002 USDT |
| 大单逐笔 | 0.002 USDT |
| 资金流 | 0.001 USDT |
| 清算图 | 0.002 USDT |
| 持仓量 | 0.001 USDT |
| 资金费率 | 0.001 USDT |
| 多空比 | 0.001 USDT |
| 大单墙 | 0.001 USDT |
| RSI 热力图 | 0.001 USDT |
| 市场深度 | 0.001 USDT |
| 灰度持仓 | 0.001 USDT |
| ETF 数据 | 0.001 USDT |
| 恐惧贪婪 | 0.0005 USDT |
