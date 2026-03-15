/**
 * cli-runner.ts
 *
 * Spawns CLI subprocesses (gemini, claude) and captures their output.
 * Input: OpenAI-format messages → formatted prompt string → CLI stdin.
 *
 * Both Gemini and Claude receive the prompt via stdin to avoid:
 *   - E2BIG (arg list too long) for large conversation histories
 *   - Gemini agentic mode (triggered by @file syntax + workspace cwd)
 *
 * Gemini is always spawned with cwd = tmpdir() so it doesn't scan the
 * workspace and enter agentic mode.
 */

import { spawn } from "node:child_process";
import { tmpdir, homedir } from "node:os";
import { ensureClaudeToken, refreshClaudeToken } from "./claude-auth.js";

/** Max messages to include in the prompt sent to the CLI. */
const MAX_MESSAGES = 20;
/** Max characters per message content before truncation. */
const MAX_MSG_CHARS = 4000;

// ──────────────────────────────────────────────────────────────────────────────
// Message formatting
// ──────────────────────────────────────────────────────────────────────────────

export interface ContentPart {
  type: string;
  text?: string;
}

export interface ChatMessage {
  role: "system" | "user" | "assistant";
  /** Plain string or OpenAI-style content array (multimodal / structured). */
  content: string | ContentPart[] | unknown;
}

/**
 * Convert OpenAI messages to a single flat prompt string.
 * Truncates to MAX_MESSAGES (keeping the most recent) and MAX_MSG_CHARS per
 * message to avoid oversized payloads.
 */
export function formatPrompt(messages: ChatMessage[]): string {
  if (messages.length === 0) return "";

  // Keep system message (if any) + last N non-system messages
  const system = messages.find((m) => m.role === "system");
  const nonSystem = messages.filter((m) => m.role !== "system");
  const recent = nonSystem.slice(-MAX_MESSAGES);
  const truncated = system ? [system, ...recent] : recent;

  // Single short user message — send bare (no wrapping needed)
  if (truncated.length === 1 && truncated[0].role === "user") {
    return truncateContent(truncated[0].content);
  }

  return truncated
    .map((m) => {
      const content = truncateContent(m.content);
      switch (m.role) {
        case "system":    return `[System]\n${content}`;
        case "assistant": return `[Assistant]\n${content}`;
        case "user":
        default:          return `[User]\n${content}`;
      }
    })
    .join("\n\n");
}

/**
 * Coerce any message content value to a plain string.
 *
 * Handles:
 *  - string          → as-is
 *  - ContentPart[]   → join text parts (OpenAI multimodal format)
 *  - other object    → JSON.stringify (prevents "[object Object]" from reaching the CLI)
 *  - null/undefined  → ""
 */
function contentToString(content: unknown): string {
  if (typeof content === "string") return content;
  if (content === null || content === undefined) return "";
  if (Array.isArray(content)) {
    return (content as ContentPart[])
      .filter((c) => c?.type === "text" && typeof c.text === "string")
      .map((c) => c.text!)
      .join("\n");
  }
  if (typeof content === "object") return JSON.stringify(content);
  return String(content);
}

function truncateContent(raw: unknown): string {
  const s = contentToString(raw);
  if (s.length <= MAX_MSG_CHARS) return s;
  return s.slice(0, MAX_MSG_CHARS) + `\n...[truncated ${s.length - MAX_MSG_CHARS} chars]`;
}

// ──────────────────────────────────────────────────────────────────────────────
// Minimal environment for spawned subprocesses
// ──────────────────────────────────────────────────────────────────────────────

/**
 * Build a minimal, safe environment for spawning CLI subprocesses.
 *
 * WHY: The OpenClaw gateway modifies process.env at runtime (OPENCLAW_* vars,
 * session context, etc.). Spreading the full process.env into spawn() can push
 * argv+envp over ARG_MAX (~2 MB on Linux) → "spawn E2BIG". Only passing what
 * the CLI tools actually need keeps us well under the limit regardless of
 * gateway runtime state.
 */
function buildMinimalEnv(): Record<string, string> {
  const pick = (key: string) => process.env[key];
  const env: Record<string, string> = { NO_COLOR: "1", TERM: "dumb" };

  for (const key of ["HOME", "PATH", "USER", "LOGNAME", "SHELL", "TMPDIR", "TMP", "TEMP"]) {
    const v = pick(key);
    if (v) env[key] = v;
  }
  for (const key of [
    "GOOGLE_APPLICATION_CREDENTIALS",
    "ANTHROPIC_API_KEY",
    "CLAUDE_API_KEY",
    "CODEX_API_KEY",
    "OPENAI_API_KEY",
    "XDG_CONFIG_HOME",
    "XDG_DATA_HOME",
    "XDG_CACHE_HOME",
    // Required for Claude Code OAuth (Gnome Keyring / libsecret access)
    "XDG_RUNTIME_DIR",
    "DBUS_SESSION_BUS_ADDRESS",
  ]) {
    const v = pick(key);
    if (v) env[key] = v;
  }

  return env;
}

// ──────────────────────────────────────────────────────────────────────────────
// Core subprocess runner
// ──────────────────────────────────────────────────────────────────────────────

export interface CliRunResult {
  stdout: string;
  stderr: string;
  exitCode: number;
}

export interface RunCliOptions {
  /**
   * Working directory for the subprocess.
   * Defaults to homedir() — a neutral dir that won't trigger agentic context scanning.
   */
  cwd?: string;
  timeoutMs?: number;
}

/**
 * Spawn a CLI and deliver the prompt via stdin.
 *
 * cwd defaults to homedir() so CLIs that scan the working directory for
 * project context (like Gemini) don't accidentally enter agentic mode.
 */
export function runCli(
  cmd: string,
  args: string[],
  prompt: string,
  timeoutMs = 120_000,
  opts: RunCliOptions = {}
): Promise<CliRunResult> {
  const cwd = opts.cwd ?? homedir();

  return new Promise((resolve, reject) => {
    const proc = spawn(cmd, args, {
      timeout: timeoutMs,
      env: buildMinimalEnv(),
      cwd,
    });

    let stdout = "";
    let stderr = "";

    proc.stdin.write(prompt, "utf8", () => {
      proc.stdin.end();
    });

    proc.stdout.on("data", (d: Buffer) => { stdout += d.toString(); });
    proc.stderr.on("data", (d: Buffer) => { stderr += d.toString(); });

    proc.on("close", (code) => {
      resolve({ stdout: stdout.trim(), stderr: stderr.trim(), exitCode: code ?? 0 });
    });

    proc.on("error", (err) => {
      reject(new Error(`Failed to spawn '${cmd}': ${err.message}`));
    });
  });
}

// ──────────────────────────────────────────────────────────────────────────────
// Gemini CLI
// ──────────────────────────────────────────────────────────────────────────────

/**
 * Run Gemini CLI in headless mode with prompt delivered via stdin.
 *
 * WHY stdin (not @file):
 *   The @file syntax (`gemini -p @/tmp/xxx.txt`) triggers Gemini's agentic
 *   mode — it scans the current working directory for project context and
 *   interprets the prompt as a task instruction, not a Q&A. This causes hangs,
 *   wrong answers, and "directory does not exist" errors when run from a
 *   project workspace.
 *
 * Gemini CLI: -p "" triggers headless mode; stdin content is the actual prompt
 * (per Gemini docs: "prompt is appended to input on stdin (if any)").
 *
 * cwd = tmpdir() — neutral empty-ish dir, prevents workspace context scanning.
 */
export async function runGemini(
  prompt: string,
  modelId: string,
  timeoutMs: number
): Promise<string> {
  const model = stripPrefix(modelId);
  // -p "" = headless mode trigger; actual prompt arrives via stdin
  const args = ["-m", model, "-p", ""];
  const result = await runCli("gemini", args, prompt, timeoutMs, { cwd: tmpdir() });

  // Filter out [WARN] lines from stderr (Gemini emits noisy permission warnings)
  const cleanStderr = result.stderr
    .split("\n")
    .filter((l) => !l.startsWith("[WARN]") && !l.startsWith("Loaded cached"))
    .join("\n")
    .trim();

  if (result.exitCode !== 0 && result.stdout.length === 0) {
    throw new Error(`gemini exited ${result.exitCode}: ${cleanStderr || "(no output)"}`);
  }

  return result.stdout || cleanStderr;
}

// ──────────────────────────────────────────────────────────────────────────────
// Claude Code CLI
// ──────────────────────────────────────────────────────────────────────────────

/**
 * Run Claude Code CLI in headless mode with prompt delivered via stdin.
 * Strips the model prefix ("cli-claude/claude-opus-4-6" → "claude-opus-4-6").
 */
export async function runClaude(
  prompt: string,
  modelId: string,
  timeoutMs: number
): Promise<string> {
  // Proactively refresh OAuth token if it's about to expire (< 5 min remaining).
  // No-op for API-key users.
  await ensureClaudeToken();

  const model = stripPrefix(modelId);
  const args = [
    "-p",
    "--output-format", "text",
    "--permission-mode", "plan",
    "--tools", "",
    "--model", model,
  ];

  const result = await runCli("claude", args, prompt, timeoutMs);

  // On 401: attempt one token refresh + retry before giving up.
  if (result.exitCode !== 0 && result.stdout.length === 0) {
    const stderr = result.stderr || "(no output)";
    if (stderr.includes("401") || stderr.includes("Invalid authentication credentials") || stderr.includes("authentication_error")) {
      // Refresh and retry once
      await refreshClaudeToken();
      const retry = await runCli("claude", args, prompt, timeoutMs);
      if (retry.exitCode !== 0 && retry.stdout.length === 0) {
        const retryStderr = retry.stderr || "(no output)";
        if (retryStderr.includes("401") || retryStderr.includes("authentication_error") || retryStderr.includes("Invalid authentication credentials")) {
          throw new Error(
            "Claude CLI OAuth token refresh failed. " +
            "Re-login required: run `claude auth logout && claude auth login` in a terminal."
          );
        }
        throw new Error(`claude exited ${retry.exitCode} (after token refresh): ${retryStderr}`);
      }
      return retry.stdout;
    }
    throw new Error(`claude exited ${result.exitCode}: ${stderr}`);
  }

  return result.stdout;
}

// ──────────────────────────────────────────────────────────────────────────────
// Model allowlist (T-103)
// ──────────────────────────────────────────────────────────────────────────────

/**
 * Default set of permitted models for the CLI bridge.
 * Matches the models registered as slash commands in index.ts.
 * Expressed as normalized "cli-<type>/<model-id>" strings (vllm/ prefix already stripped).
 *
 * To extend: pass a custom set to routeToCliRunner via the `allowedModels` option.
 * To disable the check: pass `null` for `allowedModels`.
 */
export const DEFAULT_ALLOWED_CLI_MODELS: ReadonlySet<string> = new Set([
  // Claude Code CLI
  "cli-claude/claude-sonnet-4-6",
  "cli-claude/claude-opus-4-6",
  "cli-claude/claude-haiku-4-5",
  // Gemini CLI
  "cli-gemini/gemini-2.5-pro",
  "cli-gemini/gemini-2.5-flash",
  "cli-gemini/gemini-3-pro-preview",
  "cli-gemini/gemini-3-flash-preview",
  // Aliases (map to preview variants internally)
  "cli-gemini/gemini-3-pro",   // alias → gemini-3-pro-preview
  "cli-gemini/gemini-3-flash", // alias → gemini-3-flash-preview
]);

/** Normalize model aliases to their canonical CLI model names. */
function normalizeModelAlias(normalized: string): string {
  const ALIASES: Record<string, string> = {
    "cli-gemini/gemini-3-pro":   "cli-gemini/gemini-3-pro-preview",
    "cli-gemini/gemini-3-flash": "cli-gemini/gemini-3-flash-preview",
  };
  return ALIASES[normalized] ?? normalized;
}

// ──────────────────────────────────────────────────────────────────────────────
// Router
// ──────────────────────────────────────────────────────────────────────────────

export interface RouteOptions {
  /**
   * Explicit model allowlist (normalized, vllm/ stripped).
   * Pass `null` to disable the allowlist check entirely.
   * Defaults to DEFAULT_ALLOWED_CLI_MODELS.
   */
  allowedModels?: ReadonlySet<string> | null;
}

/**
 * Route a chat completion to the correct CLI based on model prefix.
 *   cli-gemini/<id>  → gemini CLI
 *   cli-claude/<id>  → claude CLI
 *
 * Enforces DEFAULT_ALLOWED_CLI_MODELS by default (T-103).
 * Pass `allowedModels: null` to skip the allowlist check.
 */
export async function routeToCliRunner(
  model: string,
  messages: ChatMessage[],
  timeoutMs: number,
  opts: RouteOptions = {}
): Promise<string> {
  const prompt = formatPrompt(messages);

  // Strip "vllm/" prefix if present — OpenClaw sends the full provider path
  // (e.g. "vllm/cli-claude/claude-sonnet-4-6") but the router only needs the
  // "cli-<type>/<model>" portion.
  const normalized = model.startsWith("vllm/") ? model.slice(5) : model;

  // T-103: enforce allowlist unless explicitly disabled
  const allowedModels = opts.allowedModels === undefined
    ? DEFAULT_ALLOWED_CLI_MODELS
    : opts.allowedModels;

  if (allowedModels !== null && !allowedModels.has(normalized)) {
    const known = [...(allowedModels)].join(", ");
    throw new Error(
      `CLI bridge model not allowed: "${model}". Allowed: ${known || "(none)"}.`
    );
  }

  // Resolve aliases (e.g. gemini-3-pro → gemini-3-pro-preview) after allowlist check
  const resolved = normalizeModelAlias(normalized);

  if (resolved.startsWith("cli-gemini/")) return runGemini(prompt, resolved, timeoutMs);
  if (resolved.startsWith("cli-claude/")) return runClaude(prompt, resolved, timeoutMs);

  throw new Error(
    `Unknown CLI bridge model: "${model}". Use "vllm/cli-gemini/<model>" or "vllm/cli-claude/<model>".`
  );
}

// ──────────────────────────────────────────────────────────────────────────────
// Helpers
// ──────────────────────────────────────────────────────────────────────────────

function stripPrefix(modelId: string): string {
  const slash = modelId.indexOf("/");
  return slash === -1 ? modelId : modelId.slice(slash + 1);
}
