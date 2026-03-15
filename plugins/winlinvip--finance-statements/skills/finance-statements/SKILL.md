---
name: finance-statements
description: "Track financial statements (bank, credit card, insurance, CanadaLife, etc.) in memory tracking files. Use when: (1) user provides a new statement (PDF text, pasted content) to record, (2) user wants to add a statement period into an existing memory/finance/*.md file, (3) user mentions 'add to' or 'statement' with financial content. NOT for: reading existing statements, general financial questions, or non-statement documents."
---

# Finance Statements

Track and record financial statement data into memory tracking files.

## Workflow

### Step 1: Identify the Target File

Scan `memory/finance/` for files matching `*statement*` patterns:

```bash
ls memory/finance/*statement* 2>/dev/null
```

Always present the list and ask the user which file(s) to update, even if they mentioned a target. This ensures the right file is confirmed before writing.

### Step 2: Load Target File & Accept New Statement

1. Read the target file to understand its existing structure, format, and conventions
2. Accept the new statement content from the user — this includes:
   - The **source file path** (e.g., PDF filename like `MasterCard Statement-1234 2025-03-25.pdf`)
   - The **statement content** (extracted PDF text, pasted content, etc.)
   - Record both the file path and content for reference
3. Identify the statement period, card/account, and key figures from the new data

#### Page-by-Page Mode

When the user says they'll provide pages one by one (or specifies a target file upfront):

1. **After Step 1**, read the target file to learn its structure
2. **For each page** the user provides:
   - Parse the content immediately
   - Append the parsed transactions to the target file right away (don't wait for all pages)
   - Confirm what was recorded (e.g., "Page 1: recorded 15 transactions, running total $X")
3. **After the last page** (user says "done", "last page", or "that's all"):
   - Run Step 4 (validate math) against the full statement
   - Update the period index table with the summary row

This avoids losing context across many pages and gives the user incremental progress.

#### Chinese Statements

When statement content is in Chinese:

- **Translate descriptions to English** but **keep the original Chinese in parentheses**
  - Example: `Amazon Shopping (亚马逊购物)` 
- Translate column headers, summary fields, and notes to English
- Currency amounts stay as-is (CNY ¥, etc.)
- Date formats: convert to YYYY-MM-DD

### Step 3: Record

1. Match the format and conventions of the existing file exactly (table structure, headers, field names, date formats, description shortening style)
2. Add a summary row to the period index table (if one exists)
3. Add the detailed statement section with:
   - Period summary (previous balance, payments, purchases, interest, fees, new balance, rewards)
   - Transaction table with all line items
4. Insert in chronological order, before any other card sections
5. Shorten merchant descriptions to match existing style (e.g., "GOOGLE*YOUTUBE SUPER G.CO/HELPPAY#NS ..." → "Google YouTube Super")

### Step 4: Validate the Math

After merging, independently verify the statement's arithmetic:

1. **Sum all transactions** (positive = charges, negative = credits/payments)
2. **Check:** Previous Balance + Purchases & Debits − Payments & Credits + Interest + Fees = New Balance
3. **Check:** Transaction sum should equal (Purchases & Debits − Payments & Credits)
4. **Report to user:**
   - ✅ "Statement math checks out" if totals match (within $0.02 rounding tolerance)
   - ⚠️ "Discrepancy found: calculated X, statement says Y" if they don't match — flag specific items if possible

Also verify:
- Cash back / points calculations if data is available
- Payment due dates and minimum payments are recorded
- No duplicate transactions (same date + amount + description appearing twice unless genuinely separate)

### File Naming Convention

Statement files live in `memory/finance/` and follow this pattern:

```
{bank}-{holder}-{type}-{accountid}-statements.md
```

- **bank:** Institution name (rbc, bmo, cibc, td, mbna, manulife, hsbc-hk, scb)
- **holder:** Account holder — `john`, `jane`, or `joint`
- **type:** Account type (chequing, saving, mc, visa)
- **accountid:** Last digits or full account number

Examples:
- `rbc-john-mc-1234-statements.md`
- `rbc-jane-saving-5678901-statements.md`
- `td-joint-9876543-statements.md`
- `bmo-jane-123456789-statements.md`

When creating a new statement file, follow this convention.

#### Create New Statement File from Existing Template

When the user wants to create a new statement file for a different bank/account using an existing file as a structural template:

1. Read the source file to extract its structure: section headings, subsection titles, table headers, summary field names, index table format
2. Create the new file (following the naming convention) with:
   - All section headings and subsection titles preserved
   - All table headers and column structures preserved
   - **No data copied** — use placeholders or leave empty rows
   - Update bank name, account number, card number references to the new account
3. Present the new file to the user for confirmation before they start adding statements

This ensures consistent formatting across all statement tracking files.

### Notes

- When a card has both primary and co-applicant transactions, keep them in separate sub-tables (matching existing format)
- Preserve existing content — only append new periods, never modify historical data
- If the statement period already exists in the file, warn the user before overwriting
