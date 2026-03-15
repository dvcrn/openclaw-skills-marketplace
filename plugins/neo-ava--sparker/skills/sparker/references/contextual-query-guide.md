# Contextual Query Construction Guide

## Why Context Matters

Many sparks have boundary conditions. A spark about "直播开场用紧迫感话术" only applies to low-price items. Without "低客单价" in the query, you might retrieve and misapply it to a high-end product launch.

## Query Template

```
"<topic> <scenario/audience> <action/phase> <key constraints>"
```

Before constructing the query, identify:
1. **What** — the task topic
2. **For whom / what scenario** — the target context
3. **What phase / action** — what you're about to do

## Examples

**BAD (too vague):**
```
"咖啡拉花"
"API设计"
"直播标题"
```

**GOOD (include scenario + task context):**
```
"咖啡拉花 写实风格 图片生成 线条圆润"
"订单查询API 包含敏感数据 筛选条件设计"
"低客单价美妆 电商直播标题 紧迫感"
```

## SparkHub Credits

Hub search costs 1 credit per unfamiliar spark retrieved (already-owned sparks are free).

If `insufficient_balance: true` is returned:
1. Inform the user once: "SparkHub credits insufficient. You can top up on SparkHub or earn credits by publishing quality sparks."
2. Switch to local-only search (`--local`) for the rest of the session.
3. Do NOT repeat the reminder — once per session is enough.

If `partial_purchase: true`, some results could not be retrieved due to mid-search balance depletion.
