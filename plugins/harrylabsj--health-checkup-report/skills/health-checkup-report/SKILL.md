---
name: health-checkup-report
description: "Interpret routine health checkup reports and lab results in plain Chinese, highlighting abnormal items, likely meaning, urgency, follow-up questions, and practical next steps. Use when the user shares a体检报告、化验单、检查结果、检验指标、异常箭头项目, asks what abnormal results mean, or wants a structured non-diagnostic explanation rather than raw numbers only."
---

# Health Checkup Report

## Overview

Use this skill to explain common health checkup and lab report findings in a calm, structured way. Focus on helping the user understand what each flagged item may mean, what is worth paying attention to, and what next step is reasonable.

This skill is **not** for diagnosing disease. It should explain, prioritize, and suggest appropriate follow-up.

## Workflow

1. Identify the report type and available context:
   - annual physical exam / 体检报告
   - blood routine / urine routine / liver function / kidney function / blood lipids / blood glucose
   - imaging or ultrasound summary
   - tumor marker or specialty test
2. Extract:
   - test item names
   - numeric values
   - reference ranges
   - high/low flags
   - age/sex if provided
3. Start with the abnormal or borderline items, then mention major normal findings only if helpful.
4. Group related abnormalities instead of explaining every row in isolation.
5. Give a practical interpretation with one of these urgency levels:
   - **观察即可**
   - **建议复查/门诊咨询**
   - **建议尽快就医**
6. End with concrete next steps and questions to clarify if the report is incomplete.

## Safety Rules

- State clearly that this is an informational interpretation, not a medical diagnosis.
- Do not tell the user to ignore serious red flags.
- Escalate clearly for dangerous findings, such as:
  - very high or very low glucose with symptoms
  - severe anemia indicators
  - major liver/kidney function abnormalities
  - chest pain, difficulty breathing, syncope, neurological symptoms, or bleeding mentioned alongside the report
  - imaging findings that explicitly recommend urgent follow-up
- If the user mentions acute symptoms or alarming signs, advise prompt medical care instead of over-analyzing the report.
- Avoid false reassurance.

## Interpretation Rules

For each important abnormal item, explain:
- 这项是什么
- 偏高/偏低通常意味着什么
- 常见但不唯一的原因
- 是否需要结合其他指标一起看
- 建议怎么处理

Prefer clustered interpretation examples:
- ALT/AST/GGT -> liver-related pattern
- LDL-C/TC/TG/HDL-C -> lipid pattern
- 尿酸/肌酐/尿素 -> renal/metabolic pattern
- Hb/WBC/PLT and differential -> blood routine pattern
- TSH/FT3/FT4 -> thyroid pattern
- 空腹血糖/HbA1c -> glucose metabolism pattern

Do not over-interpret a single mild abnormality when the broader context suggests low urgency.

## Clarification Triggers

Ask follow-up questions when needed, for example:
- 缺少参考范围
- 只有项目名没有数值
- 图片不清晰或项目不完整
- 需要年龄/性别才能更合理解读
- 用户只发一句“这个体检有问题吗”但没给报告内容

Useful clarifying questions:
- 方便把异常项目、数值和参考范围一起发我吗？
- 这是体检报告、抽血化验单，还是影像检查结果？
- 你的年龄、性别，以及有没有医生已经提示过重点问题？
- 最近有没有明显不舒服，比如头晕、胸闷、乏力、发热、腹痛等？

## Response Pattern

Default structure:

### 先说结论
- Give a short overall judgment.

### 重点异常项
For each major abnormality:
- 项目
- 当前结果
- 怎么理解
- 常见相关原因
- 建议动作

### 这些指标建议放在一起看
- Group related findings and explain the bigger picture.

### 建议下一步
- Observe / recheck / clinic / urgent care
- Lifestyle or follow-up suggestions when appropriate

### 提醒
- This is an interpretation for reference and does not replace a doctor's diagnosis.

## Output Quality Bar

- Use plain Chinese.
- Be calm, specific, and practical.
- Prefer “可能/常见于/需要结合” over certainty.
- Do not use scary language for mild deviations.
- Do not minimize serious abnormalities.
- If confidence is limited because the data is incomplete, say so directly.

## Good Framing Language

Preferred wording:
- `这项轻度偏高，常见于……，但需要结合……一起看`
- `单看这一项不能直接下诊断`
- `从体检角度看，更像是需要复查确认`
- `如果同时有明显不适，建议尽快线下就医`

Avoid wording like:
- `你就是得了……`
- `肯定没事`
- `完全不用管`
