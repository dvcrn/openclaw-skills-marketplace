---
name: gitcode-issue-reply
description: "Generate reply drafts for a single GitCode issue with similar-issue references; maintainer reviews before posting. Use when user asks to reply to or comment on an issue and provides a GitCode issue link; do not use when user only wants to fetch or query issue data. 针对单个 GitCode Issue 生成回复草稿（含相似 Issue 参考），维护者审阅后可发送评论；仅当用户要回复或评论且提供链接时使用，仅获取或查询 issue 信息时勿用。Python 3.7+ standard library only (requests optional for DeepWiki)."
---

# GitCode Issue 回复

对**单个** GitCode Issue 生成回复草稿与相似 Issue 参考，供维护者审阅后发送。

## 何时使用（须同时满足）

1. 用户表达**「回复 issue」**意图（如「回复这个 issue」「帮回复 issue #123」）。
2. 用户提供了**唯一**的 GitCode Issue 链接或 `owner/repo#number`。

仅提供链接但无回复意图时，不要使用本技能。

## 认证

**GITCODE_TOKEN**：按以下优先级读取，任一处有值即用。

| 优先级 | 来源 | 适用平台 |
|--------|------|----------|
| 1 | 进程环境变量 `GITCODE_TOKEN` | 所有平台 |
| 2 | Windows 用户级环境变量 | Windows |
| 3 | Windows 系统级环境变量 | Windows |

未配置时：提示用户到 [GitCode 个人访问令牌](https://gitcode.com/setting/token-classic) 创建并设置。

## 依赖

- **Python 3.7+** 标准库（必需）。
- **requests**（可选）：用于 DeepWiki 知识库查询。未安装时脚本仍可运行，但跳过 DeepWiki。

---

## 第一轮：生成草稿

### 1. 解析并调用脚本

- 从用户消息中解析 Issue：链接（`gitcode.com/.../issues/123`）或 `owner/repo#number`。若为后者，拼接为完整 URL：`https://gitcode.com/owner/repo/issues/number`。
- **SKILL_ROOT**：本 SKILL.md 所在目录。
- 执行（使用脚本**绝对路径**）：
  ```
  python <SKILL_ROOT>/scripts/prepare_issue_reply.py --issue-url "<完整 Issue URL>"
  ```
- 脚本可能需要 **1–3 分钟**（含 DeepWiki 查询），请耐心等待。
- 若退出码非 0 或 JSON 中 `status == "error"`，提示用户错误信息并结束。

### 2. 读取脚本输出

脚本向 stdout 打印单份 JSON。解析该 JSON。

### 3. 若已有人回复

若 `status == "already_replied"`：提示「该 Issue 已有其他人回复，已跳过」，流程结束。

### 4. 发送 Label（可选）

若 JSON 中 `label_needed == true`：
```
python <SKILL_ROOT>/scripts/post_comment.py --issue-url "<Issue URL>" --body "/label add triage-review"
```
若失败可忽略，不影响后续流程。

### 5. 两次生成（相似度 → 草稿）

JSON 中 `prompt_similarity`、`prompt_draft_partial` 为两次生成的 prompt。

- **第一次（相似度判断）**
  - 将 `prompt_similarity` 作为 prompt 生成结果。
  - 从生成结果中解析 JSON：`{"similar_issues": [123, 456]}`。若解析失败则视为空列表。

- **第二次（生成回复草稿）**
  - 将相似 Issue 列表格式化（如 `#123, #456`；若空则 `（无）`），替换 `prompt_draft_partial` 中的 `{similar_issue_numbers_formatted}`。
  - 据此生成回复草稿（去除首尾空白及「回复：」前缀），即为 **draft_reply**。

- **展示给维护者**
  - **拟回复内容（草稿）**：展示 **draft_reply**（仅供审阅与修改，尚未发送；可在会话中维护，用户修改后更新）。
  - **相似 Issue**：按「[#N](https://gitcode.com/owner/repo/issues/N) 标题」格式列出可点击链接（owner、repo 从 JSON 的 `owner`、`repo` 取），注明「仅供参考，不会加入回复内容」。
  - **DeepWiki 状态**：若 `deepwiki_status` 不为 `"ok"`，告知用户知识库查询未成功，草稿可能缺少项目背景信息。
  - **必须展示提醒语**：「审阅后请说「发送」或「回复」以发布评论，说「取消」则结束本次操作。」
  - **会话状态**：第一轮结束后视为**未确认发送**（send_confirmed=false）；**仅当**用户**后续消息**中明确说「发送」「回复」「发出去」等时，才可调用 post_comment 发送回复正文。
  - 第一轮**必须在此结束**：**不得**在本轮调用 post_comment 发送回复正文；本轮**不**发送回复评论。

---

## 第二轮：确认发送

**仅当**用户在同一会话的**后续消息**中明确表达「发送」「回复」「发出去」「就按这个回复」等**发送意图**时，才可调用 post_comment.py 发送回复正文。未收到上述任一表述前，**禁止**发送回复评论。

### 用户说「取消」

若用户在第一轮展示草稿后的**后续消息**中说「取消」「不发了」「算了」等：提示「已取消本次 Issue 回复操作」，流程结束，**不**调用 post_comment 发送任何回复内容。

### 确定发送内容

1. 若用户**本条消息**包含明确的回复正文（代码块、长段文本），用该内容。
2. 若用户之前在对话中修改过草稿，用**最后一次修改后的版本**。
3. 否则用第一轮生成的 **draft_reply**。

### 发送

确定 Issue URL 与 body 后：
- **短文本**（无换行、无引号）：
  `python <SKILL_ROOT>/scripts/post_comment.py --issue-url "<URL>" --body "<正文>"`
- **长文本或含特殊字符**：先将正文用 Write 工具写入临时文件（**写入系统临时目录或工作区目录，不要写入 SKILL_ROOT**），再：
  `python <SKILL_ROOT>/scripts/post_comment.py --issue-url "<URL>" --body-file "<临时文件路径>"`

---

## 流程示例

### 完整正常流程

```
用户：回复这个 issue https://gitcode.com/owner/repo/issues/42
  → 解析 Issue URL → 执行 prepare_issue_reply.py
  → 读取 JSON → status=ok, label_needed=true
  → 执行 post_comment.py 打 triage-review 标签
  → 生成相似 Issue 列表 [38]
  → 生成 draft_reply → 会话状态 send_confirmed=false
  → 展示草稿 + 相似 Issue + 提醒语「审阅后请说「发送」或「回复」以发布评论，说「取消」则结束本次操作。」（第一轮结束）

用户：把第二段改温和一点
  → 修改 draft_reply → 更新会话中的草稿
  → 展示修改后的草稿 + 提醒语（仍为未确认发送状态）

用户：发送
  → 触发第二轮 → 视为 send_confirmed=true
  → 取修改后的 draft_reply 写入临时文件
  → 执行 post_comment.py --body-file "<临时文件>" 发送回复正文
  → 反馈发送成功结果
```

### 取消流程

```
用户：回复这个 issue https://gitcode.com/owner/repo/issues/42
  → 生成草稿并展示 + 提醒语

用户：取消
  → 提示「已取消本次 Issue 回复操作」，流程结束，不发送回复评论
```

---

## 配置

**config.json**（可选）：

| 参数 | 含义 | 默认 |
|------|------|------|
| `issue_content_max_chars` | Issue 正文最大字符数 | 3000 |
| `history_issues_limit` | 历史 Issue 条数上限 | 100 |
| `dry_run` | 试跑模式，`true` 时不发 label | `false` |

旧键名 `content_max_chars`、`history_issues_max` 仍支持。

---

## 禁止与约定

- **禁止在用户未明确表达发送意图前发送回复正文**：仅当用户**后续消息**中出现「发送」「回复」「发出去」「就按这个回复」等明确发送意图时，才可调用 post_comment.py 发送**回复内容**；第一轮生成草稿后不得在同一轮或未经用户确认即发送回复评论；用户说「取消」时不得发送。
- 除 **prepare_issue_reply.py**、**post_comment.py** 外，不生成、不执行其他脚本。
- 发评论统一用 **post_comment.py**。
- **临时文件不得写入 SKILL_ROOT 目录**。

---

## 参考

- **Prompt 模板**：`references/prompts/similarity.txt`、`references/prompts/draft_reply.txt`。
- GitCode API：[官方文档](https://docs.gitcode.com/docs/apis/)。

## 历史版本

**v1.0.0** (2026-03-11)
- 🎉 初始版本发布
- 💬 支持生成回复草稿与相似 Issue 参考
