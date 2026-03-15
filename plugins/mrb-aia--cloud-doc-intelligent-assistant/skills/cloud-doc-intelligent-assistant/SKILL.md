---
name: cloud-doc-intelligent-assistant
description: "智能文档助手技能库，支持抓取阿里云、腾讯云、百度云、火山引擎的产品文档，进行变更检测、跨云对比分析、AI 摘要生成和定时巡检推送。当用户提到抓取云厂商文档、检查文档更新、对比不同云的产品、生成变更报告或运行文档巡检时，应触发此 skill。"
homepage: https://github.com/anthonybinaruth-dotcom/cloud-doc-skill
---

# 智能文档助手 Skill

多云文档监控与智能分析技能库，通过命令行脚本调用。

## 安装

```bash
# 方式一：从 whl 包安装（推荐分发）
pip install cloud_doc_monitor-0.3.0-py3-none-any.whl

# 方式二：从源码安装
pip install .

# 方式三：开发模式（本地调试）
pip install -r requirements.txt
```

安装后会自动获得 `cloud-doc-skill` 命令。

### 2. 配置 LLM（可选）

纯抓取功能不需要 LLM，但 AI 摘要、对比分析等功能需要。调用方需提供自己的 API Key：

```bash
# 必填（使用 AI 功能时）
export LLM_API_KEY="你的 API Key"

# 可选：自定义 API 地址和模型
export LLM_API_BASE="https://dashscope.aliyuncs.com/compatible-mode/v1"
export LLM_MODEL="qwen-turbo"
```

支持任何兼容 OpenAI Chat Completions 格式的 API（通义千问、OpenAI、DeepSeek 等）。

不设置 LLM_API_KEY 时，`fetch_doc`（不带摘要）和 `check_changes`（`with_summary=false`）仍可正常使用。

## 如何调用

所有 skill 通过 `cloud-doc-skill` 命令调用（pip install 后可用），格式：

```bash
cloud-doc-skill <skill_name> '<params_json>'
```

未安装时也可通过源码调用：

```bash
python scripts/entry.py <skill_name> '<params_json>'
```

### fetch_doc — 抓取文档

抓取指定云厂商的产品文档，支持按产品批量发现或按链接直接抓取。

```bash
# 阿里云 - 抓取单篇文档
cloud-doc-skill fetch_doc '{"cloud": "aliyun", "doc_ref": "/vpc/product-overview/what-is-vpc"}'

# 腾讯云 - 按产品名搜索文档（限制 5 篇）
cloud-doc-skill fetch_doc '{"cloud": "tencent", "product": "私有网络", "max_pages": 5}'

# 百度云 - 按 product/slug 抓取
cloud-doc-skill fetch_doc '{"cloud": "baidu", "doc_ref": "VPC/qjwvyu0at"}'

# 火山引擎 - 按 lib_id/doc_id 抓取
cloud-doc-skill fetch_doc '{"cloud": "volcano", "doc_ref": "6401/70538"}'

# 带 AI 摘要（需要 LLM_API_KEY）
cloud-doc-skill fetch_doc '{"cloud": "aliyun", "doc_ref": "/vpc/product-overview/what-is-vpc", "with_summary": true}'
```

参数：
- `cloud`（必填）：`aliyun` | `tencent` | `baidu` | `volcano`
- `product`：产品名称，按产品批量发现文档
- `doc_ref`：文档标识，直接抓取单篇
- `product` 和 `doc_ref` 至少填一个
- `with_summary`：是否生成 AI 摘要（默认 false）
- `max_pages`：最多抓取篇数（默认 20）
- `keyword`：额外搜索关键词

用户可能这样说：
- "帮我抓取阿里云 VPC 的文档"
- "获取腾讯云私有网络的产品文档"
- "拉一下百度云 DNS 的文档内容"
- "看看火山引擎弹性网卡有哪些文档"
- "抓取这个链接的文档：https://help.aliyun.com/zh/vpc/what-is-vpc"
- "把阿里云 ECS 相关的文档都抓下来，带上摘要"
- "帮我查一下腾讯云 VPN 连接的使用文档"

### check_changes — 检测变更

检测指定产品文档的变更，与 SQLite 中的历史版本对比。首次运行会建立基线，第二次运行才能检测到变更。

```bash
# 检查阿里云 VPC 最近 7 天的变更
cloud-doc-skill check_changes '{"cloud": "aliyun", "product": "vpc", "days": 7, "max_pages": 5}'

# 检查腾讯云私有网络，不带 AI 摘要
cloud-doc-skill check_changes '{"cloud": "tencent", "product": "私有网络", "with_summary": false}'

# 检查百度云 DNS 最近 30 天
cloud-doc-skill check_changes '{"cloud": "baidu", "product": "DNS", "days": 30}'
```

参数：
- `cloud`（必填）：云厂商标识
- `product`（必填）：产品名称
- `days`：检查最近 N 天的变更（默认 7）
- `max_pages`：最多检查篇数（默认 20）
- `with_summary`：是否生成变更摘要（默认 true，需要 LLM_API_KEY）
- `keyword`：额外搜索关键词

用户可能这样说：
- "阿里云 VPC 最近有什么更新"
- "腾讯云私有网络这周改了什么"
- "百度云 DNS 最近 30 天的文档变更"
- "火山引擎 NAT 网关有没有新的文档变化"
- "检查一下各云厂商 VPN 文档最近的变更"
- "最近更新了什么"
- "帮我看看阿里云网络产品文档有没有变化"

### compare_docs — 跨云对比

对比两个云厂商的产品文档，AI 分析差异点和侧重点。需要 LLM_API_KEY。

```bash
# 对比阿里云和腾讯云的 VPC
cloud-doc-skill compare_docs '{"left": {"cloud": "aliyun", "product": "vpc"}, "right": {"cloud": "tencent", "product": "私有网络"}}'

# 对比百度云和火山引擎的弹性网卡，关注能力差异
cloud-doc-skill compare_docs '{"left": {"cloud": "baidu", "product": "ENI"}, "right": {"cloud": "volcano", "product": "弹性网卡"}, "focus": "能力差异"}'

# 通过 doc_ref 直接对比两篇具体文档
cloud-doc-skill compare_docs '{"left": {"cloud": "aliyun", "doc_ref": "/vpc/product-overview/what-is-vpc"}, "right": {"cloud": "tencent", "doc_ref": "215/20046"}}'
```

参数：
- `left`（必填）：左侧文档，包含 `cloud` + `product` 或 `doc_ref`
- `right`（必填）：右侧文档，包含 `cloud` + `product` 或 `doc_ref`
- `focus`：对比关注点（如 "能力差异"、"计费模式"、"API 接口"）

用户可能这样说：
- "对比腾讯云和百度云的弹性网卡文档"
- "阿里云和火山引擎的 VPC 有什么差异"
- "比较一下各家的 DNS 解析功能"
- "腾讯云 VPN 和阿里云 VPN 的能力差异"
- "帮我分析百度云和阿里云在网络产品上的区别"
- "对比一下两家云的计费模式"
- "阿里云和腾讯云的负载均衡有什么不同"

### summarize_diff — 变更摘要

对新旧两个版本的文档内容进行 diff 和 AI 摘要。需要 LLM_API_KEY。

```bash
cloud-doc-skill summarize_diff '{"title": "VPC API 文档", "old_content": "旧版本正文...", "new_content": "新版本正文...", "focus": "参数变化"}'
```

参数：
- `title`（必填）：文档标题
- `old_content`（必填）：旧版本内容
- `new_content`（必填）：新版本内容
- `focus`：关注重点（如 "API 参数变化"、"计费规则"）
- `url`：文档 URL（可选）

用户可能这样说：
- "帮我分析这两个版本的差异"
- "总结一下这篇文档改了什么"
- "这次更新主要变了哪些内容"
- "对比一下新旧版本，重点看 API 参数变化"
- "这个文档的变更影响范围是什么"

### run_monitor — 批量巡检

批量巡检多云多产品文档，生成日报摘要，可推送通知。单文档失败不会中断整个巡检。

```bash
# 巡检阿里云和腾讯云的 VPC 文档
cloud-doc-skill run_monitor '{"clouds": ["aliyun", "tencent"], "products": ["vpc"], "days": 1}'

# 全量巡检四朵云，发送通知
cloud-doc-skill run_monitor '{"clouds": ["aliyun", "tencent", "baidu", "volcano"], "products": ["vpc", "eni", "dns"], "send_notification": true}'

# 定时巡检模式
cloud-doc-skill run_monitor '{"clouds": ["aliyun", "tencent"], "products": ["vpc"], "mode": "scheduled", "send_notification": true}'
```

参数：
- `clouds`（必填）：云厂商列表
- `products`（必填）：产品列表
- `mode`：`check_now`（默认）或 `scheduled`（定时模式，无变更也发通知）
- `days`：检查最近 N 天（默认 1）
- `max_pages`：每个产品最多检查篇数（默认 50）
- `with_summary`：是否生成摘要（默认 true）
- `send_notification`：是否发送通知（默认 false）

用户可能这样说：
- "运行一次全量巡检"
- "生成今天的云文档日报"
- "检查所有云厂商的 VPC 和 DNS 文档，发现变更就通知我"
- "定时检查阿里云和腾讯云的网络产品文档"
- "跑一下巡检，结果发到如流"
- "帮我监控四朵云的文档变化"
- "每天检查一下各家云的网络产品有没有更新"

## 支持的云厂商

| 云厂商 | cloud 值 | 产品标识格式 | 示例 |
| --- | --- | --- | --- |
| 阿里云 | `aliyun` | alias 路径 | `vpc`、`ecs`、`dns` |
| 腾讯云 | `tencent` | 中文产品名 | `私有网络`、`VPN 连接`、`云联网` |
| 百度云 | `baidu` | 大写产品代码 | `VPC`、`DNS`、`CSN` |
| 火山引擎 | `volcano` | 中文产品名 | `私有网络`、`NAT网关`、`云企业网` |

## 返回结构

所有 skill 返回统一的 JSON：

```json
{
  "machine": { "cloud": "aliyun", "items": [...], ... },
  "human": { "summary_text": "共找到 5 篇文档。" },
  "error": null
}
```

- `machine`：结构化数据，供程序读取
- `human`：人类可读的摘要文本
- `error`：正常为 `null`，出错时包含 `code` 和 `message`

## 权限说明

本技能运行时需要以下权限：

- 网络访问：需访问阿里云、腾讯云、百度云、火山引擎的文档 API 接口（HTTPS 出站）
- 文件读写：本地 SQLite 数据库存储文档历史版本（`data/` 目录）、通知文件写入（`notifications/` 目录）、日志写入（`logs/` 目录）
- 环境变量读取：读取 `LLM_API_KEY`、`LLM_API_BASE`、`LLM_MODEL` 用于 AI 功能
- 无需 root/管理员权限，无后台常驻进程

## 配置说明

`config.yaml` 支持 `${ENV_VAR}` 和 `${ENV_VAR:default}` 语法。

LLM 配置优先级：环境变量 > config.yaml 默认值

通知渠道在 `config.yaml` 的 `notifications` 中配置，支持 aiflow、如流机器人、本地文件三种。
