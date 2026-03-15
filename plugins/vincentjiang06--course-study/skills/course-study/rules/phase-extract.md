# Phase 1: Backbone Extraction

## Goal

Extract every concept, definition, formula, algorithm, code snippet, and diagram from the course PDFs, **strictly aligned to page numbers**. Zero information loss is the target.

## File reading rule

**Always use the `/pdf` skill to read PDF files.** Do not use Python, bash, or any direct file I/O. Invoke `/pdf` with the uploaded file, then work from its output.

If a file is not already a PDF, stop and ask the user to convert it using `/pdf` first before continuing.

## Backbone reference format

| Input type | Unit | Reference format |
|---|---|---|
| PDF / slide file | Page number | `Lecture X, p. Y` |
| Topic list | Section item | `Section X.Y` |
| Generated syllabus | Syllabus entry | `Module X, Section Y` |

Use the same format throughout all phases. Do not mix formats.

## Extraction procedure

### Step 1: Read via /pdf skill

Invoke the `/pdf` skill on the uploaded file. Note total page count from the output.

### Step 2: Page-by-page extraction

For EVERY page, output one block. Keep blocks dense — no padding:

```markdown
### Page X (of N) — [Slide title]

**Key content:**
- [Definitions — exact wording]
- [Formulas — $LaTeX$]
- [Algorithms — pseudocode or code block]
- [Diagrams — describe structure, name all labeled elements]
- [Tables — reproduce as Markdown]
- [Examples — reproduce in full]

**Concepts introduced:** [comma-separated]
**[EXPAND]:** [concept — reason] *(omit if nothing to flag)*
```

Empty/title pages still get a block:
```markdown
### Page 1 (of 30) — Course Title
**Key content:** [Title page — no substantive content]
**Concepts introduced:** —
```

### Step 3: Speed calibration by tier

Apply the tier set in Phase 0:

| Tier | Page handling |
|---|---|
| Light (≤60p) | Full block per page |
| Medium (61–200p) | Full block per page; write lecture summary after each lecture |
| Heavy (201–400p) | Full block per page; after each lecture, compress to concept-inventory format (concept + location + type only) before moving to next lecture |

For Heavy tier, the concept-inventory format is:
```
- [Concept name] | Lecture X, pp. Y-Z | [definition/theorem/algorithm/pattern]
```
This replaces the full block in memory but the full blocks are still written to the extract file.

### Step 4: Completeness check (fast)

```
Pages in file: N  →  "### Page X" blocks in output: must = N
```

Content-rich pages: each block ≥ 5 lines of substantive content. If shorter, re-read the page.

### Step 5: Lecture summary (append to extract file)

```markdown
## Lecture Summary

**Topic:** [main topic]
**Total pages:** N
**Key concepts (by appearance):** [numbered list — keep brief]
**Prerequisites assumed:** [from earlier lectures]
**[EXPAND] markers:** [list with page refs]
**Open questions:** [unclear or contradictory items]
```

---

## For topic list inputs

When the user pastes a topic list instead of a PDF:

1. Parse into hierarchy: Top level → Module, Second → Section, Third → Sub-concept
2. Assign numbers: `1.1`, `1.2`, `2.1`, etc.
3. Write `course-backbone.md` with the full outline
4. Show the user: "Does this structure look right?" — adjust if needed
5. Populate each section with world-knowledge concept blocks, marked `[From: world knowledge — no source PDF]`

---

## Output

- `lecture-XX-extract.md` per PDF (zero-padded)
- `course-backbone.md` if input was a topic list

## Anti-patterns

- **DO NOT** read PDFs with Python or direct file tools — use `/pdf` skill only
- **DO NOT** merge multiple pages into one block
- **DO NOT** skip pages you consider unimportant
- **DO NOT** pad with meta-commentary — dense content only
