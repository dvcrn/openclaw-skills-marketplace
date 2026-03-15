---
name: course-study
description: "Comprehensive course study, exam revision, and structured study note generation from lecture slides, course PDFs, or topic outlines. Use when the user wants to study a course, review or summarize lecture slides/PDFs, generate lecture notes or a study guide, prepare for exams (midterm, final, quiz), create revision notes or formula sheets, extract key concepts/definitions/formulas from course materials, synthesize knowledge across multiple lectures, expand understanding beyond course scope with external sources, or asks for help learning, reviewing, or revising any university or college course content in any academic subject (CS, engineering, math, science, humanities, etc.). Produces deep, multi-format study notes (Markdown + PDF) with worked examples, LaTeX formulas, cross-lecture connections, concept dependency maps, quick-reference sheets, and exam Q&A appendix — not shallow summaries."
---

# Course Study v2.0

A structured four-phase workflow for deep learning of any university or college course: Extract → Synthesize → Expand → Study. Produces high-fidelity, multi-format study materials as a single, complete PDF — not shallow summaries.

---

## Phase 0: Intake

Read `rules/phase-intake.md` and run the full intake workflow. Keep this to one exchange — do not ask questions across multiple messages.

---

## Workflow

```
Phase 0: Intake (single exchange)
  ├── PDFs → Phase 1 (Extract via /pdf skill)
  ├── Topic list → Phase 2 directly
  └── Course name → quick syllabus search → Phase 2

Phase 1: Extract (per PDF, page-aligned, using /pdf skill)
  └── Output: lecture-XX-extract.md

Phase 2: Synthesize
  └── Output: course-synthesis.md

Phase 3: Expand (web sources OR curriculum-grounded)
  └── Output: course-expansion.md

Phase 4: Study Materials
  ├── study-notes.md (always)
  ├── quick-reference.md (Exam Ready only)
  └── exam-qa.md (Exam Ready only)
```

Each phase ends with a **brief checkpoint** (see below).

---

## Phase Checkpoint

After each phase, one compact message:

```
✓ Phase [X] done — [summary in one line].
Issues? (coverage gaps / too shallow / too verbose)
Type to adjust, or just say "continue".
```

If no response issues → proceed immediately. No multi-question forms.

---

## Global Rules

1. **PDF-only input.** Use the `/pdf` skill to read all course files. Do not use Python file I/O or direct file reading for PDFs.

2. **Backbone fidelity.** Every concept traces back to its source: page number (PDF) or section number (topic list). Never lose traceability.

3. **Speed discipline.** Minimize round-trips. Batch questions. Skip steps that aren't needed for the current tier. Phase 1 and 2 intermediate files should be dense and compact — no padding, no repeated meta-commentary.

4. **No fabrication.** Phase 3 without web access: every claim marked `[Standard curriculum knowledge]`. No invented URLs, paper titles, or authors.

5. **Examples are mandatory.** Phase 4 must include worked examples for every non-trivial concept.

6. **Track progress.** Use TodoList to track which lectures have been processed.

7. **Multi-format output.** Final notes are written in format-agnostic Markdown per `rules/templates.md`. When the user requests PDF output, read `rules/pdf-export.md` for pandoc font configuration and CJK handling before converting.

8. **Prioritise flagged topics.** If the user named priority topics in Phase 0, give them deeper treatment in Phase 4 and ensure they appear in the Quick Reference and Exam Q&A.

---

## Phase 4 Output: Study Notes

The main study notes follow the structure in `rules/phase-study.md`. Every concept gets:

- **What it is** — definition, instructor's phrasing first
- **Intuition** — why it exists, what problem it solves
- **Formal treatment** — LaTeX formulas or code blocks
- **Worked example** — concrete, step-by-step
- **Connections** — prerequisites and what this enables
- **Common misconceptions**

Exam Ready appendices (Quick Reference Sheet and Exam Q&A) are generated in Phase 4 as well — see `rules/phase-study.md` Steps 6a and 6b.

---

## Reference Files

- `rules/phase-intake.md` — Phase 0 intake workflow
- `rules/phase-extract.md` — Phase 1
- `rules/phase-synthesize.md` — Phase 2
- `rules/phase-expand.md` — Phase 3
- `rules/phase-study.md` — Phase 4 (study notes + Exam Ready appendices)
- `rules/templates.md` — Format-agnostic writing rules
- `rules/pdf-export.md` — PDF conversion config (load only when PDF output is requested)
- `rules/subject-coverage.md` — Live search strategy for curriculum gap analysis
- `rules/changelog.md` — Version history

---

## Anti-Patterns

| Avoid | Why | Instead |
|-------|-----|---------|
| Skipping worked examples | Students fail on application, not definitions | Mandatory for every non-trivial concept |
| Quick Reference with prose | Defeats the purpose | One line per entry maximum |
| Exam Q&A without source refs | Student can't verify or dig deeper | Every answer cites source location |
| Ignoring Phase 0 priority topics | User told you what matters | Deeper treatment + appears in all appendices |
| Fabricating exam question styles | Misleads preparation | Draw only from what the course actually covers |
