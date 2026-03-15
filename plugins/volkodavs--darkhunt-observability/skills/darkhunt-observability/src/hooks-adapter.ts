import type { SpanBuffer } from './span-buffer.js';
import type {
  MessageInData,
  AgentStartData,
  AgentEndData,
  LlmInputData,
  LlmOutputData,
  ToolStartData,
  ToolEndData,
} from './types.js';

// ── OpenClaw Plugin SDK types ────────────────────────────────────

export interface OpenClawPluginApi {
  on(event: string, handler: (evt: any, ctx: any) => void): void;
  pluginConfig?: unknown;
  version?: string;
  processOwner?: string;
  registerService?(svc: any): void;
  registerCli?(registrar: (ctx: any) => void, opts?: { commands?: string[] }): void;
  logger?: { info: (...args: unknown[]) => void; error: (...args: unknown[]) => void };
}

// ── Hook name mapping ────────────────────────────────────────────

export interface HookMapping {
  messageIn: string;
  agentStart: string;
  agentEnd: string;
  llmInput: string;
  llmOutput: string;
  toolStart: string;
  toolEnd: string;
  shutdown: string;
}

export const DEFAULT_MAPPING: HookMapping = {
  messageIn: 'message_received',
  agentStart: 'before_agent_start',
  agentEnd: 'agent_end',
  llmInput: 'llm_input',
  llmOutput: 'llm_output',
  toolStart: 'before_tool_call',
  toolEnd: 'after_tool_call',
  shutdown: 'shutdown',
};

// ── Registration ─────────────────────────────────────────────────

export function registerHooks(
  api: OpenClawPluginApi,
  buffer: SpanBuffer,
  mapping: HookMapping = DEFAULT_MAPPING,
): void {
  // Log which hooks we're registering and available API info
  if (api.logger) {
    api.logger.info(`[tracehub] Registering hooks: ${JSON.stringify(mapping)}`);
    api.logger.info(`[tracehub] api.version: ${api.version}`);
    api.logger.info(`[tracehub] api.processOwner: ${api.processOwner}`);
    api.logger.info(`[tracehub] api keys: ${Object.keys(api).join(', ')}`);
  }

  // message_received: evt has {from, content}, ctx has {sessionKey, agentId, channelId}
  api.on(mapping.messageIn, (evt: any, ctx: any) => {
    if (api.logger) {
      api.logger.info('[tracehub] HOOK FIRED: messageIn');
      api.logger.info('[tracehub] messageIn evt keys: ' + Object.keys(evt).join(', '));
      api.logger.info('[tracehub] messageIn ctx keys: ' + Object.keys(ctx).join(', '));
      api.logger.info('[tracehub] messageIn evt.from: "' + evt.from + '" ctx.accountId: "' + ctx.accountId + '" ctx.channelId: "' + ctx.channelId + '"');
    }
    // Try multiple sources for sessionId — OpenClaw messageIn ctx has {channelId, accountId, conversationId}
    // (no sessionId/sessionKey), so conversationId is the primary source here
    const sessionId = ctx.sessionId ?? ctx.conversationId ?? evt.sessionId ?? ctx.sessionKey ?? '';
    const from = evt.from ?? ctx.from ?? 'unknown';
    const data: MessageInData = {
      sessionId,
      sessionKey: ctx.sessionKey ?? '',
      channel: ctx.channelId ?? ctx.channel ?? 'unknown',
      from,
      accountId: resolveUserId(ctx.accountId, from),
      contentLength: typeof evt.content === 'string' ? evt.content.length : (evt.contentLength ?? 0),
      ts: Date.now(),
    };
    buffer.onMessageIn(data);
    // Store accountId under ALL available ctx keys so agentStart (which uses ctx.sessionId) can find it
    if (data.accountId) {
      if (ctx.conversationId) buffer.storeAccountId(ctx.conversationId, data.accountId);
      if (ctx.sessionId) buffer.storeAccountId(ctx.sessionId, data.accountId);
      if (ctx.sessionKey) buffer.storeAccountId(ctx.sessionKey, data.accountId);
    }
  });

  // before_agent_start: evt has {prompt}, ctx has {sessionKey, agentId}
  api.on(mapping.agentStart, (evt: any, ctx: any) => {
    if (api.logger) api.logger.info('[tracehub] HOOK FIRED: agentStart');
    // Use same conversationId fallback as messageIn so accountId lookup matches
    const sessionId = ctx.sessionId ?? ctx.conversationId ?? evt.sessionId ?? '';
    const from = ctx.from ?? evt.from;
    const data: AgentStartData = {
      sessionId,
      sessionKey: ctx.sessionKey ?? '',
      agentId: ctx.agentId ?? '',
      traceName: evt.traceName ?? (typeof evt.prompt === 'string' ? evt.prompt.slice(0, 100) : undefined),
      traceTags: evt.traceTags,
      channel: ctx.channelId,
      accountId: resolveUserId(ctx.accountId, from),
      ts: Date.now(),
    };
    buffer.onAgentStart(data);
  });

  // agent_end: evt has {success, durationMs, error}, ctx has {sessionKey, agentId}
  api.on(mapping.agentEnd, (evt: any, ctx: any) => {
    if (api.logger) api.logger.info('[tracehub] HOOK FIRED: agentEnd');
    const data: AgentEndData = {
      sessionKey: ctx.sessionKey ?? '',
      agentId: ctx.agentId ?? '',
      success: evt.success ?? true,
      durationMs: evt.durationMs ?? 0,
      error: evt.error,
      ts: Date.now(),
    };
    buffer.onAgentEnd(data);
  });

  // llm_input: evt has {runId, sessionId, provider, model, systemPrompt, prompt, historyMessages}
  api.on(mapping.llmInput, (evt: any, ctx: any) => {
    if (api.logger) {
      api.logger.info('[tracehub] HOOK FIRED: llmInput');
      api.logger.info('[tracehub] llmInput evt keys: ' + Object.keys(evt).join(', '));
      api.logger.info('[tracehub] llmInput ctx keys: ' + Object.keys(ctx).join(', '));
      api.logger.info('[tracehub] llmInput evt.prompt type: ' + typeof evt.prompt + ' length: ' + (typeof evt.prompt === 'string' ? evt.prompt.length : 'N/A'));
    }

    // Extract tool results from history BEFORE creating the generation span.
    // This emits completed tool spans with their results attached.
    const sessionKey = ctx.sessionKey ?? '';
    const toolResults = extractToolResultsFromHistory(evt.historyMessages);
    if (toolResults.size > 0) {
      if (api.logger) {
        api.logger.info(`[tracehub] Found ${toolResults.size} tool result(s) in history`);
      }
      buffer.applyToolResults(toolResults, sessionKey);
    } else {
      // No results found — flush any waiting tools so they're not held forever
      buffer.applyToolResults(new Map(), sessionKey);
    }

    const data: LlmInputData = {
      sessionId: evt.sessionId ?? ctx.sessionId ?? '',
      sessionKey,
      agentId: ctx.agentId ?? '',
      model: evt.model ?? '',
      provider: evt.provider ?? '',
      runId: evt.runId ?? '',
      input: typeof evt.prompt === 'string' ? evt.prompt : undefined,
      inputLength: typeof evt.prompt === 'string' ? evt.prompt.length : undefined,
      systemPrompt: typeof evt.systemPrompt === 'string' ? evt.systemPrompt : undefined,
      systemPromptLength: typeof evt.systemPrompt === 'string' ? evt.systemPrompt.length : undefined,
      historyLength: Array.isArray(evt.historyMessages) ? evt.historyMessages.length : undefined,
      modelParameters: evt.modelParameters ? JSON.stringify(evt.modelParameters) : undefined,
      attempt: evt.attempt,
      ts: Date.now(),
    };
    buffer.onLlmInput(data);
  });

  // llm_output: evt has {runId, sessionId, provider, model, lastAssistant, usage, assistantTexts}
  api.on(mapping.llmOutput, (evt: any, ctx: any) => {
    if (api.logger) {
      api.logger.info('[tracehub] HOOK FIRED: llmOutput');
      api.logger.info('[tracehub] llmOutput evt keys: ' + Object.keys(evt).join(', '));
      api.logger.info('[tracehub] llmOutput evt.usage: ' + JSON.stringify(evt.usage));
      api.logger.info('[tracehub] llmOutput evt.lastAssistant?.usage: ' + JSON.stringify(evt.lastAssistant?.usage));
    }
    const usage = evt.usage ?? evt.lastAssistant?.usage ?? {};
    const lastAssistant = evt.lastAssistant ?? {};

    const output = extractOutput(evt);
    const data: LlmOutputData = {
      sessionKey: ctx.sessionKey ?? '',
      runId: evt.runId ?? '',
      model: evt.model ?? lastAssistant.model ?? '',
      provider: evt.provider ?? lastAssistant.provider ?? '',
      output,
      outputLength: output ? output.length : undefined,
      stopReason: lastAssistant.stopReason ?? evt.stopReason,
      inputTokens: usage.inputTokens ?? usage.input_tokens ?? usage.input,
      outputTokens: usage.outputTokens ?? usage.output_tokens ?? usage.output,
      cacheReadInputTokens: usage.cacheReadInputTokens ?? usage.cacheRead ?? usage.cache_read_input_tokens,
      cacheCreationInputTokens: usage.cacheCreationInputTokens ?? usage.cacheWrite ?? usage.cache_creation_input_tokens,
      costTotal: extractCostTotal(evt),
      costDetails: extractCostDetails(evt),
      completionStartTime: evt.completionStartTime,
      error: evt.error,
      ts: Date.now(),
    };
    buffer.onLlmOutput(data);
  });

  // before_tool_call: evt has {toolName, params}, ctx has {sessionKey, agentId}
  api.on(mapping.toolStart, (evt: any, ctx: any) => {
    if (api.logger) {
      api.logger.info('[tracehub] HOOK FIRED: toolStart ' + evt.toolName);
      api.logger.info('[tracehub] toolStart evt keys: ' + Object.keys(evt).join(', '));
    }
    // Use a stable fallback toolCallId: agentId + toolName + counter-like suffix.
    // Both start and end MUST use the same fallback logic for key matching.
    const toolCallId = evt.toolCallId ?? evt.callId ?? `${ctx.agentId ?? 'no-agent'}:${evt.toolName ?? 'unknown'}`;
    // Extract actual tool arguments. OpenClaw's before_tool_call provides:
    // evt.params = {name, callId, ...} — tool routing metadata, NOT the actual args.
    // The real tool input may be in evt.params.input, evt.input, or evt.args.
    const rawParams = evt.input ?? evt.args ?? evt.arguments
      ?? evt.params?.input ?? evt.params?.arguments ?? evt.params?.args
      ?? evt.parameters?.input ?? evt.parameters
      ?? evt.params;
    const parameters = rawParams
      ? (typeof rawParams === 'string' ? rawParams : JSON.stringify(rawParams))
      : undefined;
    if (api.logger) {
      api.logger.info(`[tracehub] toolStart ${evt.toolName} params: ${parameters?.slice(0, 200) ?? 'null'}`);
    }
    const data: ToolStartData = {
      sessionKey: ctx.sessionKey ?? '',
      agentId: ctx.agentId ?? '',
      toolName: evt.toolName ?? '',
      toolCallId,
      parameters,
      attempt: evt.attempt,
      ts: Date.now(),
    };
    buffer.onToolStart(data);
  });

  // after_tool_call: evt has {toolName, durationMs, error, result/output}, ctx has {sessionKey, agentId}
  api.on(mapping.toolEnd, (evt: any, ctx: any) => {
    if (api.logger) {
      api.logger.info('[tracehub] HOOK FIRED: toolEnd ' + evt.toolName);
      api.logger.info('[tracehub] toolEnd evt keys: ' + Object.keys(evt).join(', '));
    }
    // Must match the same fallback logic as toolStart above
    const toolCallId = evt.toolCallId ?? evt.callId ?? `${ctx.agentId ?? 'no-agent'}:${evt.toolName ?? 'unknown'}`;
    // Capture tool result directly from after_tool_call event
    const rawResult = evt.result ?? evt.output ?? evt.response ?? evt.content;
    const result = rawResult
      ? (typeof rawResult === 'string' ? rawResult : JSON.stringify(rawResult))
      : undefined;
    if (api.logger && result) {
      api.logger.info(`[tracehub] toolEnd ${evt.toolName} result (${result.length} chars)`);
    }
    const data: ToolEndData = {
      sessionKey: ctx.sessionKey ?? '',
      toolName: evt.toolName ?? '',
      toolCallId,
      success: !evt.error,
      durationMs: evt.durationMs,
      result,
      error: evt.error,
      ts: Date.now(),
    };
    buffer.onToolEnd(data);
  });
}

// ── User identity helper ────────────────────────────────────────

const USELESS_ACCOUNT_IDS = new Set(['undefined', 'default', 'null', '']);

function resolveUserId(accountId?: string, from?: string): string | undefined {
  // ctx.accountId is often "undefined" (webchat) or "default" (telegram) — useless
  if (accountId && !USELESS_ACCOUNT_IDS.has(accountId)) {
    return accountId;
  }
  // evt.from has "telegram:1382891386" on telegram — real user identity
  if (from && from !== 'unknown' && from !== '') {
    return from;
  }
  return undefined;
}

// ── Data extraction helpers ──────────────────────────────────────

function extractOutput(evt: any): string | undefined {
  if (Array.isArray(evt.assistantTexts) && evt.assistantTexts.length > 0) {
    return evt.assistantTexts.join('\n');
  }
  if (evt.lastAssistant?.content) {
    return typeof evt.lastAssistant.content === 'string'
      ? evt.lastAssistant.content
      : JSON.stringify(evt.lastAssistant.content);
  }
  return undefined;
}

function extractCostTotal(evt: any): number | undefined {
  const cost = evt.cost ?? evt.usage?.cost ?? evt.lastAssistant?.usage?.cost;
  if (!cost) return undefined;
  if (typeof cost === 'number') return cost;
  if (typeof cost === 'object' && typeof cost.total === 'number') return cost.total;
  return undefined;
}

function extractCostDetails(evt: any): string | undefined {
  const cost = evt.cost ?? evt.usage?.cost ?? evt.lastAssistant?.usage?.cost;
  if (!cost) return undefined;
  if (typeof cost === 'string') return cost;
  if (typeof cost === 'object') return JSON.stringify(cost);
  return undefined;
}

// ── Tool result extraction from history ─────────────────────────

/**
 * Parse historyMessages from llm_input to find tool_result entries.
 * Returns a map of toolCallId → result string.
 *
 * Handles multiple formats:
 * - Anthropic: {role:"user", content:[{type:"tool_result", tool_use_id:"...", content:"..."}]}
 * - OpenAI:    {role:"tool", tool_call_id:"...", content:"..."}
 * - Generic:   {role:"tool_result", tool_use_id:"...", content:"..."}
 */
function extractToolResultsFromHistory(historyMessages: unknown): Map<string, string> {
  const results = new Map<string, string>();
  if (!Array.isArray(historyMessages)) return results;

  for (const msg of historyMessages) {
    if (!msg || typeof msg !== 'object') continue;

    // Format: {role: "tool", tool_call_id: "...", content: "..."}
    const toolId = msg.tool_call_id ?? msg.tool_use_id ?? msg.toolCallId;
    if ((msg.role === 'tool' || msg.role === 'tool_result') && toolId) {
      results.set(String(toolId), contentToString(msg.content));
      continue;
    }

    // Format: {role: "user", content: [{type: "tool_result", tool_use_id: "...", content: "..."}]}
    if (Array.isArray(msg.content)) {
      for (const block of msg.content) {
        if (!block || typeof block !== 'object') continue;
        if (block.type === 'tool_result' && (block.tool_use_id || block.tool_call_id)) {
          const id = block.tool_use_id ?? block.tool_call_id;
          results.set(String(id), contentToString(block.content));
        }
      }
    }
  }

  return results;
}

function contentToString(content: unknown): string {
  if (typeof content === 'string') return content;
  if (content == null) return '';
  // Handle array content blocks: [{type:"text", text:"..."}]
  if (Array.isArray(content)) {
    return content
      .map((b: any) => (typeof b === 'string' ? b : b?.text ?? JSON.stringify(b)))
      .join('\n');
  }
  return JSON.stringify(content);
}
