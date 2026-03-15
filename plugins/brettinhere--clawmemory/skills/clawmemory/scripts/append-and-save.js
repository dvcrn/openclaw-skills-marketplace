#!/usr/bin/env node
/**
 * ClawMemory — append-and-save (v3)
 * 
 * Appends new content to a named slot.
 * Free tier rules: ≤10KB per slot, ≤10 slots per wallet.
 * If limits exceeded, returns status="limit" with clear explanation.
 * 
 * Usage:
 *   node append-and-save.js --slot "work" --content "text" [--label "title"]
 *   node append-and-save.js --slot "work" --file /path/to/file.md [--label "title"]
 *   cat content.md | node append-and-save.js --slot "work" --stdin [--label "title"]
 */
"use strict";

const { execSync } = require("child_process");
const fs   = require("fs");
const path = require("path");
const os   = require("os");

const CLI         = path.join(os.homedir(), ".clawmemory/memory-client/bin/cli.js");
const INDEX       = path.join(os.homedir(), ".clawmemory/index.json");
const SLOTS_DIR   = path.join(os.homedir(), ".clawmemory/slots");
const FREE_SIZE_KB  = 10;
const FREE_SLOTS    = 10;

if (!fs.existsSync(SLOTS_DIR)) fs.mkdirSync(SLOTS_DIR, { recursive: true });

// ── Parse args ────────────────────────────────────────────────────────────────
const args = process.argv.slice(2);
let newContent = null;
let label      = null;
let useStdin   = false;
let slotName   = "default";

for (let i = 0; i < args.length; i++) {
  if      (args[i] === "--content") newContent = args[++i];
  else if (args[i] === "--file")    newContent = fs.readFileSync(args[++i], "utf8");
  else if (args[i] === "--label")   label      = args[++i];
  else if (args[i] === "--stdin")   useStdin   = true;
  else if (args[i] === "--slot")    slotName   = args[++i].toLowerCase().replace(/\s+/g, "-").slice(0, 32);
}

async function readStdin() {
  return new Promise(resolve => {
    const chunks = [];
    process.stdin.on("data", d => chunks.push(d));
    process.stdin.on("end", () => resolve(Buffer.concat(chunks).toString("utf8")));
    process.stdin.resume();
  });
}

function runCLI(cliArgs) {
  const env = { ...process.env };
  const envFile = path.join(os.homedir(), ".clawmemory/memory-client/.env");
  if (fs.existsSync(envFile)) {
    fs.readFileSync(envFile, "utf8").split("\n").forEach(line => {
      const idx = line.indexOf("=");
      if (idx > 0) env[line.slice(0, idx).trim()] = line.slice(idx + 1).trim();
    });
  }
  return execSync(`node "${CLI}" ${cliArgs}`, {
    env, encoding: "utf8", stdio: ["pipe", "pipe", "pipe"]
  });
}

function readIndex() {
  if (!fs.existsSync(INDEX)) return {};
  try { return JSON.parse(fs.readFileSync(INDEX, "utf8")); } catch { return {}; }
}

function writeIndex(db) {
  fs.writeFileSync(INDEX, JSON.stringify(db, null, 2));
}

function parseMerkleRoot(output) {
  const m = output.match(/merkleRoot[:\s]+([0-9a-fx]+)/i)
         || output.match(/(0x[0-9a-f]{64})/i);
  return m ? m[1] : null;
}

function limitResult(reason, detail) {
  console.log(JSON.stringify({ status: "limit", reason, detail }));
  process.exit(0);
}

async function main() {
  if (useStdin) newContent = await readStdin();
  if (!newContent || !newContent.trim()) {
    console.error(JSON.stringify({ status: "error", message: "No content provided" }));
    process.exit(1);
  }

  const db  = readIndex();
  if (!db.slots) db.slots = {};

  // ── Check slot count limit ───────────────────────────────────────────────────
  const existingSlots  = Object.keys(db.slots);
  const isNewSlot      = !db.slots[slotName];
  if (isNewSlot && existingSlots.length >= FREE_SLOTS) {
    limitResult(
      "max_slots",
      `已用 ${existingSlots.length}/${FREE_SLOTS} 个免费记忆本。\n` +
      `现有记忆本：${existingSlots.join(", ")}\n` +
      `需要 MMP token 才能创建更多，或删除一个现有记忆本。`
    );
  }

  const now     = new Date();
  const dateStr = now.toISOString().replace("T", " ").slice(0, 19) + " UTC";
  const header  = `\n## ${dateStr}${label ? " — " + label : ""}\n\n`;
  const SLOT_FILE = path.join(SLOTS_DIR, `${slotName}.md`);

  // ── Load existing slot content ───────────────────────────────────────────────
  let existingContent = "";
  const currentRoot   = db.slots[slotName]?.merkleRoot;

  if (currentRoot) {
    console.log(`Loading slot "${slotName}" (${currentRoot.slice(0, 10)}...)...`);
    try {
      runCLI(`load ${currentRoot} ${SLOT_FILE}.old`);
      existingContent = fs.readFileSync(`${SLOT_FILE}.old`, "utf8");
      fs.unlinkSync(`${SLOT_FILE}.old`);
    } catch {
      console.warn("Warning: Could not load existing content, starting fresh.");
    }
  }

  // ── Build combined content ───────────────────────────────────────────────────
  const titleLine = `# ClawMemory — ${slotName}`;
  let combined;
  if (!existingContent) {
    combined = `${titleLine}\n${header}${newContent.trim()}\n`;
  } else {
    combined = existingContent.trimEnd() + header + newContent.trim() + "\n";
  }

  // ── Check size limit ─────────────────────────────────────────────────────────
  const sizeKB = Buffer.byteLength(combined, "utf8") / 1024;
  if (sizeKB > FREE_SIZE_KB) {
    limitResult(
      "size_exceeded",
      `合并后内容为 ${sizeKB.toFixed(1)}KB，超过 ${FREE_SIZE_KB}KB 免费上限。\n` +
      `需要 MMP token 存储更大的内容。\n` +
      `建议：新建一个记忆本（--slot 新名称）从头开始，` +
      `或购买 MMP（PancakeSwap: 0x30b8Bf35679E024331C813Be4bDfDB784E8E9a1E）。`
    );
  }

  // ── Write file ───────────────────────────────────────────────────────────────
  fs.writeFileSync(SLOT_FILE, combined, "utf8");
  console.log(`Slot "${slotName}": ${sizeKB.toFixed(1)}KB / ${FREE_SIZE_KB}KB`);

  // ── Save to chain ─────────────────────────────────────────────────────────────
  console.log(`Saving to chain...`);
  let saveOutput;
  try {
    saveOutput = runCLI(`save ${SLOT_FILE}`);
  } catch (e) {
    console.error(JSON.stringify({ status: "error", message: e.stdout || e.stderr || e.message }));
    process.exit(1);
  }

  const newRoot = parseMerkleRoot(saveOutput);
  if (!newRoot) {
    console.error(JSON.stringify({ status: "error", message: "Could not parse merkleRoot: " + saveOutput }));
    process.exit(1);
  }

  // ── Update index ──────────────────────────────────────────────────────────────
  if (!db.history) db.history = [];
  const version = (db.slots[slotName]?.version || 0) + 1;
  const entry = {
    slot:      slotName,
    version,
    merkleRoot: newRoot,
    savedAt:   now.toISOString(),
    label:     label || null,
    sizeKB:    parseFloat(sizeKB.toFixed(1)),
  };
  db.slots[slotName] = entry;
  db.history.push(entry);
  writeIndex(db);

  console.log(JSON.stringify({
    status:  "ok",
    slot:    slotName,
    version,
    savedAt: now.toISOString(),
    sizeKB:  parseFloat(sizeKB.toFixed(1)),
    slotsUsed: Object.keys(db.slots).length,
    slotsLeft: FREE_SLOTS - Object.keys(db.slots).length,
  }));
}

main().catch(e => {
  console.error(JSON.stringify({ status: "error", message: e.message }));
  process.exit(1);
});
