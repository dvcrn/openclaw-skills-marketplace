#!/usr/bin/env node

// web-search-pro: Unified multi-engine search with full parameter support
// Engines: Tavily, Exa, Serper, SerpAPI
// Priority: Tavily > Exa > Serper > SerpAPI (auto-select based on query + available keys)

import * as tavily from "./engines/tavily.mjs";
import * as exa from "./engines/exa.mjs";
import * as serper from "./engines/serper.mjs";
import * as serpapi from "./engines/serpapi.mjs";

const ENGINES = { tavily, exa, serper, serpapi };
const ENGINE_LIST = [tavily, exa, serper, serpapi]; // default priority order
const SEARCH_ENGINES = new Set(["google", "bing", "baidu", "yandex", "duckduckgo"]);

function usage(exitCode = 2) {
  console.error(`web-search-pro — Multi-engine AI search with full parameter control

Usage:
  search.mjs "query" [options]

Options:
  --engine <name>           Force engine: tavily|exa|serper|serpapi (default: auto)
  -n <count>                Number of results (default: 5)
  --deep                    Deep/advanced search mode (Tavily/Exa only)
  --news                    News search mode (Tavily/Serper/SerpAPI only)
  --days <n>                Limit news to last N days (Tavily news only)
  --include-domains <d,...> Only search these domains (comma-separated)
  --exclude-domains <d,...> Exclude these domains (comma-separated)
  --time-range <range>      Time filter: day|week|month|year
  --from <YYYY-MM-DD>       Results published after this date
  --to <YYYY-MM-DD>         Results published before this date
  --search-engine <name>    SerpAPI sub-engine: google|bing|baidu|yandex|duckduckgo
  --country <code>          Country code (e.g., us, cn, de)
  --lang <code>             Language code (e.g., en, zh, de)
  --json                    Output raw JSON instead of Markdown

Environment variables (configure at least one):
  TAVILY_API_KEY            Tavily API key (recommended, AI-optimized)
  EXA_API_KEY               Exa API key (semantic search)
  SERPER_API_KEY            Serper API key (Google SERP)
  SERPAPI_API_KEY           SerpAPI key (multi-engine)`);
  process.exit(exitCode);
}

function fail(message, exitCode = 2) {
  console.error(message);
  process.exit(exitCode);
}

function parseDomainList(rawValue, optionName) {
  const values = rawValue
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
  if (!values.length) {
    fail(`${optionName} expects at least one domain`);
  }
  return values;
}

function validateDateStr(rawValue, optionName) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(rawValue)) {
    fail(`${optionName} must be in YYYY-MM-DD format`);
  }
}

function readOptionValue(args, i, optionName) {
  const value = args[i + 1];
  if (value === undefined || value === "") {
    fail(`Missing value for ${optionName}`);
  }
  return value;
}

// Parse arguments
const args = process.argv.slice(2);
if (args.length === 0) usage();

const opts = {
  engine: null,
  count: 5,
  deep: false,
  news: false,
  days: null,
  includeDomains: null,
  excludeDomains: null,
  timeRange: null,
  fromDate: null,
  toDate: null,
  searchEngine: null,
  country: null,
  lang: null,
  json: false,
};

const positionals = [];
for (let i = 0; i < args.length; i++) {
  const a = args[i];

  if (a === "-h" || a === "--help") {
    usage(0);
  }

  switch (a) {
    case "--engine": {
      opts.engine = readOptionValue(args, i, "--engine");
      i++;
      break;
    }
    case "-n": {
      const raw = readOptionValue(args, i, "-n");
      opts.count = Number.parseInt(raw, 10);
      i++;
      break;
    }
    case "--deep":
      opts.deep = true;
      break;
    case "--news":
      opts.news = true;
      break;
    case "--days": {
      const raw = readOptionValue(args, i, "--days");
      opts.days = Number.parseInt(raw, 10);
      i++;
      break;
    }
    case "--include-domains": {
      const raw = readOptionValue(args, i, "--include-domains");
      opts.includeDomains = parseDomainList(raw, "--include-domains");
      i++;
      break;
    }
    case "--exclude-domains": {
      const raw = readOptionValue(args, i, "--exclude-domains");
      opts.excludeDomains = parseDomainList(raw, "--exclude-domains");
      i++;
      break;
    }
    case "--time-range": {
      opts.timeRange = readOptionValue(args, i, "--time-range");
      i++;
      break;
    }
    case "--from": {
      opts.fromDate = readOptionValue(args, i, "--from");
      i++;
      break;
    }
    case "--to": {
      opts.toDate = readOptionValue(args, i, "--to");
      i++;
      break;
    }
    case "--search-engine": {
      opts.searchEngine = readOptionValue(args, i, "--search-engine");
      i++;
      break;
    }
    case "--country": {
      opts.country = readOptionValue(args, i, "--country");
      i++;
      break;
    }
    case "--lang": {
      opts.lang = readOptionValue(args, i, "--lang");
      i++;
      break;
    }
    case "--json":
      opts.json = true;
      break;
    default:
      if (a.startsWith("-")) {
        fail(`Unknown option: ${a}`);
      }
      positionals.push(a);
  }
}

const query = positionals.join(" ").trim();
if (!query) {
  fail('Missing query. Usage: search.mjs "query" [options]');
}

function validateOptions(opts) {
  if (!Number.isInteger(opts.count) || opts.count < 1) {
    fail("-n must be a positive integer");
  }

  if (opts.days !== null && (!Number.isInteger(opts.days) || opts.days < 1)) {
    fail("--days must be a positive integer");
  }

  if (opts.days !== null && !opts.news) {
    fail("--days can only be used with --news");
  }

  if (opts.timeRange) {
    const validRanges = new Set(["day", "week", "month", "year"]);
    if (!validRanges.has(opts.timeRange)) {
      fail("--time-range must be one of: day, week, month, year");
    }
  }

  if (opts.fromDate) validateDateStr(opts.fromDate, "--from");
  if (opts.toDate) validateDateStr(opts.toDate, "--to");
  if (opts.fromDate && opts.toDate && opts.fromDate > opts.toDate) {
    fail("--from must be earlier than or equal to --to");
  }

  if (opts.searchEngine && !SEARCH_ENGINES.has(opts.searchEngine)) {
    fail("--search-engine must be one of: google, bing, baidu, yandex, duckduckgo");
  }

  if (opts.searchEngine && opts.engine && opts.engine !== "serpapi") {
    fail("--search-engine can only be used with --engine serpapi");
  }
}

validateOptions(opts);

function validateEngineCapabilities(engineName, opts) {
  const supportsDeep = engineName === "tavily" || engineName === "exa";
  const supportsNews = engineName === "tavily" || engineName === "serper" || engineName === "serpapi";

  if (opts.deep && !supportsDeep) {
    fail(`Engine ${engineName} does not support --deep`);
  }

  if (opts.news && !supportsNews) {
    fail(`Engine ${engineName} does not support --news`);
  }

  if (opts.days !== null && engineName !== "tavily") {
    fail("--days is only supported with Tavily news mode (use --engine tavily)");
  }

  if (opts.searchEngine && engineName !== "serpapi") {
    fail("--search-engine is only supported by SerpAPI");
  }
}

// Engine selection logic
function selectEngine(opts) {
  // Explicit engine choice
  if (opts.engine) {
    const eng = ENGINES[opts.engine];
    if (!eng) {
      fail(`Unknown engine: ${opts.engine}. Available: ${Object.keys(ENGINES).join(", ")}`, 1);
    }
    if (!eng.isAvailable()) {
      fail(`Engine ${opts.engine} selected but API key not configured.`, 1);
    }
    return eng;
  }

  // SerpAPI sub-engine requested -> force SerpAPI (including google)
  if (opts.searchEngine) {
    if (serpapi.isAvailable()) return serpapi;
    fail(`--search-engine ${opts.searchEngine} requires SERPAPI_API_KEY`, 1);
  }

  // News + days requires Tavily
  if (opts.news && opts.days !== null) {
    if (tavily.isAvailable()) return tavily;
    fail("--news --days requires TAVILY_API_KEY", 1);
  }

  // News search
  if (opts.news) {
    if (serper.isAvailable()) return serper;
    if (tavily.isAvailable()) return tavily;
    if (serpapi.isAvailable()) return serpapi;
    fail("--news requires SERPER_API_KEY, TAVILY_API_KEY, or SERPAPI_API_KEY", 1);
  }

  // Deep search
  if (opts.deep) {
    if (tavily.isAvailable()) return tavily;
    if (exa.isAvailable()) return exa;
    fail("--deep requires TAVILY_API_KEY or EXA_API_KEY", 1);
  }

  // Domain filtering -> prefer Tavily/Exa (native support), then fallback engines
  if (opts.includeDomains?.length || opts.excludeDomains?.length) {
    if (tavily.isAvailable()) return tavily;
    if (exa.isAvailable()) return exa;
  }

  // Default priority: Tavily > Exa > Serper > SerpAPI
  for (const eng of ENGINE_LIST) {
    if (eng.isAvailable()) return eng;
  }

  fail("No search engine configured. Set at least one API key:\n  TAVILY_API_KEY, EXA_API_KEY, SERPER_API_KEY, or SERPAPI_API_KEY", 1);
}

// Format output
function formatMarkdown(result, query) {
  const lines = [];
  const results = Array.isArray(result.results) ? result.results : [];

  lines.push(`## Search: ${query}`);
  lines.push(`**Engine**: ${result.engine}\n`);

  if (result.answer) {
    lines.push("### Answer\n");
    lines.push(result.answer);
    lines.push("\n---\n");
  }

  lines.push(`### Results (${results.length})\n`);
  for (const r of results) {
    const score = Number.isFinite(r.score) ? ` (${(r.score * 100).toFixed(0)}%)` : "";
    const published = typeof r.publishedDate === "string" ? r.publishedDate.slice(0, 10) : null;
    const date = r.date ? ` [${r.date}]` : published ? ` [${published}]` : "";
    const title = r.title || "(untitled)";
    lines.push(`- **${title}**${score}${date}`);
    lines.push(`  ${r.url || ""}`);
    if (r.content) {
      lines.push(`  ${r.content.slice(0, 400)}${r.content.length > 400 ? "..." : ""}`);
    }
    lines.push("");
  }
  return lines.join("\n");
}

// Main
try {
  const engine = selectEngine(opts);
  validateEngineCapabilities(engine.name(), opts);

  const result = await engine.search(query, opts);

  if (opts.json) {
    console.log(JSON.stringify(result, null, 2));
  } else {
    console.log(formatMarkdown(result, query));
  }
} catch (err) {
  console.error(`Error: ${err.message}`);
  process.exit(1);
}
