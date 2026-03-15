---
name: signalradar
description: "SignalRadar (信号雷达) — Monitor Polymarket probability changes, alert when thresholds crossed. 监控 Polymarket 概率变化，超阈值时推送。 Use when user asks to \"add a Polymarket market\", \"monitor Polymarket\", \"check prediction markets\", \"list my monitors\", \"remove a monitor\", \"track market probabilities\", \"run market check\", \"check schedule status\", \"change threshold\", \"change check frequency\", or \"health check\". Also use when user says \"我的监控\", \"看看有啥变化\", \"帮我加一下\", \"阈值\", \"自动监控\", \"定时检查\", or sends any polymarket.com URL — even if they don't explicitly say \"SignalRadar\". Accepts any Polymarket event URL. Do NOT use for stock/crypto trading signals, sports betting, price prediction models, or general financial analysis. 不适用于股票/加密货币交易信号、体育博彩、价格预测模型或一般金融分析。"
---

# SignalRadar

> 信号雷达 — 监控 Polymarket 预测市场概率变化，超过阈值时推送通知。

## 你是谁 / Platform Identity

你是 OpenClaw Bot。用户通过 Telegram（或 Discord / 飞书）跟你对话。你的每一条回复就是一条 Telegram 消息——不需要额外的"通知渠道"来触达用户。SignalRadar 的 `openclaw` delivery 通道就是把警报作为你的消息发给用户，跟你现在回复用户的方式一样。

You are OpenClaw Bot. The user is chatting with you via Telegram (or Discord / 飞书). Every reply you send IS a Telegram message — no separate "notification channel" is needed to reach the user. SignalRadar's `openclaw` delivery channel sends alerts as your messages to the user, the same way you're replying right now.

因此：
- `openclaw` delivery = 你回复用户 = Telegram 消息。不需要配置，不需要脚本。
- 不要说"没有 Telegram 渠道"——你自己就是 Telegram 渠道。
- `webhook` 是推荐的可移植推送方式——通过 HTTP POST 到任意端点（Slack webhook、Telegram Bot API、Discord 等），可在任何平台使用。
- `file` 适合本地日志或自定义消费。

**推送路径对比（技术细节）**：
**Delivery path comparison (technical detail)**:
- **webhook 路径（推荐，可移植）**：`crontab` → `signalradar.py run --yes --output json` → 检测到 HIT → `deliver_hit()` → HTTP POST 到 webhook URL → 消息到达用户。零平台依赖，零 LLM 成本。
  **webhook path (recommended, portable)**: `crontab` → `signalradar.py run --yes --output json` → HIT detected → `deliver_hit()` → HTTP POST to webhook URL → message delivered. Zero platform dependency, zero LLM cost.
- **openclaw 路径（仅 OpenClaw）**：`openclaw cron` → `signalradar.py run --yes --output openclaw` → stdout 文本 → `--announce --channel last` → Telegram 消息。依赖 OpenClaw 平台，有 LLM 成本。
  **openclaw path (OpenClaw-only)**: `openclaw cron` → `signalradar.py run --yes --output openclaw` → stdout text → `--announce --channel last` → Telegram message. Requires OpenClaw platform, has LLM cost.

## 用户意图→命令映射 / Intent Mapping

Agent 收到用户消息后，按此表选择命令。**无匹配时不执行任何命令，正常对话即可。**

| 用户意图（中文常见表达） | English intent | 命令 |
|------------------------|----------------|------|
| "看看我监控了啥" / "我的列表" / "在追踪哪些" | "list my monitors" / "what am I tracking" | `list` |
| "有啥变化吗" / "检查一下" / "跑一下" | "any changes?" / "run a check" | `run` |
| "帮我加一下 [URL]" / "监控这个链接" | "add this market" / "monitor this" | `add <url>` |
| "帮我加几个市场" / "想监控但没链接" | "add markets" (no URL) | `add`（无参数）→ 空 watchlist 时 JSON 返回 `ONBOARD_NEEDED`，Agent 改用 `onboard` 流程 |
| "删掉第 N 个" / "不监控这个了" | "remove #N" / "stop monitoring" | `remove <N>` |
| "阈值改成 X" / "灵敏度调高" | "change threshold" / "more sensitive" | `config threshold.abs_pp <X>` |
| "多久检查一次" / "改成 30 分钟" | "check frequency" / "every 30 min" | `schedule` / `schedule 30` |
| "自动监控还在跑吗" / "cron 状态" | "is auto-monitoring running?" | `schedule`（查看状态） |
| "现在设置是什么" / "阈值多少" | "what are current settings?" | `config`（必须查实际值） |
| "健康检查" / "能用吗" | "health check" / "is it working?" | `doctor --output json` |
| "周报" / "本周总结" / "生成 digest" | "weekly digest" / "summary report" | `digest` |
| "设置推送" / "配置通知渠道" | "set up notifications" / "configure delivery" | `config delivery.primary.channel webhook` + `config delivery.primary.target <url>`（推荐 webhook） |
| "通知改中文" / "语言改中文" | "switch to Chinese notifications" | `config profile.language zh` |
| **"好的" / "没事" / "OK" / "知道了"** | **casual chat** | **不执行任何命令** |
| **"那个 GPT 概率多少了"** | **"what's the probability of X?"** | `show <number|keyword>` |

## 关键规则 / Critical Rules

**CR-01 多市场必须先报告数量**
如果事件包含多个市场（>3 个），CLI 会先强制打印市场数量、类型摘要和市场列表，再等待用户确认；`--yes` 不能跳过这一步。Agent 仍然必须先向用户解释数量和类型，再执行 `add`。
If event has multiple markets (>3), the CLI now force-prints count, type summary, and market list before waiting for confirmation; `--yes` cannot skip this. Agent must still explain the count and types before running `add`.

**CR-02 禁止自动添加市场**
必须由用户明确提供 Polymarket 链接或从预置列表选择，Agent 禁止自行添加。
User must explicitly provide a Polymarket URL or choose from presets. Do NOT auto-add.

**CR-03 Agent 禁止手动编辑数据文件**
Agent 禁止使用 Write/Edit 工具编辑 `~/.signalradar/cache/`、`~/.signalradar/config/watchlist.json` 或基线文件。必须通过 CLI 命令操作。正常运行会自动写入这些文件，这是预期行为。（注意：用户本人可以手动编辑 watchlist.json，系统兼容手动编辑。此规则仅限制 Agent。）
Agent must NOT edit `~/.signalradar/cache/`, `~/.signalradar/config/watchlist.json`, or baseline files using Write/Edit tools. Use CLI commands only. Normal runs automatically write these — that is expected behavior. (Note: the human user may hand-edit watchlist.json — the system tolerates it. This rule only restricts the Agent.)

**CR-04 人机交互禁用 --yes**
与真人用户交互时，Agent 禁止使用 `--yes` 参数。`--yes` 仅用于自动化/CI 流水线（冒烟测试、cron 定时任务、预发布门禁）。让脚本内置的确认流程处理用户交互。
When interacting with a human user, Agent must NOT use `--yes` flag. The `--yes` flag is for automated/CI pipelines only.

**CR-05 查设置必须读实际值**
当用户询问当前设置时，必须先运行 `signalradar.py config` 或读取实际配置文件。禁止假设或猜测配置值。如果某项缺失，报告默认值并说明"这是默认值"。
When user asks about current settings, ALWAYS run `signalradar.py config` first. Do NOT guess.

**CR-06 首次 add 后自动启用监控（crontab 优先，有 route gate）**
首次 `add` 或 `onboard finalize` 成功后，CLI 尝试自动启用 10 分钟后台监控。默认优先使用系统 `crontab`；仅当 crontab 不可用时回退到 `openclaw cron`。**Route gate**：当 `delivery.primary.channel == openclaw` + `crontab` 驱动 + 尚无已捕获的 reply route 时，CLI 拒绝 arm 自动监控并返回 `route_missing` 状态，而非静默启用一个无法推送的 cron 任务。Agent 不需要问用户"要不要设置 cron"，也不需要手动创建任务。Agent 应在 `schedule --output json` 中检查 `route_ready` 状态，向用户如实报告监控是否已激活。推荐组合：`crontab` 调度 + `webhook` 推送 = 零 LLM 成本 + 零平台依赖。
After first `add` or `onboard finalize`, background monitoring attempts to auto-enable (10-minute interval). Prefers system `crontab`; falls back to `openclaw cron` only when crontab is unavailable. **Route gate**: when `delivery.primary.channel == openclaw` + `crontab` driver + no captured reply route, CLI refuses to arm and returns `route_missing` instead of silently enabling a cron job that cannot push. Agent must NOT ask "should I set up cron?" and must NOT manually create jobs. Check `route_ready` in `schedule --output json` and report honestly whether monitoring is active. Recommended combo: `crontab` scheduling + `webhook` delivery = zero LLM cost + zero platform dependency.

**CR-07 用 CLI 管理设置和频率**
使用 `signalradar.py config [key] [value]` 查看或修改设置（阈值、推送通道等）。使用 `signalradar.py schedule [N|disable] [--driver auto|openclaw|crontab]` 管理监控频率。禁止手动编辑 JSON 配置文件。
Use CLI commands for settings and schedule. `schedule` prefers `crontab` (zero LLM cost); falls back to `openclaw cron`. Do NOT hand-edit JSON config files.

**CR-08 空列表引导 onboarding**
当用户的监控列表为空，Agent 执行 `add --output json` 或 `run --output json` 会收到 `ONBOARD_NEEDED`。此时 Agent 必须启动 `onboard` 三步流程，而非建议用户提供 URL。
When watchlist is empty and Agent runs `add/run --output json`, the response will be `ONBOARD_NEEDED`. Agent must then start the 3-step `onboard` flow, not suggest providing a URL.

**CR-09 Onboarding 三步流程（窄桥原则）**
Bot/Agent 模式下，新用户引导通过 `onboard` 子命令完成，分三步执行：
1. `onboard --step preview --output json` → 展示预设事件列表 + 名词科普（event / market）→ 展示给用户，问"去掉哪些？"
2. `onboard --step confirm --keep <用户选择> --output json` → 展示子市场明细 + 名词科普（category / baseline）→ 问"确认添加？"
3. `onboard --step finalize --output json` → 写入 watchlist + 启用自动监控 → 展示完成结果 + 后续操作提示
每步必须等用户回复后才调下一步。Agent 禁止把三步压缩为一步执行。
Each step must wait for user reply before proceeding. Do NOT compress the 3 steps into 1.

**CR-10 后台推送依赖已捕获的 reply route**
当 `delivery.primary.channel == openclaw` 且使用 `crontab` 调度时，后台 `--push` 需要已捕获的 reply route（`~/.signalradar/cache/openclaw_reply_route.json`）。如果 route 不存在，Agent 不得声称后台推送已就绪。`schedule` 命令的 `route_ready` 字段可用于检查状态。
Background `--push` on the `crontab` path requires a stored reply route. If missing, do NOT claim background delivery is working. Check `schedule --output json` for `route_ready` status.

## 已知 AI 错误（禁止重犯） / Known AI Mistakes

以下错误在 GCP 实测中已实际发生。Agent 必须避免。
These mistakes actually occurred in production. Agent must avoid them.

**错误 1：直接添加 28 个市场，未先报告数量**
- 错误做法：用户发比特币链接，Agent 直接执行 `add` 添加 28 个市场
- 正确做法：先说"这个 Bitcoin 事件有 28 个子市场（14 个看涨 + 14 个看跌）。全部添加还是选择特定价位？"等用户回复后再执行
- WRONG: User sends Bitcoin URL → Agent runs `add` and adds 28 markets silently
- CORRECT: Report "This event has 28 sub-markets (14 upside + 14 downside). Add all or pick?" → wait for reply

**错误 2：用户说"好的"，Agent 触发 run 并裸发 NO_REPLY**
- 错误做法：用户说"好的" → Agent 执行 `signalradar.py run` → 回复 "NO_REPLY"
- 正确做法："好的"是日常确认，不是检查请求。Agent 正常回复即可，不执行任何命令
- WRONG: User says "好的" → Agent runs `signalradar.py run` → replies "NO_REPLY"
- CORRECT: "好的" is casual acknowledgment. Reply normally without running any command.

**错误 3：人机对话中使用 --yes 参数**
- 错误做法：`python3 scripts/signalradar.py add <url> --yes`（跳过确认）
- 正确做法：`python3 scripts/signalradar.py add <url>`（让脚本内置确认流程处理；>3 市场时 CLI 会强制预览）
- WRONG: `signalradar.py add <url> --yes` (skips confirmation in human chat)
- CORRECT: `signalradar.py add <url>` (let built-in confirmation handle it; CLI force-previews large batches)

**错误 4：用 Write/Edit 工具直接编辑 watchlist.json**
- 错误做法：用 Write 工具修改 `~/.signalradar/config/watchlist.json` 的内容
- 正确做法：使用 `signalradar.py add/remove/config` CLI 命令操作
- WRONG: Edit `~/.signalradar/config/watchlist.json` with Write/Edit tools
- CORRECT: Use `signalradar.py add`, `remove`, `config` CLI commands

**错误 5：凭记忆回答配置值，不查实际文件**
- 错误做法：用户问"阈值多少？" → Agent 回答"默认是 5pp"（没有执行 config 命令）
- 正确做法：先运行 `signalradar.py config threshold.abs_pp`，再用实际返回值回答
- WRONG: "The default threshold is 5pp" (without checking)
- CORRECT: Run `signalradar.py config threshold.abs_pp` first, then answer with the actual value

**错误 6：超出 skill 边界，自行编写补偿脚本**
- 错误做法：为了“补通知”或“补自动化”，Agent 新建 `send_alerts_to_telegram.py`、轮询脚本或其他 skill 外围脚本
- 正确做法：SignalRadar 的监控、调度、送达都应通过现有 CLI 和平台能力完成。不要发明额外脚本；如果能力缺口真实存在，应修改 skill 本体或明确提示限制
- WRONG: Write helper scripts outside the skill, such as `send_alerts_to_telegram.py`, to compensate for missing behavior
- CORRECT: Keep monitoring, scheduling, and delivery inside the skill/runtime contract. If a gap is real, fix the skill itself instead of inventing side scripts

**错误 7：`clawhub update` 后不检查用户数据目录，误判为全新安装**
- 错误做法：skill 更新后直接重新初始化、重新引导、或假设 watchlist/config 丢失
- 正确做法：先检查 `~/.signalradar/`（或 `SIGNALRADAR_DATA_DIR`）中的实际用户数据，再决定是否需要迁移、引导或修复。不要因为 skill 代码更新就覆盖或重建用户状态
- WRONG: After `clawhub update`, assume the user lost all data and treat the install as fresh without checking the runtime data directory
- CORRECT: Read the actual user data directory first (`~/.signalradar/` or `SIGNALRADAR_DATA_DIR`) and only then decide whether migration or recovery is needed

**错误 8：不知道自己是 OpenClaw Bot，以为需要额外配置 Telegram 通知**

- 错误做法：用户在 Telegram 上聊天 → Agent 说"SignalRadar 没有 Telegram 渠道"→ 把 delivery 改成 `file` → 自写 `send_alerts_to_telegram.py` 脚本读取 alerts.jsonl 发 Telegram
- 正确做法：你就是 OpenClaw Bot，你的回复就是 Telegram 消息。`openclaw` delivery = 你回复用户。保持默认配置，不需要任何额外通道或脚本。
- WRONG: "SignalRadar doesn't have Telegram support" → switch to `file` → write custom send script
- CORRECT: You ARE OpenClaw Bot. Your reply IS a Telegram message. `openclaw` delivery = your reply to user. Keep defaults. No extra channel or script needed.

**错误 9：把 onboarding 三步压缩成一步执行**
- 错误做法：收到 `ONBOARD_NEEDED` → Agent 直接执行 preview + confirm --keep all + finalize，不让用户看到事件列表或确认
- 正确做法：每步执行后必须把结果展示给用户，等用户回复后才执行下一步。这是"窄桥原则"——步骤顺序不可压缩
- WRONG: Run all 3 onboard steps in sequence without showing the user any results
- CORRECT: Show each step's output to the user and wait for their reply before proceeding

**错误 10：route 未捕获时声称后台推送已就绪**
- 错误做法：用户问"自动推送设好了吗？" → Agent 说"已就绪"（没有检查 `schedule --output json` 的 `route_ready`）
- 正确做法：先运行 `schedule --output json`，检查 `route_ready`。如果为 `false`，明确告知用户"后台推送尚未就绪，需要先和 bot 对话一次来捕获推送路由"
- WRONG: "Background push is all set!" (without checking route_ready)
- CORRECT: Check `schedule --output json` → if `route_ready: false`, tell the user delivery is not yet armed

## Quick Start / 快速开始

```bash
# Install (OpenClaw users) / 安装（OpenClaw 用户）
clawhub install signalradar

# Or clone directly / 或直接克隆
git clone https://github.com/vahnxu/signalradar.git && cd signalradar

# 1. Health check / 健康检查
python3 scripts/signalradar.py doctor --output json

# 2. Add markets (guided setup or by URL) / 添加市场（引导式或通过链接）
python3 scripts/signalradar.py add
python3 scripts/signalradar.py add https://polymarket.com/event/your-market-here

# 3. Monitoring auto-starts after first add (every 10 min)
# 首次添加后自动启动监控（每 10 分钟）

# 4. Check schedule status / 查看调度状态
python3 scripts/signalradar.py schedule

# 5. Manual check (dry-run) / 手动检查（试运行）
python3 scripts/signalradar.py run --dry-run --output json
```

## Common Tasks / 常用操作

### Add a market / 添加市场

```bash
python3 scripts/signalradar.py add                              # Guided setup / 引导式添加
python3 scripts/signalradar.py add <polymarket-event-url> [--category <name>]
```

Flow: parse URL → query Polymarket API → show market question + current probability → user confirms → record baseline.

流程：解析链接 → 查询 Polymarket API → 显示市场问题 + 当前概率 → 用户确认 → 记录基线。

- If the event has multiple markets (e.g., different date brackets), the CLI shows all markets with their current probabilities before adding. For large events (>3 markets), it also shows a type summary and forces interactive confirmation even if `--yes` was passed.
  如果事件包含多个市场（如不同日期区间），CLI 会先展示所有市场及当前概率。大事件（>3 个市场）还会显示类型摘要，并且即使传了 `--yes` 也会强制要求交互确认。
- If some markets from the event are already monitored, only new ones are added.
  如果事件中部分市场已在监控，只添加新的。
- If the market is settled/expired, a warning is shown but the user can still add it.
  如果市场已结算/过期，会显示警告，但用户仍可添加。
- Category defaults to `default` if not specified. User is not prompted for category.
  分类默认为 `default`。不会提示用户选择分类。
- On first-ever add (empty watchlist), a brief explanation of the baseline concept is shown.
  首次添加（空监控列表）时，会简要解释基线概念。

### List monitors / 查看监控列表

```bash
python3 scripts/signalradar.py list [--category <name>] [--archived]
```

Shows all entries grouped by category with global sequential numbering. Each entry shows: number, question, last-known probability (from local baseline cache), end date.

按分类分组显示所有条目，使用全局顺序编号。每条显示：编号、市场问题、最近一次基线概率（本地缓存）、结束时间。

`--archived` shows previously removed entries (preserved for export).
`--archived` 显示之前移除的条目（保留用于导出）。

### Show one monitored market / 查看单个监控市场

```bash
python3 scripts/signalradar.py show <number-or-keyword> [--output json]
```

Looks up one or more monitored markets by list number or keyword, fetches current probability, and returns a read-only snapshot without updating baselines.

按列表编号或关键词查找一个或多个已监控市场，获取当前概率，并返回只读快照，不更新基线。

### Remove a monitor / 移除监控

```bash
python3 scripts/signalradar.py remove <number>
```

Shows the entry name and asks for confirmation before removing. Removed entries are archived (moved to `archived` array in `~/.signalradar/config/watchlist.json`) with full history preserved.

显示条目名称并在移除前要求确认。移除的条目会被归档（移至 `~/.signalradar/config/watchlist.json` 的 `archived` 数组），完整历史保留。

### Run a check / 执行检查

```bash
python3 scripts/signalradar.py run [--dry-run] [--output json]
```

Checks all active entries against Polymarket API. If probability change exceeds threshold, sends alert via configured delivery channel.

检查所有活跃条目的 Polymarket 概率。如果变化超过阈值，通过配置的推送通道发送警报。

- Settled/expired entries are skipped during run, with a summary at the end: "N entries settled, consider removing."
  已结算/过期的条目在运行时跳过，结尾汇总提示："N 个条目已结算，建议移除。"
- When multiple markets trigger in the same run, they are listed in the same notification. Current v0.8.3 does not collapse realtime HIT alerts into event-level groups.
  同一次运行中多个市场同时触发时，会列在同一条通知里。当前 v0.8.3 的实时 HIT 通知还不会进一步按事件折叠。
- After a HIT is pushed, the baseline updates to the new probability value. The notification text includes "baseline updated to XX%."
  HIT 推送后，基线更新为新的概率值。通知文本包含"基线已更新至 XX%"。
- `--dry-run` fetches and evaluates but writes no state.
  `--dry-run` 只获取和评估，不写入任何状态。
- `--output openclaw` is reserved for platform background runs. It emits `HEARTBEAT_OK` on quiet checks, user-ready HIT text on realtime alerts, and digest text when a scheduled digest is due and the primary delivery channel is `openclaw`.
  `--output openclaw` 预留给平台后台任务使用。静默检查时输出 `HEARTBEAT_OK`；当主推送通道为 `openclaw` 时，实时命中会输出可直接发送给用户的警报文本；若定期报告到点，也会输出周报文本。

### Manage schedule / 管理调度

```bash
python3 scripts/signalradar.py schedule                        # Show current status / 显示当前状态
python3 scripts/signalradar.py schedule 10                     # Auto driver (crontab-first) / 自动选择驱动（优先 crontab）
python3 scripts/signalradar.py schedule 10 --driver openclaw   # Force openclaw cron / 强制使用 openclaw cron
python3 scripts/signalradar.py schedule 10 --driver crontab    # Force system crontab / 强制使用系统 crontab
python3 scripts/signalradar.py schedule disable                # Disable auto-monitoring / 禁用自动监控
```

### Generate or preview digest / 生成或预览周报

```bash
python3 scripts/signalradar.py digest
python3 scripts/signalradar.py digest --dry-run
python3 scripts/signalradar.py digest --force
python3 scripts/signalradar.py digest --output json
python3 scripts/signalradar.py digest --output openclaw --force
```

`digest` compares the current monitored state with the previous digest snapshot, not with per-run baselines.
`digest` 比较的是“当前监控状态”与“上一份周报快照”，不是单次运行基线。

### View or change config / 查看或修改配置

```bash
python3 scripts/signalradar.py config                          # Show all settings / 显示所有设置
python3 scripts/signalradar.py config check_interval_minutes   # Show one setting / 显示单项设置
python3 scripts/signalradar.py config threshold.abs_pp 8.0     # Change threshold / 修改阈值
```

### Health check / 健康检查

```bash
python3 scripts/signalradar.py doctor --output json
```

Returns `{"status": "HEALTHY"}` if Python version and network connectivity are OK.
如果 Python 版本和网络连接正常，返回 `{"status": "HEALTHY"}`。

## Understanding Results / 理解运行结果

| Status | Meaning / 含义 | Action / 操作 |
|--------|----------------|---------------|
| `BASELINE` | First observation for an entry / 条目的首次观测 | Baseline recorded; no alert sent / 记录基线，不发送警报 |
| `HIT` | Change exceeds threshold / 变化超过阈值 | Alert sent via delivery channel; baseline updated / 通过推送通道发送警报，基线更新 |
| `NO_REPLY` | No entries crossed threshold / 无条目超过阈值 | Nothing to report / 无需报告 |
| `SILENT` | Change below threshold / 变化低于阈值 | No alert sent / 不发送警报 |

### HIT output example / HIT 输出示例

```json
{
  "status": "HIT",
  "request_id": "9f98e47e-6e0e-4563-b7c8-87a3b19e97af",
  "hits": [
    {
      "entry_id": "polymarket:12345:gpt5-release-june:evt_67890",
      "slug": "gpt5-release-june",
      "question": "GPT-5 released by June 30, 2026?",
      "current": 0.41,
      "baseline": 0.32,
      "abs_pp": 9.0,
      "confidence": "high",
      "reason": "abs_pp 9.0 >= threshold 5.0"
    }
  ],
  "ts": "2026-03-02T08:00:00Z"
}
```

When presenting a HIT to the user / 向用户展示 HIT 时：
> **GPT-5 released by June 30, 2026?**: 32% → 41% (+9pp), threshold 5pp crossed. Baseline updated to 41%.
> **GPT-5 在 2026 年 6 月 30 日前发布？**：32% → 41%（+9pp），超过 5pp 阈值。基线已更新至 41%。

### Same-event grouped HIT / 同事件合并 HIT

When multiple markets from the same event trigger / 同一事件多个市场同时触发时：
> **Bitcoin price (March 31)** — 3 markets crossed threshold:
> - BTC > $100k: 45% → 58% (+13pp), baseline updated to 58%
> - BTC > $110k: 23% → 35% (+12pp), baseline updated to 35%
> - BTC > $120k:  8% → 19% (+11pp), baseline updated to 19%

### Empty watchlist / 空监控列表

If there are no entries, run returns / 如果没有条目，run 返回：
```json
{"status": "NO_REPLY", "message": "Watchlist is empty. Use 'signalradar.py add <url>' to add entries."}
```

## Configuration (Optional) / 配置（可选）

All settings have sensible defaults. Runtime configuration lives at `~/.signalradar/config/signalradar_config.json`.
所有设置都有合理的默认值。运行时配置文件位于 `~/.signalradar/config/signalradar_config.json`。

| Setting / 设置 | Default / 默认值 | Description / 说明 |
|----------------|-------------------|---------------------|
| `threshold.abs_pp` | 5.0 | Global threshold in percentage points / 全局阈值（百分点） |
| `threshold.per_category_abs_pp` | `{}` | Per-category override / 按分类覆盖阈值，如 `{"AI": 4.0}` |
| `threshold.per_entry_abs_pp` | `{}` | Per-entry override, key = entry_id / 按条目覆盖阈值 |
| `delivery.primary.channel` | `openclaw` | `openclaw`, `file`, or `webhook` / 推送通道 |
| `delivery.primary.target` | `direct` | Path (file) or URL (webhook) / 文件路径或 webhook 地址 |
| `digest.frequency` | `weekly` | `off` / `daily` / `weekly` / `biweekly` / 定期报告频率 |
| `digest.day_of_week` | `monday` | Weekly / biweekly digest weekday / 周报发送星期 |
| `digest.time_local` | `09:00` | Digest local send time / 周报本地发送时间 |
| `digest.top_n` | `10` | Max movers shown in human-readable digest / 周报文本展示的最大变化条目数 |
| `baseline.cleanup_after_expiry_days` | 90 | Days after market end date to clean up baseline / 市场到期后清理基线的天数 |
| `profile.timezone` | `Asia/Shanghai` | Display timezone / 显示时区 |
| `profile.language` | `""` | System-message locale (`zh` / `en`); empty = automatic detection (env first, timezone fallback) / 系统文案语言，空值=自动识别（优先环境变量，其次时区回退） |

### Delivery adapters / 推送适配器

- **`webhook`** (recommended / 推荐) — HTTP POST to external endpoint. Set `target` to webhook URL. Works with Slack, Telegram Bot API, Discord, or any HTTP endpoint. Fully portable across all platforms (OpenClaw, Claude Code, standalone). When paired with `crontab` scheduling driver, delivers notifications with zero LLM cost and zero platform dependency.
  HTTP POST 到外部端点。将 `target` 设为 webhook 地址。支持 Slack、Telegram Bot API、Discord 或任意 HTTP 端点。完全可移植，在任何平台（OpenClaw、Claude Code、独立部署）上均可使用。配合 `crontab` 调度驱动，实现零 LLM 成本、零平台依赖的推送。
- **`file`** — appends alerts to a local JSONL file. Set `target` to file path. Portable across all platforms.
  将警报追加写入本地 JSONL 文件。将 `target` 设为文件路径。可跨平台使用。
- **`openclaw`** (OpenClaw-only / 仅 OpenClaw) — OpenClaw 平台集成选项。交互式对话中 Agent 回复即通知；后台通过 `openclaw cron` announce 推送。不可移植到其他平台。
  OpenClaw platform integration. In interactive chat, Agent reply IS the notification; background delivery via `openclaw cron` announce. Not portable to other platforms.

When user asks to set up notifications, recommend `webhook` first (portable, zero platform dependency). Explain that `openclaw` works automatically in OpenClaw interactive chat but is not portable.
当用户要求设置推送通知时，优先推荐 `webhook`（可移植，零平台依赖）。说明 `openclaw` 在 OpenClaw 交互对话中自动生效但不可移植。

For full configuration reference, see `references/config.md`.
完整配置参考请查看 `references/config.md`。

## Periodic Report / 定期报告

SignalRadar v0.8.3 implements digest reporting. The digest uses the same delivery channel family as HIT alerts, but it compares against the previous digest snapshot instead of the per-run alert baseline.

SignalRadar v0.8.3 已实现定期报告。周报沿用与 HIT 相同的推送通道体系，但比较基线来自“上一份周报快照”，不是单次运行的告警基线。

Digest behavior / 周报行为：
- Includes both entries that already triggered realtime HIT alerts this period and entries that never crossed the realtime threshold but still changed net-over-period.
  同时包含“本期已经触发过实时 HIT 的条目”和“虽然没触发实时阈值、但周期净变化仍然显著的条目”。
- Human-readable digest groups large multi-market events by event, shows only top movers, and avoids dumping every market into Telegram.
  面向人的周报会按事件折叠大规模多市场事件，只展示代表性变化，避免把所有市场逐条刷屏到 Telegram。
- Full detail remains available through `digest --output json`.
  完整明细通过 `digest --output json` 提供。
- Scheduled digest checks piggyback on normal monitoring runs; SignalRadar does not create a second standalone scheduler just for digest.
  定期报告复用正常监控调度触发；SignalRadar 不会为周报再创建第二套独立调度器。
- The first automatic digest after setup/update is bootstrap-only: SignalRadar writes the initial digest snapshot silently and starts user-facing digest delivery from the next report cycle. Use `digest --force` if you want an immediate preview now.
  首次自动周报是“静默建快照”：SignalRadar 会先写入初始周报快照，不立即打扰用户；真正面向用户的自动周报从下一个周期开始。若需要立刻预览，请使用 `digest --force`。

## Local State (What This Skill Writes) / 本地状态（此 Skill 写入的文件）

| Path / 路径 | Purpose / 用途 | When written / 写入时机 |
|--------------|----------------|-------------------------|
| `~/.signalradar/config/watchlist.json` | Monitored entries + archived entries / 监控条目 + 归档条目 | By `add` and `remove` commands / `add` 和 `remove` 命令执行时 |
| `~/.signalradar/cache/baselines/*.json` | Last-seen probability per market / 每个市场最后一次概率 | Every non-dry-run check / 每次非试运行的检查 |
| `~/.signalradar/cache/events/*.jsonl` | Audit log of all decisions / 所有决策的审计日志 | Every non-dry-run check / 每次非试运行的检查 |
| `~/.signalradar/cache/last_run.json` | Last run timestamp and status / 最后一次运行的时间戳和状态 | Every non-dry-run check / 每次非试运行的检查 |
| `~/.signalradar/cache/digest_state.json` | Last digest snapshot and report key / 上一份周报快照及周期标识 | After digest bootstrap or successful digest delivery / 首次静默建快照后，及每次周报成功发送后 |

- `--dry-run` fetches and evaluates without writing any state.
  `--dry-run` 只获取和评估，不写入任何状态。
- The human user (not Agent) may hand-edit `~/.signalradar/config/watchlist.json` (e.g., to change categories). The system tolerates manual edits. Agent must use CLI commands only — see CR-03.
  用户本人（非 Agent）可以手动编辑 `~/.signalradar/config/watchlist.json`（如更改分类）。系统兼容手动编辑。Agent 必须使用 CLI 命令——见 CR-03。
- Runtime state lives outside the skill directory under `~/.signalradar/`.
  运行时状态位于 skill 目录外的 `~/.signalradar/`。

## Scheduling / 调度

SignalRadar attempts to auto-enable 10-minute background monitoring after the first successful `add` or `onboard finalize` (v0.9.0). The default driver is system `crontab` with `--push` (zero LLM cost, delivers via `openclaw message send`); falls back to `openclaw cron` only when crontab is unavailable. **Route gate**: when `delivery.primary.channel == openclaw` + `crontab` driver + no captured reply route, the CLI refuses to arm and returns `route_missing` instead of silently enabling a cron job that cannot push.

SignalRadar 在首次 `add` 或 `onboard finalize` 成功后尝试自动启用 10 分钟后台监控（v0.9.0）。默认驱动是系统 `crontab` + `--push`（零 LLM 成本，通过 `openclaw message send` 推送）；仅在 crontab 不可用时回退到 `openclaw cron`。**Route gate**：当推送通道为 `openclaw` + `crontab` 驱动 + 尚无已捕获的 reply route 时，CLI 拒绝启用 cron 任务并返回 `route_missing`，不会静默启用无法推送的调度。

On the first successful `add`, if `profile.language` is still empty, SignalRadar snapshots the detected system-message language into user config so background cron notifications remain stable.
首次 `add` 成功时，如果 `profile.language` 仍为空，SignalRadar 会把检测到的系统文案语言写入用户配置，避免后台 cron 路径再依赖瞬时环境推断。

Manage via the `schedule` command / 通过 `schedule` 命令管理：

```bash
signalradar.py schedule              # Show current status / 显示当前状态
signalradar.py schedule 30           # Auto driver (crontab-first) / 自动选择驱动（优先 crontab）
signalradar.py schedule disable      # Disable auto-monitoring completely / 完全禁用自动监控
signalradar.py schedule 10 --driver openclaw  # Force openclaw cron / 强制使用 openclaw cron
signalradar.py schedule 10 --driver crontab   # Force system crontab / 强制使用系统 crontab
```

Minimum interval: 5 minutes (prevents overlapping runs).
最小间隔：5 分钟（防止运行重叠）。

### Threshold vs Frequency / 阈值 vs 频率

- **Threshold / 阈值** controls *sensitivity* — how much a probability must change before an alert fires. Managed per-category or per-entry via `signalradar.py config`.
  控制*灵敏度*——概率需要变化多少才会触发警报。通过 `signalradar.py config` 按分类或按条目管理。
- **Frequency / 频率** controls *how often* SignalRadar checks markets. Managed globally via `signalradar.py schedule`.
  控制 SignalRadar *多久检查一次*市场。通过 `signalradar.py schedule` 全局管理。

These are independent: a 5pp threshold with 10-minute frequency checks every 10 minutes and alerts on 5pp+ changes. A 3pp threshold with 30-minute frequency checks less often but is more sensitive when it does.

二者独立：5pp 阈值 + 10 分钟频率 = 每 10 分钟检查一次，5pp 以上变化时警报。3pp 阈值 + 30 分钟频率 = 检查频率低但灵敏度更高。

## Troubleshooting / 故障排除

| Error Code / 错误码 | Cause / 原因 | Fix / 修复 |
|---------------------|-------------|------------|
| `SR_TIMEOUT` | Polymarket API timeout / API 超时 | Check network; retry after 30s / 检查网络，30 秒后重试 |
| `SR_SOURCE_UNAVAILABLE` | Cannot reach gamma-api.polymarket.com / 无法连接 API | Verify DNS and internet access / 检查 DNS 和网络 |
| `SR_VALIDATION_ERROR` | Malformed entry data / 条目数据格式错误 | Run `python3 scripts/validate_schema.py` / 运行验证脚本 |
| `SR_ROUTE_FAILURE` | Delivery adapter failed / 推送适配器失败 | Check delivery config / 检查推送配置 |
| `SR_CONFIG_CONFLICT` | Contradictory config values / 配置值冲突 | Review config for duplicate keys / 检查配置是否有重复键 |
| `SR_PERMISSION_DENIED` | Insufficient permissions / 权限不足 | Check file permissions on config/ and cache/ / 检查文件权限 |

## AI Agent 指令（完整版） / AI Agent Instructions

### 默认行为 / Agent Default Behavior

Agent 在执行 SignalRadar 命令时，应遵循以下默认行为：

**命令输出处理**：Agent 应使用 `--output json` 获取结构化数据，然后自己翻译为用户友好的自然语言消息发送给用户。禁止将原始 JSON 或状态码直接发给用户。
Use `--output json` to get structured data, then translate it to user-friendly natural language. Never send raw JSON or status codes to the user.

**run vs run --dry-run 选择**：
- 用户明确要求检查（"检查一下"/"跑一下"）→ 使用 `run`（会更新基线）
- Agent 想展示当前状态但不确定用户是否想更新基线 → 使用 `run --dry-run`（只读不写）
- User explicitly asks to check → `run` (updates baselines)
- Agent wants to show status but unsure about updating → `run --dry-run` (read-only)

**网络错误处理**：收到 `SR_TIMEOUT` 或 `SR_SOURCE_UNAVAILABLE` 时，Agent 应告知用户"Polymarket API 暂时无法访问，请稍后再试"，不要自动重试。
On `SR_TIMEOUT` or `SR_SOURCE_UNAVAILABLE`, tell user "Polymarket API temporarily unavailable, please try later." Do not auto-retry.

**已结算市场处理**：添加已结算/过期的市场时，Agent 应主动告知用户"这个市场已结算，添加后不会产生新的警报。确定要添加吗？"让用户决定。
When adding settled/expired markets, proactively tell user: "This market is settled. Adding it won't produce new alerts. Still add?" Let user decide.

**单市场查询优先用 `show`**：如果用户问"那个 GPT 概率多少了"，优先运行 `show <关键词或编号>`。只有在用户明确要"顺便检查全部市场"时才用 `run`。
For single-market lookups, prefer `show <keyword-or-number>`. Use `run` only when the user wants a full check of all monitored markets.

### 结果展示 / Presenting Results

禁止将原始状态码（NO_REPLY、HIT、BASELINE、SILENT、ERROR）直接发送给用户。必须翻译为自然语言。
NEVER output raw status codes directly to user. Always translate to natural language.

- **HIT**：始终显示市场问题、概率变化（旧% → 新%）、变化幅度（pp），以及"基线已更新至 X%"。同一事件多个市场触发时合并展示。
  Always show market question, probability change (old% → new%), magnitude in pp, and "baseline updated to X%". Group by event when multiple markets trigger.
- **BASELINE**：告诉用户"首次运行——已为 N 个市场记录基线。稍后再次运行以检测变化。"不要将 BASELINE 呈现为问题。
  Tell user: "First run — baselines recorded for N markets. Run again later to detect changes."
- **NO_REPLY**：简要确认"已检查所有市场，没有超过阈值的变化。"
  Briefly confirm: "All markets checked. No changes exceeded the threshold."
- **空监控列表**：引导用户添加市场："当前没有监控市场。发一个 Polymarket 链接给我，或者说'帮我加几个'浏览预置事件。"
  Guide user: "No markets monitored. Send me a Polymarket URL, or say 'add some' to browse presets."
- **DIGEST**：展示周报标题（注意根据频率说"日报"/"周报"/"双周报"）、活跃/新增/已结算条目数、变化最大的 top movers 列表，以及下次报告日期。如果是首次周报（无历史快照），说明"这是首份报告，暂无上期对比"。如果 `digest.frequency` 为 `off`，告知用户"定期报告已关闭"并说明如何开启（`config digest.frequency weekly`）。
  Show digest title (match frequency: "Daily"/"Weekly"/"Biweekly"), active/new/settled counts, top movers list, and next report date. For first digest (no previous snapshot), explain "This is the first report — no prior comparison available." If `digest.frequency` is `off`, tell user it's disabled and how to enable it.
- **用户说"没收到周报"**：运行 `digest --dry-run --output json` 诊断。根据返回字段判断：
  - `due: false` + `due_reason: "before_schedule"` → 告知下次周报时间（`scheduled_local` 字段）
  - `due: false` + `due_reason: "already_sent"` → 本期已发送过
  - `due: false` + `due_reason: "disabled"` → 周报已关闭，引导开启
  - `due: false` + `due_reason: "bootstrap_snapshot"` → 系统刚完成首轮静默建快照，真正的自动周报会从下一个周期开始
  - `first_report: true` → 首次运行，需等下一个报告周期
  When user says "I never got a digest": run `digest --dry-run --output json` and check `due`, `due_reason`, `first_report`, `scheduled_local` fields to diagnose.

### 禁止操作 / Prohibited Actions

- 禁止自动发现或建议添加市场。等待用户提供链接。
  Do not auto-discover or suggest markets to add. Wait for user.
- 禁止在 `schedule` 命令流程外创建 cron 任务。
  Do not create cron jobs outside of `schedule` command.
- Agent 禁止手动编辑 `~/.signalradar/cache/`、`~/.signalradar/config/watchlist.json` 或基线文件（见 CR-03）。
  Agent must not manually edit data files (see CR-03).
- 不要假设有模式——没有模式概念。直接运行 `signalradar.py run`。
  No modes exist. Just run `signalradar.py run`.
- 禁止提及或尝试使用 Notion 集成（已在 v0.5.0 中移除）。
  Do not mention Notion integration (removed in v0.5.0).
- 用户日常对话（"好的"/"没事"/"OK"/"知道了"）不是命令，禁止触发任何 signalradar 操作。
  Casual chat ("好的"/"OK"/"没事") is NOT a command. Do NOT trigger any signalradar operation.
- **禁止修改 delivery 通道设置**，除非用户明确要求。你就是 OpenClaw Bot，`openclaw` 通道 = 你回复用户。不要因为"没有 Telegram 渠道"而改配置——见"你是谁"。
  Do NOT change delivery channel unless user explicitly asks. You are OpenClaw Bot; `openclaw` channel = your reply to user. See "Platform Identity".

### 语言处理 / Language Handling

- 系统消息（HIT 通知、周报、运行状态文本）跟随 `profile.language`，支持 `zh` 和 `en`；空值时自动识别（优先环境变量，若后台环境没有语言上下文，则按配置时区回退，例如 `Asia/Shanghai` → `zh`）。
  System messages (HIT notifications, digest text, run status text) follow `profile.language`, supporting `zh` and `en`; empty values use automatic detection (environment first, then timezone fallback when background jobs have no locale context).
- 市场问题始终以 Polymarket API 返回的原始英文显示。不要翻译市场问题。
  Market questions always displayed in original English from API. Do not translate.

## References / 参考

- `references/config.md` — Full configuration reference / 完整配置参考
- `references/protocol.md` — Data contract (EntrySpec, SignalEvent, DeliveryEnvelope) / 数据契约
- `references/operations.md` — SLO targets, retry policy / SLO 目标、重试策略
