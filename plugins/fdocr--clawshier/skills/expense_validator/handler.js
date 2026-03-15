#!/usr/bin/env node
require("dotenv").config({ path: require("path").resolve(__dirname, "../../.env") });

const { fingerprint } = require("../../lib/hashing");
const { getColumn } = require("../../lib/googleSheets");

const CURRENCY_ALIASES = { "$": "USD", "€": "EUR", "£": "GBP", "¥": "JPY" };
const FINGERPRINT_COLUMN = "I";

function normalize(expense) {
  expense.vendor = (expense.vendor || "").trim();
  expense.date = (expense.date || "").trim();
  expense.category = (expense.category || "Other").trim();

  if (CURRENCY_ALIASES[expense.currency]) {
    expense.currency = CURRENCY_ALIASES[expense.currency];
  }
  expense.currency = (expense.currency || "USD").toUpperCase().trim();

  expense.total = parseFloat(expense.total) || 0;
  expense.subtotal = parseFloat(expense.subtotal) || expense.total;
  expense.tax = parseFloat(expense.tax) || 0;

  return expense;
}

function validate(expense) {
  const missing = [];
  if (!expense.vendor) missing.push("vendor");
  if (!expense.date) missing.push("date");
  if (!expense.total) missing.push("total");
  if (missing.length) throw new Error(`Missing required fields: ${missing.join(", ")}`);
}

async function main() {
  let input = "";
  for await (const chunk of process.stdin) input += chunk;

  const expense = normalize(JSON.parse(input));
  validate(expense);

  expense.fingerprint = fingerprint(expense.vendor, expense.date, expense.total);

  const spreadsheetId = process.env.GOOGLE_SHEETS_ID;
  const existing = await getColumn(spreadsheetId, FINGERPRINT_COLUMN);

  if (existing.includes(expense.fingerprint)) {
    throw new Error(
      `Duplicate receipt detected (vendor: ${expense.vendor}, date: ${expense.date}, total: ${expense.total})`
    );
  }

  process.stdout.write(JSON.stringify(expense));
}

main().catch((err) => {
  process.stderr.write(JSON.stringify({ error: err.message }));
  process.exit(1);
});
