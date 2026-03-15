---
name: hkd-currency-converter
description: "实时HKD汇率转换 + 简单历史趋势，香港用户专用，低价实用工具"
---

# 💱 HKD汇率转换神器 v1.1.0

实时查询港币汇率，支持 **USD / CNY / EUR / GBP** 四大货币，可附带 7 天历史趋势分析。  
每次查询扣 **1 token**（1 USDT = 1000 tokens），token 不足时自动返回充值链接。

---

## 📦 安装依赖

```bash
npm install axios
```

---

## 🚀 用法示例

```bash
# 基础转换（单一货币）
node skill.js "1000 HKD to USD"

# 一次看全部常见货币
node skill.js "1000 HKD"

# 指定货币 + 7天历史趋势
node skill.js "500 HKD to CNY 历史"
node skill.js "100 HKD to EUR 7天趋势"

# 模拟 OpenClaw 注入 userId
OPENCLAW_USER_ID=user_abc123 node skill.js "1000 HKD to USD"
```

---

## ⚙️ 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SKILLPAY_API_KEY` | SkillPay 商户 Key（可覆盖硬码） | 见 skill.js 顶部 |
| `OPENCLAW_USER_ID` | 当前用户 ID（OpenClaw 自动注入） | `"anonymous"` |

---

## 🔑 SkillPay 计费说明

- **Endpoint**: `POST https://api.skillpay.me/api/v1/billing/charge`
- **Header**: `X-API-Key: <your_key>`
- **Body**: `{ "userId": "<openclaw_user_id>" }`
- **Billing Model**: Unified Collection，1 call = 1 token（固定扣费，无需传 amount）
- **充值门槛**: 最低约 8 USDT；token 不足时 API 返回 `payment_url`，Skill 直接透传给用户

---

## 🚢 发布命令

```bash
# 进入 Skill 目录后执行
clawhub publish . \
  --slug hkd-currency-converter-waz1xuan \
  --name "HKD汇率转换神器" \
  --description "实时HKD转USD/CNY/EUR + 趋势，香港专用" \
  --tags finance,currency,hongkong,utility \
  --emoji 💱 \
  --price 0.001 \
  --price-currency USDT
```

---

## 📂 目录结构

```
hkd-currency-converter/
├── hkd-currency-converter.md   ← Skill 主文档（本文件）
├── skill.js                    ← Node.js 执行入口
└── package.json
```

**package.json**

```json
{
  "name": "hkd-currency-converter",
  "version": "1.1.0",
  "description": "实时HKD汇率转换 + 历史趋势",
  "main": "skill.js",
  "dependencies": {
    "axios": "^1.6.0"
  }
}
```

---

> 汇率数据：[exchangerate.host](https://api.exchangerate.host)（免费无 Key）  
> 计费托管：[SkillPay.me](https://skillpay.me) · by 王 🤴 (@waz1xuan)
