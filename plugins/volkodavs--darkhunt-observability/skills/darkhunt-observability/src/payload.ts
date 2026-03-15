import type { PayloadMode } from './types.js';

// ── Size limits (bytes) ────────────────────────────────────────────

export const LIMIT_INPUT = 4 * 1024;
export const LIMIT_OUTPUT = 4 * 1024;
export const LIMIT_TOOL_PARAMS = 2 * 1024;
export const LIMIT_COST_DETAILS = 512;
export const LIMIT_MODEL_PARAMS = 512;
export const LIMIT_SINGLE_ATTR = 8 * 1024;
export const LIMIT_TOTAL_SPAN = 64 * 1024;

// Debug mode truncation limits (characters)
export const DEBUG_INPUT_CHARS = 500;
export const DEBUG_OUTPUT_CHARS = 500;
export const DEBUG_TOOL_PARAMS_CHARS = 1000;
export const DEBUG_SYSTEM_PROMPT_CHARS = 200;

// ── Safe-tool allowlist ────────────────────────────────────────────

const SAFE_TOOLS = new Set([
  // OpenClaw 16 built-in tools
  'exec', 'read', 'write', 'edit',
  'web_search', 'web_fetch', 'message', 'process',
  'sessions_spawn', 'session_status', 'subagents', 'agents_list',
  'browser', 'cron', 'memory_search', 'nodes',
  // Claude-style aliases
  'Read', 'Write', 'Edit', 'Grep', 'Glob', 'Bash', 'Agent',
]);

// ── Core functions ─────────────────────────────────────────────────

export function truncate(value: string, maxBytes: number): string {
  const encoded = Buffer.from(value, 'utf-8');
  if (encoded.length <= maxBytes) return value;

  const suffix = `... [truncated, ${value.length} chars total]`;
  const suffixBytes = Buffer.byteLength(suffix, 'utf-8');
  const available = maxBytes - suffixBytes;
  if (available <= 0) return suffix;

  // Truncate at byte level then decode safely
  let truncated = encoded.subarray(0, available).toString('utf-8');
  // Remove potential partial multi-byte character at the end
  if (truncated.endsWith('\uFFFD')) {
    truncated = truncated.slice(0, -1);
  }
  return truncated + suffix;
}

export function truncateChars(value: string, maxChars: number): string {
  if (value.length <= maxChars) return value;
  const suffix = `... [truncated, ${value.length} chars total]`;
  return value.slice(0, maxChars) + suffix;
}

export function shouldIncludeContent(mode: PayloadMode): boolean {
  return mode !== 'metadata';
}

export function sanitizeToolParams(
  toolName: string,
  params: string | undefined,
  mode: PayloadMode,
): string | undefined {
  if (!params) return undefined;

  // Unknown/third-party tools: redact in all modes (could contain secrets)
  if (!SAFE_TOOLS.has(toolName)) {
    // In metadata mode, skip entirely; in debug/full, show redaction marker
    if (mode === 'metadata') return undefined;
    return JSON.stringify({ redacted: true });
  }

  // Safe tools: always include params (they're operational metadata, not private content).
  // These show what happened — file paths, commands, search queries.
  if (mode === 'metadata') {
    return truncateChars(params, DEBUG_TOOL_PARAMS_CHARS);
  }

  if (mode === 'debug') {
    return truncateChars(params, DEBUG_TOOL_PARAMS_CHARS);
  }

  return truncate(params, LIMIT_TOOL_PARAMS);
}

/**
 * Extract the primary argument from tool parameters for the REQUEST section.
 * Returns the most meaningful value (command, path, query, url) for known tools.
 */
export function formatToolInput(toolName: string, parametersJson: string | undefined): string | undefined {
  if (!parametersJson) return undefined;
  try {
    const params = JSON.parse(parametersJson);
    if (typeof params === 'object' && params !== null) {
      const primary = params.command ?? params.path ?? params.file
        ?? params.query ?? params.url ?? params.pattern;
      if (primary) return String(primary);
    }
  } catch { /* not JSON */ }
  return parametersJson;
}

/**
 * Extract clean text from tool result JSON, stripping OpenClaw content wrappers.
 * Handles: {content: [{type:"text", text:"..."}], details: {...}}
 */
export function cleanToolResult(result: string | undefined): string | undefined {
  if (!result) return undefined;
  try {
    const parsed = JSON.parse(result);
    if (typeof parsed === 'object' && parsed !== null) {
      if (Array.isArray(parsed.content)) {
        const texts = parsed.content
          .filter((b: any) => b?.type === 'text' && b?.text)
          .map((b: any) => b.text);
        if (texts.length > 0) return texts.join('\n');
      }
      if (parsed.aggregated != null) return String(parsed.aggregated);
      if (parsed.text != null) return String(parsed.text);
    }
  } catch { /* not JSON — return as-is */ }
  return result;
}

/**
 * Clean up OpenClaw generation input by stripping system-injected boilerplate.
 * - Replaces [media attached: /path/file.jpg (mime)] with [image: file.jpg]
 * - Strips "To send an image back..." instruction block
 * - Strips "Conversation info (untrusted metadata):" + JSON
 * - Strips "Sender (untrusted metadata):" + JSON
 * - Strips <media:image> tags
 */
export function cleanGenerationInput(input: string | undefined): string | undefined {
  if (!input) return undefined;

  let cleaned = input;

  // [media attached: /path/to/file.ext (mime/type) | /path] → [image: file.ext]
  cleaned = cleaned.replace(
    /\[media attached:\s*[^\]]*\/([^\s|)\]]+)\s*\([^)]*\)[^\]]*\]/g,
    (_, filename) => `[image: ${filename}]`,
  );

  // Strip image instruction block
  cleaned = cleaned.replace(
    /To send an image back.*?Keep caption in the text body\.\n?/gs,
    '',
  );

  // Strip "Conversation info (untrusted metadata):" + fenced JSON
  cleaned = cleaned.replace(
    /Conversation info \(untrusted metadata\):\s*\n```json?\n[\s\S]*?```\s*\n*/g,
    '',
  );

  // Strip "Sender (untrusted metadata):" + fenced JSON
  cleaned = cleaned.replace(
    /Sender \(untrusted metadata\):\s*\n```json?\n[\s\S]*?```\s*\n*/g,
    '',
  );

  // Strip <media:image> / <media:video> etc. tags
  cleaned = cleaned.replace(/<media:\w+>\s*/g, '');

  // Collapse multiple blank lines
  cleaned = cleaned.replace(/\n{3,}/g, '\n\n').trim();

  return cleaned || undefined;
}

export function sanitizeToolResult(
  toolName: string,
  result: string | undefined,
  mode: PayloadMode,
): string | undefined {
  if (!result) return undefined;

  // Unknown/third-party tools: never include results
  if (!SAFE_TOOLS.has(toolName)) return undefined;

  // Safe tools: include result in all modes (it shows what happened)
  if (mode === 'metadata' || mode === 'debug') {
    return truncateChars(result, DEBUG_OUTPUT_CHARS);
  }

  return truncate(result, LIMIT_OUTPUT);
}

/**
 * Apply payload mode to content attributes.
 * Returns a new map with content attributes stripped/truncated per mode.
 */
export function applyPayloadMode(
  attrs: Record<string, string | number | boolean | string[]>,
  mode: PayloadMode,
): Record<string, string | number | boolean | string[]> {
  const result = { ...attrs };

  if (mode === 'metadata') {
    delete result['openclaw.observation.input'];
    delete result['openclaw.observation.output'];
    delete result['openclaw.observation.system_prompt'];
    delete result['openclaw.observation.model.parameters'];
    // Note: openclaw.tool.parameters is NOT deleted here — safe tool params
    // are included even in metadata mode (handled by sanitizeToolParams)
    return result;
  }

  if (mode === 'debug') {
    if (typeof result['openclaw.observation.input'] === 'string') {
      result['openclaw.observation.input'] = truncateChars(
        result['openclaw.observation.input'] as string,
        DEBUG_INPUT_CHARS,
      );
    }
    if (typeof result['openclaw.observation.output'] === 'string') {
      result['openclaw.observation.output'] = truncateChars(
        result['openclaw.observation.output'] as string,
        DEBUG_OUTPUT_CHARS,
      );
    }
    if (typeof result['openclaw.observation.system_prompt'] === 'string') {
      result['openclaw.observation.system_prompt'] = truncateChars(
        result['openclaw.observation.system_prompt'] as string,
        DEBUG_SYSTEM_PROMPT_CHARS,
      );
    }
    if (typeof result['openclaw.observation.model.parameters'] === 'string') {
      result['openclaw.observation.model.parameters'] = truncate(
        result['openclaw.observation.model.parameters'] as string,
        LIMIT_MODEL_PARAMS,
      );
    }
    // Tool params handled separately via sanitizeToolParams
  }

  // Full mode: enforce byte limits
  if (mode === 'full') {
    if (typeof result['openclaw.observation.input'] === 'string') {
      result['openclaw.observation.input'] = truncate(
        result['openclaw.observation.input'] as string,
        LIMIT_INPUT,
      );
    }
    if (typeof result['openclaw.observation.output'] === 'string') {
      result['openclaw.observation.output'] = truncate(
        result['openclaw.observation.output'] as string,
        LIMIT_OUTPUT,
      );
    }
    if (typeof result['openclaw.observation.system_prompt'] === 'string') {
      result['openclaw.observation.system_prompt'] = truncate(
        result['openclaw.observation.system_prompt'] as string,
        LIMIT_INPUT,
      );
    }
    if (typeof result['openclaw.observation.model.parameters'] === 'string') {
      result['openclaw.observation.model.parameters'] = truncate(
        result['openclaw.observation.model.parameters'] as string,
        LIMIT_MODEL_PARAMS,
      );
    }
  }

  return result;
}

/**
 * Enforce the total span size limit. If over 64KB, drop content attributes
 * first (input, output, tool.parameters, model.parameters), then truncate
 * remaining large attributes.
 */
export function enforceSpanSizeLimit(
  attrs: Record<string, string | number | boolean | string[]>,
  maxBytes: number = LIMIT_TOTAL_SPAN,
): Record<string, string | number | boolean | string[]> {
  const result = { ...attrs };

  // Enforce per-attribute limit
  for (const [key, val] of Object.entries(result)) {
    if (typeof val === 'string' && Buffer.byteLength(val, 'utf-8') > LIMIT_SINGLE_ATTR) {
      result[key] = truncate(val, LIMIT_SINGLE_ATTR);
    }
  }

  if (estimateSize(result) <= maxBytes) return result;

  // Drop content attributes in priority order (largest first)
  const droppable = [
    'openclaw.observation.system_prompt',
    'openclaw.observation.input',
    'openclaw.observation.output',
    'openclaw.tool.parameters',
    'openclaw.observation.model.parameters',
  ];

  for (const key of droppable) {
    delete result[key];
    if (estimateSize(result) <= maxBytes) return result;
  }

  return result;
}

function estimateSize(attrs: Record<string, unknown>): number {
  let size = 0;
  for (const [key, val] of Object.entries(attrs)) {
    size += Buffer.byteLength(key, 'utf-8');
    if (typeof val === 'string') {
      size += Buffer.byteLength(val, 'utf-8');
    } else if (Array.isArray(val)) {
      size += Buffer.byteLength(JSON.stringify(val), 'utf-8');
    } else {
      size += 8; // numbers, booleans
    }
  }
  return size;
}
