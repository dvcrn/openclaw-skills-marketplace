# Quote Safety

## Purpose

Use this reference when the user asks for a quote, a famous line, a writer/poet citation, or anything that could tempt the model to invent attribution.

The rule is simple: **if attribution is not highly reliable, do not attribute**.

## Allowed outputs

### 1. Reliable attributed quote
Use only when highly confident that both the wording and the attribution are correct.

Format:

> 引用金句：……  
> —— 作者 / 作品

### 2. Non-attributed line
Use when the sentence is useful but the source is uncertain.

Format:

> 表达句：……

Do not imply that it is famous or sourced.

### 3. Original line
Use when no safe reliable quote is available or when a custom line fits better.

Format:

> 表达句：……

Do not force an "原创" label unless the user explicitly asks whether it is original.

## Hard rules

- Never fabricate a quote.
- Never guess an author.
- Never attach a famous name to a line just because it sounds plausible.
- Never use hedges like “好像是某某说的 / 据说出自 / 像某某写的” to smuggle in fake authority.
- Never output “某某风格名言 —— 某某”.

## Safe downgrade strategy

If any uncertainty exists, downgrade in this order:
1. Whitelist-backed reliable attributed quote
2. Non-attributed line
3. Custom natural line

When in doubt, choose 2.

## Red-flag cases

Treat these as high risk for false attribution:
- widely circulated internet lines with no clear source
- modern motivational one-liners often misattributed to classic writers
- short poetic lines that “sound like” Tagore, Rilke, Neruda, Borges, Pessoa, 鲁迅, 张爱玲, 三毛, etc.
- translated quotes with many conflicting versions
- lines remembered approximately rather than verbatim

## Response wording for uncertainty

Use phrases like:
- 这句话我不建议署名，避免误引。
- 这类表达适合改为无署名版本。
- 如果你要的是准确表达，我更建议用原创风格句。

Avoid verbose disclaimers. Keep the user-facing output clean.

## Reliability standard

Only attribute when you are highly confident in all three:
1. the wording is substantially correct
2. the author is correct
3. the work/source is correct when included

If any one of these is shaky, do not attribute.

## Examples

### Safe
> 原创风格句（非名人原句）：你难过的不是辛苦本身，而是那些没有回声的认真。

### Safe
> 表达句：有些疲惫，不是因为走太远，而是因为很久没人问你累不累。

### Unsafe
> 鲁迅说：有些疲惫，不是因为走太远，而是因为很久没人问你累不累。

### Unsafe
> 像泰戈尔写过的那样：……

## Crisis handling

If the user shows signs of self-harm, suicide, violence, or extreme despair:
- do not pivot into literary beautification
- respond with care first
- encourage reaching a trusted person or professional support
- if giving a line, keep it supportive and grounded, not romanticized
