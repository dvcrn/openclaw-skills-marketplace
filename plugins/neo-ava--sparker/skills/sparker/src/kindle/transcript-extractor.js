// Transcript Extractor — extract knowledge from conversations, meeting minutes,
// speech-to-text transcripts, and chat logs.
//
// Unlike document ingestion which processes structured prose, this module handles
// multi-speaker dialogue where knowledge is scattered across conversation flow:
//   - Meeting minutes / notes
//   - Audio/video transcription (ASR output)
//   - Chat exports (WeChat, Feishu, DingTalk, Slack)
//   - Interview records
//   - Debriefs / retrospectives
//
// Key difference: the LLM prompt understands speaker turns, identifies role-based
// contributions (never names), extracts decisions, consensus, disagreements,
// lessons learned, and experience signals buried in discussion.

var fs = require('fs');
var path = require('path');
var { createRawSpark } = require('./extractor');
var { appendRawSpark } = require('../core/storage');
var { resolveLLMConfig, callLLM } = require('../core/openclaw-config');

var TRANSCRIPT_PROMPT = [
  'You are an expert at extracting reusable professional knowledge from conversations.',
  'Below is a transcript — it could be a meeting, interview, debrief, chat log, or ASR output.',
  '',
  'Extract every piece of REUSABLE EXPERIENTIAL KNOWLEDGE. Focus on:',
  '',
  '1. **Decisions & rationale**: "We decided X because Y"',
  '2. **Lessons learned**: "Last time X happened, we learned Y"',
  '3. **Heuristic rules**: "In situation X, always do Y"',
  '4. **Boundary conditions**: "X works except when Y"',
  '5. **Failure cases**: "X failed because Y, next time do Z"',
  '6. **Consensus opinions**: points multiple speakers agreed on',
  '7. **Disagreements**: conflicting views that reveal nuance',
  '8. **Data points**: specific numbers, benchmarks, thresholds mentioned',
  '9. **Workflow insights**: "The process should be X→Y→Z"',
  '10. **Audience/user insights**: "Users/customers actually think/do X"',
  '',
  'For EACH insight, output a JSON object with the **six-dimension structure**:',
  '',
  '  knowledge_type   — "rule" | "preference" | "pattern" | "boundary" | "lesson" | "data_point"',
  '  when             — { trigger: string (what triggers this knowledge),',
  '                       conditions: string[] (preconditions for applicability) }',
  '  where            — { domain: string, sub_domain: string, scenario: string, audience: string }',
  '  why              — string (why this knowledge matters or works)',
  '  how              — { summary: string (one-sentence action), detail: string (step-by-step if applicable) }',
  '  result           — { expected_outcome: string }',
  '  not              — array of { condition: string, effect: string, reason: string }',
  '                     (when this does NOT apply)',
  '  speaker_role     — role of the person who said this (NEVER use real names)',
  '  speaker_alias    — stable pseudonym for this speaker within the transcript',
  '                     (use "Person_A", "Person_B", etc. — same person = same alias)',
  '  evidence         — brief quote from the transcript (anonymize names to roles)',
  '  agreement_level  — "consensus" | "single_opinion" | "debated"',
  '',
  'IMPORTANT:',
  '- Replace ALL personal names with stable pseudonyms (张总→Person_A, 小李→Person_B)',
  '- The SAME person must have the SAME alias throughout the transcript',
  '- Also provide their role description in speaker_role (e.g. "运营总监", "技术负责人")',
  '- Skip small talk, logistics, greetings — only extract professional knowledge',
  '- One conversation often yields 5-20 insights; don\'t under-extract',
  '- If the transcript is too noisy (pure ASR), do your best with what\'s intelligible',
  '',
  'Return a JSON array. Only return JSON, no markdown fences.',
  'If no extractable knowledge, return [].',
  '',
  '## Transcript',
  '{{content}}',
].join('\n');

var CHUNK_SIZE = 6000;
var CHUNK_OVERLAP = 500;

function detectTranscriptFormat(text) {
  if (!text) return 'unknown';
  var lines = text.slice(0, 3000).split('\n');
  var srtPattern = /^\d+\s*$/;
  var timePattern = /\d{2}:\d{2}:\d{2}/;
  var speakerPattern = /^[\w\u4e00-\u9fff]+[：:]/m;
  var bracketSpeaker = /^\[[\w\u4e00-\u9fff]+\]/m;
  var timestampSpeaker = /\d{2}:\d{2}(?::\d{2})?\s+[\w\u4e00-\u9fff]+[：:]/m;

  var hasSrt = lines.some(function (l) { return srtPattern.test(l.trim()); }) &&
    lines.some(function (l) { return timePattern.test(l); });
  if (hasSrt) return 'srt';

  if (timestampSpeaker.test(text.slice(0, 3000))) return 'timestamped_dialogue';
  if (bracketSpeaker.test(text.slice(0, 3000))) return 'bracket_dialogue';
  if (speakerPattern.test(text.slice(0, 3000))) return 'speaker_dialogue';

  return 'plain';
}

function preprocessTranscript(text, format) {
  if (format === 'srt') {
    return text
      .replace(/^\d+\s*\n/gm, '')
      .replace(/\d{2}:\d{2}:\d{2}[,.]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[,.]\d{3}\s*\n/g, '')
      .replace(/\n{3,}/g, '\n\n')
      .trim();
  }
  return text;
}

function chunkTranscript(text) {
  if (text.length <= CHUNK_SIZE) return [text];

  var chunks = [];
  var start = 0;
  while (start < text.length) {
    var end = Math.min(start + CHUNK_SIZE, text.length);
    if (end < text.length) {
      var newline = text.lastIndexOf('\n', end);
      if (newline > start + CHUNK_SIZE * 0.5) end = newline;
    }
    chunks.push(text.slice(start, end));
    start = end - CHUNK_OVERLAP;
    if (start < 0) start = 0;
    if (end >= text.length) break;
  }
  return chunks;
}

function buildTranscriptPrompt(content, meta) {
  var header = '';
  if (meta) {
    if (meta.meeting_topic) header += 'Meeting topic: ' + meta.meeting_topic + '\n';
    if (meta.domain) header += 'Domain: ' + meta.domain + '\n';
    if (meta.date) header += 'Date: ' + meta.date + '\n';
    if (meta.participants_count) header += 'Participants: ~' + meta.participants_count + '\n';
    if (header) header = '## Metadata\n' + header + '\n';
  }
  return TRANSCRIPT_PROMPT.replace('{{content}}', header + String(content || '').slice(0, 8000));
}

function parseTranscriptResponse(text) {
  if (!text) return [];
  var cleaned = text.trim();
  if (cleaned.startsWith('```')) {
    cleaned = cleaned.replace(/^```(?:json)?\n?/, '').replace(/\n?```$/, '');
  }
  try {
    var arr = JSON.parse(cleaned);
    if (!Array.isArray(arr)) return [];
    return arr.filter(function (item) {
      return item && item.heuristic;
    });
  } catch (e) {
    return [];
  }
}

function deduplicateInsights(allInsights) {
  var seen = {};
  return allInsights.filter(function (ins) {
    var key = (ins.heuristic || '').toLowerCase().replace(/\s+/g, ' ').trim();
    if (seen[key]) return false;
    seen[key] = true;
    return true;
  });
}

async function extractFromTranscript(filePath, opts) {
  var o = opts || {};
  var content;
  try {
    content = fs.readFileSync(filePath, 'utf8');
  } catch (e) {
    return { error: 'Cannot read file: ' + filePath, candidates: [] };
  }

  if (!content || content.trim().length < 50) {
    return { error: 'Transcript too short or empty', candidates: [] };
  }

  var format = detectTranscriptFormat(content);
  var processed = preprocessTranscript(content, format);
  var chunks = chunkTranscript(processed);

  var llmConfig = resolveLLMConfig();
  var allInsights = [];

  for (var ci = 0; ci < chunks.length; ci++) {
    var prompt = buildTranscriptPrompt(chunks[ci], {
      meeting_topic: o.topic || null,
      domain: o.domain || null,
      date: o.date || null,
      participants_count: o.participants_count || null,
    });

    var response = await callLLM(prompt, Object.assign({}, llmConfig, {
      max_tokens: 4000,
      temperature: 0.15,
    }));

    var insights = parseTranscriptResponse(response);
    allInsights = allInsights.concat(insights);
  }

  allInsights = deduplicateInsights(allInsights);
  if (allInsights.length === 0) {
    return { file: filePath, format: format, chunks: chunks.length, candidates: [] };
  }

  var candidates = [];
  for (var i = 0; i < allInsights.length; i++) {
    var ins = allInsights[i];

    // V2: extract six-dimension fields from LLM response
    var insWhen = ins.when || {};
    var insWhere = ins.where || {};
    var insHow = ins.how || {};
    var insNot = ins.not || [];
    var insDomain = insWhere.domain || ins.domain || o.domain || 'general';
    var insSubDomain = insWhere.sub_domain || ins.sub_domain || null;
    var heuristic = (insHow.summary || ins.heuristic || '');
    // Backward-compat: map not_applicable_when to not[] if LLM uses old format
    if (insNot.length === 0 && Array.isArray(ins.not_applicable_when)) {
      insNot = ins.not_applicable_when.map(function (c) {
        return { condition: c, effect: 'not_applicable', reason: '' };
      });
    }

    var spark = createRawSpark({
      source: 'human_teaching',
      trigger: 'transcript_extraction: ' + path.basename(filePath),
      content: heuristic,
      domain: insDomain,
      extraction_method: 'transcript_extraction',
      confirmation_status: o.auto_confirm ? 'human_confirmed' : 'unconfirmed',
      confidence: o.auto_confirm ? 0.40 : 0.18,
      tags: [
        ins.knowledge_type || ins.heuristic_type || 'rule',
        insSubDomain,
        ins.agreement_level === 'consensus' ? 'consensus' : null,
      ].filter(Boolean),
      when: { trigger: insWhen.trigger || heuristic, conditions: insWhen.conditions || ins.applicable_when || [] },
      where: { domain: insDomain, sub_domain: insSubDomain, scenario: insWhere.scenario || '', audience: insWhere.audience || '' },
      why: ins.why || '',
      how: { summary: heuristic, detail: insHow.detail || '' },
      result: { expected_outcome: (ins.result && ins.result.expected_outcome) || '' },
      not: insNot,
      knowledge_type: ins.knowledge_type || ins.heuristic_type || 'rule',
      card: {
        heuristic: heuristic,
        heuristic_type: ins.knowledge_type || ins.heuristic_type || 'rule',
        context_envelope: {
          domain: insDomain,
          sub_domain: insSubDomain,
          source_type: 'transcript',
          transcript_format: format,
          speaker_role: ins.speaker_role || null,
          speaker_alias: ins.speaker_alias || null,
        },
        boundary_conditions: insNot.map(function (n) {
          return { condition: n.condition || '', effect: n.effect || 'not_applicable', reason: n.reason || '' };
        }),
        applicable_when: insWhen.conditions || ins.applicable_when || [],
        evidence: ins.evidence ? {
          source_document: path.basename(filePath),
          quote: ins.evidence,
          agreement_level: ins.agreement_level || 'single_opinion',
        } : null,
      },
    });

    if (!o.dry_run) {
      appendRawSpark(spark);
    }
    candidates.push(spark);
  }

  return {
    file: filePath,
    format: format,
    chunks_processed: chunks.length,
    candidates: candidates,
  };
}

// Convenience: extract from raw text string (e.g., pasted transcript or stdin)
async function extractFromTranscriptText(text, opts) {
  var o = opts || {};
  var tmpDir = require('os').tmpdir();
  var tmpFile = path.join(tmpDir, 'sparker_transcript_' + Date.now() + '.txt');
  try {
    fs.writeFileSync(tmpFile, text, 'utf8');
    return await extractFromTranscript(tmpFile, o);
  } finally {
    try { fs.unlinkSync(tmpFile); } catch (e) { /* best effort */ }
  }
}

module.exports = {
  extractFromTranscript,
  extractFromTranscriptText,
  detectTranscriptFormat,
  preprocessTranscript,
  chunkTranscript,
  buildTranscriptPrompt,
  parseTranscriptResponse,
};
