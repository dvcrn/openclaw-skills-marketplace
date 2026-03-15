---
name: clawshier
description: "Scan receipt or invoice photos sent via chat, extract expense data using OpenAI Vision, validate and deduplicate, then log to a Google Spreadsheet. Responds with a short summary of what was added."
---

> Generated note: shared plugin assets for this package live at the plugin root. Common local references were rewritten when they appeared in backticks or markdown links.

# Receipt Expense Tracker

Process receipt and invoice photos into structured expenses and log them to Google Sheets.

## When to Activate

Activate this skill when the user sends a **photo or image** and any of these apply:

- The message mentions receipts, invoices, expenses, or purchases
- The image appears to be a receipt, invoice, or bill
- The user asks to log, track, or record an expense
- The user asks to add something to their expense spreadsheet

Do **not** activate for images that are clearly not financial documents (memes, screenshots of conversations, etc.).

## Pipeline

Run each step sequentially. If a step fails, retry it up to **2 times** before reporting the error.

### Step 1 — OCR

Save the received image to a temporary file, then extract text:

```bash
node skills/receipt_ocr/handler.js --image <path_to_image>
```

Output schema:

```json
{ "ocr_text": "STARBUCKS\n123 Main St..." }
```

### Step 2 — Structure

Pipe the OCR output to the structurer:

```bash
echo '<step1_output>' | node skills/expense_structurer/handler.js
```

Output schema:

```json
{
  "date": "2026-03-05",
  "vendor": "Starbucks",
  "items": [
    { "description": "Caffe Latte", "quantity": 1, "amount": 5.95 }
  ],
  "subtotal": 5.95,
  "tax": 0.52,
  "total": 6.47,
  "currency": "USD",
  "category": "Food & Drink"
}
```

### Step 3 — Validate

Pipe the structured expense to the validator:

```bash
echo '<step2_output>' | node skills/expense_validator/handler.js
```

This step:
- Generates a SHA-256 fingerprint from `vendor + date + total`
- Checks Google Sheets for duplicate fingerprints
- Normalizes currency codes and trims whitespace
- Validates all required fields are present

If a **duplicate is found**, stop the pipeline and tell the user:

> "This receipt appears to already be logged (vendor, date, total match an existing entry). Skipping."

Output schema (adds `fingerprint` field):

```json
{
  "date": "2026-03-05",
  "vendor": "Starbucks",
  "items": [...],
  "subtotal": 5.95,
  "tax": 0.52,
  "total": 6.47,
  "currency": "USD",
  "category": "Food & Drink",
  "fingerprint": "a1b2c3..."
}
```

### Step 4 — Store

Pipe the validated expense to the store:

```bash
echo '<step3_output>' | node skills/expense_store_sheets/handler.js
```

Appends a row with columns: Date, Vendor, Category, Items, Subtotal, Tax, Total, Currency, Fingerprint, Added At.

Output schema:

```json
{ "success": true, "row": 42 }
```

## Response

After a successful pipeline run, reply with a short summary:

> Added expense: **{vendor}** — {total} {currency} on {date} ({category}). Row #{row} in your spreadsheet.

## Error Handling

- Retry each step up to 2 times on failure
- If a step fails after retries, respond with which step failed and the error message
- If the image is not a receipt/invoice (OCR returns no useful text), tell the user:
  > "I couldn't detect a receipt or invoice in that image. Could you try again with a clearer photo?"

## Setup

```bash
npm install
cp .env.example .env
# Fill in OPENAI_API_KEY, GOOGLE_SHEETS_ID, GOOGLE_SERVICE_ACCOUNT_KEY
```

See `../../README.md` for full setup instructions.
