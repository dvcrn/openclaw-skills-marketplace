# Phase 4: Structured Deep Study Notes

## Goal

Produce the **final, comprehensive study notes** integrating all prior phases into a single authoritative document. This is the deliverable the student will actually use.

## What this phase is — and isn't

Phase 4 is a creative synthesis, not a rewrite of Phase 1. It:
- Follows the **backbone structure** (lecture/section order from Phase 1) as the skeleton
- Weaves in **cross-lecture connections** from Phase 2 at the right moments
- Integrates **external knowledge** from Phase 3 where it deepens understanding
- Adds **concrete worked examples** for every non-trivial concept
- Maintains **concise, precise technical writing** — not verbose, not skeletal

The backbone from Phase 1 is the spine. Phases 2 and 3 are the flesh.

## Procedure

### Step 1: Build the document skeleton

Follow the backbone structure strictly. Every backbone unit (lecture page group or section) becomes a heading. A reader can hold the original slides / topic list in one hand and the study notes in the other and see a 1:1 correspondence.

```markdown
# [Course Name] — Study Notes

## About these notes
[What these notes cover, how they're structured, what sources they draw from]

## Lecture 1 / Module 1: [Title]
### 1.1 [Topic] ([source location])
...
### 1.2 [Topic] ([source location])
...
```

Source location format — use whichever applies:
- PDF input: `(Lecture 1, pp. 3-7)`
- Topic list input: `(Section 1.2)`

### Step 2: Write each concept block

Calibrate depth to concept importance:

```markdown
### [Concept Name] ([source location])

**What it is:** [1-3 sentence definition. Instructor's phrasing first, then clarification.]

**Intuition:** [Why does this exist? What problem does it solve? Use analogies for complex ideas.]

**Formal treatment:**
[Formula / algorithm in LaTeX or code block. Explain each symbol/variable.]

**Example:**
[Concrete, worked example. For algorithms: step-by-step trace. For formulas: plug in numbers.]

**Real-world application:** [From Phase 3. How used in industry? Specific tools, cases.]

**Connections:** [From Phase 2. Prerequisites + what this concept enables.]

**Common misconceptions:** [What do students typically get wrong?]

**References:** [source location + Phase 3 source if used]
```

| Concept weight | Required sections |
|---|---|
| Core / exam-critical | All seven |
| Important supporting | What + Formal + Example + Connections |
| Minor / context | What + brief note |

### Step 3: Insert cross-lecture bridges

At every lecture/module boundary, insert a bridge:

```markdown
---
> **Bridge:** Lecture 3 introduced the problem of [X]. Lecture 4 now presents [Y] as a solution. The key shift is from [understanding the problem] to [designing a mechanism]. Note that [Y] assumes [Z] from Lecture 2 ([source location]).
---
```

Bridges transform a set of notes into a coherent learning narrative.

### Step 4: Verify completeness (fast pass)

Run a quick cross-reference — do not re-read everything in full:
- Spot-check: do the Phase 1 concept lists match headings in study notes? Flag any missing.
- Confirm no `[TODO]` placeholders remain.
- Confirm Phase 3 expansion entries are embedded (not appended at the end).
- Source locations present on all concepts? If any are missing, add from Phase 1.

### Step 5: Format output

Write in format-agnostic Markdown per [templates.md](templates.md). Generate `study-notes.md` as primary output. For PDF export, apply the `/pdf` skill — do not use Python or pandoc directly.

### Step 6: Generate Exam Ready appendices (Exam Ready mode only)

If the user selected **Exam Ready** in Phase 0 — or requests it now for the first time — generate two additional files after `study-notes.md` is complete. Do not restart earlier phases; generate the appendices from the outputs already produced.

#### 6a: quick-reference.md

A compact reference card designed for last-minute review or open-book use.

Rules:
- Every entry fits in one table row or one bullet — no prose paragraphs
- Ordered by **exam relevance** (most likely to appear on exam first), not lecture order
- Infer exam relevance from: Phase 2 course narrative, Phase 2 gap flags, [EXPAND] markers from Phase 1, and user-specified priority topics from Phase 0
- Source refs omitted (speed over traceability in this document)

Structure:
```markdown
# Quick Reference: [Course Name]

## Formulas
| Name | Formula | Notes |
|------|---------|-------|
| [Name] | $[LaTeX]$ | [When to use / key constraint] |

## Key Definitions
- **[Term]:** [One sentence]

## Algorithms
| Name | Time | Space | Key idea |
|------|------|-------|----------|
| [Name] | O(?) | O(?) | [One line] |

## Common Traps
- [Specific mistake students make and what the correct behaviour is]

## X vs Y (Decision Tables)
[When you have two or more easily confused concepts, a two-column comparison table]
```

#### 6b: exam-qa.md

A bank of exam-style questions with full worked solutions.

Question sourcing rules (in priority order):
1. **Phase 2 gaps and [EXPAND] markers** — concepts the course treated superficially are prime exam targets
2. **User-specified priority topics** from Phase 0
3. **Cross-cutting concepts** from Phase 2 synthesis (themes that span multiple lectures)
4. **Core definitions** — one definition question per major concept

Question type selection by subject:
| Subject type | Emphasis |
|---|---|
| Math / engineering / CS algorithms | Worked problems (show-your-work format) |
| CS systems / architecture | Compare-and-contrast + design scenarios |
| Sciences | Explain-the-phenomenon + calculation |
| Humanities / social sciences | Short essay + source interpretation |
| Mixed | All types, weighted by lecture content |

Format per question:
```markdown
### Q[N]: [Short title]
**Type:** [Definition / Worked problem / Compare / Design / Essay]
**Likely exam weight:** [High / Medium / Low]

[Question text — specific, unambiguous, matches the difficulty of the course]

**Answer:**
[Full solution. For worked problems: show every step. For compare: use a structured table or bullet pairs. For essay: a model answer outline.]

**Common mistake:** [What students typically get wrong on this question]
**Source:** [Lecture X, pp. Y-Z or Section X.Y]
```

Minimum coverage: 3 questions per major topic. At least one worked problem if the subject involves calculation or algorithms.

## Writing style

**Concise but complete.** Every sentence earns its place. Cut filler, keep substance.

**Active voice.** "The scheduler assigns processes" not "Processes are assigned."

**Technical precision.** Correct terminology. Define on first use.

**Progressive disclosure.** Within each concept: intuition first (accessible) → formal (precise) → example (concrete) → connections (advanced). A reader can stop at any level and still learn something.

**Code and formulas are first-class.** Format correctly, comment where non-obvious, never truncate.

## Anti-patterns

- **DO NOT** produce study notes shorter than Phase 1 extractions. Phase 4 is longer because it adds examples, connections, and explanations.
- **DO NOT** skip examples. "Definition without example" is the single most common failure mode.
- **DO NOT** break the backbone order. Forward/backward links are fine; the primary structure must follow it.
- **DO NOT** omit Phase 3 expansion content if Phase 3 was run.
- **DO NOT** write walls of text — use headings, code blocks, and formula blocks for visual rhythm.
- **DO NOT** produce content that only works in Markdown — follow templates.md format rules throughout.
- **DO NOT** (Exam Ready) write prose in quick-reference.md — it is a lookup table, not a summary.
- **DO NOT** (Exam Ready) write trivial questions in exam-qa.md — each question must require genuine understanding to answer.
- **DO NOT** (Exam Ready) generate questions only from easy, well-covered topics — the most valuable questions come from Phase 2 gaps and [EXPAND] markers.
