---
name: invoice-scan
description: "AI-powered invoice scanning and data extraction from images and PDFs. Use when: (1) user sends an invoice image/PDF to scan or extract data from, (2) converting paper/scanned invoices to structured JSON, CSV, or Excel, (3) validating invoice arithmetic or classifying document types (invoice vs receipt vs other), (4) processing handwritten invoices, stamps, or multi-language documents (Chinese, Russian, European, etc.), (5) user asks to read/parse/extract an invoice. Works in two modes: agent-native (uses your own vision — no API key needed) or CLI standalone (needs ANTHROPIC_API_KEY). Supports Claude vision models."
---

# Invoice Scan

Extract structured data from any invoice — printed, handwritten, multi-language, stamped.

## Setup

Install dependencies once:

```bash
cd {SKILL_DIR}/scripts && npm install --production
```

Set API key — check env `ANTHROPIC_API_KEY`. If not set, ask the user:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

## Scanning

### CLI

```bash
node {SKILL_DIR}/scripts/cli.js scan <image-or-pdf> [options]
```

Options:
- `--format json|csv|excel` (default: json)
- `--output <path>` — write to file (xlsx for excel)
- `--api-key <key>` — override env key
- `--accept strict|relaxed|any` — doc type filter (default: relaxed)
- `--no-preprocess` — skip image enhancement
- `--model <model>` — Anthropic model (default: claude-sonnet-4-20250514)

### Library

```javascript
const { scanInvoice, formatOutput } = require('{SKILL_DIR}/scripts');
const invoice = await scanInvoice(filePath, { apiKey });

// Format
const json = formatOutput(invoice, 'json');
const csv  = formatOutput(invoice, 'csv');
const xlsx = formatOutput(invoice, 'excel'); // Buffer — write to .xlsx
```

## Agent-Native Mode (No API Key)

If you have vision capabilities, skip the CLI entirely:

1. Read the image yourself using the image tool
2. Extract fields following the schema in `references/canonical-schema.md`
3. Run validation: `require('{SKILL_DIR}/scripts/validation/arithmetic').validateArithmetic(invoice)`
4. Format output: `formatOutput(invoice, 'excel')`

This avoids an API call — you ARE the vision model.

## Conversational Use

When user sends an invoice:

1. Save the image, run `scanInvoice(path, { apiKey })`
2. Summarise:
```
📄 Invoice #12345 | 2026-02-15
   Supplier: Acme Ltd → Buyer: TechCorp UK
   Net: £1,125.00 | VAT: £225.00 | Gross: £1,350.00
   Items: 3 | Arithmetic: ✅ | Quality: good (9/9)
```
3. If rejected: "Classified as {type}, not an invoice."
4. Offer: "Want JSON, CSV, or Excel?"

## Output Formats

**JSON** — full canonical schema, all fields, nested objects.

**CSV** — Zoho-style flat: one row per line item, header fields repeated per row. 41 columns.

**Excel** — Sheet 1 "Invoice": same flat table as CSV. Sheet 2 "Validation": arithmetic, errors, warnings, field confidence, stamps, handwriting annotations.

## What Gets Extracted

**Header**: invoice#, dates, supplier/buyer (name, address, VAT#), currency, payment terms, bank details (IBAN/BIC/account/sort).

**Line items**: description, qty, unit, price, total, VAT %, SKU, discount.

**References**: PO, contract, GRN, inspection, timesheet, project, proforma.

**Additional**: handwritten notes, stamps/seals, document language.

## Validation

- **9 document types**: invoice, credit-note, receipt, purchase-order, delivery-note, confirmation, statement, other-financial, not-financial
- **Arithmetic**: line sums, VAT calcs, gross = net + VAT
- **15 business rules**: missing fields, suspicious numbers, receipt signals
- **Quality score**: 0.0–1.0 (good ≥0.7, partial ≥0.3, poor <0.3)

## Accept Modes

- `strict` — invoices + credit notes only
- `relaxed` (default) — also receipts, proformas
- `any` — extracts all, just classifies

## Multi-Language & Locale

Auto-detects language. Handles: US/UK (1,234.56), European (1.234,56), French (1 234,56), Indian (1,23,456.78). Tested: English, Chinese, Russian, Filipino, German.

## References

- **Full schema**: Read `references/canonical-schema.md`
- **Validation rules**: Read `references/validation-rules.md`
