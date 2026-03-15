---
name: provider-sync
description: "Sync provider model lists into OpenClaw config (dry-run preview → confirm → apply). Trigger: /provider_sync"
---

# Provider Sync

触发方式：在聊天里输入 `/provider_sync`。

## 交互式用法（默认，无按钮）
当你只发送 `/provider_sync`（不带任何参数）时，我会回复一组**蓝色命令选项**（可直接点击/复制发送）：

选 provider（默认 dry-run，不写配置）：
/provider_sync provider=cli-usa
/provider_sync provider=cliplus
/provider_sync provider=newapi
/provider_sync provider=all

新增 provider（向导）：
/provider_sync add

> 说明：这是“无 inline button 也能点选”的默认方案，任何环境都可用。
> 
> 你也可以一步到位直接写：/provider_sync provider=<cli-usa|cliplus|newapi|all>（默认 dry-run）。

## 适用场景
- 拉取上游 `/v1/models`（OpenAI 兼容）并同步到本地 `openclaw.json`
- 规范化模型字段（contextWindow/maxTokens/input/reasoning 等）
- 先预览差异（dry-run），确认后再写入（apply），写前自动备份
- （v2 默认）同步时会裁剪 `agents.defaults.models`，让 `/models` 菜单条目 **永远对齐** `models.providers.<provider>.models`

## v2 Breaking（重要）
- 默认会 prune `agents.defaults.models`（删除该 provider 下“上游不存在”的条目），避免 `/models` 里出现“菜单很多但不可用”。
- 如果你希望保留旧行为（不删除白名单条目），使用：`--no-prune-agent-aliases`

## 使用方法（推荐）
### 方式 A：交互式（默认）
- 发送：`/provider_sync`
- 然后在我返回的“蓝色命令选项”里点一个（或复制发送）：
  - /provider_sync provider=cli-usa
  - /provider_sync provider=cliplus
  - /provider_sync provider=newapi
  - /provider_sync provider=all
- 新增 provider：发送 /provider_sync add 进入文本向导（会先 dry-run 验证，再二次确认写入配置）

### 方式 B：直接带参数（一步到位）
把下面任意一行发出去即可（默认 dry-run）：
- `/provider_sync provider=cli-usa`
- `/provider_sync provider=cliplus`
- `/provider_sync provider=newapi`
- `/provider_sync provider=all`

### 方式 C：新增 provider（一步到位，非交互）
如果你不想走向导，也可以直接提供信息（私聊使用）：
- `/provider_sync add providerId=<id> baseUrl=<.../v1> apiKey=<可选>`
  - 注意：真正写入前仍会先 dry-run 验证，并二次确认

写入（会备份；仍建议先预览）：
- `/provider_sync provider=all mode=apply`

重启 Gateway（可选，生效更稳；会短暂断线）：
- `/restart`

### 指定 provider
- 预览：
  - `/provider_sync provider=cli-usa`
  - `/provider_sync provider=cliplus`
  - `/provider_sync provider=newapi`

## 权限/安全口径（默认建议）
- 群聊：仅允许 dry-run / check-only（只读）；不要在群聊写配置。
- 私聊：允许 apply（写入）与重启（需二次确认）。

## 重启封装（你要的“闭环”）
- 这个 skill 的脚本只负责“对比/写配置”。
- **重启属于网关级操作**，为避免误触，一般拆成第二步。
- 最简闭环就是：apply 完后直接发一次 `/restart`。

## 参数（与脚本对应）
- `provider=<id|all>`：必填（`all` 表示遍历 `models.providers` 下所有 provider）
- `mode=dry-run|check-only|apply`：默认 dry-run
- 其他高级参数（可选）：
  - `config=<path>`（默认 `/root/.openclaw/openclaw.json`）
  - `mapping=<path>`（默认 `references/mapping.openai-models.json`）
  - `profile=generic|gemini`
  - `probe=openai-responses,openai-completions`

## 备注（实现边界）
- 这个 skill 的“按钮面板”属于聊天交互层能力；在未启用 Telegram inlineButtons 的实例上，依然能用本文件提供的纯文本命令完成全部操作。
- 缓存：脚本会在写缓存前做敏感字段剔除（token/cookie/apiKey/authorization 等 key）。

## Main script
- `scripts/provider_sync.py`
