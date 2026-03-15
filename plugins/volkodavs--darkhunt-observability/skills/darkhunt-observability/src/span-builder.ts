import {
  SpanKind,
  SpanStatusCode,
  TraceFlags,
  type HrTime,
  type SpanContext,
  type SpanStatus,
  type SpanAttributes,
} from '@opentelemetry/api';
import type { ReadableSpan } from '@opentelemetry/sdk-trace-base';
import type { IResource } from '@opentelemetry/resources';
import type {
  BufferedAgent,
  BufferedGeneration,
  BufferedTool,
  MessageInData,
  AgentEndData,
  LlmOutputData,
  ToolEndData,
  PayloadMode,
} from './types.js';
import { INSTRUMENTATION_LIBRARY } from './types.js';
import {
  applyPayloadMode,
  enforceSpanSizeLimit,
  sanitizeToolParams,
  sanitizeToolResult,
  formatToolInput,
  cleanToolResult,
  cleanGenerationInput,
} from './payload.js';

// ── Time helpers ───────────────────────────────────────────────────

export function msToHrTime(epochMs: number): HrTime {
  const seconds = Math.floor(epochMs / 1000);
  const nanos = (epochMs % 1000) * 1_000_000;
  return [seconds, nanos];
}

function hrTimeDiff(start: HrTime, end: HrTime): HrTime {
  let seconds = end[0] - start[0];
  let nanos = end[1] - start[1];
  if (nanos < 0) {
    seconds -= 1;
    nanos += 1_000_000_000;
  }
  return [seconds, nanos];
}

// ── Base span factory ──────────────────────────────────────────────

interface SpanOpts {
  name: string;
  traceId: string;
  spanId: string;
  parentSpanId?: string;
  startTime: HrTime;
  endTime: HrTime;
  status: SpanStatus;
  attributes: SpanAttributes;
  resource: IResource;
}

function createReadableSpan(opts: SpanOpts): ReadableSpan {
  const spanContext: SpanContext = {
    traceId: opts.traceId,
    spanId: opts.spanId,
    traceFlags: TraceFlags.SAMPLED,
  };

  return {
    name: opts.name,
    kind: SpanKind.INTERNAL,
    spanContext: () => spanContext,
    parentSpanId: opts.parentSpanId,
    startTime: opts.startTime,
    endTime: opts.endTime,
    status: opts.status,
    attributes: opts.attributes,
    links: [],
    events: [],
    duration: hrTimeDiff(opts.startTime, opts.endTime),
    ended: true,
    resource: opts.resource,
    instrumentationLibrary: INSTRUMENTATION_LIBRARY,
    droppedAttributesCount: 0,
    droppedEventsCount: 0,
    droppedLinksCount: 0,
  };
}

// ── Span type factories ────────────────────────────────────────────

export function buildAgentSpan(
  buffered: BufferedAgent,
  endData: AgentEndData,
  resource: IResource,
): ReadableSpan {
  const endTime = msToHrTime(endData.ts);

  const attrs: Record<string, string | number | boolean | string[]> = {
    'openclaw.observation.type': 'agent',
    'openclaw.session.id': buffered.sessionId,
    'openclaw.session.key': buffered.sessionKey,
    'openclaw.agent.id': buffered.agentId,
  };

  if (buffered.accountId) attrs['user.id'] = buffered.accountId;
  if (buffered.runId) attrs['openclaw.run.id'] = buffered.runId;
  const agentSvcVersion = resource.attributes['service.version'];
  if (agentSvcVersion) attrs['service.version'] = String(agentSvcVersion);
  if (buffered.traceName) attrs['openclaw.trace.name'] = buffered.traceName;
  if (buffered.traceTags) attrs['openclaw.trace.tags'] = buffered.traceTags;
  if (buffered.channel) attrs['openclaw.channel'] = buffered.channel;

  let status: SpanStatus = { code: SpanStatusCode.UNSET };
  if (!endData.success) {
    status = {
      code: SpanStatusCode.ERROR,
      message: endData.error ?? 'agent failed',
    };
    attrs['openclaw.observation.level'] = 'ERROR';
    if (endData.error) attrs['openclaw.observation.status_message'] = endData.error;
  } else {
    attrs['openclaw.observation.level'] = 'DEFAULT';
  }

  return createReadableSpan({
    name: `agent ${buffered.agentId}`,
    traceId: buffered.traceId,
    spanId: buffered.spanId,
    startTime: buffered.startTime,
    endTime,
    status,
    attributes: attrs as SpanAttributes,
    resource,
  });
}

export function buildGenerationSpan(
  buffered: BufferedGeneration,
  endData: LlmOutputData,
  resource: IResource,
  payloadMode: PayloadMode,
  firstTokenTs?: number,
): ReadableSpan {
  const endTime = msToHrTime(endData.ts);

  const attrs: Record<string, string | number | boolean | string[]> = {
    'openclaw.observation.type': 'generation',
    'openclaw.observation.model.name': endData.model || buffered.model,
    'gen_ai.request.model': endData.model || buffered.model,
    'gen_ai.system': endData.provider || buffered.provider,
  };

  if (buffered.sessionId) attrs['openclaw.session.id'] = buffered.sessionId;
  if (buffered.accountId) attrs['user.id'] = buffered.accountId;

  // Belt-and-suspenders: set service.version on span attrs too
  const svcVersion = resource.attributes['service.version'];
  if (svcVersion) attrs['service.version'] = String(svcVersion);

  // Tokens (always included)
  if (endData.inputTokens != null) attrs['gen_ai.usage.input_tokens'] = endData.inputTokens;
  if (endData.outputTokens != null) attrs['gen_ai.usage.output_tokens'] = endData.outputTokens;
  if (endData.cacheReadInputTokens != null) attrs['gen_ai.usage.cache_read_input_tokens'] = endData.cacheReadInputTokens;
  if (endData.cacheCreationInputTokens != null) attrs['gen_ai.usage.cache_creation_input_tokens'] = endData.cacheCreationInputTokens;

  // tokens.total — sum of all token components
  const totalTokens = (endData.inputTokens ?? 0) + (endData.outputTokens ?? 0)
    + (endData.cacheReadInputTokens ?? 0) + (endData.cacheCreationInputTokens ?? 0);
  if (totalTokens > 0) attrs['gen_ai.usage.total_tokens'] = totalTokens;

  // Cost (always included)
  if (endData.costTotal != null) attrs['openclaw.cost.total'] = endData.costTotal;
  if (endData.costDetails) {
    attrs['openclaw.observation.cost_details'] = endData.costDetails;
    // Parse cost breakdown for individual cost attributes
    try {
      const cd = JSON.parse(endData.costDetails);
      if (cd.input != null) attrs['openclaw.cost.input'] = cd.input;
      if (cd.output != null) attrs['openclaw.cost.output'] = cd.output;
      const cacheReadCost = cd.cache_read ?? cd.cacheRead;
      if (cacheReadCost != null) attrs['openclaw.cost.cache_read'] = cacheReadCost;
    } catch { /* ignore parse errors */ }
  }

  // Content metadata (always included)
  if (buffered.inputLength != null) attrs['openclaw.observation.input_length'] = buffered.inputLength;
  if (endData.outputLength != null) attrs['openclaw.observation.output_length'] = endData.outputLength;
  if (buffered.systemPromptLength != null) attrs['openclaw.observation.system_prompt_length'] = buffered.systemPromptLength;
  if (buffered.historyLength != null) attrs['openclaw.observation.history_length'] = buffered.historyLength;

  // Stop reason (always included)
  if (endData.stopReason) {
    attrs['openclaw.stop_reason'] = endData.stopReason;
    attrs['gen_ai.response.finish_reasons'] = [endData.stopReason];
  }

  // Timing — prefer runtime firstTokenTs (precise streaming event) over completionStartTime
  if (firstTokenTs) {
    const startMs = buffered.startTime[0] * 1000 + buffered.startTime[1] / 1_000_000;
    const ttft = Math.round(firstTokenTs - startMs);
    if (ttft > 0) attrs['openclaw.timing.time_to_first_token_ms'] = ttft;
  } else if (endData.completionStartTime) {
    attrs['openclaw.observation.completion_start_time'] = endData.completionStartTime;
    const completionMs = new Date(endData.completionStartTime).getTime();
    const startMs = buffered.startTime[0] * 1000 + buffered.startTime[1] / 1_000_000;
    const ttft = Math.round(completionMs - startMs);
    if (ttft > 0) attrs['openclaw.timing.time_to_first_token_ms'] = ttft;
  }
  if (buffered.attempt != null) attrs['openclaw.observation.attempt'] = buffered.attempt;

  // Content (mode-dependent) — format as JSON message arrays for clean server-side parsing
  const cleanedInput = cleanGenerationInput(buffered.input);
  if (cleanedInput) {
    attrs['openclaw.observation.input'] = JSON.stringify([{ role: 'user', content: cleanedInput }]);
  }
  if (endData.output) {
    attrs['openclaw.observation.output'] = JSON.stringify([{ role: 'assistant', content: endData.output }]);
  }
  if (buffered.systemPrompt) {
    attrs['openclaw.observation.system_prompt'] = buffered.systemPrompt;
  }
  if (buffered.modelParameters) attrs['openclaw.observation.model.parameters'] = buffered.modelParameters;

  // Apply payload mode + size limits
  const finalAttrs = enforceSpanSizeLimit(applyPayloadMode(attrs, payloadMode));

  let status: SpanStatus = { code: SpanStatusCode.UNSET };
  if (endData.error) {
    status = { code: SpanStatusCode.ERROR, message: endData.error };
    finalAttrs['openclaw.observation.level'] = 'ERROR';
    finalAttrs['openclaw.observation.status_message'] = endData.error;
  } else {
    finalAttrs['openclaw.observation.level'] = 'DEFAULT';
  }

  return createReadableSpan({
    name: `generation ${endData.model || buffered.model}`,
    traceId: buffered.traceId,
    spanId: buffered.spanId,
    parentSpanId: buffered.parentSpanId,
    startTime: buffered.startTime,
    endTime,
    status,
    attributes: finalAttrs as SpanAttributes,
    resource,
  });
}

export function buildToolSpan(
  buffered: BufferedTool,
  endData: ToolEndData,
  resource: IResource,
  payloadMode: PayloadMode,
  toolResult?: string,
): ReadableSpan {
  const endTime = msToHrTime(endData.ts);

  const attrs: Record<string, string | number | boolean | string[]> = {
    'openclaw.observation.type': 'tool',
    'gen_ai.tool.name': buffered.toolName,
    'gen_ai.tool.call.id': buffered.toolCallId,
    'openclaw.tool.success': endData.success,
  };

  if (buffered.sessionId) attrs['openclaw.session.id'] = buffered.sessionId;
  if (buffered.accountId) attrs['user.id'] = buffered.accountId;
  if (buffered.model) attrs['gen_ai.request.model'] = buffered.model;
  if (buffered.attempt != null) attrs['openclaw.tool.attempt'] = buffered.attempt;
  if (buffered.meta) attrs['openclaw.tool.meta'] = buffered.meta;
  const toolSvcVersion = resource.attributes['service.version'];
  if (toolSvcVersion) attrs['service.version'] = String(toolSvcVersion);

  // Tool parameters (mode-dependent + safe-tool allowlist)
  const sanitized = sanitizeToolParams(buffered.toolName, buffered.parameters, payloadMode);
  if (sanitized) attrs['openclaw.tool.parameters'] = sanitized;

  // Tool input — populate REQUEST section with the primary argument (command, path, etc.)
  const toolInput = formatToolInput(buffered.toolName, buffered.parameters);
  if (toolInput) {
    attrs['openclaw.observation.input'] = JSON.stringify([{ role: 'user', content: toolInput }]);
  }

  // Tool result — clean content wrappers, then sanitize for RESPONSE section
  const cleaned = cleanToolResult(toolResult);
  const sanitizedResult = sanitizeToolResult(buffered.toolName, cleaned ?? toolResult, payloadMode);
  if (sanitizedResult) {
    attrs['openclaw.observation.output'] = JSON.stringify([{ role: 'tool', content: sanitizedResult }]);
  }

  const finalAttrs = enforceSpanSizeLimit(attrs);

  let status: SpanStatus = { code: SpanStatusCode.UNSET };
  if (!endData.success) {
    status = {
      code: SpanStatusCode.ERROR,
      message: endData.error ?? 'tool failed',
    };
    finalAttrs['openclaw.observation.level'] = 'ERROR';
    if (endData.error) finalAttrs['openclaw.observation.status_message'] = endData.error;
  } else {
    finalAttrs['openclaw.observation.level'] = 'DEFAULT';
  }

  return createReadableSpan({
    name: buffered.toolName,
    traceId: buffered.traceId,
    spanId: buffered.spanId,
    parentSpanId: buffered.parentSpanId,
    startTime: buffered.startTime,
    endTime,
    status,
    attributes: finalAttrs as SpanAttributes,
    resource,
  });
}

export function buildMessageSpan(
  data: MessageInData,
  traceId: string,
  spanId: string,
  resource: IResource,
): ReadableSpan {
  const time = msToHrTime(data.ts);

  const attrs: SpanAttributes = {
    'openclaw.observation.type': 'event',
    'openclaw.observation.level': 'DEFAULT',
    'openclaw.session.id': data.sessionId,
    'openclaw.channel': data.channel,
    'openclaw.message.from': data.from,
    'openclaw.message.content_length': data.contentLength,
  };
  if (data.accountId) attrs['user.id'] = data.accountId;

  return createReadableSpan({
    name: `message.in ${data.channel}`,
    traceId,
    spanId,
    startTime: time,
    endTime: time, // zero-duration
    status: { code: SpanStatusCode.UNSET },
    attributes: attrs,
    resource,
  });
}
