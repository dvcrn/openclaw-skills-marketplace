---
name: feishu-task-status
description: "Use when working in Feishu and the task is likely to take more than a few seconds, involves multiple tool calls, heavy search, document generation, coding, or when the user asks whether OpenClaw is still running. Uses sessions_spawn, sessions_list, subagents, and session_status to provide visible in-progress updates and completion handoff instead of silent waiting."
homepage: https://docs.openclaw.ai/session-tool
---

# Feishu Task Status

Use this skill in Feishu chats when the user needs confidence that the task is
still running.

If the chat should stay free for additional user prompts while longer work
continues, pair this with `feishu-parallel-dispatch`.

This skill is especially important when:

- the task needs web search, verification, file generation, coding, or multiple tools
- the task may take longer than about 10-15 seconds
- the user asks "还在吗", "进度如何", "是不是卡住了", or similar

## Goal

Avoid silent waiting in Feishu.

Also avoid fake activity. Do not narrate internal tool calls, planning steps,
or raw status payloads to the user.

Prefer a visible two-step experience:

1. Immediate acknowledgement: tell the user the task has started
2. Deferred completion: use a spawned sub-task so the final result arrives later
3. Periodic progress heartbeat: if the task is still active, let heartbeat-driven follow-ups send a short status update about every 3 minutes
4. Stall handling: if the task is still active but appears stuck, tell the user proactively instead of waiting for them to ask

## Long-Task Workflow

When the task is long-running:

1. Send a short acknowledgement in the current Feishu chat, for example:
   - `已收到，开始执行。这个任务会分阶段处理，完成后我会自动回你结果。`
   - `开始处理，当前会先做搜索/整理/生成，完成后直接回到这个会话。`
2. Use `sessions_spawn` to run the heavy work as a sub-agent task.
3. Prefer the most appropriate specialist agent when spawning:
   - research -> external information, fact verification, comparisons
   - office -> team PM, meeting notes, shared planning
   - slides -> personal planning, personal reviews, personal organization
   - main -> general long tasks that do not clearly belong elsewhere
4. Let the spawned task deliver the final answer back to the originating chat.

Do not send a second meta-message such as "我先检查一下" if you can immediately
perform the check or the next step. Act first, then report the real result.

## When The User Asks For Progress

If the user asks whether the task is still running:

1. Use `sessions_list` or `subagents` to find active child runs
2. Use `session_status` on the relevant run if needed
3. Reply with a short status summary and an estimated percentage when possible
4. Make it clear that the percentage is an estimate, not an exact meter

Do not claim that a task is still actively progressing unless there is actual
evidence of active child work, a just-triggered continuation step, or a fresh
tool/result transition in the current session.

If there is no active child run but the last explicit user request is still
unfinished and the next bounded step is obvious, continue that unfinished
request immediately instead of replying only that there is no running task.

If there is no active child run because a background task vanished or ended too
early before the deliverable was complete, respawn one bounded continuation
child and keep the task moving.

## Automatic 3-Minute Progress Updates

If the Feishu task remains active for a while, do not wait for the user to ask.

Use the heartbeat-driven pattern to:

1. check active child tasks about every 3 minutes
2. infer the current stage
3. send a short progress update with an estimated percentage
4. if the stage has not changed for too long, send a blocker summary plus the fallback you are trying

If there is no active child but the last explicit request is still clearly
unfinished, do not answer with a passive status line. Restart a bounded
continuation step first, then report that recovery in one short line.

Example automatic update:

- `进度播报：行业调研 正在整理，约 55%。`
- `进度播报：PPT 正在生成，约 80%。`

## Estimated Progress Percentages

When reporting progress, prefer this rough stage mapping:

- `已接单` -> about `5%`
- `排队中` -> about `10%`
- `搜索中` / `收集资料中` -> about `15%-35%`
- `整理中` / `分析中` -> about `40%-65%`
- `生成文件中` / `写作中` / `制作 PPT 中` -> about `70%-90%`
- `收尾中` / `准备回复` -> about `95%`
- `已完成` -> `100%`
- `执行失败` -> `0%`

Use one percentage, not a range, in the actual Feishu reply. Pick the number
that best matches the observed stage.

Examples:

- `还在执行，当前在搜索资料，估计进度 25%。`
- `还在跑，已经进入文档生成阶段，估计进度 80%。`
- `任务还没结束，当前没有报错，估计进度 55%。`
- `刚完成最后一步，结果马上回你，估计进度 95%。`

Counter-example:

- Do not say `当前进度 75%` only because you intend to keep thinking.
- Do not promise `三分钟后汇报` if no real background task or continuation step
  exists.

## Per-Task Progress Lists

If multiple child tasks are running, show them line by line with status plus
estimated percentage.

Example:

- `#1 行业调研：搜索中，约 30%`
- `#2 周报整理：生成文件中，约 82%`
- `#3 PPT：等待外部工具，约 60%`

Keep the wording short and Feishu-friendly.

## Preferred Status Labels

Use short, human-readable Feishu wording:

- `已接单`
- `执行中`
- `搜索中`
- `整理中`
- `生成文件中`
- `等待外部工具`
- `疑似卡住`
- `已完成`
- `执行失败`

## Practical Rules

- Do not keep the user staring at a silent chat for a long task
- For short tasks, reply normally; do not spawn unnecessarily
- For long tasks, prefer `sessions_spawn` over blocking the main chat
- Never print raw tool JSON, action objects, session ids, or command schemas in a Feishu reply
- Never answer a retry/continue prompt with a plan-of-attack only; continue the unfinished work or return the concrete blocker
- If there is no active spawned task but the previous explicit request is only partially completed, resume that request instead of falling back to a generic "no active task" reply
- If an unfinished task lost its active child session unexpectedly, recreate a bounded continuation child instead of leaving the user to manually restart the whole workflow
- If a spawned task fails, tell the user plainly and say what failed
- If a spawned task appears stuck, do not wait for the user to ask. Send a blocker note, the likely cause, and the fallback or next input needed
- When reporting progress, keep it to one or two short lines
- Progress percentages are estimates derived from task stage, not exact runtime math
- For long active tasks in Feishu, prefer one concise progress heartbeat about every 3 minutes instead of complete silence
- If the current stage is unclear, report the stage in words first and give a conservative estimate
- In Feishu, clarity matters more than technical detail
- If two heartbeat cycles pass with no meaningful progress, stop sounding optimistic and surface the stall
- If there is no active child run and no fresh continuation step has been
  launched, do not fabricate a live progress percentage; either restart the
  task or say plainly that no active background run currently exists

## Examples

### Example A: Long research task

User asks:
`帮我调研一下最近 AI Agent 框架，并整理成对比表`

Do:

1. Acknowledge immediately
2. Spawn `research`
3. Return final comparison when the child run finishes

### Example B: Long office file task

User asks:
`帮我生成一份项目周报和配套 PPT`

Do:

1. Acknowledge immediately
2. Spawn `office` or `slides` depending on the center of gravity
3. Return files when finished

### Example C: User asks if it is stuck

User asks:
`你是不是卡住了？`

Do:

1. Check active sub-task state
2. Reply with plain status
3. If there is no active run, say so directly
