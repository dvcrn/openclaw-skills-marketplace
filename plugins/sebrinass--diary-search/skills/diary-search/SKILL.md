---
name: diary-search
description: "检索日记与会话内容，支持中文分词、BM25搜索、时间衰减排序。用于搜索日记、查找历史对话、导出会话记录的场景。"
---

# Diary Search

日记与会话检索插件，让你可以搜索 OpenClaw 记录的日记内容和历史对话。

**源代码**: [GitHub](https://github.com/sebrinass/diary-search) | **npm**: [diary-search](https://www.npmjs.com/package/diary-search)

## 安装步骤

**第一步：安装插件**

```bash
npm install -g diary-search
```

**第二步：更新配置**

在 `~/.openclaw/openclaw.json` 的 `plugins.load.paths` 中添加：

```json
"~/.npm-global/lib/node_modules/diary-search"
```

完整示例：

```json
{
  "plugins": {
    "enabled": true,
    "load": {
      "paths": [
        "~/.npm-global/lib/node_modules/diary-search"
      ]
    }
  }
}
```

**第三步：重启 Gateway**

```bash
openclaw gateway restart
```

## 使用方法

安装完成后，直接对我说：

### 日记搜索
```
搜索我上周关于"项目架构"的日记
搜索 2026-02 月关于"数据库优化"的讨论
查找昨天提到的"bug"
查看我的日记统计
```

### 会话检索
```
列出昨天的会话
列出 2026-03-03 的会话
搜索我之前说的"webchat"
导出会话 77762d1f 的对话内容
```

## 工具说明

### 日记工具

#### diary_search

搜索日记内容。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query | string | ✅ | 搜索关键词 |
| limit | number | ❌ | 返回条数，默认 5 |
| time_filter | string | ❌ | 时间过滤器 |

**time_filter 可选值：**
- `today` / `yesterday` / `last_week` / `last_month` / `this_month`
- `YYYY-MM`（如 2026-02）
- `YYYY-MM-DD`（如 2026-02-28）

#### diary_stats

获取日记统计信息。

### 会话工具

#### session_list_by_date

按日期列出会话文件。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| date | string | ✅ | 日期（today/yesterday/YYYY-MM-DD/YYYY-MM） |
| agent | string | ❌ | Agent 名称，默认 xiaobu |

#### session_search

搜索会话消息内容。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query | string | ✅ | 搜索关键词 |
| date | string | ❌ | 日期过滤 |
| limit | number | ❌ | 返回条数，默认 5 |
| agent | string | ❌ | Agent 名称，默认 xiaobu |

#### session_export

导出会话的纯对话文本。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| session_id | string | ✅ | 会话ID（可以是前缀） |
| agent | string | ❌ | Agent 名称，默认 xiaobu |
| include_thinking | boolean | ❌ | 是否包含 AI 思考过程，默认 false |

## 日记格式

支持 `.md`、`.txt`、`.markdown` 文件，文件名建议使用 `YYYY-MM-DD.md` 格式。
