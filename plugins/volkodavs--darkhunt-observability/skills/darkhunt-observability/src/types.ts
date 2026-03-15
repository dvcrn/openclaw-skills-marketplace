import type { HrTime } from '@opentelemetry/api';

// ── Plugin config ──────────────────────────────────────────────────

export type PayloadMode = 'metadata' | 'debug' | 'full';

export interface PluginConfig {
  traces_endpoint: string;
  logs_endpoint?: string;
  headers?: Record<string, string>;
  payload_mode: PayloadMode;
  batch_delay_ms: number;
  batch_max_size: number;
  export_timeout_ms: number;
  enabled: boolean;
  debug?: boolean;
}

// ── Observation types ──────────────────────────────────────────────

export type ObservationType = 'agent' | 'generation' | 'tool' | 'event';

// ── Buffered state (held between start/end events) ─────────────────

export interface BufferedAgent {
  sessionId: string;
  sessionKey: string;
  agentId: string;
  spanId: string;
  traceId: string;
  startTime: HrTime;
  traceName?: string;
  traceTags?: string[];
  channel?: string;
  accountId?: string;
  model?: string;
  /** OpenClaw native run identifier from runtime.events.onAgentEvent */
  runId?: string;
}

export interface BufferedGeneration {
  spanId: string;
  parentSpanId: string;
  traceId: string;
  model: string;
  provider: string;
  startTime: HrTime;
  input?: string;
  inputLength?: number;
  systemPrompt?: string;
  systemPromptLength?: number;
  historyLength?: number;
  modelParameters?: string;
  attempt?: number;
  sessionKey: string;
  sessionId: string;
  accountId?: string;
}

export interface BufferedTool {
  spanId: string;
  parentSpanId: string;
  traceId: string;
  toolName: string;
  toolCallId: string;
  startTime: HrTime;
  parameters?: string;
  attempt?: number;
  sessionKey: string;
  sessionId: string;
  accountId?: string;
  model?: string;
  /** Human-readable tool description from runtime agent event meta */
  meta?: string;
}

// ── Event data from OpenClaw hooks ─────────────────────────────────

export interface MessageInData {
  sessionId: string;
  sessionKey: string;
  channel: string;
  from: string;
  accountId?: string;
  contentLength: number;
  ts: number; // epoch ms
}

export interface AgentStartData {
  sessionId: string;
  sessionKey: string;
  agentId: string;
  traceName?: string;
  traceTags?: string[];
  channel?: string;
  accountId?: string;
  ts: number;
}

export interface AgentEndData {
  sessionKey: string;
  agentId: string;
  success: boolean;
  durationMs: number;
  error?: string;
  ts: number;
}

export interface LlmInputData {
  sessionId: string;
  sessionKey: string;
  agentId: string;
  model: string;
  provider: string;
  runId: string;
  input?: string;
  inputLength?: number;
  systemPrompt?: string;
  systemPromptLength?: number;
  historyLength?: number;
  modelParameters?: string;
  attempt?: number;
  ts: number;
}

export interface LlmOutputData {
  sessionKey: string;
  runId: string;
  model: string;
  provider: string;
  output?: string;
  outputLength?: number;
  stopReason?: string;
  inputTokens?: number;
  outputTokens?: number;
  cacheReadInputTokens?: number;
  cacheCreationInputTokens?: number;
  costTotal?: number;
  costDetails?: string;
  completionStartTime?: string;
  error?: string;
  ts: number;
}

export interface ToolStartData {
  sessionKey: string;
  agentId: string;
  toolName: string;
  toolCallId: string;
  parameters?: string;
  attempt?: number;
  ts: number;
}

export interface ToolEndData {
  sessionKey: string;
  toolName: string;
  toolCallId: string;
  success: boolean;
  durationMs?: number;
  result?: string;
  error?: string;
  ts: number;
}

export interface LlmUsageData {
  sessionKey: string;
  model: string;
  provider: string;
  inputTokens: number;
  outputTokens: number;
  cacheTokens?: number;
  durationMs: number;
}

// ── Instrumentation library constant ───────────────────────────────

export const INSTRUMENTATION_LIBRARY = {
  name: 'tracehub-telemetry',
  version: '0.1.0',
} as const;
