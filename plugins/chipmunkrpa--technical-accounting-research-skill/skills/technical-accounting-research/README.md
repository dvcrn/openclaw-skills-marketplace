# Technical Accounting Research Skill

A Codex skill for technical accounting issue research and documentation under U.S. GAAP / SEC-focused reporting contexts.

## What It Does

- Forces clarification questions before analysis.
- Confirms output format (`memo`, `email`, or `q-and-a`) before drafting.
- Performs internet research of relevant guidance (FASB, AICPA, SEC, Big 4 interpretive sources).
- Applies standards to the fact pattern and produces a DOCX deliverable.

## Skill Layout

- `SKILL.md`: Core workflow and behavior rules.
- `agents/openai.yaml`: UI metadata for invocation.
- `references/`: Clarification checklist, source hierarchy, JSON schema, sample payload.
- `scripts/build_accounting_report_docx.py`: DOCX report generator.

## Requirements

- Python 3.11+
- `python-docx`

Install dependency:

```bash
python -m pip install --user python-docx
```

## Generate a DOCX Report

```bash
python scripts/build_accounting_report_docx.py \
  --input-json references/example_report_input.json \
  --output-docx output/technical-accounting-report.docx \
  --format memo
```

Allowed formats: `memo`, `email`, `q-and-a`.

## License

This project is licensed under the MIT License. See `LICENSE`.
