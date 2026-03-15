import type { ReadableSpan } from '@opentelemetry/sdk-trace-base';
import type { IResource } from '@opentelemetry/resources';
import type {
  PayloadMode,
  BufferedAgent,
  BufferedGeneration,
  BufferedTool,
  MessageInData,
  AgentStartData,
  AgentEndData,
  LlmInputData,
  LlmOutputData,
  ToolStartData,
  ToolEndData,
} from './types.js';
import { traceIdFromSession, randomSpanId } from './trace-id.js';
import {
  buildAgentSpan,
  buildGenerationSpan,
  buildToolSpan,
  buildMessageSpan,
  msToHrTime,
} from './span-builder.js';

export type SpansReadyCallback = (spans: ReadableSpan[]) => void;

interface CompletedTool {
  buffered: BufferedTool;
  endData: ToolEndData;
}

export class SpanBuffer {
  private agents = new Map<string, BufferedAgent>();
  private generations = new Map<string, BufferedGeneration>();
  private tools = new Map<string, BufferedTool>();
  // Track which tool.end calls we've seen (for deduplication)
  private toolEndSeen = new Map<string, boolean>();
  // Tools that have ended but await result from next llm_input
  private completedTools = new Map<string, CompletedTool>();
  // Store accountId from messageIn, keyed by sessionId/conversationId
  private sessionAccountIds = new Map<string, string>();
  // Fallback: most recent accountId (handles key mismatch between messageIn and agentStart)
  private latestAccountId?: string;
  // Fallback: most recent sessionId (for cron/background agents that lack session context)
  private latestSessionId?: string;
  // Runtime event data: runId from onAgentEvent lifecycle start, keyed by sessionKey
  private runtimeRunIds = new Map<string, string>();
  // Runtime event data: tool meta from onAgentEvent tool result, keyed by toolCallId
  private runtimeToolMeta = new Map<string, string>();
  // Runtime event data: first assistant token timestamp, keyed by runId
  private runtimeFirstTokenTs = new Map<string, number>();

  constructor(
    private resource: IResource,
    private payloadMode: PayloadMode,
    private onSpansReady: SpansReadyCallback,
  ) {}

  // ── Runtime event ingestion (from onAgentEvent) ────────────────

  onRuntimeEvent(event: {
    runId: string;
    stream: string;
    data: any;
    sessionKey: string;
    ts: number;
  }): void {
    const { runId, stream, data, sessionKey } = event;

    if (stream === 'lifecycle' && data?.phase === 'start') {
      // Store runId for this sessionKey so we can attach it to agent spans
      this.runtimeRunIds.set(sessionKey, runId);
      // Attach runId to existing agent buffer if it's already been created by the hook
      for (const [, agent] of this.agents) {
        if (agent.sessionKey === sessionKey && !agent.runId) {
          agent.runId = runId;
        }
      }
    }

    if (stream === 'tool' && data?.phase === 'result' && data?.toolCallId) {
      // Store meta description for tool spans
      if (data.meta) {
        this.runtimeToolMeta.set(data.toolCallId, data.meta);
      }
    }

    if (stream === 'assistant' && data?.delta) {
      // First assistant token — record timestamp for TTFT calculation
      if (!this.runtimeFirstTokenTs.has(runId)) {
        this.runtimeFirstTokenTs.set(runId, event.ts);
      }
    }
  }

  /** Get runtime runId for a sessionKey */
  getRuntimeRunId(sessionKey: string): string | undefined {
    return this.runtimeRunIds.get(sessionKey);
  }

  /** Get and consume tool meta for a toolCallId */
  consumeToolMeta(toolCallId: string): string | undefined {
    const meta = this.runtimeToolMeta.get(toolCallId);
    if (meta) this.runtimeToolMeta.delete(toolCallId);
    return meta;
  }

  /** Get and consume first-token timestamp for a runId */
  consumeFirstTokenTs(runId: string): number | undefined {
    const ts = this.runtimeFirstTokenTs.get(runId);
    if (ts) this.runtimeFirstTokenTs.delete(runId);
    return ts;
  }

  // ── Message (immediate, no buffering) ──────────────────────────

  onMessageIn(data: MessageInData): void {
    // Store accountId for this session so generation/tool spans can use it
    if (data.accountId) {
      this.sessionAccountIds.set(data.sessionId, data.accountId);
      this.latestAccountId = data.accountId;
    }
    if (data.sessionId) {
      this.latestSessionId = data.sessionId;
    }
    const traceId = traceIdFromSession(data.sessionId);
    const spanId = randomSpanId();
    const span = buildMessageSpan(data, traceId, spanId, this.resource);
    this.onSpansReady([span]);
  }

  /** Store accountId under additional keys (called from hooks-adapter for cross-hook matching) */
  storeAccountId(key: string, accountId: string): void {
    if (key) this.sessionAccountIds.set(key, accountId);
  }

  // ── Agent lifecycle ────────────────────────────────────────────

  onAgentStart(data: AgentStartData): void {
    const key = this.agentKey(data.sessionKey, data.agentId);
    const spanId = randomSpanId();

    // Get accountId: from agentStart ctx (if available), from stored messageIn, or latest fallback
    // messageIn stores by ctx.conversationId, agentStart uses ctx.sessionId — these may differ
    const accountId = data.accountId || this.sessionAccountIds.get(data.sessionId) || this.latestAccountId;

    const sessionId = data.sessionId || this.latestSessionId || '';
    if (sessionId) this.latestSessionId = sessionId;
    const traceId = traceIdFromSession(sessionId);

    this.agents.set(key, {
      sessionId,
      sessionKey: data.sessionKey,
      agentId: data.agentId,
      spanId,
      traceId,
      startTime: msToHrTime(data.ts),
      traceName: data.traceName,
      traceTags: data.traceTags,
      channel: data.channel,
      accountId,
      runId: this.runtimeRunIds.get(data.sessionKey),
    });
  }

  onAgentEnd(data: AgentEndData): void {
    const key = this.agentKey(data.sessionKey, data.agentId);
    const buffered = this.agents.get(key);
    if (!buffered) return;

    // Flush any completed tools still waiting for results
    this.flushCompletedToolsForSession(data.sessionKey);

    const span = buildAgentSpan(buffered, data, this.resource);
    this.agents.delete(key);
    this.onSpansReady([span]);
  }

  // ── Generation lifecycle ───────────────────────────────────────

  onLlmInput(data: LlmInputData): void {
    const key = this.generationKey(data.sessionKey, data.runId);
    const agentKey = this.agentKey(data.sessionKey, data.agentId);
    const agent = this.agents.get(agentKey);

    // Backfill: cron jobs have no messageIn, so agentStart may lack sessionId.
    // The LLM event provides evt.sessionId — propagate it to the agent buffer
    // so that subsequent tool spans also get the correct sessionId.
    if (agent && !agent.sessionId && data.sessionId) {
      agent.sessionId = data.sessionId;
    }
    // Propagate model to agent so tool spans can inherit it
    if (agent && data.model) {
      agent.model = data.model;
    }

    const spanId = randomSpanId();

    this.generations.set(key, {
      spanId,
      parentSpanId: agent?.spanId ?? '',
      traceId: agent?.traceId ?? traceIdFromSession(data.sessionId),
      model: data.model,
      provider: data.provider,
      startTime: msToHrTime(data.ts),
      input: data.input,
      inputLength: data.inputLength,
      systemPrompt: data.systemPrompt,
      systemPromptLength: data.systemPromptLength,
      historyLength: data.historyLength,
      modelParameters: data.modelParameters,
      attempt: data.attempt,
      sessionKey: data.sessionKey,
      sessionId: agent?.sessionId ?? data.sessionId ?? '',
      accountId: agent?.accountId,
    });
  }

  onLlmOutput(data: LlmOutputData): void {
    const key = this.generationKey(data.sessionKey, data.runId);
    const buffered = this.generations.get(key);
    if (!buffered) return;

    // Get first-token timestamp from runtime assistant streaming events
    const runId = this.runtimeRunIds.get(data.sessionKey);
    const firstTokenTs = runId ? this.consumeFirstTokenTs(runId) : undefined;

    const span = buildGenerationSpan(buffered, data, this.resource, this.payloadMode, firstTokenTs);
    this.generations.delete(key);
    this.onSpansReady([span]);
  }

  // ── Tool lifecycle ─────────────────────────────────────────────

  onToolStart(data: ToolStartData): void {
    const key = this.toolKey(data.sessionKey, data.toolCallId);
    const agentKey = this.agentKey(data.sessionKey, data.agentId);
    const agent = this.agents.get(agentKey);

    const spanId = randomSpanId();
    // Always produce a valid traceId: from agent context, or derive from sessionKey
    const traceId = agent?.traceId || traceIdFromSession(data.sessionKey || `orphan-tool-${data.toolCallId}`);

    this.tools.set(key, {
      spanId,
      parentSpanId: agent?.spanId ?? '',
      traceId,
      toolName: data.toolName,
      toolCallId: data.toolCallId,
      startTime: msToHrTime(data.ts),
      parameters: data.parameters,
      attempt: data.attempt,
      sessionKey: data.sessionKey,
      sessionId: agent?.sessionId ?? '',
      accountId: agent?.accountId,
      model: agent?.model,
      meta: this.runtimeToolMeta.get(data.toolCallId),
    });
  }

  onToolEnd(data: ToolEndData): void {
    const key = this.toolKey(data.sessionKey, data.toolCallId);
    const seenKey = key;

    // Handle dual tool.end: OpenClaw emits two tool.end records per tool.
    // First: {success, toolName}, Second: {success, toolName, durationMs}
    // Only complete the span when durationMs is present, or on the second call.
    if (data.durationMs == null) {
      if (this.toolEndSeen.has(seenKey)) {
        // Second call without duration — complete anyway
        this.completeToolSpan(key, data);
        this.toolEndSeen.delete(seenKey);
      } else {
        this.toolEndSeen.set(seenKey, true);
      }
      return;
    }

    // Has durationMs — complete the span
    this.completeToolSpan(key, data);
    this.toolEndSeen.delete(seenKey);
  }

  /**
   * Mark a tool as completed but hold it for result extraction.
   * The span will be emitted when the next llm_input provides historyMessages
   * containing the tool result, or on agentEnd/flushStale.
   */
  private completeToolSpan(key: string, data: ToolEndData): void {
    const buffered = this.tools.get(key);
    if (!buffered) return;

    this.tools.delete(key);
    this.completedTools.set(key, { buffered, endData: data });
  }

  /**
   * Apply tool results extracted from historyMessages, then emit matched tool spans.
   * Called from hooks-adapter when llm_input provides historyMessages.
   */
  applyToolResults(results: Map<string, string>, sessionKey: string): void {
    if (results.size === 0 && this.completedTools.size === 0) return;

    const toEmit: ReadableSpan[] = [];

    for (const [key, entry] of this.completedTools) {
      if (entry.buffered.sessionKey !== sessionKey) continue;

      // Prefer historyMessages result, fall back to result captured directly from after_tool_call
      const result = results.get(entry.buffered.toolCallId) ?? entry.endData.result;
      const span = buildToolSpan(entry.buffered, entry.endData, this.resource, this.payloadMode, result);
      toEmit.push(span);
      this.completedTools.delete(key);
    }

    if (toEmit.length > 0) {
      this.onSpansReady(toEmit);
    }
  }

  /**
   * Flush completed tools for a session (on agentEnd — no more results coming).
   * Uses result from after_tool_call if available (for single-turn tool use).
   */
  private flushCompletedToolsForSession(sessionKey: string): void {
    const toEmit: ReadableSpan[] = [];

    for (const [key, entry] of this.completedTools) {
      if (entry.buffered.sessionKey === sessionKey) {
        const span = buildToolSpan(entry.buffered, entry.endData, this.resource, this.payloadMode, entry.endData.result);
        toEmit.push(span);
        this.completedTools.delete(key);
      }
    }

    if (toEmit.length > 0) {
      this.onSpansReady(toEmit);
    }
  }

  // ── Orphan cleanup ─────────────────────────────────────────────

  flushStale(maxAgeMs: number): void {
    const now = Date.now();

    for (const [key, buffered] of this.agents) {
      const ageMs = now - hrTimeToMs(buffered.startTime);
      if (ageMs > maxAgeMs) {
        const endData: AgentEndData = {
          sessionKey: buffered.sessionKey,
          agentId: buffered.agentId,
          success: false,
          durationMs: ageMs,
          error: 'span timed out without end event',
          ts: now,
        };
        const span = buildAgentSpan(buffered, endData, this.resource);
        this.agents.delete(key);
        this.onSpansReady([span]);
      }
    }

    for (const [key, buffered] of this.generations) {
      const ageMs = now - hrTimeToMs(buffered.startTime);
      if (ageMs > maxAgeMs) {
        const endData: LlmOutputData = {
          sessionKey: buffered.sessionKey,
          runId: '',
          model: buffered.model,
          provider: buffered.provider,
          error: 'span timed out without end event',
          ts: now,
        };
        const span = buildGenerationSpan(buffered, endData, this.resource, this.payloadMode);
        this.generations.delete(key);
        this.onSpansReady([span]);
      }
    }

    for (const [key, buffered] of this.tools) {
      const ageMs = now - hrTimeToMs(buffered.startTime);
      if (ageMs > maxAgeMs) {
        const endData: ToolEndData = {
          sessionKey: buffered.sessionKey,
          toolName: buffered.toolName,
          toolCallId: buffered.toolCallId,
          success: false,
          error: 'span timed out without end event',
          ts: now,
        };
        const span = buildToolSpan(buffered, endData, this.resource, this.payloadMode);
        this.tools.delete(key);
        this.onSpansReady([span]);
      }
    }

    // Flush completed tools waiting for results
    for (const [key, entry] of this.completedTools) {
      const ageMs = now - hrTimeToMs(entry.buffered.startTime);
      if (ageMs > maxAgeMs) {
        const span = buildToolSpan(entry.buffered, entry.endData, this.resource, this.payloadMode);
        this.completedTools.delete(key);
        this.onSpansReady([span]);
      }
    }
  }

  // ── Key helpers ────────────────────────────────────────────────

  private agentKey(sessionKey: string, agentId: string): string {
    return `${sessionKey}:${agentId}`;
  }

  private generationKey(sessionKey: string, runId: string): string {
    return `${sessionKey}:${runId}`;
  }

  private toolKey(sessionKey: string, toolCallId: string): string {
    return `${sessionKey}:${toolCallId}`;
  }
}

function hrTimeToMs(hr: [number, number]): number {
  return hr[0] * 1000 + hr[1] / 1_000_000;
}
