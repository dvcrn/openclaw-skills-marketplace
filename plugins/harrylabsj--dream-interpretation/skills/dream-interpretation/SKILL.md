---
name: dream-interpretation
description: "用中文理解并解读用户描述的梦境：优先上网搜索“周公解梦/解梦/梦见/梦到”相关中文资料，提炼传统民俗解释；当用户还想知道现实含义时，补充一段现代心理学视角。Use when the user describes a dream, asks“这个梦什么意思/帮我解梦/周公解梦/梦见XX代表什么/梦到XX是什么意思”, or wants a Chinese web-grounded dream interpretation rather than pure freeform speculation."
---

# Dream Interpretation

## Overview

Use this skill to turn a free-form dream description into a concise, internet-grounded 周公解梦 style interpretation. Prefer web evidence over guessing, and clearly separate commonly repeated interpretations from uncertainty.

## Workflow

1. Extract the key dream symbols, actions, people, places, objects, colors, and emotions from the user's description.
2. Search the web for 周公解梦 interpretations of the most important symbols and combinations.
3. Read 2-4 relevant sources and compare overlaps instead of trusting a single page.
4. Synthesize a short answer that explains:
   - the main symbols in the dream
   - the most common interpretation patterns
   - any conflicting or low-confidence points
5. If the dream is vague, ask 1-3 clarifying questions before interpreting.

## Search Strategy

Prefer Chinese queries and keep them concrete.

Recommended query patterns:

- `周公解梦 <核心意象>`
- `梦见 <核心意象> 周公解梦`
- `梦到 <动作> <对象> 解梦`
- `周公解梦 <意象A> <意象B>`

Examples:

- `周公解梦 掉牙`
- `梦见 蛇 周公解梦`
- `梦到 考试迟到 解梦`
- `周公解梦 飞行 追赶`

When the dream contains many details, prioritize the 1-3 strongest symbols rather than searching every minor element.

## Interpretation Rules

- Ground the answer in what multiple sources commonly say.
- Avoid presenting folklore as fact; frame it as a traditional interpretation.
- If sources disagree, say so directly.
- Do not invent citations or claim certainty you do not have.
- Keep the tone helpful and light; dream interpretation is suggestive, not diagnostic.
- Default to a dual-perspective answer for Chinese users: `周公解梦视角` + `现代心理学视角`.
- If the user explicitly wants only 周公解梦 or only 心理学解读, follow that preference.

## Response Pattern

Default structure:

### 梦里的关键信号
- List the top symbols or events.

### 周公解梦里常见的说法
- Summarize the overlapping interpretations from the sources.

### 现代心理学怎么看
- Give a grounded, non-mystical interpretation based on emotion, stress, recent experiences, unfinished concerns, relationships, or subconscious rehearsal.
- Keep this section clearly separate from folk explanations.

### 怎么理解更合适
- Offer a balanced takeaway tied to the user's dream details.

### 提醒
- Mention that 周公解梦属于传统民俗解读，仅供参考，不应代替现实判断。

## Clarification Triggers

Ask follow-up questions when any of these block a useful search:

- the main symbol is unclear
- multiple unrelated scenes are mixed together
- the dream depends on who a person is but their relationship is unknown
- the user only says "我做了个怪梦" without details

Example clarifying questions:

- 梦里最强烈的画面是什么？
- 你印象最深的是人物、动物，还是某个动作？
- 梦里你的情绪更偏紧张、害怕、开心，还是平静？

## Output Quality Bar

- Be concise by default.
- Use plain Chinese unless the user asks for another language.
- Prefer natural trigger language in Chinese user scenarios, especially phrases like：`帮我解梦`、`周公解梦`、`梦见XX什么意思`、`梦到XX代表什么`。
- Do not over-expand into mysticism.
- Cite source URLs or source names when the user asks for依据, or when confidence is low.
