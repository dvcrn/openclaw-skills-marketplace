# i18n Terminology (zh-CN / en-US)

## Scope

This file defines bilingual wording for `bazi-daily` output to keep Chinese and English responses semantically aligned.

## Translation Rules

1. Keep technical consistency across all sections in the 10-part response template.
2. Use `natal` for intrinsic chart context and `daily flow` for date-based context.
3. Keep evidence tags as internal canonical keys: `[B-结构]`, `[C-调候]`, `[A-原理]`.
4. In English output, optional display aliases are allowed: `[B-Structure]`, `[C-Climate]`, `[A-Principle]`.
5. Avoid deterministic wording; prefer probabilistic wording such as "tendency", "leaning", and "suggestion".

## Preferred Terminology

| 中文 | English | Type | Notes |
|---|---|---|---|
| 八字 | Bazi | keep pinyin | Keep `Bazi` capitalized. |
| 四柱 | Four Pillars | translatable | Year/Month/Day/Hour pillars. |
| 年柱/月柱/日柱/时柱 | Year/Month/Day/Hour Pillar | translatable | Keep slash-separated order when listed. |
| 流年 | Annual Flow | translatable | Date-based external cycle. |
| 流月 | Monthly Flow | translatable | Date-based external cycle. |
| 流日 | Daily Flow | translatable | Date-based external cycle. |
| 日主 | Day Master | translatable | Do not translate as "self master". |
| 十神 | Ten Gods | translatable | Fixed technical term in Bazi context. |
| 格局 | Structure Pattern | translatable | Avoid "格局=style/layout". |
| 成格/破格 | formed/broken structure | translatable | Use lower case in sentence flow. |
| 用神 | Yongshen (favorable element) | hybrid | Keep pinyin + brief gloss once per reply. |
| 忌神 | Jishen (unfavorable element) | hybrid | Keep pinyin + brief gloss once per reply. |
| 调候 | climate adjustment | translatable | Refers to thermal/moisture balancing logic. |
| 寒暖燥湿 | cold/warm/dry/damp balance | translatable | Keep four-way balance framing. |
| 月令 | month command | translatable | Do not translate as calendar month only. |
| 气机 | qi dynamics | hybrid | Keep `qi` as pinyin. |
| 喜忌 | favorable vs avoid | translatable | Used for action suggestions, not fate claims. |
| 宜 | Do Today | translatable | Actionable positive suggestions. |
| 忌 | Avoid Today | translatable | Actionable caution suggestions. |
| 命盘 | natal chart | translatable | Chart summary section wording. |
| 取用 | choose the useful principle | translatable | Can be paraphrased in English for clarity. |

## Forbidden / Discouraged Mappings

- Do not translate `十神` as "ten gods of destiny".
- Do not translate `气机` as "airflow" or "weather".
- Do not translate `调候` as generic "seasonal mood".
- Do not translate `用神` as "god of use" or "main god".
- Do not translate `格局` as "format", "layout", or "pattern design".

## Style Guidance by Language

- `zh-CN`: maintain concise classical-logic phrasing, but avoid fatalistic statements.
- `en-US`: keep domain terms precise and readable; add one-line gloss for hybrid terms when first mentioned.
- Both languages: preserve B->C->A sequencing and 10-section response structure.
