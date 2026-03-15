#!/usr/bin/env node
require("dotenv").config({ path: require("path").resolve(__dirname, "../../.env") });

const OpenAI = require("openai");

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
const model = process.env.OPENAI_MODEL || "gpt-4o";

const SYSTEM_PROMPT = `You are a receipt parser. Given raw OCR text from a receipt or invoice, extract structured data as JSON.

Required fields:
- date: ISO 8601 date string (YYYY-MM-DD). Infer the year if missing.
- vendor: Business or store name.
- items: Array of { description, quantity, amount }. Use quantity 1 if not specified.
- subtotal: Number. If missing, sum the item amounts.
- tax: Number. Use 0 if not visible.
- total: Number. The final total paid.
- currency: ISO 4217 code (e.g. USD, EUR). Infer from symbols or country context.
- category: One of: "Food & Drink", "Transport", "Groceries", "Shopping", "Utilities", "Health", "Entertainment", "Travel", "Office", "Other".

Respond ONLY with valid JSON matching this schema. No markdown, no explanation.`;

async function main() {
  let input = "";
  for await (const chunk of process.stdin) input += chunk;

  const { ocr_text } = JSON.parse(input);
  if (!ocr_text) throw new Error("Missing ocr_text in input");

  const response = await openai.chat.completions.create({
    model,
    response_format: { type: "json_object" },
    messages: [
      { role: "system", content: SYSTEM_PROMPT },
      { role: "user", content: ocr_text },
    ],
    max_tokens: 1024,
  });

  const structured = JSON.parse(response.choices[0].message.content);

  const required = ["date", "vendor", "items", "total", "currency", "category"];
  for (const field of required) {
    if (structured[field] === undefined || structured[field] === null) {
      throw new Error(`Missing required field: ${field}`);
    }
  }

  process.stdout.write(JSON.stringify(structured));
}

main().catch((err) => {
  process.stderr.write(JSON.stringify({ error: err.message }));
  process.exit(1);
});
