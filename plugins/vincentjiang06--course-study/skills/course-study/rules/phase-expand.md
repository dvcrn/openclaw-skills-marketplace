# Phase 3: External Knowledge Expansion

## Goal

Expand the knowledge base **beyond the course boundary** with precisely sourced external knowledge. The result should make the student's understanding deeper and broader than the course alone provides.

## Step 0: Check operating mode

This phase operates in one of two modes, determined in Phase 0:

**Mode A — Web-enabled (WebSearch + WebFetch available)**
Run the full three-layer search strategy below.

**Mode B — Curriculum-grounded (no web access)**
Do NOT search the web. Instead, expand using stable, well-established knowledge from standard CS/engineering curricula. Every claim must be marked `[Standard curriculum knowledge]`. Do not invent URLs, paper titles, author names, or implementation details. If you are uncertain about a claim, omit it or flag it as `[Uncertain — verify before exam]`. The goal is to avoid hallucination causing review distortion, not to produce maximum volume.

If Mode B was chosen but the user now wants to enable web access, stop and ask them to grant WebSearch permission before continuing.

---

## Expansion targets (both modes)

Process expansion targets in this priority order. **Hard cap: maximum 15 targets per course.** If there are more, present a ranked list and ask the user to confirm which to include.

1. **[EXPAND] markers** from Phase 1 — concepts explicitly flagged as needing external investigation.
2. **Gaps and shallow topics** from Phase 2 — concepts the course covers superficially or misses.
3. **Core concepts** — central concepts that benefit from real-world grounding.

---

## Mode A: Web-enabled search strategy

For each target, use up to three layers. Stop when you have sufficient quality material.

### Layer 1: Industry & practical knowledge

Search for specific, deep content:
- Official documentation (Linux kernel docs, RFC, MDN, etc.)
- Engineering blogs from reputable companies (Google AI Blog, AWS Architecture, etc.)
- GitHub implementations (link to specific file/function, not repo root)
- Stack Overflow canonical answers for common confusions

Query tips: Use formal concept name + "implementation" / "in practice" / "architecture". Avoid generic "what is X" queries.

### Layer 2: Academic literature

Search for:
- The original paper introducing the concept
- Recent surveys
- Papers that extend or challenge the course's treatment

For each paper: title, authors, arXiv ID or DOI, year, and 1-3 sentences on its relevance.

### Layer 3: Cross-verification

When multiple sources are found, note where they agree (builds confidence) and where they disagree (flags nuance). If the course material contradicts an authoritative external source, flag this explicitly.

---

## Mode B: Curriculum-grounded expansion

For each target concept:

1. Describe the standard treatment of this concept in the field (textbook-level knowledge).
2. Identify what the course's treatment adds, simplifies, or omits compared to the standard.
3. Add the "bigger picture" context: where does this concept fit in the field? What problems does it address?
4. Note common misconceptions that standard curricula address.

All content marked `[Standard curriculum knowledge]`. No fictional sources.

---

## Output format

Organize by concept, not by search layer:

```markdown
# Course Expansion: [Course Name]

## [Concept Name]
**Source in course:** [Lecture X, pp. Y-Z | Section X.Y] — [brief note on course treatment]
**Why expand:** [EXPAND marker / gap from synthesis / core concept]

### What the course doesn't cover
[The specific gap this expansion addresses.]

### Expanded understanding
[Mode A: what industry or research adds. Mode B: standard curriculum context.]
**Sources:**
- [Mode A] [Page Title](URL) — one-line note
- [Mode B] [Standard curriculum knowledge — topic area]

### Key insight
[2-4 sentences: what the student gains here that the slides don't provide.]

### Cross-verification note *(Mode A only)*
[Agreement/disagreement across sources, if applicable.]

---
```

## Source citation rules

**Mode A:** Every factual claim needs a traceable source. Acceptable forms:
- Web: `[Title](full URL)`
- Paper: `Author et al., "Title" (Year). arXiv:ID` or `DOI:xxx`
- Docs: `[Doc Section](URL)` with version
- Fallback: `[Standard curriculum knowledge — topic area]` — use sparingly

**Never cite a source you haven't actually retrieved.** If search fails, write: "No high-quality external source found for [concept]; expansion based on course material and general domain knowledge."

**Mode B:** All claims `[Standard curriculum knowledge]`. No citations to sources not in hand.

## Depth calibration

| Concept | Mode A depth | Mode B depth |
|---|---|---|
| Core + [EXPAND] marked | All 3 layers, 300-500 words | 200-300 words, curriculum context |
| Core, well-covered | Layer 1 only, 100-200 words | 100 words, brief context |
| Gap from Phase 2 | Layers 1-2, 200-300 words | 150 words, what standard treatment adds |
| Minor/tangential | Skip or 1-2 sentences | Skip |

## Anti-patterns

- **DO NOT** dump raw search results without analysis.
- **DO NOT** expand more than 15 concepts — prioritize by value.
- **DO NOT** cite sources you haven't retrieved (Mode A) or invent sources (Mode B).
- **DO NOT** let this phase substitute for understanding the course — it enriches, it doesn't replace.
- **DO NOT** include outdated content without flagging it as historical.
- **DO NOT** (Mode B) state uncertain claims confidently. If unsure, omit or flag.
