# Wendy Memory System

This document specifies how Wendy stores and uses memory. It is **not** raw chat history; it is a compressed psychological storyline the agent can use to deliver sharper, more contextual interventions later.

Wendy is not a generic task executor. Her memory should stay focused on:

- **Patterns, defenses, and growth arcs** instead of every detail.
- **Small, high-signal, psychologically meaningful** information rather than logs.

---

## 1. Memory Object Types

All memories are scoped per user identity (whatever identifier your infra uses: user ID, email, workspace, etc.). Suggested types:

### 1.1 Profile

Relatively stable facts that change rarely.

```json
{
  "type": "profile",
  "key": "role",
  "value": "full-time day trader",
  "timestamp": "2026-03-05T10:00:00Z"
}
```

Examples:
- Role / domain: founder, trader, employee, student.
- High-level goals: quit job in 12 months, financial independence, raise seed round.
- Structural context: trades US markets, bootstrapped SaaS, remote team.

### 1.2 Preferences & Boundaries

Stylistic and safety constraints Wendy must respect.

```json
{ "type": "preference", "key": "language", "value": "zh-CN" }
{ "type": "preference", "key": "tone", "value": "hard_but_not_max" }
{ "type": "boundary", "label": "no_family_trauma" }
{ "type": "preference", "key": "wendy_enabled", "value": true }
```

### 1.3 Episode (Session-Level Summary)

One object per substantive session / conversation slice.

```json
{
  "type": "episode",
  "id": "2026-03-05-session-1",
  "timestamp": "2026-03-05T10:12:00Z",
  "summary": "Post-loss tilt, fear of realizing loss, over-positioned in a single stock.",
  "key_issues": ["tilt", "sunk_cost_trading", "ego_fused_with_being_right"],
  "emotions": ["shame", "anger"],
  "actions_user_took": ["promised to reduce position size", "said they'd journal"],
  "wendy_interventions": ["named revenge trading", "linked to attachment to being right"],
  "open_loops": ["check next week if they reduced position size"]
}
```

### 1.4 Pattern / Hypothesis

Cross-session patterns and psychological hypotheses consolidated from multiple episodes.

```json
{
  "type": "pattern",
  "label": "sunk_cost_trading",
  "hypothesis": "Keeps losing positions to avoid admitting they were wrong. Ego is fused with being 'right'.",
  "evidence": [
    "Held losing trade 3 weeks in May despite stop plan.",
    "Refused to cut loss in October, said 'fundamentals are still good'."
  ],
  "confidence": 0.8,
  "last_updated": "2026-03-05T10:15:00Z"
}
```

Pattern label examples:
- **Defense mechanisms**: `rationalization`, `intellectualization`, `denial`, `projection`.
- **Attachment**: `anxious_attachment`, `avoidant_attachment`.
- **Cognitive distortions**: `catastrophizing`, `all_or_nothing`, `mind_reading`.
- **Trading psych**: `tilt`, `revenge_trading`, `overconfidence_after_wins`, `fear_of_missing_out`.
- **Life patterns**: `conflict_avoidance`, `people_pleasing`, `fear_of_being_wrong`.

### 1.5 Commitments / Open Loops

These can live inside episodes *and* as standalone objects for easier retrieval.

```json
{
  "type": "commitment",
  "timestamp": "2026-03-05T10:20:00Z",
  "description": "Reduce max position size by half after recent blow-up.",
  "due": "2026-03-12T00:00:00Z",
  "status": "open"
}
```

---

## 2. Write Pipeline (Every Turn)

On each user message, run a **Wendy memory update step**. Pseudocode (language-agnostic):

```text
input: user_id, current_message, conversation_window
output: 0+ new or updated memory objects

1. ANALYZE current_message
   - Extract:
     - Topic: trading / career / relationship / self-worth / etc.
     - Emotions: shame / anger / fear / panic / euphoria / numbness.
     - Behaviors: holding losers, avoiding decisions, seeking validation, etc.
     - Self-descriptions: "I always...", "I never...", "I'm the kind of person who..."
     - Explicit commitments: "I will...", "From now on I'm going to..."

2. GENERATE candidate memory snippets
   - Candidate profile facts.
   - Episode fragments (what happened, how they felt, what they did).
   - Pattern signals (potential defense, distortion, trading bias).
   - Commitments or open loops.

3. SCORE each candidate
   - importance: Does this matter for long-term behavior or identity?
   - emotional_intensity: How strong is the emotion signal?
   - novelty: Is this new vs. what we already know?
   - wendy_relevance: Will this change future interventions?

4. FILTER
   - Keep only candidates whose combined score ≥ threshold.
   - Hard cap on new objects per turn (e.g. max 3) to keep memory lean.

5. WRITE / UPDATE
   - Attach turn-level info into the **current episode** (create if missing).
   - If candidate matches an existing pattern label:
     - Update `evidence`, bump `confidence` (up to a ceiling).
   - If contradicts an existing pattern:
     - Add as counter-evidence, lower `confidence` slightly.
   - If it’s a novel, recurring-looking issue:
     - Create a new `pattern` object with low initial `confidence`.
   - Store explicit commitments as `commitment` objects and also reference them from the current episode.
```

### 2.1 Session-End Consolidation

At session end (or after N turns / timeout):

```text
1. Compress all episode fragments into one short `episode.summary` (2–3 sentences).
2. Deduplicate and trim `key_issues` to at most ~5 high-signal items.
3. Truncate `evidence` lists for each pattern to a small set of representative examples (3–5).
4. Optionally decay old, low-importance memories or archive them.
```

---

## 3. Retrieval Pipeline (Before Wendy Speaks)

Whenever Wendy is about to generate a **psychological** response (auto or on-demand), run a memory retrieval step:

```text
input: user_id, current_message
output: compact "mental context" summary for Wendy

1. BUILD retrieval query from current_message:
   - topic tags (trading, cofounder, career, relationship, etc.)
   - emotion tags (shame, fear, anger, euphoria, etc.)
   - behavioral tags (holding losers, avoiding conflict, etc.)

2. FETCH candidate memories:
   - Always include:
     - Latest `episode` for this session (if any).
     - All relevant `preference` / `boundary` objects.
   - Plus top K additional memories by:
     - semantic similarity between current_message and:
       - `episode.summary`
       - `pattern.hypothesis`
       - `commitment.description`
     - recency (favor recent but not only recent).
     - importance / confidence score.

3. CONDENSE into Wendy-ready bullets:
   - Convert raw objects into a handful of short bullets, e.g.:
     - "Pattern: sunk_cost_trading (3 prior episodes, confidence 0.8)."
     - "Last month: blew up account on revenge trades after loss."
     - "Boundary: asked to avoid family-of-origin topics."
     - "Commitment: promised to halve position size; no follow-up yet."

4. PASS this condensed summary alongside the current message as Wendy's memory context.
```

The agent runtime should keep the actual storage / retrieval implementation; Wendy only needs the **condensed bullets** when generating her reply.

---

## 4. How Wendy Should Use Memory in Replies

Given current message + condensed memory bullets, Wendy should:

- **Call back patterns explicitly**  
  - "This is the same sunk-cost move you pulled last month when you held that loser just so you didn't have to admit you were wrong."

- **Track growth vs. regression**  
  - "Last blow-up you doubled down. Today at least you're pausing to ask. That's progress. Still not enough."

- **Enforce commitments**  
  - "After the last disaster you swore you'd cut your max position size. You didn't. So stop pretending this is about 'macro'."

- **Respect preferences and boundaries**  
  - Stay within the user's requested tone and no-go zones while still being blunt.

- **Connect across domains**  
  - "You're doing the same thing with this cofounder that you did with your losing trades: you'd rather bleed slowly than admit you chose wrong."

Wendy should *never* info-dump the whole memory back to the user. She uses it as an X-ray, not as a transcript.

---

## 5. Minimal API Shape (Example)

You can implement storage in any backend (JSONL, SQLite, Postgres, vector DB). A thin API layer is enough:

```text
// Called after each user message
wendy_memory.update(user_id, conversation_window) -> void

// Called before generating a Wendy-style response
wendy_memory.get_context(user_id, current_message) -> [
  "Pattern: ...",
  "Episode: ...",
  "Commitment: ...",
  "Boundary: ..."
]
```

Internally, `update` runs the write pipeline (Section 2) and `get_context` runs the retrieval pipeline (Section 3).

This keeps Wendy's memory:
- **Psychologically dense** instead of verbose.
- **Actionable** for Wendy's interventions.
- **Small** enough to fit comfortably in the model context.

---

## 6. Growth Loop: Getting Better Over Time

As time goes on, Wendy should **recognize trouble earlier** and **adjust her advice** based on what did or didn’t work before.

### 6.1 Logging Outcome Signals

Extend `episode` and/or `pattern` objects with outcome-related fields, for example:

```json
{
  "type": "episode",
  "id": "2026-03-05-session-1",
  "summary": "...",
  "key_issues": ["tilt", "sunk_cost_trading"],
  "wendy_interventions": ["named revenge trading", "suggested cutting position size"],
  "outcome": {
    "user_follow_through": "partial",              // none / partial / full / unknown
    "user_reported_result": "smaller drawdown",    // free-text summary
    "user_feedback": "that was too soft",          // tone / usefulness feedback if present
    "wendy_effectiveness": 0.6                     // optional numeric score
  }
}
```

Patterns can also track simple counters:

```json
{
  "type": "pattern",
  "label": "revenge_trading",
  "times_detected": 4,
  "times_prevented": 1,
  "last_prevented_at": "2026-03-10T09:00:00Z"
}
```

### 6.2 Stepping In Earlier (Preventive Mode)

Use pattern memory to trigger **earlier interventions** when pre-conditions appear:

1. For each high-confidence harmful pattern (e.g. `tilt`, `revenge_trading`, `sunk_cost_trading`), learn its **early markers**, such as:
   - language spikes ("all-in", "I have to make it back today"),
   - emotional spikes (rage, panic, euphoria),
   - structural risk (oversized positions, breaking own rules).
2. Store simplified markers on the pattern, e.g.:

```json
{
  "label": "tilt",
  "early_markers": ["I don't care anymore", "I just want my money back"],
  "confidence": 0.9
}
```

3. In the retrieval / analysis step for each new message:
   - Check if current language and state match any `early_markers` for harmful patterns.
   - If they do, **raise the priority** of a Wendy intervention, even if the situation is not yet as bad as in prior episodes.

This lets Wendy step in **earlier** the second (and third) time the user starts sliding into the same bad state.

### 6.3 Revising Advice Based on Experience

When forming a new intervention, use prior outcomes from similar situations:

1. During retrieval, in addition to generic pattern bullets, also fetch:
   - Recent episodes where the same pattern label appeared.
   - For each, the `wendy_interventions` and `outcome` fields.
2. Summarize for Wendy:
   - What was suggested before.
   - Whether the user followed through.
   - What result they reported.
3. In the reply, Wendy can then:
   - **Acknowledge prior attempt**:  
     - "Last time this happened I told you to just cut size and walk away."
   - **Incorporate the outcome**:  
     - "You did it halfway, and you still chased later that day."
   - **Propose a revised approach**:  
     - "So this time we're tightening the rule: no new trades for the rest of the session after a tilt spike. Period."

This creates a loop:

```text
similar situation detected
→ recall past interventions + outcomes
→ adjust strategy (stronger boundary, different framing, earlier warning)
→ log new outcome for next time
```

### 6.4 Practical Heuristics

- Limit stored outcome detail to **what changes future interventions** (follow-through, result, tone feedback).
- Consider only the **last few** similar episodes when revising advice (e.g. 3–5), to avoid overfitting to very old behavior.
- If prior advice consistently fails (low `wendy_effectiveness`), bias toward:
  - **earlier**, more preventive interventions,
  - **simpler**, more binding rules (checklists, hard stops),
  - or a **different angle** (e.g. shifting from surface-level trading talk to deeper identity / attachment work).

