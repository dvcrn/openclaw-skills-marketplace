# ConvoAI Detail Collection

Reached from [intake](README.md) after ConvoAI is identified as the primary product.
This file is for ConvoAI-specific follow-up only.

## Language Detection

Detect the user's language from their most recent message:
- If the user writes in **Chinese** → use the **ZH** prompts below
- If the user writes in **English** (or any other language) → use the **EN** prompts below

Maintain the detected language consistently throughout the entire intake flow.

## Prerequisites

Before starting, the user should have:
- Completed the main kickoff intake
- A clear use case description
- Platform / client-stack context already collected if relevant
- Backend language already collected if relevant

## Questions

Use a friendly but explicit follow-up flow:
- Ask one question at a time
- Keep prompts short
- Skip anything the user already answered
- Do not group provider choices into a large form

Defaults policy:
- ASR vendor recommended default: `fengming`
- ASR language recommended default: `en-US` for clearly English scenarios, otherwise `zh-CN`
- LLM recommended default: `deepseek`
- TTS recommended default: `bytedance`

Blocking rule:
- Credentials status (Q1) must be explicitly answered or confirmed
- ASR vendor (Q4) must be explicitly answered or confirmed
- ASR language (Q5) must be explicitly answered or confirmed
- LLM provider (Q2) must be explicitly answered or confirmed
- TTS provider (Q3) must be explicitly answered or confirmed

"Use the default" counts as an explicit answer.
Silence, omission, or inference does NOT.

Ask **one at a time** only when needed. Skip any question the user already answered during main intake
or in the user's initial request.
Doc index status is already determined by the main intake — do not re-check here.

### Q1 — Credentials & App Certificate

**ZH:**
> "你有 Agora 账号和项目凭证吗？"
>
> 需要以下信息：
> - `AppID` — 项目标识
> - `App Certificate` — 是否已开启？
> - `Customer Key` + `Customer Secret` — 仅在使用 Basic Auth 鉴权时需要（ConvoAI 也支持 RTC Token 鉴权，此时不需要）
>
> 选择：
> - A. 都准备好了，App Certificate 已开启
> - B. 都准备好了，App Certificate 未开启（或不确定）
> - C. 有账号但还没创建项目
> - D. 还没有账号

**EN:**
> "Do you have an Agora account and project credentials?"
>
> Required:
> - `AppID` — project identifier
> - `App Certificate` — is it enabled?
> - `Customer Key` + `Customer Secret` — only needed for Basic Auth (ConvoAI also supports RTC Token auth, which doesn't require these)
>
> Options:
> - A. All ready, App Certificate is enabled
> - B. All ready, App Certificate is not enabled (or unsure)
> - C. Have an account but haven't created a project yet
> - D. Don't have an account yet

**If A** → Record `certificate = enabled`, token generation needed later.

| | Prompt |
|---|--------|
| ZH | "App Certificate 已开启，ConvoAI 创建 agent 时需要传入 RTC Token。我会在后续帮你生成 Token，需要用到 `AGORA_APP_CERTIFICATE` 环境变量。" |
| EN | "App Certificate is enabled. ConvoAI requires an RTC Token when creating an agent. I'll help you generate one later — you'll need the `AGORA_APP_CERTIFICATE` env var." |

**If B** → Record `certificate = not enabled`, token = empty string.

| | Prompt |
|---|--------|
| ZH | "如果后续在 Console 开启了 App Certificate，就需要改为传入 Token，否则 agent 会加入频道失败。" |
| EN | "If you enable App Certificate later in Console, you'll need to start passing a Token, otherwise the agent will fail to join the channel." |

**If C or D** → Direct to https://console.shengwang.cn/ and pause until ready.

### Q2 — LLM

**ZH:**
> "LLM 先用默认的 DeepSeek 可以吗？也可以指定其他供应商。"
> - A. 阿里云（aliyun）
> - B. 字节跳动（bytedance）
> - C. 深度求索（deepseek）
> - D. 腾讯（tencent）
> - E. 用默认的就行（deepseek）

**EN:**
> "Is it okay to start with the default LLM, DeepSeek? You can also choose another provider."
> - A. Alibaba Cloud (aliyun)
> - B. ByteDance (bytedance)
> - C. DeepSeek (deepseek)
> - D. Tencent (tencent)
> - E. Use the default (deepseek)

**Default:** deepseek

### Q3 — TTS

**ZH:**
> "TTS 先用默认的火山引擎可以吗？也可以指定其他供应商。"
> - A. 字节跳动 / 火山引擎（bytedance）
> - B. 微软（microsoft）
> - C. MiniMax（minimax）
> - D. 阿里 CosyVoice（cosyvoice）
> - E. 腾讯（tencent）
> - F. 阶跃星辰（stepfun）
> - G. 用默认的就行（bytedance）

**EN:**
> "Is it okay to start with the default TTS, ByteDance? You can also choose another provider."
> - A. ByteDance / Volcengine (bytedance)
> - B. Microsoft (microsoft)
> - C. MiniMax (minimax)
> - D. Alibaba CosyVoice (cosyvoice)
> - E. Tencent (tencent)
> - F. StepFun (stepfun)
> - G. Use the default (bytedance)

**Default:** bytedance (Volcengine TTS)

### Q4 — ASR Vendor

**ZH:**
> "ASR 先用默认的凤鸣可以吗？也可以指定其他供应商。"
> - A. 声网凤鸣（fengming）— 默认
> - B. 腾讯（tencent）
> - C. 微软（microsoft）
> - D. 科大讯飞（xfyun）
> - E. 科大讯飞大模型（xfyun_bigmodel）
> - F. 科大讯飞方言（xfyun_dialect）
> - G. 用默认的就行（fengming）

**EN:**
> "Is it okay to start with the default ASR, Fengming? You can also choose another provider."
> - A. Agora Fengming (fengming) — default
> - B. Tencent (tencent)
> - C. Microsoft (microsoft)
> - D. iFlytek (xfyun)
> - E. iFlytek BigModel (xfyun_bigmodel)
> - F. iFlytek Dialect (xfyun_dialect)
> - G. Use the default (fengming)

**Default:** fengming

### Q5 — ASR Language

Choose the recommended default from the use case:
- English use case -> `en-US`
- Chinese or unspecified use case -> `zh-CN`

Even when the recommended value is obvious, the user must still confirm or override it.

**ZH:**
> "识别语言先用默认的 [zh-CN / en-US] 可以吗？也可以指定其他语言。"
> - A. 中文（zh-CN，支持中英混合）
> - B. 英文（en-US）
> - C. 其他（请说明）
> - D. 用默认的就行

**EN:**
> "Is it okay to start with the default recognition language, [zh-CN / en-US]? You can also choose another language."
> - A. Chinese (zh-CN, supports Chinese-English mix)
> - B. English (en-US)
> - C. Other (please specify)
> - D. Use the default

**Default:** `en-US` for clearly English scenarios, otherwise `zh-CN`

---

## Output: Structured Spec

**ZH:**
```
ConvoAI 需求规格
─────────────────────────────
凭证状态：        [已就绪 / 需先创建]
App Certificate： [已开启 / 未开启]
Token：           [需要生成 / 空字符串]
ASR：             [fengming (default applied) / tencent / microsoft / xfyun / xfyun_bigmodel / xfyun_dialect]
ASR 语言：        [zh-CN (default applied) / en-US (default applied) / ja-JP / ko-KR / ...]
LLM：             [aliyun / bytedance / deepseek (default applied) / tencent]
TTS：             [bytedance (default applied) / minimax / tencent / microsoft / cosyvoice / stepfun]
─────────────────────────────
```

**EN:**
```
ConvoAI Spec
─────────────────────────────
Credentials:      [Ready / Need to create]
App Certificate:  [Enabled / Not enabled]
Token:            [Need to generate / Empty string]
ASR:              [fengming (default applied) / tencent / microsoft / xfyun / xfyun_bigmodel / xfyun_dialect]
ASR Language:     [zh-CN (default applied) / en-US (default applied) / ja-JP / ko-KR / ...]
LLM:              [aliyun / bytedance / deepseek (default applied) / tencent]
TTS:              [bytedance (default applied) / minimax / tencent / microsoft / cosyvoice / stepfun]
─────────────────────────────
```

The backend language should come from the main kickoff summary rather than this file.

## Defaults

| Field | Default | Notes (ZH) | Notes (EN) |
|-------|---------|------------|------------|
| App Certificate | Not enabled | 如果用户不确定，按未开启处理，提醒后续开启需改传 Token | If user is unsure, treat as not enabled; remind them to pass Token if enabled later |
| ASR vendor | `fengming` | 推荐默认值，需由用户确认后才按 `default applied` 记录 | Recommended default; only record as `default applied` after user confirmation |
| ASR language | `zh-CN` / `en-US` | 推荐默认值，英文场景优先 `en-US`，其他场景优先 `zh-CN`；需用户确认 | Recommended default; prefer `en-US` for clearly English use cases, otherwise `zh-CN`; requires user confirmation |
| LLM vendor | `deepseek` | 推荐默认值，需由用户确认后才按 `default applied` 记录 | Recommended default; only record as `default applied` after user confirmation |
| TTS vendor | `bytedance` | 推荐默认值，需由用户确认后才按 `default applied` 记录 | Recommended default; only record as `default applied` after user confirmation |

> ASR/TTS/LLM valid values come from the /join API docs — see [convoai-restapi/start-agent.md](../references/conversational-ai/convoai-restapi/start-agent.md) for the /join schema and vendor params. Do not invent values.

## Route After Collection

Pass the structured spec to [conversational-ai](../references/conversational-ai/README.md).
The product module will use the spec to fetch the right docs and generate code.

Key routing hints:
- Dev = Go → run `bash skills/voice-ai-integration/scripts/fetch-doc-content.sh "docs://default/convoai/restful/get-started/quick-start-go"`
- Dev = Java → run `bash skills/voice-ai-integration/scripts/fetch-doc-content.sh "docs://default/convoai/restful/get-started/quick-start-java"`
- Dev = Python/curl → run `bash skills/voice-ai-integration/scripts/fetch-doc-content.sh "docs://default/convoai/restful/get-started/quick-start"`
- App Certificate = Enabled → also run [token-server](../references/token-server/README.md)
- If fetch fails → use Generation Rules + fallback URL
