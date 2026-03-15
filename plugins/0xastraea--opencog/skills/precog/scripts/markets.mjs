#!/usr/bin/env node
// List Precog prediction markets.
//
// Usage:
//   node markets.mjs           # active markets only, with predictions
//   node markets.mjs --all     # all markets (titles only, no prices)
//
// Env: PRECOG_RPC_URL (optional)
import { fileURLToPath } from "url";
import * as client from "./lib/client.mjs";
import { parseArgs } from "./lib/args.mjs";

export async function main(deps = {}) {
  const { read, outcomes, pct, status, date } = { ...client, ...deps };
  const _parseArgs = deps.parseArgs ?? parseArgs;

  const a     = _parseArgs();
  const total = await read("createdMarkets");
  if (total === 0n) { console.log("No markets found."); return []; }

  const showAll = "all" in a;
  const result  = [];

  // ── --all: list every market with status, no prices ───────────────────────
  if (showAll) {
    console.log(`\nAll Markets (${total})\n`);
    for (let i = 0; i < Number(total); i++) {
      const market = await read("markets", [BigInt(i)]);
      const [question, , , , , , , , , endTs] = market;
      const s = status(endTs);
      console.log(`  [${i}]  ${question}  [${s}]`);
      result.push({ id: i, question, status: s });
    }
  } else {
    // ── Default: active markets with leading prediction and token ─────────────
    const active = [];
    for (let i = 0; i < Number(total); i++) {
      const market = await read("markets", [BigInt(i)]);
      const [question, , , , outcomesRaw, , , , , endTs] = market;
      if (status(endTs) !== "active") continue;

      const rawOuts = outcomes(outcomesRaw);
      // outcomes() splits by "|"; some markets use "," — normalise
      const outs = (rawOuts.length === 1 && rawOuts[0].includes(","))
        ? rawOuts[0].split(",").map(s => s.trim()).filter(Boolean)
        : rawOuts;
      let prediction = null;
      let token = null;
      try {
        const [buyPrices] = await read("marketPrices", [BigInt(i)]);
        let bestIdx = 1;
        for (let j = 2; j <= outs.length; j++) {
          if (buyPrices[j] > buyPrices[bestIdx]) bestIdx = j;
        }
        prediction = { label: outs[bestIdx - 1], pct: pct(buyPrices[bestIdx]) };
      } catch {}
      try {
        const [, , colSymbol] = await read("marketCollateralInfo", [BigInt(i)]);
        token = colSymbol;
      } catch {}

      active.push({ id: i, question, endTs, outs, prediction, token });
    }

    if (active.length === 0) {
      console.log("\nNo active markets.\n");
      return result;
    }

    console.log(`\nActive Markets (${active.length})\n`);
    for (const m of active) {
      const tok = m.token ? `  💰 ${m.token}` : "";
      console.log(`[${m.id}] ${m.question}`);
      if (m.prediction) {
        console.log(`    📈 ${m.prediction.label}  ${m.prediction.pct}%${tok}  📅 ${date(m.endTs)}`);
      } else {
        console.log(`    📅 ${date(m.endTs)}`);
      }
      console.log("");
      result.push(m);
    }
  }

  if (showAll) console.log("");
  return result;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  main().catch(e => { console.error(e.message); process.exit(1); });
}
