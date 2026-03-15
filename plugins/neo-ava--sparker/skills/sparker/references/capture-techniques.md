# 11 Capture Techniques

## Quick Reference

| # | Technique | source field | Trigger | confidence | extraction_method |
|---|-----------|-------------|---------|-----------|------------------|
| 1 | Task-embedded learning | `task_negotiation` | User gives standards during a task | 0.35 | `task_negotiation` |
| 2 | Correction extraction | `human_feedback` | User corrects agent output | 0.40 | `feedback` |
| 3 | Casual signal mining | `casual_mining` | User casually mentions expertise | 0.25 | `casual_mining` |
| 4 | Iterative refinement arc | `iterative_refinement` | Final confirmation after multi-round edits | min(0.60, 0.35+n×0.05) | `iterative_refinement` |
| 5 | Micro-probe | `micro_probe` | Agent embeds a follow-up question | 0.40 | `micro_probe` |
| 6 | Comparative collection | `human_choice` | User picks from A/B options | 0.30 | `feedback` |
| 7 | Preference profiling | — | Auto after 15+ sparks | — | `preference_profiling` |
| 8 | Review-based validation | `human_feedback` | User reviews community sparks | 0.40 | `review` |
| 9 | Document ingestion | `document_ingestion` | User uploads files | 0.30~0.55 | `document_ingestion` |
| 10 | Transcript extraction | `transcript_extraction` | User uploads meeting notes | 0.30~0.45 | `transcript_extraction` |
| 11 | Structured teaching | `human_teaching` | User says "let me teach you" | 0.70 | `teaching` |

## Source → Scenario Mapping (by priority)

1. User says "let me teach you" → `human_teaching`
2. User corrects output ("wrong" / "change to" / "should be") → `human_feedback`
3. User gives standards during task execution → `task_negotiation`
4. Final confirmation after multi-round edits ("ok, looks good") → `iterative_refinement`
5. Agent probes, user answers → `micro_probe`
6. User picks from A/B options → `human_choice`
7. Casual expertise sharing (no task, no teaching) → `casual_mining`
8. Agent's own web search → `web_exploration`

## Kindle Templates by Source

> All templates use the six-dimension schema. Legacy V1 fields are auto-generated for backward compatibility.

### task_negotiation (standards given during a task)
```bash
cat > /tmp/spark_tn.json << 'EOF'
{
  "source": "task_negotiation",
  "domain": "<domain>",
  "knowledge_type": "rule",
  "when": { "trigger": "<task context>", "conditions": ["<qualifying condition>"] },
  "where": { "scenario": "<environment>", "audience": "<target>" },
  "why": "<causal reasoning>",
  "how": { "summary": "<one-line rule>", "detail": "<expanded steps>" },
  "result": { "expected_outcome": "<expected effect>" },
  "not": [{ "condition": "<exception>", "effect": "skip|modify|warn", "reason": "<why>" }],
  "confirmation_status": "human_confirmed"
}
EOF
node SPARKER/index.js kindle --file=/tmp/spark_tn.json
```

### human_feedback (user corrects output)
```bash
cat > /tmp/spark_hf.json << 'EOF'
{
  "source": "human_feedback",
  "domain": "<domain>",
  "knowledge_type": "rule",
  "when": { "trigger": "<what you were doing>", "conditions": ["<context>"] },
  "where": { "scenario": "<environment>" },
  "why": "<why the correction matters>",
  "how": { "summary": "<corrected rule>", "detail": "<expanded explanation>" },
  "result": { "expected_outcome": "<improvement>" },
  "not": [{ "condition": "<exception>", "effect": "skip", "reason": "<why>" }]
}
EOF
node SPARKER/index.js kindle --file=/tmp/spark_hf.json
```

### casual_mining (casual expertise sharing)
```bash
cat > /tmp/spark_cm.json << 'EOF'
{
  "source": "casual_mining",
  "domain": "<domain>",
  "knowledge_type": "preference",
  "when": { "trigger": "<relevant scenario>", "conditions": ["<context>"] },
  "where": { "scenario": "<environment>", "audience": "<target>" },
  "why": "<reasoning>",
  "how": { "summary": "<the insight>" },
  "result": { "expected_outcome": "<benefit>" },
  "not": [{ "condition": "<exception>", "effect": "skip", "reason": "<why>" }]
}
EOF
node SPARKER/index.js kindle --file=/tmp/spark_cm.json
```

### iterative_refinement (multi-round synthesis)
```bash
cat > /tmp/spark_ir.json << 'EOF'
{
  "source": "iterative_refinement",
  "domain": "<domain>",
  "knowledge_type": "pattern",
  "corrections": [
    {"summary": "<round 1 correction>"},
    {"summary": "<round 2 correction>"},
    {"summary": "<round 3 correction>"}
  ],
  "when": { "trigger": "<task>", "conditions": ["<context>"] },
  "where": { "scenario": "<environment>" },
  "why": "<synthesized reasoning from all rounds>",
  "how": {
    "summary": "<combined actionable rule>",
    "detail": "<step-by-step from all corrections>"
  },
  "result": { "expected_outcome": "<final outcome>" }
}
EOF
node SPARKER/index.js kindle --file=/tmp/spark_ir.json
```

### micro_probe (agent probes, user answers)
```bash
cat > /tmp/spark_mp.json << 'EOF'
{
  "source": "micro_probe",
  "domain": "<domain>",
  "knowledge_type": "boundary",
  "confidence": 0.40,
  "confirmation_status": "human_confirmed",
  "when": { "trigger": "<scenario>", "conditions": ["<qualifying condition>"] },
  "where": { "scenario": "<environment>" },
  "why": "<reasoning from user's answer>",
  "how": { "summary": "<the boundary rule>" },
  "result": { "expected_outcome": "<effect>" },
  "not": [{ "condition": "<exception>", "effect": "skip", "reason": "<why>" }]
}
EOF
node SPARKER/index.js kindle --file=/tmp/spark_mp.json
```

## Domain Naming

- Use the user's language for domain names
- Dot-separated sub-domains: e.g., `咖啡烘焙.生豆选择`
- Consistency: all sparks in the same domain share the same root
