#!/usr/bin/env node

function usage() {
  console.error(`Usage: search.mjs "here is your query" [-n 5] [--start_time "2026-01-01T00:00:00Z"] [--end_time "2026-01-31T23:59:59Z"]`);
  process.exit(2);
}

const args = process.argv.slice(2);
if (args.length === 0 || args[0] === "-h" || args[0] === "--help") usage();

const query = args[0];
let n = 5;
let startTime = null;
let endTime = null;

for (let i = 1; i < args.length; i++) {
  const param = args[i];
  if (param === "-n") {
    n = Number.parseInt(args[i + 1] ?? "5", 10);
    i++;
    continue;
  }
  if (param === "--start_time") {
    startTime = args[i + 1] ?? null;
    i++;
    continue;
  }
  if (param === "--end_time") {
    endTime = args[i + 1] ?? null;
    i++;
    continue;
  }
  console.error(`Unknown arg: ${param}`);
  usage();
}

const apiKey = (process.env.OCTEN_API_KEY ?? "").trim();
if (!apiKey) {
  console.error("Missing OCTEN_API_KEY. Please set it in the environment variables. example: export OCTEN_API_KEY=your-api-key");
  process.exit(1);
}

const body = {
  query: query,
  count: Math.max(1, Math.min(n, 20))
};

if (startTime) {
  body.start_time = startTime;
}

if (endTime) {
  body.end_time = endTime;
}

const resp = await fetch("https://api.octen.ai/search", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-Api-Key": apiKey,
  },
  body: JSON.stringify(body),
});

if (!resp.ok) {
  const text = await resp.text().catch(() => "");
  throw new Error(`Octen Search failed (${resp.status}): ${text}`);
}

const respBody = await resp.json();

if (respBody.code !== 0) {
  throw new Error(`Octen Search failed (${respBody.code}): ${respBody.message}`);
}

const results = (respBody.data?.results ?? []).slice(0, n);

console.log(`Found ${results.length} search result items from Octen\n`);

if (results.length === 0) {
  console.log("No search results found.");
  process.exit(0);
}

console.log("## Search Results\n");

for (const r of results) {
  const title = String(r?.title ?? "").trim();
  const url = String(r?.url ?? "").trim();
  const highlight = String(r?.highlight ?? "").trim();
  const timePublished = String(r?.time_published ?? "").trim();
  
  if (!title || !url) continue;

  console.log(`- **Title**: ${title}`);
  console.log(`  **URL**: ${url}`);
  if (timePublished) {
    console.log(`  **TimePublished**: ${timePublished}`);
  }
  if (highlight) {
    console.log(`  **Highlight**: ${highlight}`);
  }
  console.log();
}
