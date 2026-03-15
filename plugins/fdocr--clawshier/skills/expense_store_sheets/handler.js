#!/usr/bin/env node
require("dotenv").config({ path: require("path").resolve(__dirname, "../../.env") });

const { appendRow } = require("../../lib/googleSheets");

async function main() {
  let input = "";
  for await (const chunk of process.stdin) input += chunk;

  const expense = JSON.parse(input);
  const spreadsheetId = process.env.GOOGLE_SHEETS_ID;

  const itemsSummary = (expense.items || [])
    .map((i) => `${i.description} x${i.quantity || 1}`)
    .join("; ");

  const row = [
    expense.date,
    expense.vendor,
    expense.category,
    itemsSummary,
    expense.subtotal,
    expense.tax,
    expense.total,
    expense.currency,
    expense.fingerprint,
    new Date().toISOString(),
  ];

  const rowNumber = await appendRow(spreadsheetId, row);

  process.stdout.write(JSON.stringify({ success: true, row: rowNumber }));
}

main().catch((err) => {
  process.stderr.write(JSON.stringify({ error: err.message }));
  process.exit(1);
});
