# Phase 2: Cross-Lecture Deep Synthesis

## Goal

Build a **deep conceptual structure** of the entire course by connecting knowledge across all lectures/sections. This is NOT a simple merge — it requires applying world knowledge, revealing relationships the slides only imply, and identifying what the course doesn't teach.

## Source references

Throughout this phase, use the backbone reference format established in Phase 1:
- PDF input: `Lecture X, pp. Y-Z`
- Topic list / syllabus input: `Section X.Y`

Never reference source locations that don't exist in Phase 1 outputs.

## Procedure

### Step 1: Build the concept inventory

Read all `lecture-XX-extract.md` files using the Read tool (these are Markdown files, not PDFs — no `/pdf` skill needed here). For each concept, record:
- First appearance (source location)
- All subsequent mentions (source locations)
- Type: definition / theorem / algorithm / design pattern / tool

**For Medium/Heavy tier courses (> 60 pages):** work in batches of 3-4 lectures at a time, building a running inventory. Do not hold all lectures in context simultaneously.

### Step 2: Dependency analysis

For each concept, determine:
- **Hard prerequisites:** must be understood first (e.g., gradient descent before backpropagation)
- **Soft relations:** related but not prerequisite (e.g., TCP and UDP are peers)
- **Hierarchy:** is this an instance of a more general concept? (e.g., quicksort ⊂ divide-and-conquer)

Use world knowledge to infer dependencies the slides don't state explicitly. If a concept is used before it's defined, flag it as a gap.

### Step 3: Identify the course narrative

Every well-designed course tells a story. Identify:

- **Main thread:** the central question the course builds toward (e.g., "How do OS manage shared resources safely?")
- **Supporting threads:** recurring themes (e.g., "performance vs. safety tradeoffs", "layered abstraction")
- **Progression pattern:** linear? spiral? breadth-first then depth?

### Step 4: Fill conceptual gaps

Find the standard curriculum baseline for this subject using the search strategy in [subject-coverage.md](subject-coverage.md). Run 1-2 targeted searches (e.g., `"[subject] university course syllabus topics"`) to identify what a standard course in this field covers. This works for any subject — not just CS.

If both searches return low-quality results (no syllabi, no textbook tables of contents, no course pages), fall back to Mode B (world knowledge) and mark the gap analysis: `[Gap analysis based on curriculum knowledge — web results insufficient]`. Do not retry the same queries or invent sources.

Compare the actual course materials against this baseline. Identify:
- **Core topics missing from the course** → high-priority flag for Phase 3
- Topics covered **superficially** → medium-priority, candidates for Phase 3 expansion
- **Simplified models** that gloss over important nuance → note the gap

For each gap: "The slides present [X] as [simplified]. The full picture includes [missing piece]. This matters because [why]."

### Step 5: Produce the synthesis document

```markdown
# Course Synthesis: [Course Name]

## Course narrative
[2-3 paragraphs: what story this course tells, the central question it answers, how it builds]

## Knowledge architecture
[Organized by theme/module — NOT by lecture/section order]

### Module: [Theme Name]
**Core concepts:** [list]
**Dependency chain:** A → B → C (brief explanation of each link)
**Key insight:** [the "aha" that connects these concepts]
**Covered in:** [source locations]

[Repeat for each module]

## Cross-cutting patterns
[Tradeoffs, design principles, recurring proof techniques that appear across modules]

## Concept dependency graph
[Text representation: which concepts depend on which]

## Gaps and flags
[Topics that are shallow, missing, or oversimplified — with source locations and notes for Phase 3]

## Ambiguities and contradictions
[Inconsistencies between lectures, or places where the material is unclear]
```

## Depth expectations

For a 12-lecture course, synthesis should be substantial but not padded. Target: every module section has a dependency chain and a key insight. Skip the narrative fluff — the value is in the connections and gaps, not word count.

The test: could a student read this and understand the *architecture* of the subject — what depends on what, and what the course missed?

## Anti-patterns

- **DO NOT** concatenate lecture summaries — that's Phase 1, not synthesis.
- **DO NOT** limit yourself to what's literally in the slides — use world knowledge for the "why."
- **DO NOT** produce a flat list of concepts — the value is in the relationships.
- **DO NOT** skip gap analysis — identifying what the course doesn't teach is as important as what it does.
- **DO NOT** reference source locations that don't appear in Phase 1 outputs.
