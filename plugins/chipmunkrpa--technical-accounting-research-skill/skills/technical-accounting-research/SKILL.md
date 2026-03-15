---
name: technical-accounting-research
description: "Research technical accounting treatment and financial statement disclosure for specific transactions using U.S. GAAP and SEC-focused sources. Use when a user asks how to account for a transaction, what journal entries, presentation, or disclosures are required, or needs accounting-position documentation in memo, email, or Q-and-A DOCX format."
---

# Technical Accounting Research

## Overview

Handle transaction-specific accounting questions through a fixed sequence: gather facts, confirm output format, research guidance online, apply standards, and deliver a DOCX report.

## Required Behavior

- Ask clarification questions before analysis.
- Confirm requested output format: `memo`, `email`, or `q-and-a`.
- Research the internet before final conclusions, even if guidance seems familiar.
- Distinguish authoritative guidance from interpretive guidance.
- Cite sources with links and accessed date in the deliverable.
- State assumptions explicitly when facts remain unknown.

## Workflow

### 1. Intake and Scope

- Capture the user issue in one sentence.
- Confirm reporting basis and jurisdiction (`US GAAP`, `SEC filer status`, and whether disclosures are public-company or private-company focused).
- Confirm reporting period and materiality context.

### 2. Clarification Questions (Mandatory)

- Use [references/clarification-question-bank.md](references/clarification-question-bank.md).
- Ask only the questions needed for the fact pattern; do not skip critical facts.
- Pause analysis until enough facts are available to form a defensible conclusion.
- If facts stay incomplete, proceed with explicit assumptions and sensitivity notes.

### 3. Output Format Confirmation (Mandatory)

- Ask which format is required (`memo` for formal documentation, `email` for concise communication, `q-and-a` for direct question and answer support).
- If no preference is provided, default to `memo`.

### 4. Research Guidance

- Research sources using the priority and reliability rules in [references/source-priority.md](references/source-priority.md).
- Prefer primary and authoritative sources first (FASB/SEC/AICPA standard-setting materials).
- Use Big 4 publications as interpretive support, not sole authority.
- Capture citation labels and URLs for each source used.

### 5. Technical Analysis

- Frame the accounting issue.
- Map facts to recognition, measurement, presentation, and disclosure guidance.
- Evaluate reasonable alternatives and explain rejection rationale.
- Conclude with recommended accounting treatment, disclosure direction, and key risks.
- Include journal entry examples when useful for implementation.

### 6. Draft and Materialize DOCX

- Build a JSON payload using [references/report-json-schema.md](references/report-json-schema.md).
- Run:

```bash
python scripts/build_accounting_report_docx.py \
  --input-json <analysis.json> \
  --output-docx <technical-accounting-report.docx> \
  --format <memo|email|q-and-a>
```

- The script produces a DOCX with:
- Title and metadata.
- Facts and issue statement.
- Guidance table with links.
- Analysis and conclusion.
- Disclosure considerations.
- Open items and assumptions.

### 7. Quality Check

- Confirm the conclusion is consistent with cited guidance.
- Confirm all significant assumptions are disclosed.
- Confirm the output format matches user request.
- Confirm every external source in the analysis has a URL listed in the report.

## Resources

- Clarifying question checklist: [references/clarification-question-bank.md](references/clarification-question-bank.md)
- Source hierarchy and citation rules: [references/source-priority.md](references/source-priority.md)
- JSON format for DOCX generation: [references/report-json-schema.md](references/report-json-schema.md)
- Example report payload: [references/example_report_input.json](references/example_report_input.json)
- DOCX generator: `scripts/build_accounting_report_docx.py`

## Dependency

Install once if needed:

```bash
python -m pip install --user python-docx
```
