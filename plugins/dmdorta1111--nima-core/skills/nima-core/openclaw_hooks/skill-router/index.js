/**
 * Dynamic Skill Router — OpenClaw Plugin
 * ========================================
 * Fires on `before_agent_start` to replace the static full-skill list
 * with a semantically retrieved subset (top-K relevant skills only).
 *
 * Instead of injecting all 169 skill descriptions every turn (~8KB),
 * this plugin embeds the user message and retrieves only the 10 most
 * relevant skills (~500 bytes). ~95% token savings.
 *
 * Architecture:
 *   User message → Voyage embedding → cosine similarity vs skill index
 *   + BM25 keyword fallback → top-K skills → inject as <available_skills>
 *
 * Author: Lilu + David
 * Date: 2026-02-26
 */

import { execFile } from "node:child_process";
import { promisify } from "node:util";
const execFileAsync = promisify(execFile);
import { existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import os from "node:os";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Paths
const DEFAULT_INDEX_PATH = join(os.homedir(), ".openclaw", "skill_router", "index.db");
const ROUTER_SCRIPT = join(os.homedir(), ".openclaw", "workspace", "tools", "skill_router", "skill_router.py");
const PYTHON_BIN = join(os.homedir(), ".openclaw", "workspace", ".venv", "bin", "python3");

// Config
const TOP_K = 10;
const QUERY_TIMEOUT_MS = 8000;
const MIN_QUERY_LENGTH = 3;

// Cache to avoid re-embedding identical messages
let lastQuery = "";
let lastResult = "";
let lastQueryTime = 0;
const CACHE_TTL_MS = 5000;

/**
 * Extract the user's message from the agent context.
 * OpenClaw passes messages as the last user turn.
 */
function extractUserMessage(ctx) {
  try {
    const msgs = ctx?.messages || ctx?.conversation || [];
    for (let i = msgs.length - 1; i >= 0; i--) {
      if (msgs[i]?.role === "user") {
        const content = msgs[i]?.content;
        if (typeof content === "string") return content.slice(0, 400);
        if (Array.isArray(content)) {
          const text = content.find(c => c.type === "text")?.text;
          if (text) return text.slice(0, 400);
        }
      }
    }
    return "";
  } catch {
    return "";
  }
}

/**
 * Check if the skill index exists and is populated.
 */
function indexExists(indexPath) {
  return existsSync(indexPath || DEFAULT_INDEX_PATH);
}

/**
 * Run the skill_router.py script and return the <available_skills> XML block.
 */
async function runRouter(query, topK, useVoyage, indexPath) {
  const env = {
    ...process.env,
    SKILL_ROUTER_INDEX: indexPath || DEFAULT_INDEX_PATH,
  };

  const args = [
    ROUTER_SCRIPT,
    query,
    "--top", String(topK),
    "--format", "xml",
    ...(useVoyage === false ? ["--no-voyage"] : []),
  ];

  const result = await execFileAsync(PYTHON_BIN, args, {
    timeout: QUERY_TIMEOUT_MS,
    encoding: "utf8",
    env,
  });

  return result.stdout.trim();
}

/**
 * Main hook handler — fires before every agent turn.
 */
export default {
  name: "skill-router",

  async beforeAgentStart(ctx, config) {
    const enabled = config?.enabled !== false;
    const skipSubagents = config?.skipSubagents !== false;
    const topK = config?.topK || TOP_K;
    const useVoyage = config?.useVoyage !== false;
    const indexPath = config?.indexPath || DEFAULT_INDEX_PATH;

    // Skip if disabled
    if (!enabled) return;

    // Skip subagent sessions
    if (skipSubagents && ctx?.sessionKey?.includes(":subagent:")) return;

    // Skip if index doesn't exist (graceful degradation)
    if (!indexExists(indexPath)) {
      console.error("[skill-router] ⚠️  Index not found — falling back to full skill list.");
      console.error(`[skill-router]    Run: python3 ${ROUTER_SCRIPT.replace("skill_router.py", "skill_indexer.py")} --rebuild`);
      return;
    }

    // Extract user message
    const query = extractUserMessage(ctx);
    if (!query || query.length < MIN_QUERY_LENGTH) return;

    // Cache check
    const now = Date.now();
    if (query === lastQuery && (now - lastQueryTime) < CACHE_TTL_MS && lastResult) {
      ctx.systemPromptSuffix = (ctx.systemPromptSuffix || "") + "\n\n" + lastResult;
      return;
    }

    try {
      const xmlBlock = await runRouter(query, topK, useVoyage, indexPath);

      if (xmlBlock && xmlBlock.includes("<available_skills>")) {
        // Replace the full skill list injection with the dynamic one
        // OpenClaw injects <available_skills> into systemPromptSuffix —
        // we override it here with the trimmed version.
        ctx.skillsOverride = xmlBlock;

        // Cache result
        lastQuery = query;
        lastResult = xmlBlock;
        lastQueryTime = now;

        // Count injected skills for logging
        const count = (xmlBlock.match(/<skill>/g) || []).length;
        console.error(`[skill-router] ✅ Injected ${count}/${topK} skills for: "${query.slice(0, 60)}..."`);
      }
    } catch (err) {
      // Graceful degradation — never break the agent turn
      console.error(`[skill-router] ⚠️  Router error (falling back): ${err.message}`);
    }
  },
};
