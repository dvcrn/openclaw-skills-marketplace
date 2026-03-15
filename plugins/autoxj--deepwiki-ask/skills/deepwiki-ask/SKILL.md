---
name: deepwiki-ask
description: "通过 DeepWiki MCP 对仓库单次提问。Query a repository with a single question via DeepWiki. 用户提供 owner/repo 和问题时触发。"
---

# DeepWiki 仓库问答（单次提问）

通过 DeepWiki MCP 对指定仓库发起一次问答，不保存历史。

## 触发场景

- 用户询问某仓库的作用、结构或功能
- 用户提供仓库名（owner/repo）并带有问题

## 参数

| 参数   | 必填 | 说明           |
|--------|------|----------------|
| repo   | 是   | 仓库名 owner/repo |
| question | 是 | 要问的问题     |

## Agent 执行流程

1. 从用户消息提取 **repo**（owner/repo）和 **question**。
2. 执行（必须加 `--json`）：
   ```
   python <SKILL_ROOT>/deepwiki_ask.py -r <owner/repo> -q "<question>" --json
   ```
   Windows 下中文问题若编码异常，可把问题写入 UTF-8 文件后：`-q @<SKILL_ROOT>/temp_q.txt`
3. 解析 stdout JSON：`status == "success"` 则展示 `answer`；`status == "error"` 则提示 `message`。
4. 请求可能需 30–120 秒，需等待。

输出示例：
```json
{"status": "success", "repo": "owner/repo", "question": "...", "answer": "..."}
{"status": "error", "repo": "owner/repo", "message": "..."}
```

## 配置

`config.json`：`request_timeout_seconds`（10–600，默认 120）、`request_max_retries`（0–10，默认 3）。

## 错误处理

- 仓库格式错误：提示 owner/repo 格式
- 超时/网络错误：脚本重试后返回 `status: "error"`，Agent 提示用户检查网络
