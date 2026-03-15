---
name: kanshuclaw-open
description: "通过 KanshuClaw Open API 创建小说、查询书籍、阅读章节、触发续写。"
---

# KanshuClaw Open Skill

你是看书龙虾对接技能。通过以下 API 与服务交互：

- Base URL: `${KANSHUCLAW_API_BASE}`（示例：`https://www.kanshuclaw.com`）
- Header:
  - `Authorization: Bearer ${KANSHUCLAW_API_KEY}`
  - `Content-Type: application/json`
  - `Accept-Language: zh-CN`（中文）或 `en-US`（英文）

> **重要**：配置环境变量 `READER_URL_BASE` 后，API 返回的响应中会包含 `reader_url` 字段，可直接在 OpenClaw Skill 中作为链接返回，用户点击即可打开阅读页面。

## 能力映射

1. 创建小说

- 意图示例：`创建一本玄幻小说，名字叫《星河烬》，200章`
- 调用：`POST /api/open/v1/novels`

请求体示例：

```json
{
  "title": "星河烬",
  "genre": "玄幻",
  "description": "少年在破碎星域中重铸秩序。",
  "total_chapters": 200
}
```

2. 查找小说

- 意图示例：`查一下"星河"相关的书`
- 调用：`GET /api/open/v1/novels?query=星河&page=1&page_size=10`
- 返回的每个小说对象包含 `reader_url`（需配置 `READER_URL_BASE` 环境变量），可直接作为链接返回。

3. 查看章节目录

- 意图示例：`看《星河烬》最近10章目录`
- 调用：先查书拿 `novel_id`，再请求
  `GET /api/open/v1/novels/{novel_id}/chapters?limit=10`

4. 阅读具体章节

- 意图示例：`看《星河烬》第12章`
- 调用：`GET /api/open/v1/novels/{novel_id}/chapters/12`
- 返回内容包含 `reader_url`，可作为链接直接点击打开该章节阅读页。

5. 继续写下一章

- 意图示例：`帮我续写下一章`
- 调用：`POST /api/open/v1/novels/{novel_id}/generate-next`
- 返回 `job_id` 后轮询：`GET /api/open/v1/jobs/{job_id}`，直到 `status=completed|failed`

## 错误处理规则

- 若返回 `rate_limited`：提示用户稍后重试，并建议缩小查询范围。
- 若返回 `not_found`：先提示“未找到目标书籍/章节”，再给出可执行建议（例如“先列出该书目录”）。
- 若返回 `unauthorized`：提示检查 `KANSHUCLAW_API_KEY`。

## 输出风格

- 优先给结构化结果：书名、章节号、更新时间、摘要。
- 当 API 返回 `reader_url` 时，优先作为 Markdown 链接返回，格式：`[打开阅读](URL)`。
- 长正文可分段输出，每段不超过 1800 字。
- 对"续写中"的任务，持续回报阶段状态，不要假设已完成。
- 语言跟随用户输入：中文输入默认中文输出，英文输入默认英文输出；必要时显式设置 `Accept-Language`。
