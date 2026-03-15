# Distillation Examples — Good vs Bad Sparks

A spark is NOT a quote of what the user said. It is a **distilled experience** covering the full causal chain, structured into six dimensions (WHEN, WHERE, WHY, HOW, RESULT, NOT).

Before writing each dimension, mentally reconstruct:
1. **WHEN** — What task/need was I handling when this became relevant?
2. **WHERE** — What environment? What platform? Who is the audience?
3. **WHY** — What was the causal chain? What did I do → what went wrong/right → why?
4. **HOW** — What is the actionable rule? One-line summary + expanded steps.
5. **RESULT** — What effect does following this produce? Quantify if possible.
6. **NOT** — When should this NOT be applied? What are the exceptions?

---

## Example 1: Image Generation (咖啡拉花)

**BAD — Shallow capture:**
```json
{
  "how": { "summary": "拉花要圆润", "detail": "不对，拉花应该更圆润" },
  "why": ""
}
```
Problems: "圆润" relative to what? No WHY, no WHEN, no NOT. Zero actionable context.

**GOOD — Full distillation:**
```json
{
  "source": "human_feedback",
  "domain": "图片生成.咖啡拉花",
  "knowledge_type": "rule",
  "when": {
    "trigger": "生成咖啡拉花图片",
    "conditions": ["心形图案", "写实风格"]
  },
  "where": {
    "scenario": "AI生图工具输出咖啡拉花效果图",
    "audience": "咖啡师/咖啡爱好者"
  },
  "why": "生成的心形图案顶部弧线过尖、两侧不对称。实际咖啡拉花因牛奶流体特性，线条天然柔和不会出现锐角。选圆润弧线而非锐角，因为流体力学决定了牛奶在咖啡表面的自然形态。",
  "how": {
    "summary": "咖啡拉花图片生成：所有线条应模拟流体特性，弧线圆润无锐角，心形顶部弧度≥底部",
    "detail": "生成拉花时在prompt中强调'smooth flowing lines, no sharp angles, natural milk foam texture'。心形图案确保顶部弧度大于底部。避免几何精确的对称，保留手工拉花的微小不对称感。"
  },
  "result": {
    "expected_outcome": "拉花图片更自然真实，用户满意度提升"
  },
  "not": [
    {"condition": "卡通/简笔画风格", "effect": "modify", "reason": "艺术化风格允许夸张线条，不必严格模拟流体"}
  ]
}
```

---

## Example 2: API Design (后端开发)

**BAD — Shallow capture:**
```json
{
  "how": { "summary": "用POST不用GET", "detail": "" },
  "why": ""
}
```

**GOOD — Full distillation:**
```json
{
  "source": "human_feedback",
  "domain": "后端开发.API设计",
  "knowledge_type": "rule",
  "when": {
    "trigger": "设计包含敏感数据或复杂嵌套条件的查询接口",
    "conditions": ["筛选条件含敏感ID", "参数需要嵌套结构"]
  },
  "where": {
    "scenario": "RESTful API设计",
    "audience": "后端开发者"
  },
  "why": "GET的query params会暴露在URL中被日志/浏览器历史记录/中间代理缓存捕获，敏感数据泄露风险高。且query params对复杂嵌套筛选表达力不足，需要反复URL编码。",
  "how": {
    "summary": "包含敏感数据或复杂嵌套条件的查询接口应使用POST+请求体，而非GET+query params",
    "detail": "将筛选条件放入POST请求体的JSON中，支持嵌套对象和数组。URL保持简洁如POST /api/orders/query。请求体示例：{\"customer_ids\": [...], \"date_range\": {...}}。"
  },
  "result": {
    "expected_outcome": "避免敏感数据泄露，支持任意复杂度的筛选条件"
  },
  "not": [
    {"condition": "简单公开查询(如分页、排序)", "effect": "skip", "reason": "无敏感数据且参数简单时GET更符合REST语义"}
  ]
}
```

---

## Example 3: Data Visualization (商务报告图表)

**BAD — Shallow capture:**
```json
{
  "how": { "summary": "图表颜色要好看", "detail": "" }
}
```

**GOOD — Full distillation:**
```json
{
  "source": "human_feedback",
  "domain": "数据可视化.商务报告图表",
  "knowledge_type": "preference",
  "when": {
    "trigger": "为商务报告生成图表",
    "conditions": ["正式场合", "面向管理层"]
  },
  "where": {
    "scenario": "季度营收报告、年度总结等正式商务文档",
    "audience": "企业管理层/投资人"
  },
  "why": "默认的红蓝绿高饱和配色在商务文档中显得不专业且视觉杂乱。低饱和色系传递专业感和信任感，浅金色作为强调色能有效突出关键数据点而不破坏整体沉稳基调。",
  "how": {
    "summary": "商务报告图表配色：主色深蓝+辅色灰蓝，仅用浅金色强调关键数据，避免高饱和多色",
    "detail": "主色深蓝(#2C3E50)用于主要数据系列，辅色灰蓝(#7F8C8D)用于次要数据，浅金(#F39C12)仅用于强调1-2个关键数据点。整体不超过3种颜色。"
  },
  "result": {
    "expected_outcome": "图表视觉更专业协调，符合商务审美"
  },
  "not": [
    {"condition": "面向C端用户的营销物料", "effect": "skip", "reason": "营销场景需要更鲜艳的配色吸引注意力"}
  ]
}
```

---

## Contextual Query Construction Examples

**BAD queries (too vague, will miss context-specific sparks):**
```
node SPARKER/index.js search "咖啡拉花" --domain=图片生成
node SPARKER/index.js search "API设计" --domain=后端开发
node SPARKER/index.js search "直播标题" --domain=直播策划
```

**GOOD queries (include scenario + task context):**
```
node SPARKER/index.js search "咖啡拉花 写实风格 图片生成 线条圆润" --domain=图片生成
node SPARKER/index.js search "订单查询API 包含敏感数据 筛选条件设计" --domain=后端开发
node SPARKER/index.js search "低客单价美妆 电商直播标题 紧迫感" --domain=直播策划
```

**Template:** `"<topic> <scenario/audience> <action/phase> <key constraints>"`

This matters because many sparks have boundary conditions — e.g., a spark about "直播开场用紧迫感话术" only applies to low-price items. Without "低客单价" in the query, you might retrieve and misapply it to a high-end product launch.

---

## Domain Naming Convention

- **Use the user's language** for domain names (Chinese users → Chinese domains)
- **Dot-separated sub-domains:** `咖啡烘焙.生豆选择`, `咖啡烘焙.烘焙曲线`
- **Consistency:** all sparks in the same domain must share the same root domain name
