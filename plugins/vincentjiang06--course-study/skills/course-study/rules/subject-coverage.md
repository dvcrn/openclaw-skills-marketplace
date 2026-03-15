# Curriculum Coverage Search Strategy

This file defines how to find and evaluate standard curriculum coverage for **any academic subject**. It replaces hardcoded topic lists — which only covered 8 CS/engineering subjects — with a live search approach that works for any course a student might take.

## When this is used

1. **Phase 0, Mode 3 (broad topic input):** User gives only a course name. Search for the standard syllabus before generating an outline.
2. **Phase 2, Step 4 (gap analysis):** Compare the actual course materials against what a standard course in this subject would cover.

---

## How to search for curriculum coverage

### Step 1: Identify the subject and level

From the user's input, determine:
- Subject name (e.g., "Organic Chemistry", "Econometrics", "Byzantine History")
- Level: introductory / intermediate / advanced (infer from context or ask)
- Region/system if relevant (e.g., UK A-level vs. US university)

### Step 2: Execute search queries (Mode A — web enabled)

Run 2-3 targeted searches. Prefer queries that surface syllabi, textbook tables of contents, and university course pages over generic explainers.

**Recommended query patterns:**

```
"[subject] university course syllabus topics"
"[subject] undergraduate curriculum [key textbook author OR university name]"
"[subject] course outline week by week"
"[subject] exam topics [university level]"
```

**Examples:**
- `"organic chemistry undergraduate syllabus topics"`
- `"econometrics course outline core topics"`
- `"Byzantine history university course curriculum"`
- `"linear algebra textbook Strang table of contents"`

**Target sources (in priority order):**
1. University course pages (MIT OpenCourseWare, Stanford, etc.) — authoritative syllabi
2. Canonical textbook tables of contents — stable, widely adopted
3. ACM/IEEE curriculum guidelines (for CS/engineering) — standardized
4. Wikipedia outlines ("Outline of [subject]") — broad coverage, good for unfamiliar fields
5. Major MOOC syllabi (Coursera, edX) — reflects current teaching practice

### Step 3: Extract the topic structure

From the search results, identify:
- **Core topics:** appear in multiple independent syllabi → these are universally expected
- **Common topics:** appear in most syllabi → likely covered but not guaranteed
- **Specialized topics:** appear in only some syllabi → may indicate course emphasis or advanced treatment

Discard topics that are:
- Specific to one institution's particular framing
- Clearly prerequisite knowledge not part of this course
- Graduate-level topics for an undergraduate course

### Step 4: Validate with standard references

If a textbook is clearly associated with this subject, check its table of contents as a sanity check. A topic in every major textbook is definitively "core." A topic in no major textbook is either niche or misidentified.

---

## Mode B fallback (no web access)

If web search is unavailable, use world knowledge. Apply this reasoning:

1. What would a student need to know to be considered "competent" in this field after one university course?
2. What concepts appear in every introductory treatment of this subject?
3. What does the course likely build toward? (What's the "final boss" concept of the curriculum?)

State explicitly: "No web search available — outline based on standard curriculum knowledge. Please verify against your actual course syllabus."

For well-established STEM subjects (mathematics, physics, chemistry, biology, standard engineering disciplines, core CS courses), world knowledge is reliable enough to generate a solid outline.

For humanities, social sciences, or niche technical subjects, add a stronger caveat and encourage the user to provide a reference syllabus or textbook.

---

## Phase 2 gap analysis application

After identifying the standard coverage for the subject, compare against Phase 1 extractions:

| Gap type | Action |
|---|---|
| Core topic entirely missing | High-priority Phase 3 target; flag prominently in synthesis |
| Core topic covered superficially | Medium-priority; note the gap and depth needed |
| Common topic missing | Low-priority; mention as "this course does not cover X, which standard curricula often include" |
| Specialized topic missing | Note only if student's Phase 0 emphasis indicated interest in this area |

**Always be specific about the gap:** don't just say "thermodynamics is missing" — say "the course covers reaction enthalpy (Lecture 3) but does not treat entropy or Gibbs free energy, which are core to understanding reaction spontaneity in standard physical chemistry curricula."

---

## Note on CS/engineering subjects

For the 8 most common CS/engineering courses (OS, Networks, DSA, Databases, Computer Architecture, ML/DL, Distributed Systems, Compilers), web search is still the preferred approach. World knowledge fallback is reliable for these subjects given their stable, well-documented curricula.
