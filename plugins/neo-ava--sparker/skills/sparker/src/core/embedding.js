// Local embedding client — calls OpenAI-compatible or Doubao multimodal API.
// Gracefully returns null when no embedding endpoint is configured.
// Config resolution: STP_EMBEDDING_* env vars > OpenClaw provider auto-detection.
//
// Auto-detects Doubao multimodal format when endpoint URL contains "multimodal":
//   Request:  { model, input: [{ type: "text", text: "..." }] }
//   Response: { data: { embedding: [...] } }
// Otherwise uses standard OpenAI format:
//   Request:  { model, input: "text" | ["text1", ...] }
//   Response: { data: [{ embedding: [...] }] }

var { resolveEmbeddingConfig } = require('./openclaw-config');

var BATCH_SIZE = Number(process.env.STP_EMBEDDING_BATCH_SIZE) || 16;
var TIMEOUT_MS = Number(process.env.STP_EMBEDDING_TIMEOUT_MS) || 30000;

function isEmbeddingAvailable() {
  var cfg = resolveEmbeddingConfig();
  return !!(cfg && cfg.endpoint);
}

function isMultimodal(endpoint) {
  return endpoint.indexOf('multimodal') >= 0;
}

function buildHeaders(cfg) {
  var headers = { 'Content-Type': 'application/json' };
  if (cfg.apiKey) headers['Authorization'] = 'Bearer ' + cfg.apiKey;
  return headers;
}

function buildRequestBody(cfg, texts) {
  var model = cfg.model || 'default';
  if (isMultimodal(cfg.endpoint)) {
    var inputArray = Array.isArray(texts) ? texts : [texts];
    return {
      model: model,
      input: inputArray.map(function (t) { return { type: 'text', text: t }; }),
    };
  }
  return { model: model, input: texts };
}

function parseResponse(data) {
  // OpenAI format: { data: [{ embedding: [...] }, ...] }
  if (data.data && Array.isArray(data.data)) {
    var vectors = [];
    for (var i = 0; i < data.data.length; i++) {
      var item = data.data[i];
      if (item.embedding && Array.isArray(item.embedding)) {
        vectors.push(item.embedding);
      }
    }
    if (vectors.length > 0) return vectors;
  }
  // Doubao multimodal: { data: { embedding: [...] } }
  if (data.data && !Array.isArray(data.data) && typeof data.data === 'object') {
    if (data.data.embedding && Array.isArray(data.data.embedding)) {
      return [data.data.embedding];
    }
  }
  // Simple: { embedding: [...] }
  if (data.embedding && Array.isArray(data.embedding)) {
    return [data.embedding];
  }
  // Ollama: { embeddings: [[...], ...] }
  if (data.embeddings && Array.isArray(data.embeddings)) {
    return data.embeddings;
  }
  return [];
}

async function getEmbedding(text) {
  var cfg = resolveEmbeddingConfig();
  if (!cfg || !cfg.endpoint) return null;

  try {
    var res = await fetch(cfg.endpoint, {
      method: 'POST',
      headers: buildHeaders(cfg),
      body: JSON.stringify(buildRequestBody(cfg, text)),
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
    if (!res.ok) {
      process.stderr.write('[embedding] API error ' + res.status + '\n');
      return null;
    }
    var data = await res.json();
    var vectors = parseResponse(data);
    return vectors.length > 0 ? vectors[0] : null;
  } catch (e) {
    process.stderr.write('[embedding] Request failed: ' + e.message + '\n');
    return null;
  }
}

async function getEmbeddings(texts) {
  var cfg = resolveEmbeddingConfig();
  if (!cfg || !cfg.endpoint) return texts.map(function () { return null; });

  var results = new Array(texts.length).fill(null);

  // Multimodal endpoints don't support batch array — call one at a time
  if (isMultimodal(cfg.endpoint)) {
    for (var k = 0; k < texts.length; k++) {
      results[k] = await getEmbedding(texts[k]);
    }
    return results;
  }

  // Standard OpenAI: batch via array input
  for (var i = 0; i < texts.length; i += BATCH_SIZE) {
    var batch = texts.slice(i, i + BATCH_SIZE);
    try {
      var res = await fetch(cfg.endpoint, {
        method: 'POST',
        headers: buildHeaders(cfg),
        body: JSON.stringify(buildRequestBody(cfg, batch)),
        signal: AbortSignal.timeout(TIMEOUT_MS * 2),
      });
      if (!res.ok) {
        process.stderr.write('[embedding] Batch API error ' + res.status + '\n');
        continue;
      }
      var data = await res.json();
      var vectors = parseResponse(data);
      for (var j = 0; j < vectors.length && i + j < texts.length; j++) {
        results[i + j] = vectors[j];
      }
    } catch (e) {
      process.stderr.write('[embedding] Batch failed: ' + e.message + '\n');
    }
  }

  return results;
}

module.exports = {
  isEmbeddingAvailable: isEmbeddingAvailable,
  getEmbedding: getEmbedding,
  getEmbeddings: getEmbeddings,
};
