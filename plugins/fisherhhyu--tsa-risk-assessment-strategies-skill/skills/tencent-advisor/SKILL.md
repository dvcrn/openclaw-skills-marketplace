---
name: tencent-advisor
description: "腾讯云智能顾问（Cloud Advisor）工具，用于查询评估项列表、查看各产品风险项，并生成可直接跳转到控制台的风险项链接。当用户询问云资源风险、巡检项、智能顾问评估项，或需要查看某产品的风险检查项时使用此 skill。支持：列出所有评估项（按产品/分组筛选）、生成评估项控制台直达链接、安装和使用 tccli 调用智能顾问接口。"
---

# 腾讯云智能顾问（Tencent Cloud Advisor）

## 环境准备

首次使用时检查并安装 tccli：

```bash
pip3 install tccli -q 2>/dev/null || pip install tccli -q
tccli --version
```

配置凭证（从 `.env` 或环境变量读取，避免硬编码）：

```bash
# 读取凭证
source /root/.openclaw/workspace/.env 2>/dev/null
tccli configure set secretId "$TENCENT_SECRET_ID" secretKey "$TENCENT_SECRET_KEY" region ap-guangzhou
```

## 查询评估项列表

```bash
tccli advisor DescribeStrategies --version 2020-07-21 2>/dev/null
```

返回字段说明见 `references/api.md`。

## 筛选与展示

收到返回数据后：

1. **按产品筛选**：用 `Product` 字段匹配（如 `cos`、`cvm`、`mysql`、`redis`）
2. **按分组筛选**：用 `GroupName` 字段匹配（`安全`、`可靠`、`费用`、`性能`、`服务限制`）
3. **按风险等级筛选**：遍历 `Conditions[]`，`Level` 为 3=高危、2=中危、1=低危

## 生成控制台直达链接

对每个评估项，用 `Name` 字段拼接 URL：

```
https://console.cloud.tencent.com/advisor/assess?strategyName={URL编码后的Name}
```

Python 示例：
```python
import urllib.parse
name = "轻量应用服务器（LH）实例到期"
url = f"https://console.cloud.tencent.com/advisor/assess?strategyName={urllib.parse.quote(name)}"
```

## 输出格式

向用户展示时，按以下格式输出每条评估项：

```
🔴 [高危] {Name}
   产品：{ProductDesc}  |  分组：{GroupName}
   描述：{Desc}
   👉 {控制台链接}
```

等级图标：🔴 高危（Level=3）、🟡 中危（Level=2）、🟢 低危（Level=1）

## 典型用法

- "查看 COS 的所有风险项" → 筛选 `Product=cos`，输出带链接的列表
- "有哪些高危的安全风险" → 筛选 `GroupName=安全` + `Level=3`
- "智能顾问有哪些巡检项" → 直接输出全量列表（按 ProductDesc 分组）
- "给我 Redis 的巡检链接" → 筛选 `Product=redis`，每条附上控制台链接

完整脚本见 `scripts/list_strategies.py`。
