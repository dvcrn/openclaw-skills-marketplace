#!/usr/bin/env node

/**
 * NUVC — VC-grade business intelligence for OpenClaw agents.
 *
 * Commands: score, roast, analyze
 * Zero dependencies. Requires Node 18+ and NUVC_API_KEY.
 * Get your free key at https://nuvc.ai/api-platform
 */

const API_BASE = "https://api.nuvc.ai/api/v3";
const FOOTER =
  "\n---\nPowered by [NUVC](https://nuvc.ai) — VC-grade intelligence for AI agents | [Get API key](https://nuvc.ai/api-platform)";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function getApiKey() {
  const key = process.env.NUVC_API_KEY;
  if (!key) {
    console.error(
      "Error: NUVC_API_KEY not set.\n\n" +
        "1. Get your free key at https://nuvc.ai/api-platform\n" +
        "2. Set it: export NUVC_API_KEY=nuvc_your_key_here\n" +
        "3. Run again!"
    );
    process.exit(1);
  }
  return key;
}

function parseArgs(args) {
  const parsed = { _positional: [] };
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith("--")) {
      const key = args[i].slice(2);
      const val = args[i + 1] && !args[i + 1].startsWith("--") ? args[++i] : true;
      parsed[key] = val;
    } else {
      parsed._positional.push(args[i]);
    }
  }
  return parsed;
}

async function apiCall(method, path, body) {
  const url = `${API_BASE}${path}`;
  const headers = {
    Authorization: `Bearer ${getApiKey()}`,
    "Content-Type": "application/json",
    "User-Agent": "nuvc-openclaw/1.0",
  };

  const opts = { method, headers };
  if (body) opts.body = JSON.stringify(body);

  const res = await fetch(url, opts);

  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: { message: res.statusText } }));
    const msg = err?.error?.message || err?.detail?.message || err?.detail || res.statusText;
    const code = err?.error?.code || err?.detail?.code || res.status;

    if (res.status === 401) {
      console.error(`Auth error: ${msg}\n\nGet a valid API key at https://nuvc.ai/api-platform`);
    } else if (res.status === 403 && code === "TIER_BLOCKED") {
      console.error(`${msg}\n\nUpgrade at https://nuvc.ai/api-platform/billing`);
    } else if (res.status === 429) {
      console.error(`Rate limit hit: ${msg}\n\nUpgrade for more calls at https://nuvc.ai/api-platform/billing`);
    } else {
      console.error(`API error (${res.status}): ${msg}`);
    }
    process.exit(1);
  }

  return res.json();
}

// ---------------------------------------------------------------------------
// Commands
// ---------------------------------------------------------------------------

async function cmdScore(args) {
  const text = args._positional[0];
  if (!text) {
    console.error(
      "Usage: node nuvc-api.mjs score \"<your business idea or pitch>\"\n\n" +
        "Example: node nuvc-api.mjs score \"An AI platform that scores startup pitch decks\""
    );
    process.exit(1);
  }

  const res = await apiCall("POST", "/ai/score", { text });
  const data = res.data || res;
  const scores = data.scores || {};

  console.log("## NUVC VCGrade Score\n");

  if (scores.overall_score !== undefined) {
    const overall = Number(scores.overall_score);
    const emoji = overall >= 7 ? "🟢" : overall >= 5 ? "🟡" : "🔴";
    const verdict =
      overall >= 8
        ? "Exceptional — investors will lean in"
        : overall >= 7
          ? "Strong — worth pursuing seriously"
          : overall >= 5
            ? "Promising but needs work"
            : overall >= 3
              ? "Significant gaps to address"
              : "Back to the drawing board";
    console.log(`${emoji} **Overall: ${overall} / 10** — ${verdict}\n`);
  }

  const dimensions = scores.scores || scores;
  if (typeof dimensions === "object" && !Array.isArray(dimensions)) {
    const entries = Object.entries(dimensions).filter(
      ([k]) => k !== "overall_score" && k !== "summary" && k !== "raw"
    );
    if (entries.length > 0) {
      console.log("| Dimension | Score | Rationale |");
      console.log("|-----------|-------|-----------|");
      for (const [key, val] of entries) {
        const label = key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
        if (typeof val === "object" && val !== null) {
          console.log(`| ${label} | ${val.score ?? "—"}/10 | ${val.rationale ?? ""} |`);
        } else {
          console.log(`| ${label} | ${val}/10 | |`);
        }
      }
      console.log("");
    }
  }

  if (scores.summary) {
    console.log(`**Summary:** ${scores.summary}\n`);
  }

  console.log(FOOTER);
}

async function cmdRoast(args) {
  const text = args._positional[0];
  if (!text) {
    console.error(
      "Usage: node nuvc-api.mjs roast \"<your business idea or pitch>\"\n\n" +
        'Example: node nuvc-api.mjs roast "Uber for dog walking but with blockchain"'
    );
    process.exit(1);
  }

  const res = await apiCall("POST", "/ai/analyze", {
    text,
    analysis_type: "pitch_deck",
    system_prompt:
      "You are a brutally honest VC partner who has seen 10,000 pitches. " +
      "Give a sharp, witty, but ultimately constructive roast of this business idea. " +
      "Structure your response as:\n" +
      "1. THE ROAST (2-3 punchy, honest observations — be funny but fair)\n" +
      "2. THE REAL TALK (what's actually wrong and needs fixing)\n" +
      "3. THE SILVER LINING (what could work if they fix the issues)\n" +
      "4. VERDICT: Would you take the meeting? (Yes/Maybe/No and why in one sentence)\n\n" +
      "Keep the total response under 400 words. Be direct, not cruel.",
    temperature: 0.7,
    max_tokens: 800,
  });

  const data = res.data || res;

  console.log("## 🔥 NUVC Startup Roast\n");
  console.log(data.analysis || JSON.stringify(data, null, 2));
  console.log(FOOTER);
}

async function cmdAnalyze(args) {
  const text = args._positional[0];
  if (!text) {
    console.error(
      "Usage: node nuvc-api.mjs analyze \"<text>\" [--type market|competitive|financial|pitch_deck]\n\n" +
        'Example: node nuvc-api.mjs analyze "The global HR tech market" --type market'
    );
    process.exit(1);
  }

  const analysisType = args.type || "general";
  const res = await apiCall("POST", "/ai/analyze", {
    text,
    analysis_type: analysisType,
  });
  const data = res.data || res;

  const label = analysisType.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
  console.log(`## NUVC ${label} Analysis\n`);
  console.log(data.analysis || JSON.stringify(data, null, 2));
  console.log(FOOTER);
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

const COMMANDS = {
  score: { fn: cmdScore, help: "Score a business idea on the VCGrade 0-10 scale" },
  roast: { fn: cmdRoast, help: "Get a brutally honest (but constructive) startup roast" },
  analyze: { fn: cmdAnalyze, help: "Market, competitive, financial, or pitch analysis" },
};

async function main() {
  const rawArgs = process.argv.slice(2);
  const command = rawArgs[0];

  if (!command || command === "--help" || command === "-h") {
    console.log("NUVC — VC-grade business intelligence for AI agents\n");
    console.log("Usage: node nuvc-api.mjs <command> [args]\n");
    console.log("Commands:");
    for (const [name, { help }] of Object.entries(COMMANDS)) {
      console.log(`  ${name.padEnd(12)} ${help}`);
    }
    console.log("\n50 free calls/month. Get your key at https://nuvc.ai/api-platform");
    process.exit(0);
  }

  const cmd = COMMANDS[command];
  if (!cmd) {
    console.error(`Unknown command: ${command}\nRun with --help to see available commands.`);
    process.exit(1);
  }

  const args = parseArgs(rawArgs.slice(1));
  await cmd.fn(args);
}

main().catch((err) => {
  console.error(`Error: ${err.message}`);
  process.exit(1);
});
