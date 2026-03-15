---
name: explorer
description: "Search and analyze trending GitHub repositories by topics, star count, and creation date. Supports filtering by multiple tags, minimum stars, and time range. Use when the user needs to discover popular open-source projects on GitHub. Optionally uses GITHUB_TOKEN for higher API rate limits."
---

# GitHub Projects Explorer

发现并分析 GitHub 上的热门开源项目，支持多维度搜索和筛选。

发现并分析 GitHub 上的热门开源项目，支持多维度搜索和筛选。

## 功能特性

- 🏷️ **多标签筛选** - 支持一个或多个项目标签
- ⭐ **Star 数量过滤** - 按最低 Star 数筛选
- 📅 **时间范围** - 筛选最近 N 天内创建的项目
- 🔤 **编程语言** - 按编程语言筛选
- 📊 **智能排序** - 支持 Stars/Forks/更新时间排序

## 前提条件

### 可选：配置 GitHub Token

GitHub API 有请求限制（未认证 60次/小时，认证 5000次/小时）。

```bash
# 获取 Token: https://github.com/settings/tokens
export GITHUB_TOKEN="your_github_token"
```

添加到 `~/.zshrc`：
```bash
echo 'export GITHUB_TOKEN="your-token"' >> ~/.zshrc
source ~/.zshrc
```

## 使用方法

### 基础搜索

**按标签搜索：**
```bash
python3 scripts/github_projects.py --topic python
```

**多个标签（与关系）：**
```bash
python3 scripts/github_projects.py --topic python --topic machine-learning
```

### 按 Star 数量筛选

```bash
# 查找 Star > 1000 的 Python 项目
python3 scripts/github_projects.py --topic python --stars 1000

# 查找 Star > 10000 的 AI 项目
python3 scripts/github_projects.py --topic ai --stars 10000
```

### 按时间筛选（最近 N 天）

```bash
# 最近 30 天内创建的 Python 项目
python3 scripts/github_projects.py --topic python --days 30

# 最近 7 天内创建的高 Star AI 项目
python3 scripts/github_projects.py --topic ai --stars 100 --days 7
```

### 按编程语言筛选

```bash
# Rust 语言的项目
python3 scripts/github_projects.py --lang rust --stars 1000

# Go 语言的项目
python3 scripts/github_projects.py --lang go --stars 500 --days 30

# TypeScript 项目
python3 scripts/github_projects.py --lang typescript --topic react --stars 500
```

### 综合示例

```bash
# AI 项目：最近30天、Python、Star>500
python3 scripts/github_projects.py \
  --topic ai --topic python \
  --stars 500 \
  --days 30

# Rust 工具：高 Star、最近90天
python3 scripts/github_projects.py \
  --topic rust \
  --stars 5000 \
  --days 90 \
  --limit 50

# 前端框架：JavaScript、Star>1000
python3 scripts/github_projects.py \
  --topic frontend \
  --lang javascript \
  --stars 1000 \
  --sort updated
```

## 输出格式

示例输出：
```
🔥 找到 30 个热门项目:

1. 🌟 facebook/react
   📝 A declarative, efficient, and flexible JavaScript library...
   🔗 https://github.com/facebook/react
   📊 Stars: 220,000 | Forks: 45,000 | Language: JavaScript
   🏷️  Tags: react, frontend, javascript
   📅 Created: 2013-05-24 | Updated: 2024-02-03

2. ⭐ microsoft/vscode
   📝 Visual Studio Code
   🔗 https://github.com/microsoft/vscode
   📊 Stars: 150,000 | Forks: 30,000 | Language: TypeScript
   ...
```

## 命令参数

| 参数 | 简写 | 说明 | 示例 |
|------|------|------|------|
| `--topic` | `-t` | 项目标签（可多次使用） | `-t python -t ai` |
| `--stars` | `-s` | 最少 Star 数量 | `--stars 1000` |
| `--days` | `-d` | 最近 N 天内创建 | `--days 30` |
| `--lang` | `-l` | 编程语言 | `--lang rust` |
| `--limit` | - | 返回数量（默认30） | `--limit 50` |
| `--sort` | - | 排序方式 | `--sort stars` |

### 排序选项

- `stars` - 按 Star 数量（默认，降序）
- `forks` - 按 Fork 数量
- `updated` - 按最近更新时间
- `created` - 按创建时间

## 热门标签推荐

| 领域 | 推荐标签 |
|------|----------|
| AI/ML | `ai`, `machine-learning`, `deep-learning`, `nlp`, `computer-vision` |
| 前端 | `frontend`, `react`, `vue`, `angular`, `javascript`, `typescript` |
| 后端 | `backend`, `api`, `microservices`, `nodejs`, `python` |
| 移动开发 | `mobile`, `ios`, `android`, `flutter`, `react-native` |
|  DevOps | `devops`, `docker`, `kubernetes`, `ci-cd`, `terraform` |
| 数据 | `database`, `big-data`, `analytics`, `sql`, `nosql` |
| 安全 | `security`, `cybersecurity`, `penetration-testing` |
| 工具 | `cli`, `tools`, `productivity`, `automation` |

## 常见问题

**错误：API 请求限制 reached**
→ 设置 GITHUB_TOKEN 提高限制：
```bash
export GITHUB_TOKEN="your-token"
```

**没有返回结果**
→ 尝试放宽条件：
- 降低 `--stars` 数值
- 增加 `--days` 天数
- 减少 `--topic` 标签数量

**搜索结果不准确**
→ 使用更具体的标签：
- 用 `machine-learning` 而不是 `ml`
- 用 `natural-language-processing` 而不是 `nlp`

## 使用场景

### 场景1：追踪新兴技术
```bash
# 最近30天的热门 AI 项目
python3 scripts/github_projects.py --topic ai --stars 100 --days 30 --limit 50
```

### 场景2：学习优秀项目
```bash
# 高星 Python 项目
python3 scripts/github_projects.py --topic python --stars 10000 --limit 20
```

### 场景3：发现新工具
```bash
# 最近7天的开发者工具
python3 scripts/github_projects.py --topic developer-tools --topic cli --days 7 --stars 50
```

### 场景4：技术调研
```bash
# 对比不同语言的 Web 框架
python3 scripts/github_projects.py --topic web-framework --lang rust --stars 1000
python3 scripts/github_projects.py --topic web-framework --lang go --stars 1000
```

## 参考

- GitHub Search API: [references/github_api.md](references/github_api.md)
- GitHub 官方文档: https://docs.github.com/en/rest/search
