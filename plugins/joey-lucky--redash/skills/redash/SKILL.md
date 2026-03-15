---
name: redash
description: "通过 Redash API 查询、执行、创建数据分析任务。当用户需要查询 Redash 数据、执行 SQL、搜索已有报表、查看 dashboard、或执行临时 adhoc SQL 查询时使用本 skill。关键词：redash、查询、SQL、dashboard、AUM、数据分析、报表。"
---

# Redash Skill

通过脚本与 Redash API 交互，执行数据查询和管理操作。

## 环境准备

脚本路径：`~/.claude/skills/redash/redash.py`

脚本运行时需要 `REDASH_API_KEY` 环境变量。如果脚本报错提示未设置该变量，说明用户还没有完成初始化，需要引导用户按如下步骤操作：

1. 登录 Redash（https://zhu.yingmi-inc.com），在右上角个人头像 → **Edit Profile** → **API Key** 处复制 Key
2. 提供 Key 后，执行 `init` 命令将其持久化写入 shell 配置文件（见下方命令说明）

`REDASH_URL` 默认已内置为zhu.yingmi-inc.com，无需手动配置，但是如果用户的redash地址不是这个，可以引导用户更改

## 命令一览

### 初始化（首次使用必须执行）

```bash
python3 ~/.claude/skills/redash/redash.py init <YOUR_API_KEY>
```

脚本会自动检测当前使用的 shell（zsh/bash/fish/ksh/csh 等）及操作系统，将 `REDASH_API_KEY` 写入对应的 rc 文件（如 `~/.zshrc`、`~/.bashrc`、`~/.bash_profile`、`~/.config/fish/config.fish` 等）。写入后按提示执行 `source <rc文件>` 使配置立即生效。若 Key 已存在则自动更新，不会重复写入。

### 搜索/列出 queries

```bash
# 列出最近 25 条
python3 ~/.claude/skills/redash/redash.py list-queries

# 按关键词搜索
python3 ~/.claude/skills/redash/redash.py list-queries -q "AUM"
```

### 获取 query 详情

```bash
python3 ~/.claude/skills/redash/redash.py get-query 3052
```

### 获取 query 最近一次缓存结果（推荐，不触发 SQL）

```bash
python3 ~/.claude/skills/redash/redash.py get-latest-result 3052
```

直接读取 `latest_query_data_id` 对应的缓存，零计算成本。

### 执行已有 query（真实触发 SQL，成本较高）

```bash
python3 ~/.claude/skills/redash/redash.py execute-query 3052
```

会实际执行背后的 SQL，适合需要最新数据时使用。自动轮询 job 状态，完成后以表格形式展示结果。

### 执行 adhoc SQL（不保存）

```bash
python3 ~/.claude/skills/redash/redash.py execute-adhoc \
  --sql "select count(*) from ying99_scrm.contact_user" \
  --data-source-id 41
```

`--data-source-id` 默认为 `41`（线上 SCRM 库），可省略。

### 创建新 query

```bash
python3 ~/.claude/skills/redash/redash.py create-query \
  --name "新查询名称" \
  --sql "select 1" \
  --data-source-id 41 \
  --description "可选描述"
```

### 列出/搜索 dashboards

```bash
# 列出所有 dashboards
python3 ~/.claude/skills/redash/redash.py list-dashboards

# 按关键词过滤（客户端过滤，支持中文）
python3 ~/.claude/skills/redash/redash.py list-dashboards -q "用户"
```

### 获取 dashboard 详情

```bash
# 使用 slug
python3 ~/.claude/skills/redash/redash.py get-dashboard broker-return
```

## 常用信息
- **默认数据源 ID**：`41`（名为 `TiDB-6.X DP专用`，包含 `ying99_scrm` 库）

## 典型使用流程

1. 先 `list-queries -q 关键词` 找到 query ID
2. 用 `get-query <id>` 查看 SQL 内容
3. 用 `execute-query <id>` 获取最新结果
4. 需要自定义 SQL 时用 `execute-adhoc --sql "..."`
5. 执行脚本如果出现错误，并且是由于你自己使用错误导致的，可以随时更新当前SKILL.md中的“使用经验”，避免下次重复犯错

## 使用经验

- `get-dashboard` 的 slug 如果以 `-` 开头（如 `-_2`），需要用 `--` 分隔符避免被 argparse 当作参数，正确写法：`python3 redash.py get-dashboard -- -_2`
- `AUM在管` Query ID：`3052`
- **查询时须带库名**：如 `select 1 from ying99_scrm.contact_user`
