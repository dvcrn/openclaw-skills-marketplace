# GRAPH_EXTRACTION.md — MindGraph Write Grammar

Canonical reference for **when and how** to utilize the 18 cognitive tools during
conversations, sub-agent tasks, heartbeat passes, and Polymarket events.

Full schema (52 node types): `skills/mindgraph/SCHEMA.md`
API documentation: `skills/mindgraph/SKILL.md`

**Golden rule:** Use the high-level cognitive tools in `mindgraph-client.js` instead of raw node creation. They handle atomic edge wiring and metadata automatically.

---

## Part 1A: Main Session Triggers (Jaadu ↔ Shan conversation)

### Reality Layer — Capture Ground Truth
Use `mg.ingest(label, content, type, { sourceUid, medium, url })`

| What happened | Tool call | Type |
|---------------|-----------|------|
| New document/URL/email read | `mg.ingest` | `source` |
| Specific quote or fact found | `mg.ingest` | `snippet` |
| Event observed (rejection, strike) | `mg.ingest` | `observation` |
| New person/org/service mentioned | `mg.manageEntity` | `create` |

### Epistemic Layer — Reasoning & Beliefs
Use `mg.addArgument`, `mg.addInquiry`, and `mg.addStructure`

| What happened | Tool call | Usage notes |
|---------------|-----------|-------------|
| Fact bundle (Claim + Evidence) | `mg.addArgument` | Always bundle Evidence + Warrant |
| Hypothesis or Open Question | `mg.addInquiry` | Link to what it addresses |
| Bug or surprising behavior | `mg.addInquiry` | Use type: `anomaly` |
| Lesson learned / reusable Pattern | `mg.addStructure` | Use type: `pattern` or `concept` |

### Intent Layer — Commitments & Choice
Use `mg.addCommitment` and `mg.deliberate`

| What happened | Tool call | Policy |
|---------------|-----------|--------|
| New Goal or Project proposed | `mg.addCommitment` | **NARRATE BEFORE WRITING** |
| Intermediate checkpoint | `mg.addCommitment` | Use type: `milestone` |
| Fork in the road / Choice to make | `mg.deliberate` | `action: 'open_decision'` |
| Hard rule stated ("always/never") | `mg.governance` | `action: 'create_policy'`, pass rule as `policyContent` |
| Soft preference stated | `mg.memoryConfig` | `action: 'set_preference'` |

### Action/Agent Layer — Planning & Work
Use `mg.plan`, `mg.governance`, and `mg.execution`

| What happened | Tool call | Usage notes |
|---------------|-----------|-------------|
| Multi-step strategy designed | `mg.plan` | `action: 'create_plan'` |
| Atomic unit of work assigned | `mg.plan` | `action: 'create_task'` |
| Action taken (email sent, post) | `mg.execution` | `action: 'start'` then `'complete'` |
| Behavioral rule for agents | `mg.governance` | `action: 'create_policy'` |

---

## Part 1B: Sub-Agent Task Outputs

Sub-agents write structured outputs using the bridge or client. 
Include in every sub-agent task prompt:
```
Record your findings using the MindGraph cognitive layer:
  - Observation/Intel: mg.ingest("<label>", "<content>", "observation")
  - Entity: mg.manageEntity({ action: "create", label: "...", entityType: "..." })
  - Planning: mg.plan({ action: "create_task", label: "...", description: "..." })
```

---

## Part 1C: Polymarket Positions

Positions are managed as a **deliberation bundle**:

### Opening a position
1.  **Thesis:** `mg.addInquiry("<Market Thesis>", "<content>", "hypothesis")`
2.  **Decision:** `mg.deliberate({ action: "open_decision", label: "Enter position...", description: "Thesis: ..." })`
3.  **Resolve:** `mg.deliberate({ action: "resolve", decisionUid, chosenOptionUid, resolutionRationale: "Price at {X}¢" })`

### Price updates
Use `mg.ingest` with `type: 'observation'`. Link to the position Decision node using `TraceEntry` edges via `mg.sessionOp`.

---

## Part 2: Decision Status Reference

| Status | Meaning | Steady state? |
|--------|---------|---------------|
| `open` | Still being deliberated | No |
| `resolved` | Made and in force | Yes |
| `superseded` | Replaced by another decision | Terminal |
| `reversed` | Explicitly undone, not replaced | Terminal |

**Never use** `completed`, `active`, `locked` for Decisions.

---

## Part 3: Heartbeat Extraction Pass

Run after system checks.

1.  **Scan recent conversation (last 60 min)**: Apply Part 1A triggers.
2.  **Threshold**: Would this node still be useful in 7 days without the chat context?
3.  **Write**: Use the 18 cognitive tools.
4.  **Trace**: Log the extraction session via `mg.sessionOp({ action: 'trace' })`.
5.  **Memory**: If a write affects future behavior, update MEMORY.md.

---

## Part 4: Required Fields Cheatsheet

CozoDB FTS only indexes `label` and `summary`.
**Policy**: Always populate the `summary` field (or `description`/`content` which the client maps to summary) for every node.

- **Goal/Project**: Needs `description`, `status`, `priority`.
- **Claim/Observation**: Needs `content`.
- **Decision**: Needs `question` and `status`.
- **Constraint**: Needs `description`.
- **Anomaly**: Needs `description`, `anomaly_type`.
