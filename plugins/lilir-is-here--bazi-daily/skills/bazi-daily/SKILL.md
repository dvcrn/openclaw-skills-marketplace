---
name: bazi-daily
description: "面向“今日运势/今天适合做X吗/今日宜忌”与 “today’s fortune / is today good for X / what to do or avoid today” 的八字日运解读技能。自动读取当日日期并查询流年流月流日，结合用户四柱分析；首次用户无档案时先引导录入四柱并写入长期记忆。Supports both Chinese and English users with language-aware responses."
---

# Bazi Daily

## Knowledge Source Architecture (Mandatory)

将经典分为三个独立知识源，禁止混成单一“综合库”：

- A.《滴天髓》库（原则层）：用于“为什么”和方向性判断（气机、取用总纲、论命哲学）。
- B.《渊海子平》库（结构层）：用于格局判定、十神结构、用神框架（先定结构再谈细节）。
- C.《穷通宝鉴》库（调候层）：用于月令气候、寒暖燥湿与调候药方（对结构结论做气候校正）。

固定来源文件（优先包内 txt，PDF 仅人工回退）：
- `A.滴天髓`（优先）：`references/classics/A_滴天髓.txt`
- `B.渊海子平`（优先）：`references/classics/B_渊海子平.txt`
- `C.穷通宝鉴`（优先）：`references/classics/C_穷通宝鉴.txt`
- 若包内文本缺失，仅在操作者已显式提供对应 PDF 时再使用 PDF 回退；不要假设固定本机路径。

调用顺序必须是：`B 结构 -> C 调候 -> A 解释`。
路由细则见 [references/classic-sources-routing.md](references/classic-sources-routing.md)。

## Workflow

1. 识别触发意图。
2. 路由输出语言（见 `Language Routing Rules`）。
3. 从会话上下文提取 `user_id` 与 `user_timezone`。
4. 以用户时区自动计算 `today_local`（`YYYY-MM-DD`）。
5. 调 heartbeat `bazi_profile_get` 读取用户四柱档案。
6. 若未命中四柱档案，请用户补充四柱并调 heartbeat `bazi_profile_upsert` 写入长期记忆。
7. 根据 `today_local` 查询 `bazi_daily_calendar`。
8. 按“五步编排”完成分析并输出结论、依据和建议。

默认年度数据源文件：`assets/bazi_daily_calendar_2026.csv`。
维护脚本：`scripts/import_bazi_calendar.py`。
经典文本预处理脚本：`scripts/extract_classics_text.py`。

术语与翻译约束见 [references/i18n-terminology.md](references/i18n-terminology.md)。

## Language Routing Rules

1. 输出语言优先级：`user_locale` > 最近一条用户消息语言检测 > 默认 `zh-CN`。
2. 支持语言仅限 `zh-CN` 与 `en-US`；其他 locale 统一回退到 `zh-CN`。
3. 语言检测回退只影响展示层，不改变分析流程与 `B->C->A` 推理顺序。
4. 证据标签内部键名固定保留中文：`[B-结构]`、`[C-调候]`、`[A-原理]`。
5. 英文展示时，可补充映射说明：`[B-Structure]`、`[C-Climate]`、`[A-Principle]`（仅展示映射，不替换内部标签）。
6. 回复时只输出单一语言版本，避免中英同屏重复。

## Five-Step Orchestration (Mandatory)

在通过日期与流运查询闸门后，必须按以下步骤执行：

1. `step1 解析命盘`
   - 提取四柱、十神分布、日主强弱初判、月令、格局候选（可多候选）。
2. `step2 结构优先（渊海子平）`
   - 用 B 库先判结构与格局成立条件，给出主格/兼格与用神框架。
3. `step3 调候校正（穷通宝鉴）`
   - 用 C 库对寒暖燥湿做修正，必要时覆盖或微调 step2 的用神次序。
4. `step4 气机解释（滴天髓）`
   - 用 A 库解释最终结论背后的气机逻辑，使结论成体系、可说明。
5. `step5 输出`
   - 输出“结论 + 依据 + 建议”，并标明依据来自 A/B/C 哪一类规则。

## Mandatory Pre-Analysis Gates

每次输出运势分析前，必须先完成以下两个步骤：
1. 获取当前日期：基于 `user_timezone` 计算 `today_local`（`YYYY-MM-DD`）。
2. 查询数据表：使用 `today_local` 查询 `bazi_daily_calendar` 以获取 `flow_year`、`flow_month`、`flow_day`。

未完成以上两个步骤时，禁止进入“运势结论/宜忌建议”输出。

## Trigger Phrases

将下列表达视为高优先级触发：
- “今日运势”
- “今天适合 xxx 吗？”
- “今天宜做什么/忌做什么？”
- “我今天的运气怎么样？”
- “帮我看今天的八字运势”
- "today's fortune"
- "is today good for xxx?"
- "what should I do or avoid today?"
- "how is my luck today?"
- "check my bazi luck for today"

若用户没有显式说“八字”，但语义是“今天是否适合某事”，默认按本技能流程处理。

## First-Time Onboarding

当找不到用户四柱记忆时：
1. 明确告知需要四柱后才能进行个性化日运分析（按输出语言选择模板）：
   - `zh-CN`: “要做个性化今日运势解读，我需要你的八字四柱（年柱/月柱/日柱/时柱）。”
   - `en-US`: "To provide a personalized daily reading, I need your Four Pillars (Year/Month/Day/Hour)."
2. 请用户直接提供四柱，格式优先：`年柱/月柱/日柱/时柱`（英文可接受 `Year/Month/Day/Hour Pillars`）。
3. 若用户不清楚四柱，建议使用可信的万年历或四柱排盘工具查询后再回传（英文提示可说明 “look up Four Pillars and send back”）。
4. 校验最小完整性（四柱都存在）。
5. 调 heartbeat `bazi_profile_upsert` 将结构化结果写入长期记忆。
6. 写入成功后继续本次分析，不要求用户重新提问。

长期记忆建议键：
- `bazi_profile.pillars.year`
- `bazi_profile.pillars.month`
- `bazi_profile.pillars.day`
- `bazi_profile.pillars.hour`
- `bazi_profile.source`（如 `user_provided`）
- `bazi_profile.updated_at`（ISO 日期时间）

若用户后续主动更正四柱，以最新输入覆盖旧值。

heartbeat 请求响应与错误码约定见 [references/heartbeat-contract.md](references/heartbeat-contract.md)。

## Date And Lookup Rules

1. 自动读取当前日期，禁止要求用户手动输入日期。
2. 优先使用会话上下文中的 `user_timezone` 计算当日日期。
3. 若 `user_timezone` 缺失，回退 `Asia/Shanghai` 并记录 `timezone_fallback=true`。
4. 查询数据表时使用标准日期键（`YYYY-MM-DD`），即 `today_local`。
5. 期望查得字段：`flow_year`、`flow_month`、`flow_day`。
6. 若当天无记录，明确告知“缺少当日流运数据”，并仅给出有限建议，不伪造结果。
7. 每次运势分析请求都必须执行一次日期计算与一次数据表查询，不得跳过。

数据表字段约定见 [references/bazi-calendar-schema.md](references/bazi-calendar-schema.md)。
数据文件导入规范见 [references/bazi-calendar-schema.md](references/bazi-calendar-schema.md) 中的 “Data Source File” 与 “Import Mapping”。
## Analysis Rules

1. 结构判定优先级高于主观经验；先判“是否成格/破格”，再谈强弱喜忌。
2. 调候可修正结构结论，但不可跳过结构直接给药方。
3. 解释层必须回扣气机，不得只给“吉/凶”标签。
4. 明确区分三类依据：
- 结构依据（B《渊海子平》）
- 调候依据（C《穷通宝鉴》）
- 原理依据（A《滴天髓》）
5. 先给“今日总体倾向”，再回答用户具体问题，再给“宜/忌”。
6. 输出“宜”与“忌”各 2-4 条，保持可执行。
7. 避免绝对化、宿命化表达；用“倾向/建议”措辞。

## Evidence Tagging Rules

每条关键结论至少绑定一个来源标签：

- `[B-结构]`：格局、十神结构、用神框架判断。
- `[C-调候]`：寒暖燥湿、月令气候修正。
- `[A-原理]`：气机方向、总纲解释。

若三源结论冲突，按优先级处理并显式说明：
1. 先保留 `B` 的结构边界；
2. 再用 `C` 做季节性校正；
3. 最后用 `A` 解释“为何这样取舍”。

## Failure Handling

1. heartbeat 读取失败时，按“未知档案”处理并进入首次引导；同时按输出语言提示：
   - `zh-CN`: “记忆服务暂不可用，本次可先临时分析。”
   - `en-US`: "Memory service is temporarily unavailable. I can still provide a one-time analysis."
   若用户不清楚四柱，补充建议其使用可信排盘工具查询四柱。
2. heartbeat 写入失败时，继续使用用户本次输入完成分析；同时按输出语言提示：
   - `zh-CN`: “本次已解读，但暂未保存，下次可能需要再次提供。”
   - `en-US`: "This reading is complete, but it wasn't saved. You may need to provide your pillars again next time."
3. 当日流运缺失时，必须先确认“已执行当日查询且未命中”，再按输出语言提示：
   - `zh-CN`: “缺少当日流运数据，仅基于四柱给出有限建议。”
   - `en-US`: "Today's flow data is missing. I can only provide limited guidance based on your natal pillars."

## Response Template

按以下顺序组织回答（中英文都必须保持同一 10 段结构）：
1. 今日日期 / Date (`YYYY-MM-DD`)
2. 当日流运 / Daily Flows（流年/流月/流日）
3. 命盘摘要 / Natal Summary（十神/强弱初判/月令/格局候选）
4. 结构结论 / Structure Verdict（`[B-结构]`）
5. 调候校正 / Climate Adjustment（`[C-调候]`）
6. 气机解释 / Principle Rationale（`[A-原理]`）
7. 对用户提问的直接结论 / Direct Answer
8. 今日“宜”列表 / Do Today（2-4 条）
9. 今日“忌”列表 / Avoid Today（2-4 条）
10. 一句风险提示 / Risk Note（非决定性，仅供参考）

## Guardrails

- 不编造缺失的四柱与流运数据。
- 不编造经典原文；如记忆不确定，改用“原则性转述”并标注“意译”。
- 不输出医疗、法律、投资等确定性结论。
- 用户未提供时柱时，不自动推断；要求补全。
- 禁止跳过 `B->C->A` 顺序直接下结论。

## Logging Suggestions

建议每次请求记录以下字段，便于排障与 UAT 复盘：
- `user_id`
- `user_timezone`
- `user_locale`
- `output_language`
- `language_detection_source`（`user_locale|message_detected|default`）
- `today_local`
- `timezone_fallback`
- `memory_hit`
- `calendar_hit`
- `heartbeat_get_status`
- `heartbeat_upsert_status`
- `structure_source_hit`（B）
- `climate_source_hit`（C）
- `principle_source_hit`（A）
- `final_yongshen_framework`
- `climate_adjustment_applied`

## UAT Cases

1. 首次用户输入“今日运势”，期望：要求四柱 -> heartbeat 写入成功 -> 返回完整解读。
2. 同一用户再次输入“今天适合谈合作吗？”，期望：不再询问四柱，直接返回结论与宜忌。
3. 用户时区为 `Asia/Shanghai`，在 00:05 与 23:55 测试，期望：`today_local` 与用户本地日期一致。
4. 构造当日无流运记录，期望：输出缺失提示，不编造流年流月流日。
5. 模拟 heartbeat upsert 失败，期望：本次照常解读，附“未保存”提示。
6. 模拟 heartbeat get 失败，期望：进入首次引导，流程不断。
7. 构造“结构与调候结论不一致”案例，期望：输出中明确展示 `B->C->A` 取舍链路。
8. 检查回答文本，期望：关键结论至少各含一个 `[B-结构]/[C-调候]/[A-原理]` 标签。
