---
name: mba-thesis-advisor
description: "MBA thesis advisor for improving academic papers to award-winning quality. Use when a user wants to: (1) upgrade an MBA thesis to top-tier quality (e.g., Tsinghua excellent graduation thesis), (2) diagnose problems with an existing thesis draft, (3) rewrite thesis sections with critical analysis (\"writing style B\"), (4) build a strong theoretical framework, (5) identify and articulate the original contribution (novelty) of a thesis, or (6) revise conclusions to be insightful and non-trivial. Handles LaTeX-based theses (thuthesis template preferred) and Chinese MBA thesis conventions. Trigger phrases: \"帮我改论文\", \"MBA论文\", \"优秀毕业论文\", \"thesis improvement\", \"论文诊断\", \"帮同学改论文\"."
---

# MBA Thesis Advisor Skill

This skill guides you through diagnosing, restructuring, and elevating an MBA thesis
from a passing draft to award-winning quality. It is based on proven techniques for
Tsinghua MBA theses but applies broadly to any Chinese or international MBA program.

---

## Core Philosophy: Writing Style B (批判性写法)

Most MBA thesis drafts use **Writing Style A**: describe a company's problem →
apply standard frameworks (SWOT, PEST, Porter's Five Forces) → propose generic
recommendations. This produces forgettable, low-scoring work.

**Writing Style B** (critical-analytical) is what separates excellent theses:

- Start with an **insider observation** that contradicts the conventional wisdom
- Build a framework that **explains the mechanism**, not just describes the phenomenon
- Produce **conclusions that are non-obvious**, falsifiable, and boundary-conditioned
- The reader finishes thinking: *"I wouldn't have known this without this paper"*

**Three markers of Style B:**
1. Counterintuitive finding backed by data
2. Identified mechanism (not just correlation)
3. Clear boundary conditions ("this holds when X, fails when Y")

---

## Phase 1: Diagnosis

### Step 1.1 — Read All Chapters

Read every `.tex` file in the `mydata/` directory (or equivalent), including:
`chap01.tex` through `chap05.tex`, `abstract.tex`

For each chapter, assess:
- What claim is being made?
- What evidence supports it?
- Is this original or could it appear in any industry report?

### Step 1.2 — Score the Draft

Rate the draft on five dimensions:

| Dimension | Question | Red Flag |
|-----------|----------|----------|
| **Contribution** | What does this paper say that no one has said before? | "Any MBA textbook covers this" |
| **Insider access** | Does the author leverage their unique position? | All evidence is publicly available |
| **Theory fit** | Does the framework match the research question? | SWOT used as the primary lens |
| **Data quality** | Are claims supported by specific numbers? | Qualitative description only |
| **Conclusion rigor** | Are conclusions falsifiable and bounded? | "Company should improve X" |

### Step 1.3 — Identify the Insider Angle

Ask the author five questions to unlock their insider perspective. See
`references/diagnostic-questions.md` for the full question set.

The answers to these questions are the **raw material** for the entire rewrite.
Do not proceed to Phase 2 without them.

---

## Phase 2: Framework Upgrade

### Step 2.1 — Choose the Right Theoretical Backbone

Replace or supplement generic MBA frameworks with higher-level academic theory:

| Research Context | Recommended Framework |
|-----------------|----------------------|
| Organizational change / R&D management | Dynamic Capabilities (Teece 2007) |
| Cross-cultural / institutional environment | Institutional Isomorphism (DiMaggio & Powell 1983) |
| Strategy execution failure | Principal-Agent Theory + Path Dependency |
| Technology adoption | Absorptive Capacity (Cohen & Levinthal 1990) |
| Team / org design | Team Topologies + Conway's Law |
| VUCA / uncertainty | VUCA framework + Scenario Planning |
| Supply chain / platform | Resource-Based View (Barney 1991) |

**Rule:** PEST and Porter's Five Forces are acceptable as *context-setting tools*
in Chapter 2–3, but must NOT be the primary analytical lens in Chapter 4.

### Step 2.2 — Build the Analytical Framework Diagram

Create a framework diagram (Figure in Chapter 2 or Chapter 1) that shows:
1. External environment pressures → Company response mechanisms → Outcomes
2. Where the theoretical lens applies
3. The research question mapped onto the framework

This diagram becomes the "backbone" referenced throughout the thesis.

---

## Phase 3: Excavate the Original Contribution

### Step 3.1 — Find the Mechanism

From the insider angle (Phase 1, Step 1.3), identify a **mechanism**: a causal
chain that explains WHY something happens, not just that it happens.

Template:
> "[Company/industry] faces [problem]. Conventional wisdom says [X]. But our
> analysis shows the real mechanism is [Y]: when [condition], [cause] leads to
> [effect] because [mechanism]. This matters because [implication]."

### Step 3.2 — Name the Contribution

Give the original contribution a **memorable name or label**. Examples:
- "运动式研发" (campaign-style R&D)
- "本土化悖论" (localization paradox)
- "监管驱动的战略漂移" (regulatory-driven strategic drift)

A named concept is citable, memorable, and signals academic seriousness.

### Step 3.3 — State the Contribution Explicitly

In the thesis conclusion chapter, add a dedicated subsection:

```latex
\subsection{理论贡献}
本文的主要理论贡献包括：
\begin{enumerate}
  \item \textbf{概念提出：}...（原创概念名称）...
  \item \textbf{机制识别：}...（因果机制）...
  \item \textbf{框架整合：}...（理论整合方式）...
\end{enumerate}
```

---

## Phase 4: Rewrite Critical Sections

### Chapter 4 (Core Analysis) — Priority Rewrite

This chapter must carry the weight of the thesis. Checklist:
- [ ] Opens with the research question, not background narrative
- [ ] Every section heading makes a **claim**, not a topic label
  - Bad: "4.2 公司战略分析"
  - Good: "4.2 监管趋严下CT公司战略漂移的三重机制"
- [ ] Each subsection: claim → evidence → mechanism → implication
- [ ] At least one counterintuitive finding per major section
- [ ] Quantitative evidence (even rough estimates with justification)

### Chapter 5 (Conclusion) — Critical Rewrite

Replace generic recommendations with:
1. **Core finding statement** (1 paragraph): the single most important thing this paper shows
2. **Theoretical contribution** (named concepts, mechanisms)
3. **Managerial implications** (specific to THIS company, not any company)
4. **Boundary conditions**: when do these findings NOT apply?
5. **Limitations and future research**

Avoid these phrases in conclusions:
- "企业应加强…" (generic)
- "建议公司提升…" (not actionable)
- "未来可进一步研究…" (vague)

### Chapter 2 (Literature Review) — Targeted Additions

Add 3–5 foundational papers for the chosen theoretical framework (Step 2.1).
Structure: existing theory → gap → how this paper fills the gap.

---

## Phase 5: Data and Evidence

### Step 5.1 — Identify Data Sources

For Chinese internet/tech companies: annual reports (IR pages), WIND, Bloomberg
For industrial/agriculture companies: CNKI industry reports, company IR pages,
China customs data (海关总署), Ministry of Agriculture data

### Step 5.2 — Minimum Evidence Standards

Each major claim in Chapter 4 needs at least ONE of:
- A specific number with source citation
- A named internal event/decision (anonymized if needed)
- A direct quote from interview/survey (if primary research was conducted)
- A comparison across time periods or competitors

### Step 5.3 — Figures and Tables

Minimum recommended figures for a strong thesis:
- 1 framework diagram (Chapter 2)
- 1–2 trend charts (Chapter 3: industry context)
- 1–2 comparison tables (Chapter 4: company vs. peers)
- 1 summary framework (Chapter 5: contribution visualization)

Use Python + matplotlib/seaborn for charts. Save as both PDF (for LaTeX) and PNG.

---

## Phase 6: Quality Check

Before finalizing, verify:

### Academic Rigor Checklist
- [ ] Every claim has a citation or data point
- [ ] No paragraph is purely descriptive (each ends with "so what")
- [ ] Theory names are correctly cited with original authors and year
- [ ] Conclusion matches what was promised in the introduction

### Style B Checklist
- [ ] At least one finding that surprises the reader
- [ ] Original concept or mechanism named and defined
- [ ] "Theoretical contribution" section explicitly states novelty
- [ ] Recommendations are specific to this company/case

### LaTeX/Formatting Checklist (thuthesis)
- [ ] All figures referenced with `\ref{}` and captioned
- [ ] Tables have proper `\caption{}` and footnotes for data sources
- [ ] Bibliography uses consistent citation style
- [ ] Abstract clearly states research question, method, finding, contribution

---

## LaTeX Workflow Notes

**Thesis root file:** typically `my-thesis.tex`
**Chapter files:** `mydata/chap01.tex` through `mydata/chap05.tex`
**Figures:** place in `myfigure/` or `figures/`; reference with relative path

**Build command:**
```bash
cd <thesis-root>
latexmk -xelatex my-thesis.tex
```

**Git workflow:** commit only source files; ignore build artifacts.
Standard `.gitignore` entries: `*.pdf`, `*.log`, `*.aux`, `*.synctex.gz`, `*.bbl`, `*.blg`
Do NOT ignore: `myfigure/*.py`, `myfigure/*.png`, `mydata/*.tex`, `refs.bib`, `abstract.tex`

---

## References

See `references/` directory for:
- `diagnostic-questions.md` — Five questions to unlock the author's insider perspective
- `framework-selection.md` — Guide to choosing the right theoretical framework
- `style-b-examples.md` — Before/after examples of Style A → Style B rewrites
