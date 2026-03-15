# Tencent Cloud Advisor Skill

[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue?style=flat-square)](https://openclaw.ai)
[![Tencent Cloud](https://img.shields.io/badge/Tencent%20Cloud-Advisor-green?style=flat-square)](https://console.cloud.tencent.com/advisor)
[![Python](https://img.shields.io/badge/Python-3.8+-yellow?style=flat-square)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-lightgray?style=flat-square)](./LICENSE)

> 腾讯云智能顾问（Cloud Advisor）工具，用于查询评估项列表、查看各产品风险项，并生成可直接跳转到控制台的风险项链接。

## 📋 概述

本 Skill 为 OpenClaw 提供腾讯云智能顾问（Cloud Advisor）集成能力，帮助用户：

- 查询所有云资源评估项
- 按产品（COS、CVM、MySQL、Redis 等）筛选风险项
- 按分组（安全、可靠、费用、性能、服务限制）筛选
- 按风险等级（高危/中危/低危）筛选
- 生成控制台直达链接，一键跳转查看详情

## 🏷️ 适用场景

- 云资源巡检自动化
- 安全风险排查
- 成本优化建议获取
- 性能瓶颈分析
- 合规性检查

## ⚡ 快速开始

### 环境准备

1. 安装 tccli：

```bash
pip3 install tccli -q
# 或
pip install tccli -q
```

2. 配置凭证：

```bash
# 方式一：环境变量
export TENCENT_SECRET_ID="your_secret_id"
export TENCENT_SECRET_KEY="your_secret_key"

# 方式二：读取 .env 文件（OpenClaw 自动加载）
# 凭证将自动从 /root/.openclaw/workspace/.env 读取
```

3. 验证安装：

```bash
tccli --version
```

### 基本用法

#### 命令行直接查询

```bash
# 列出所有评估项
python3 scripts/list_strategies.py

# 按产品筛选（如 COS）
python3 scripts/list_strategies.py --product cos

# 按分组筛选（如 安全）
python3 scripts/list_strategies.py --group 安全

# 按风险等级筛选（3=高危）
python3 list_strategies.py --level 3

# 组合筛选：COS + 高危
python3 list_strategies.py --product cos --level 3
```

#### OpenClaw 对话中使用

| 用户意图 | 触发指令 |
|---------|---------|
| 查看 COS 风险项 | `查看 COS 的所有风险项` |
| 安全高危项 | `有哪些高危的安全风险` |
| 巡检项列表 | `智能顾问有哪些巡检项` |
| 生成巡检链接 | `给我 Redis 的巡检链接` |

## 📖 详细功能

### 1. 查询评估项列表

```bash
tccli advisor DescribeStrategies --version 2020-07-21
```

返回字段说明：

| 字段 | 说明 |
|------|------|
| `StrategyId` | 评估项 ID |
| `Name` | 评估项名称 |
| `Desc` | 评估项描述 |
| `Product` | 产品标识（如 cos、cvm） |
| `ProductDesc` | 产品中文描述 |
| `GroupName` | 分组名称（安全/可靠/费用/性能/服务限制） |
| `Conditions` | 风险条件数组，含 `Level`（1=低危, 2=中危, 3=高危） |

### 2. 筛选规则

- **按产品筛选**：`Product` 字段精确匹配
- **按分组筛选**：`GroupName` 字段包含匹配
- **按风险等级筛选**：遍历 `Conditions[]`，匹配 `Level` 值

### 3. 生成控制台链接

每个评估项可生成控制台直达链接：

```
https://console.cloud.tencent.com/advisor/assess?strategyName={URL编码后的Name}
```

Python 示例：

```python
import urllib.parse
name = "轻量应用服务器（LH）实例到期"
url = f"https://console.cloud.tencent.com/advisor/assess?strategyName={urllib.parse.quote(name)}"
```

## 📊 输出格式

向用户展示时，按以下格式输出：

```
🔴 [高危] {评估项名称}
   产品：{产品描述}  |  分组：{分组名称}
   描述：{评估项描述}
   👉 {控制台链接}
```

等级图标：
- 🔴 高危（Level=3）
- 🟡 中危（Level=2）
- 🟢 低危（Level=1）

## 📁 项目结构

```
tencent-advisor/
├── SKILL.md                 # Skill 定义文件
├── README.md                # 本文件
├── scripts/
│   └── list_strategies.py  # 主查询脚本
└── references/
    └── api.md              # API 字段参考
```

## 🔧 配置说明

### 凭证优先级

1. 环境变量 `TENCENT_SECRET_ID` / `TENCENT_SECRET_KEY`
2. 环境变量 `SECRETID` / `SECRETKEY`
3. `.env` 文件（OpenClaw workspace 目录）

### 地区配置

默认地区：`ap-guangzhou`（广州）

如需修改，编辑 `scripts/list_strategies.py` 中的 `configure_tccli` 函数：

```python
subprocess.run([
    "tccli", "configure", "set",
    "secretId", secret_id,
    "secretKey", secret_key,
    "region", "ap-shanghai"  # 改为其他地区
], capture_output=True)
```

## ⚠️ 注意事项

1. **权限要求**：需要腾讯云账号具备 `advisor:DescribeStrategies` 权限
2. **API 限制**：智能顾问 API 有调用频率限制，建议批量查询后缓存结果
3. **链接有效期**：控制台链接基于评估项名称生成，如有重名请使用 StrategyId

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License - see [LICENSE](./LICENSE) for details

## 🔗 相关链接

- [腾讯云智能顾问文档](https://cloud.tencent.com/document/product/1272)
- [tccli 安装指南](https://cloud.tencent.com/document/product/440/34011)
- [OpenClaw 文档](https://docs.openclaw.ai)
