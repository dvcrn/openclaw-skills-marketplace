/**
 * proxy-server.ts
 *
 * Minimal OpenAI-compatible HTTP proxy server.
 * Routes POST /v1/chat/completions to the appropriate CLI tool.
 * Supports both streaming (SSE) and non-streaming responses.
 *
 * OpenClaw connects via the "vllm" provider with baseUrl pointing here.
 */

import http from "node:http";
import { randomBytes } from "node:crypto";
import { type ChatMessage, routeToCliRunner } from "./cli-runner.js";
import { scheduleTokenRefresh, setAuthLogger, stopTokenRefresh } from "./claude-auth.js";
import { grokComplete, grokCompleteStream, type ChatMessage as GrokChatMessage } from "./grok-client.js";
import { geminiComplete, geminiCompleteStream, type ChatMessage as GeminiBrowserChatMessage } from "./gemini-browser.js";
import { claudeComplete, claudeCompleteStream, type ChatMessage as ClaudeBrowserChatMessage } from "./claude-browser.js";
import { chatgptComplete, chatgptCompleteStream, type ChatMessage as ChatGPTBrowserChatMessage } from "./chatgpt-browser.js";
import type { BrowserContext } from "playwright";

export type GrokCompleteOptions = Parameters<typeof grokComplete>[1];
export type GrokCompleteStreamOptions = Parameters<typeof grokCompleteStream>[1];
export type GrokCompleteResult = Awaited<ReturnType<typeof grokComplete>>;

export interface ProxyServerOptions {
  port: number;
  apiKey?: string; // if set, validates Authorization: Bearer <key>
  timeoutMs?: number;
  log: (msg: string) => void;
  warn: (msg: string) => void;
  /** Returns the current authenticated Grok BrowserContext (null if not logged in) */
  getGrokContext?: () => BrowserContext | null;
  /** Async lazy connect — called when getGrokContext returns null */
  connectGrokContext?: () => Promise<BrowserContext | null>;
  /** Override for testing — replaces grokComplete */
  _grokComplete?: typeof grokComplete;
  /** Override for testing — replaces grokCompleteStream */
  _grokCompleteStream?: typeof grokCompleteStream;
  /** Returns the current authenticated Gemini BrowserContext (null if not logged in) */
  getGeminiContext?: () => BrowserContext | null;
  /** Async lazy connect — called when getGeminiContext returns null */
  connectGeminiContext?: () => Promise<BrowserContext | null>;
  /** Override for testing — replaces geminiComplete */
  _geminiComplete?: typeof geminiComplete;
  /** Override for testing — replaces geminiCompleteStream */
  _geminiCompleteStream?: typeof geminiCompleteStream;
  /** Returns the current authenticated Claude BrowserContext (null if not logged in) */
  getClaudeContext?: () => BrowserContext | null;
  /** Async lazy connect — called when getClaudeContext returns null */
  connectClaudeContext?: () => Promise<BrowserContext | null>;
  /** Override for testing — replaces claudeComplete */
  _claudeComplete?: typeof claudeComplete;
  /** Override for testing — replaces claudeCompleteStream */
  _claudeCompleteStream?: typeof claudeCompleteStream;
  /** Returns the current authenticated ChatGPT BrowserContext (null if not logged in) */
  getChatGPTContext?: () => BrowserContext | null;
  /** Async lazy connect — called when getChatGPTContext returns null */
  connectChatGPTContext?: () => Promise<BrowserContext | null>;
  /** Override for testing — replaces chatgptComplete */
  _chatgptComplete?: typeof chatgptComplete;
  /** Override for testing — replaces chatgptCompleteStream */
  _chatgptCompleteStream?: typeof chatgptCompleteStream;
  /** Returns human-readable expiry string for each web provider (null = no login yet) */
  getExpiryInfo?: () => {
    grok: string | null;
    gemini: string | null;
    claude: string | null;
    chatgpt: string | null;
  };
  /** Plugin version string for the status page */
  version?: string;
  /** Returns the BitNet llama-server base URL (default: http://127.0.0.1:8082) */
  getBitNetServerUrl?: () => string;
}

/** Available CLI bridge models for GET /v1/models */
export const CLI_MODELS = [
  // ── Claude Code CLI ───────────────────────────────────────────────────────
  { id: "cli-claude/claude-sonnet-4-6", name: "Claude Sonnet 4.6 (CLI)",  contextWindow: 200_000,   maxTokens: 8_192 },
  { id: "cli-claude/claude-opus-4-6",   name: "Claude Opus 4.6 (CLI)",    contextWindow: 200_000,   maxTokens: 8_192 },
  { id: "cli-claude/claude-haiku-4-5",  name: "Claude Haiku 4.5 (CLI)",   contextWindow: 200_000,   maxTokens: 8_192 },
  // ── Gemini CLI ────────────────────────────────────────────────────────────
  { id: "cli-gemini/gemini-2.5-pro",      name: "Gemini 2.5 Pro (CLI)",   contextWindow: 1_000_000, maxTokens: 8_192 },
  { id: "cli-gemini/gemini-2.5-flash",    name: "Gemini 2.5 Flash (CLI)", contextWindow: 1_000_000, maxTokens: 8_192 },
  { id: "cli-gemini/gemini-3-pro-preview",name: "Gemini 3 Pro (CLI)",     contextWindow: 1_000_000, maxTokens: 8_192 },
  { id: "cli-gemini/gemini-3-pro",        name: "Gemini 3 Pro (CLI, alias)", contextWindow: 1_000_000, maxTokens: 8_192 },
  // Grok web-session models (requires /grok-login)
  { id: "web-grok/grok-3",           name: "Grok 3 (web session)",           contextWindow: 131_072, maxTokens: 131_072 },
  { id: "web-grok/grok-3-fast",      name: "Grok 3 Fast (web session)",      contextWindow: 131_072, maxTokens: 131_072 },
  { id: "web-grok/grok-3-mini",      name: "Grok 3 Mini (web session)",      contextWindow: 131_072, maxTokens: 131_072 },
  { id: "web-grok/grok-3-mini-fast", name: "Grok 3 Mini Fast (web session)", contextWindow: 131_072, maxTokens: 131_072 },
  // Gemini web-session models (requires /gemini-login)
  { id: "web-gemini/gemini-2-5-pro",   name: "Gemini 2.5 Pro (web session)",   contextWindow: 1_000_000, maxTokens: 8192 },
  { id: "web-gemini/gemini-2-5-flash", name: "Gemini 2.5 Flash (web session)", contextWindow: 1_000_000, maxTokens: 8192 },
  { id: "web-gemini/gemini-3-pro",     name: "Gemini 3 Pro (web session)",     contextWindow: 1_000_000, maxTokens: 8192 },
  { id: "web-gemini/gemini-3-flash",   name: "Gemini 3 Flash (web session)",   contextWindow: 1_000_000, maxTokens: 8192 },
  // Claude web-session models (requires /claude-login)
  { id: "web-claude/claude-sonnet",     name: "Claude Sonnet (web session)",     contextWindow: 200_000, maxTokens: 8192 },
  { id: "web-claude/claude-opus",       name: "Claude Opus (web session)",       contextWindow: 200_000, maxTokens: 8192 },
  { id: "web-claude/claude-haiku",      name: "Claude Haiku (web session)",      contextWindow: 200_000, maxTokens: 8192 },
  // ChatGPT web-session models (requires /chatgpt-login)
  { id: "web-chatgpt/gpt-4o",           name: "GPT-4o (web session)",            contextWindow: 128_000, maxTokens: 16_384 },
  { id: "web-chatgpt/gpt-4o-mini",      name: "GPT-4o Mini (web session)",       contextWindow: 128_000, maxTokens: 16_384 },
  { id: "web-chatgpt/gpt-4.1",          name: "GPT-4.1 (web session)",           contextWindow: 1_047_576, maxTokens: 32_768 },
  { id: "web-chatgpt/o3",               name: "o3 (web session)",                contextWindow: 200_000, maxTokens: 100_000 },
  { id: "web-chatgpt/o4-mini",          name: "o4-mini (web session)",           contextWindow: 200_000, maxTokens: 100_000 },
  { id: "web-chatgpt/gpt-5",            name: "GPT-5 (web session)",             contextWindow: 1_047_576, maxTokens: 32_768 },
  { id: "web-chatgpt/gpt-5-mini",       name: "GPT-5 Mini (web session)",        contextWindow: 1_047_576, maxTokens: 32_768 },
  // ── Local BitNet inference ──────────────────────────────────────────────────
  { id: "local-bitnet/bitnet-2b",       name: "BitNet b1.58 2B (local CPU inference)", contextWindow: 4_096, maxTokens: 2_048 },
];

// ──────────────────────────────────────────────────────────────────────────────
// Server
// ──────────────────────────────────────────────────────────────────────────────

export function startProxyServer(opts: ProxyServerOptions): Promise<http.Server> {
  return new Promise((resolve, reject) => {
    const server = http.createServer((req, res) => {
      handleRequest(req, res, opts).catch((err: Error) => {
        opts.warn(`[cli-bridge] Unhandled request error: ${err.message}`);
        if (!res.headersSent) {
          res.writeHead(500, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ error: { message: err.message, type: "internal_error" } }));
        }
      });
    });

    // Stop the token refresh interval when the server closes (timer-leak prevention)
    server.on("close", () => {
      stopTokenRefresh();
    });

    server.on("error", (err) => reject(err));
    server.listen(opts.port, "127.0.0.1", () => {
      opts.log(
        `[cli-bridge] proxy server listening on http://127.0.0.1:${opts.port}`
      );
      // Start proactive OAuth token refresh scheduler for Claude Code CLI.
      setAuthLogger(opts.log);
      void scheduleTokenRefresh();
      resolve(server);
    });
  });
}

// ──────────────────────────────────────────────────────────────────────────────
// Request router
// ──────────────────────────────────────────────────────────────────────────────

async function handleRequest(
  req: http.IncomingMessage,
  res: http.ServerResponse,
  opts: ProxyServerOptions
): Promise<void> {
  // CORS preflight
  if (req.method === "OPTIONS") {
    res.writeHead(204, corsHeaders());
    res.end();
    return;
  }

  const url = req.url ?? "/";

  // Health check
  if (url === "/health" || url === "/v1/health") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ status: "ok", service: "openclaw-cli-bridge" }));
    return;
  }

  // Browser status page — human-readable HTML dashboard
  if ((url === "/status" || url === "/") && req.method === "GET") {
    const expiry = opts.getExpiryInfo?.() ?? { grok: null, gemini: null, claude: null, chatgpt: null };
    const version = opts.version ?? "?";

    const providers = [
      { name: "Grok",     icon: "𝕏",  expiry: expiry.grok,    loginCmd: "/grok-login",    ctx: opts.getGrokContext?.() ?? null },
      { name: "Gemini",   icon: "✦",  expiry: expiry.gemini,  loginCmd: "/gemini-login",  ctx: opts.getGeminiContext?.() ?? null },
      { name: "Claude",   icon: "◆",  expiry: expiry.claude,  loginCmd: "/claude-login",  ctx: opts.getClaudeContext?.() ?? null },
      { name: "ChatGPT",  icon: "◉",  expiry: expiry.chatgpt, loginCmd: "/chatgpt-login", ctx: opts.getChatGPTContext?.() ?? null },
    ];

    function statusBadge(p: typeof providers[0]): { label: string; color: string; dot: string } {
      if (p.ctx !== null) return { label: "Connected", color: "#22c55e", dot: "🟢" };
      if (!p.expiry) return { label: "Never logged in", color: "#6b7280", dot: "⚪" };
      if (p.expiry.startsWith("⚠️ EXPIRED")) return { label: "Expired", color: "#ef4444", dot: "🔴" };
      if (p.expiry.startsWith("🚨")) return { label: "Expiring soon", color: "#f59e0b", dot: "🟡" };
      return { label: "Logged in", color: "#3b82f6", dot: "🔵" };
    }

    const rows = providers.map(p => {
      const badge = statusBadge(p);
      const expiryText = p.expiry
        ? p.expiry.replace(/[⚠️🚨✅🕐]/gu, "").trim()
        : `Not logged in — run <code>${p.loginCmd}</code>`;
      return `
        <tr>
          <td style="padding:12px 16px;font-weight:600;font-size:15px">${p.icon} ${p.name}</td>
          <td style="padding:12px 16px">
            <span style="background:${badge.color}22;color:${badge.color};border:1px solid ${badge.color}44;
                         border-radius:6px;padding:3px 10px;font-size:13px;font-weight:600">
              ${badge.dot} ${badge.label}
            </span>
          </td>
          <td style="padding:12px 16px;color:#9ca3af;font-size:13px">${expiryText}</td>
          <td style="padding:12px 16px;color:#6b7280;font-size:12px;font-family:monospace">${p.loginCmd}</td>
        </tr>`;
    }).join("");

    const cliModels = CLI_MODELS.filter(m => m.id.startsWith("cli-"));
    const webModels = CLI_MODELS.filter(m => m.id.startsWith("web-"));
    const localModels = CLI_MODELS.filter(m => m.id.startsWith("local-"));
    const modelList = (models: typeof CLI_MODELS) =>
      models.map(m => `<li style="margin:2px 0;font-size:13px;color:#d1d5db"><code style="color:#93c5fd">${m.id}</code></li>`).join("");

    const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CLI Bridge Status</title>
  <meta http-equiv="refresh" content="30">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: #0f1117; color: #e5e7eb; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; min-height: 100vh; padding: 32px 24px; }
    h1 { font-size: 22px; font-weight: 700; color: #f9fafb; margin-bottom: 4px; }
    .subtitle { color: #6b7280; font-size: 13px; margin-bottom: 28px; }
    .card { background: #1a1d27; border: 1px solid #2d3148; border-radius: 12px; overflow: hidden; margin-bottom: 24px; }
    .card-header { padding: 14px 16px; border-bottom: 1px solid #2d3148; font-size: 12px; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; }
    table { width: 100%; border-collapse: collapse; }
    tr:not(:last-child) td { border-bottom: 1px solid #1f2335; }
    .models { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    ul { list-style: none; padding: 12px 16px; }
    .footer { color: #374151; font-size: 12px; text-align: center; margin-top: 16px; }
    code { background: #1e2130; padding: 1px 5px; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>🌉 CLI Bridge</h1>
  <p class="subtitle">v${version} &nbsp;·&nbsp; Port ${opts.port} &nbsp;·&nbsp; Auto-refreshes every 30s</p>

  <div class="card">
    <div class="card-header">Web Session Providers</div>
    <table>
      <thead>
        <tr style="background:#13151f">
          <th style="padding:10px 16px;text-align:left;font-size:12px;color:#4b5563;font-weight:600">Provider</th>
          <th style="padding:10px 16px;text-align:left;font-size:12px;color:#4b5563;font-weight:600">Status</th>
          <th style="padding:10px 16px;text-align:left;font-size:12px;color:#4b5563;font-weight:600">Session</th>
          <th style="padding:10px 16px;text-align:left;font-size:12px;color:#4b5563;font-weight:600">Login</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  </div>

  <div class="models">
    <div class="card">
      <div class="card-header">CLI Models (${cliModels.length})</div>
      <ul>${modelList(cliModels)}</ul>
    </div>
    <div class="card">
      <div class="card-header">Web Session Models (${webModels.length})</div>
      <ul>${modelList(webModels)}</ul>
    </div>
    <div class="card">
      <div class="card-header">Local Models (${localModels.length})</div>
      <ul>${modelList(localModels)}</ul>
    </div>
  </div>

  <p class="footer">openclaw-cli-bridge-elvatis v${version} &nbsp;·&nbsp; <a href="/v1/models" style="color:#4b5563">/v1/models</a> &nbsp;·&nbsp; <a href="/health" style="color:#4b5563">/health</a></p>
</body>
</html>`;

    res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
    res.end(html);
    return;
  }

  // Model list
  if (url === "/v1/models" && req.method === "GET") {
    const now = Math.floor(Date.now() / 1000);
    res.writeHead(200, { "Content-Type": "application/json", ...corsHeaders() });
    res.end(
      JSON.stringify({
        object: "list",
        data: CLI_MODELS.map((m) => ({
          id: m.id,
          object: "model",
          created: now,
          owned_by: "openclaw-cli-bridge",
          // CLI-proxy models stream plain text — no tool/function call support
          capabilities: {
            tools: !(m.id.startsWith("cli-gemini/") || m.id.startsWith("cli-claude/") || m.id.startsWith("local-bitnet/")),
          },
        })),
      })
    );
    return;
  }

  // Chat completions
  if (url === "/v1/chat/completions" && req.method === "POST") {
    // Auth check
    if (opts.apiKey) {
      const auth = req.headers.authorization ?? "";
      const token = auth.startsWith("Bearer ") ? auth.slice(7) : "";
      if (token !== opts.apiKey) {
        res.writeHead(401, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: { message: "Unauthorized", type: "auth_error" } }));
        return;
      }
    }

    const body = await readBody(req);
    let parsed: {
      model: string;
      messages: ChatMessage[];
      stream?: boolean;
    };

    try {
      parsed = JSON.parse(body) as typeof parsed;
    } catch {
      res.writeHead(400, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ error: { message: "Invalid JSON body", type: "invalid_request_error" } }));
      return;
    }

    const { model, messages, stream = false } = parsed as { model: string; messages: ChatMessage[]; stream?: boolean; tools?: unknown };
    const hasTools = Array.isArray((parsed as { tools?: unknown }).tools) && (parsed as { tools?: unknown[] }).tools!.length > 0;

    if (!model || !messages?.length) {
      res.writeHead(400, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ error: { message: "model and messages are required", type: "invalid_request_error" } }));
      return;
    }

    // CLI-proxy models (cli-gemini/*, cli-claude/*) are plain text completions —
    // they cannot process tool/function call schemas. Return a clear 400 so
    // OpenClaw can surface a meaningful error instead of getting a garbled response.
    const isCliModel = model.startsWith("cli-gemini/") || model.startsWith("cli-claude/"); // local-bitnet/* exempt: llama-server silently ignores tools
    if (hasTools && isCliModel) {
      res.writeHead(400, { "Content-Type": "application/json" });
      res.end(JSON.stringify({
        error: {
          message: `Model ${model} does not support tool/function calls. Use a native API model (e.g. github-copilot/gpt-5-mini) for agents that need tools.`,
          type: "invalid_request_error",
          code: "tools_not_supported",
        }
      }));
      return;
    }

    opts.log(`[cli-bridge] ${model} · ${messages.length} msg(s) · stream=${stream}${hasTools ? " · tools=unsupported→rejected" : ""}`);

    const id = `chatcmpl-cli-${randomBytes(6).toString("hex")}`;
    const created = Math.floor(Date.now() / 1000);

    // ── Grok web-session routing ──────────────────────────────────────────────
    if (model.startsWith("web-grok/")) {
      let grokCtx = opts.getGrokContext?.() ?? null;
      // Lazy connect: if context is null but a connector is provided, try now
      if (!grokCtx && opts.connectGrokContext) {
        grokCtx = await opts.connectGrokContext();
      }
      if (!grokCtx) {
        res.writeHead(503, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: { message: "No active grok.com session. Use /grok-login to authenticate.", code: "no_grok_session" } }));
        return;
      }
      const grokModel = model.replace("web-grok/", "");
      const timeoutMs = opts.timeoutMs ?? 120_000;
      const grokMessages = messages as GrokChatMessage[];
      const doGrokComplete = opts._grokComplete ?? grokComplete;
      const doGrokCompleteStream = opts._grokCompleteStream ?? grokCompleteStream;
      try {
        if (stream) {
          res.writeHead(200, { "Content-Type": "text/event-stream", "Cache-Control": "no-cache", Connection: "keep-alive", ...corsHeaders() });
          sendSseChunk(res, { id, created, model, delta: { role: "assistant" }, finish_reason: null });
          const result = await doGrokCompleteStream(
            grokCtx,
            { messages: grokMessages, model: grokModel, timeoutMs },
            (token) => sendSseChunk(res, { id, created, model, delta: { content: token }, finish_reason: null }),
            opts.log
          );
          sendSseChunk(res, { id, created, model, delta: {}, finish_reason: result.finishReason });
          res.write("data: [DONE]\n\n");
          res.end();
        } else {
          const result = await doGrokComplete(grokCtx, { messages: grokMessages, model: grokModel, timeoutMs }, opts.log);
          res.writeHead(200, { "Content-Type": "application/json", ...corsHeaders() });
          res.end(JSON.stringify({
            id, object: "chat.completion", created, model,
            choices: [{ index: 0, message: { role: "assistant", content: result.content }, finish_reason: result.finishReason }],
            usage: { prompt_tokens: result.promptTokens ?? 0, completion_tokens: result.completionTokens ?? 0, total_tokens: (result.promptTokens ?? 0) + (result.completionTokens ?? 0) },
          }));
        }
      } catch (err) {
        const msg = (err as Error).message;
        opts.warn(`[cli-bridge] Grok error for ${model}: ${msg}`);
        if (!res.headersSent) {
          res.writeHead(500, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ error: { message: msg, type: "grok_error" } }));
        }
      }
      return;
    }
    // ─────────────────────────────────────────────────────────────────────────

    // ── Gemini web-session routing ────────────────────────────────────────────
    if (model.startsWith("web-gemini/")) {
      let geminiCtx = opts.getGeminiContext?.() ?? null;
      if (!geminiCtx && opts.connectGeminiContext) {
        geminiCtx = await opts.connectGeminiContext();
      }
      if (!geminiCtx) {
        res.writeHead(503, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: { message: "No active gemini.google.com session. Use /gemini-login to authenticate.", code: "no_gemini_session" } }));
        return;
      }
      const timeoutMs = opts.timeoutMs ?? 120_000;
      const geminiMessages = messages as GeminiBrowserChatMessage[];
      const doGeminiComplete = opts._geminiComplete ?? geminiComplete;
      const doGeminiCompleteStream = opts._geminiCompleteStream ?? geminiCompleteStream;
      try {
        if (stream) {
          res.writeHead(200, { "Content-Type": "text/event-stream", "Cache-Control": "no-cache", Connection: "keep-alive", ...corsHeaders() });
          sendSseChunk(res, { id, created, model, delta: { role: "assistant" }, finish_reason: null });
          const result = await doGeminiCompleteStream(
            geminiCtx,
            { messages: geminiMessages, model, timeoutMs },
            (token) => sendSseChunk(res, { id, created, model, delta: { content: token }, finish_reason: null }),
            opts.log
          );
          sendSseChunk(res, { id, created, model, delta: {}, finish_reason: result.finishReason });
          res.write("data: [DONE]\n\n");
          res.end();
        } else {
          const result = await doGeminiComplete(geminiCtx, { messages: geminiMessages, model, timeoutMs }, opts.log);
          res.writeHead(200, { "Content-Type": "application/json", ...corsHeaders() });
          res.end(JSON.stringify({
            id, object: "chat.completion", created, model,
            choices: [{ index: 0, message: { role: "assistant", content: result.content }, finish_reason: result.finishReason }],
            usage: { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 },
          }));
        }
      } catch (err) {
        const msg = (err as Error).message;
        opts.warn(`[cli-bridge] Gemini browser error for ${model}: ${msg}`);
        if (!res.headersSent) {
          res.writeHead(500, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ error: { message: msg, type: "gemini_browser_error" } }));
        }
      }
      return;
    }
    // ─────────────────────────────────────────────────────────────────────────

    // ── Claude web-session routing ────────────────────────────────────────────
    if (model.startsWith("web-claude/")) {
      let claudeCtx = opts.getClaudeContext?.() ?? null;
      if (!claudeCtx && opts.connectClaudeContext) {
        claudeCtx = await opts.connectClaudeContext();
      }
      if (!claudeCtx) {
        res.writeHead(503, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: { message: "No active claude.ai session. Use /claude-login to authenticate.", code: "no_claude_session" } }));
        return;
      }
      const timeoutMs = opts.timeoutMs ?? 120_000;
      const claudeMessages = messages as ClaudeBrowserChatMessage[];
      const doClaudeComplete = opts._claudeComplete ?? claudeComplete;
      const doClaudeCompleteStream = opts._claudeCompleteStream ?? claudeCompleteStream;
      try {
        if (stream) {
          res.writeHead(200, { "Content-Type": "text/event-stream", "Cache-Control": "no-cache", Connection: "keep-alive", ...corsHeaders() });
          sendSseChunk(res, { id, created, model, delta: { role: "assistant" }, finish_reason: null });
          const result = await doClaudeCompleteStream(
            claudeCtx,
            { messages: claudeMessages, model, timeoutMs },
            (token) => sendSseChunk(res, { id, created, model, delta: { content: token }, finish_reason: null }),
            opts.log
          );
          sendSseChunk(res, { id, created, model, delta: {}, finish_reason: result.finishReason });
          res.write("data: [DONE]\n\n");
          res.end();
        } else {
          const result = await doClaudeComplete(claudeCtx, { messages: claudeMessages, model, timeoutMs }, opts.log);
          res.writeHead(200, { "Content-Type": "application/json", ...corsHeaders() });
          res.end(JSON.stringify({
            id, object: "chat.completion", created, model,
            choices: [{ index: 0, message: { role: "assistant", content: result.content }, finish_reason: result.finishReason }],
            usage: { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 },
          }));
        }
      } catch (err) {
        const msg = (err as Error).message;
        opts.warn(`[cli-bridge] Claude browser error for ${model}: ${msg}`);
        if (!res.headersSent) {
          res.writeHead(500, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ error: { message: msg, type: "claude_browser_error" } }));
        }
      }
      return;
    }
    // ─────────────────────────────────────────────────────────────────────────

    // ── ChatGPT web-session routing ──────────────────────────────────────────
    if (model.startsWith("web-chatgpt/")) {
      let chatgptCtx = opts.getChatGPTContext?.() ?? null;
      if (!chatgptCtx && opts.connectChatGPTContext) {
        chatgptCtx = await opts.connectChatGPTContext();
      }
      if (!chatgptCtx) {
        res.writeHead(503, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: { message: "No active chatgpt.com session. Use /chatgpt-login to authenticate.", code: "no_chatgpt_session" } }));
        return;
      }
      const chatgptModel = model.replace("web-chatgpt/", "");
      const timeoutMs = opts.timeoutMs ?? 120_000;
      const chatgptMessages = messages as ChatGPTBrowserChatMessage[];
      const doChatGPTComplete = opts._chatgptComplete ?? chatgptComplete;
      const doChatGPTCompleteStream = opts._chatgptCompleteStream ?? chatgptCompleteStream;
      try {
        if (stream) {
          res.writeHead(200, { "Content-Type": "text/event-stream", "Cache-Control": "no-cache", Connection: "keep-alive", ...corsHeaders() });
          sendSseChunk(res, { id, created, model, delta: { role: "assistant" }, finish_reason: null });
          const result = await doChatGPTCompleteStream(
            chatgptCtx,
            { messages: chatgptMessages, model: chatgptModel, timeoutMs },
            (token) => sendSseChunk(res, { id, created, model, delta: { content: token }, finish_reason: null }),
            opts.log
          );
          sendSseChunk(res, { id, created, model, delta: {}, finish_reason: result.finishReason });
          res.write("data: [DONE]\n\n");
          res.end();
        } else {
          const result = await doChatGPTComplete(chatgptCtx, { messages: chatgptMessages, model: chatgptModel, timeoutMs }, opts.log);
          res.writeHead(200, { "Content-Type": "application/json", ...corsHeaders() });
          res.end(JSON.stringify({
            id, object: "chat.completion", created, model,
            choices: [{ index: 0, message: { role: "assistant", content: result.content }, finish_reason: result.finishReason }],
            usage: { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 },
          }));
        }
      } catch (err) {
        const msg = (err as Error).message;
        opts.warn(`[cli-bridge] ChatGPT browser error for ${model}: ${msg}`);
        if (!res.headersSent) {
          res.writeHead(500, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ error: { message: msg, type: "chatgpt_browser_error" } }));
        }
      }
      return;
    }
    // ─────────────────────────────────────────────────────────────────────────

    // ── BitNet local inference routing ────────────────────────────────────────
    if (model.startsWith("local-bitnet/")) {
      const bitnetUrl = opts.getBitNetServerUrl?.() ?? "http://127.0.0.1:8082";
      const timeoutMs = opts.timeoutMs ?? 120_000;
      // llama-server (BitNet build) crashes with std::runtime_error on multi-part
      // content arrays (ref: https://github.com/ggerganov/llama.cpp/issues/8367).
      // Flatten all message content to plain strings before forwarding.
      const flattenContent = (content: unknown): string => {
        if (typeof content === "string") return content;
        if (Array.isArray(content)) {
          return content
            .filter((c): c is { type: string; text?: string } => typeof c === "object" && c !== null)
            .map((c) => (c.type === "text" && typeof c.text === "string" ? c.text : ""))
            .join("");
        }
        return String(content ?? "");
      };
      // BitNet has a 4096 token context window. Long sessions blow it up and
      // cause a hard C++ crash (no graceful error). Truncate to system prompt +
      // last 10 messages (~2k tokens max) to stay safely within the limit.
      const BITNET_MAX_MESSAGES = 6;
      // Replace the full system prompt (MEMORY.md etc, ~2k+ tokens) with a
      // minimal one so BitNet's 4096-token context isn't blown by the system msg alone.
      const BITNET_SYSTEM = "You are Akido, a concise AI assistant. Answer briefly and directly. Current user: Emre. Timezone: Europe/Berlin.";
      const allFlat = parsed.messages.map((m) => ({
        role: m.role,
        content: flattenContent(m.content),
      }));
      const nonSystemMsgs = allFlat.filter((m) => m.role !== "system");
      const truncated = nonSystemMsgs.slice(-BITNET_MAX_MESSAGES);
      const bitnetMessages = [{ role: "system", content: BITNET_SYSTEM }, ...truncated];
      const requestBody = JSON.stringify({ ...parsed, messages: bitnetMessages, tools: undefined });

      try {
        const targetUrl = new URL("/v1/chat/completions", bitnetUrl);
        const proxyRes = await new Promise<http.IncomingMessage>((resolve, reject) => {
          const proxyReq = http.request(
            {
              hostname: targetUrl.hostname,
              port: parseInt(targetUrl.port),
              path: targetUrl.pathname,
              method: "POST",
              headers: { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(requestBody) },
              timeout: timeoutMs,
            },
            resolve
          );
          proxyReq.on("error", reject);
          proxyReq.on("timeout", () => { proxyReq.destroy(new Error("BitNet request timed out")); });
          proxyReq.write(requestBody);
          proxyReq.end();
        });

        // Forward status + headers
        const fwdHeaders: Record<string, string> = { ...corsHeaders() };
        const ct = proxyRes.headers["content-type"];
        if (ct) fwdHeaders["Content-Type"] = ct;
        if (stream) {
          fwdHeaders["Cache-Control"] = "no-cache";
          fwdHeaders["Connection"] = "keep-alive";
        }
        res.writeHead(proxyRes.statusCode ?? 200, fwdHeaders);
        proxyRes.pipe(res);
      } catch (err) {
        const msg = (err as Error).message;
        if (msg.includes("ECONNREFUSED") || msg.includes("ECONNRESET") || msg.includes("ENOTFOUND")) {
          res.writeHead(503, { "Content-Type": "application/json", ...corsHeaders() });
          res.end(JSON.stringify({
            error: {
              message: "BitNet server not running. Start with: sudo systemctl start bitnet-server",
              type: "bitnet_error",
              code: "bitnet_unavailable",
            },
          }));
        } else {
          opts.warn(`[cli-bridge] BitNet error for ${model}: ${msg}`);
          if (!res.headersSent) {
            res.writeHead(500, { "Content-Type": "application/json", ...corsHeaders() });
            res.end(JSON.stringify({ error: { message: msg, type: "bitnet_error" } }));
          }
        }
      }
      return;
    }
    // ─────────────────────────────────────────────────────────────────────────

    // ── CLI runner routing (Gemini / Claude Code) ─────────────────────────────
    let content: string;
    try {
      content = await routeToCliRunner(model, messages, opts.timeoutMs ?? 120_000);
    } catch (err) {
      const msg = (err as Error).message;
      opts.warn(`[cli-bridge] CLI error for ${model}: ${msg}`);
      res.writeHead(500, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ error: { message: msg, type: "cli_error" } }));
      return;
    }

    if (stream) {
      res.writeHead(200, {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
        ...corsHeaders(),
      });

      // Role chunk
      sendSseChunk(res, { id, created, model, delta: { role: "assistant" }, finish_reason: null });

      // Content in chunks (~50 chars each for natural feel)
      const chunkSize = 50;
      for (let i = 0; i < content.length; i += chunkSize) {
        sendSseChunk(res, {
          id,
          created,
          model,
          delta: { content: content.slice(i, i + chunkSize) },
          finish_reason: null,
        });
      }

      // Stop chunk
      sendSseChunk(res, { id, created, model, delta: {}, finish_reason: "stop" });
      res.write("data: [DONE]\n\n");
      res.end();
    } else {
      const response = {
        id,
        object: "chat.completion",
        created,
        model,
        choices: [
          {
            index: 0,
            message: { role: "assistant", content },
            finish_reason: "stop",
          },
        ],
        usage: { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 },
      };

      res.writeHead(200, { "Content-Type": "application/json", ...corsHeaders() });
      res.end(JSON.stringify(response));
    }

    return;
  }

  // 404
  res.writeHead(404, { "Content-Type": "application/json" });
  res.end(JSON.stringify({ error: { message: `Not found: ${url}`, type: "not_found" } }));
}

// ──────────────────────────────────────────────────────────────────────────────
// Helpers
// ──────────────────────────────────────────────────────────────────────────────

function sendSseChunk(
  res: http.ServerResponse,
  params: {
    id: string;
    created: number;
    model: string;
    delta: Record<string, unknown>;
    finish_reason: string | null;
  }
): void {
  const chunk = {
    id: params.id,
    object: "chat.completion.chunk",
    created: params.created,
    model: params.model,
    choices: [
      { index: 0, delta: params.delta, finish_reason: params.finish_reason },
    ],
  };
  res.write(`data: ${JSON.stringify(chunk)}\n\n`);
}

function readBody(req: http.IncomingMessage): Promise<string> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    req.on("data", (d: Buffer) => chunks.push(d));
    req.on("end", () => resolve(Buffer.concat(chunks).toString("utf8")));
    req.on("error", reject);
  });
}

function corsHeaders(): Record<string, string> {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
  };
}
