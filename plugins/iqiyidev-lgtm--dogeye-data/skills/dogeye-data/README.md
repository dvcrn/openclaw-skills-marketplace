# DogEye Skill

实时加密货币市场数据查询

## 安装

```bash
# 克隆到 skills 目录
git clone https://github.com/phpspy/dogeye-skill.git ~/.openclaw/skills/dogeye

# 或者本地安装
cd dogeye_skill
pip install -e .
```

## 配置

```bash
export DOGEYE_USER_ID="your_unique_id"
```

## 使用

```bash
# 大单交易
dogeye block-trades BTC
dogeye block-trades ETH

# 资金流
dogeye fund-flow BTC --period 1D
dogeye fund-flow ETH --period 1H

# 多空比
dogeye long-short BTC

# 资金费率
dogeye funding BTC

# 恐惧贪婪指数
dogeye fear-greed

# RSI 热力图
dogeye rsi-heatmap --coins BTC,ETH,SOL --timeframe 1H

# 市场深度
dogeye market-depth BTC

# 灰度持仓
dogeye grayscale BTC

# ETF 数据
dogeye etf btc

# 查询配额
dogeye quota
```

## API

数据来自 https://api.leilei.uk

## 计费

- 每日免费 100 次调用
- 超出后按调用次数扣费

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