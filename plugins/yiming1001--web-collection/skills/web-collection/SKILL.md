---
name: web-collection
description: "Browser plugin data collection for Douyin/TikTok/Xiaohongshu via a local bridge, including one-shot closed-loop runs (collect → poll → export → return table link)."
---

# Web Collection

Use this skill when the user wants to collect platform data with the browser extension bridge, especially for:

- 抖音 / TikTok / 小红书采集
- 关键词搜索、作者采集、链接采集、评论采集
- 闭环测试（采集 + 导出 + 返回链接）
- 严格 JSON 输出结果

Prefer the bundled script below instead of hand-writing curl flows.

## Base directory

Resolve `{baseDir}` as the parent directory of this `SKILL.md`.

## Primary entry

Use the bundled script:

```bash
{baseDir}/scripts/collect_and_export_loop.sh
```

It handles the full loop:

1. ensure bridge is reachable
2. wait for idle state
3. start `/api/collect`
4. recover from `TASK_RUNNING` when possible
5. poll task status until `completed` or `error`
6. when export is requested, require `export.status=completed` and return `export.tableUrl`

## Standard closed-loop invocation

When the user gives explicit parameters, pass them directly.

Example:

```bash
{baseDir}/scripts/collect_and_export_loop.sh \
  --platform douyin \
  --method videoKeyword \
  --keyword "美食探店" \
  --max-items 3 \
  --feature video \
  --mode search \
  --interval 300 \
  --fetch-detail true \
  --detail-speed fast \
  --auto-export true \
  --export-mode personal \
  --ensure-bridge \
  --bridge-cmd 'node /Users/zhym/coding/web_pluging/web_collection/bridge/bridge-server.js' \
  --force-stop-before-start
```

Notes:

- `--keyword` is repeatable for multiple keywords.
- Use `--link` for link-based methods.
- For user requests that explicitly require `--ensure-bridge`, always include it.
- If the user specifies a bridge command, use it exactly.

## Quick wrapper

For the common Douyin video keyword flow, you can use:

```bash
{baseDir}/scripts/run.sh --keyword "小龙虾AI助手" --max-items 10 --ensure-bridge --bridge-cmd 'node /Users/zhym/coding/web_pluging/web_collection/bridge/bridge-server.js'
```

This wrapper defaults to:

- `platform=douyin`
- `method=videoKeyword`
- `feature=video`
- `mode=search`
- `interval=300`
- `fetchDetail=true`
- `detailSpeed=fast`
- `autoExport=true`
- `exportMode=personal`
- `force-stop-before-start=true`

## Output rules

When the user asks for a strict output shape, do not add commentary.

Typical final fields:

- `taskId`
- `status`
- `export.status` or `exportStatus`
- `export.tableUrl` or `tableUrl`

If the task fails, return the same shape with empty strings where needed rather than adding a long explanation, unless the user asked for diagnosis.

## Troubleshooting

- If bridge is unreachable, use `--ensure-bridge --bridge-cmd 'node .../bridge-server.js'`.
- If `pluginConnected=false`, the bridge may be up but the browser extension is not connected.
- If a previous task is stuck, use `--force-stop-before-start`.
- Prefer the bundled script over manual `curl` unless debugging.
