// Auto-detect and reuse OpenClaw's model provider configuration.
// Falls back to STP_* / SPARK_* env vars if openclaw config not found.
//
// This allows sparker to work out-of-the-box when distributed to other
// openclaw users — no extra env vars needed.

var fs = require('fs');
var path = require('path');

var _cache = null;

function loadOpenClawConfig() {
  if (_cache) return _cache;

  var home = process.env.HOME || process.env.USERPROFILE || '/root';
  var modelsPath = path.join(home, '.openclaw', 'agents', 'main', 'agent', 'models.json');
  var mainPath = path.join(home, '.openclaw', 'openclaw.json');

  var providers = null;
  var primaryModel = null;

  // Read main config for primary model setting
  try {
    var mainRaw = fs.readFileSync(mainPath, 'utf8');
    var mainCfg = JSON.parse(mainRaw);
    if (mainCfg.agents && mainCfg.agents.defaults && mainCfg.agents.defaults.model) {
      primaryModel = mainCfg.agents.defaults.model.primary || null;
    }
    if (mainCfg.models && mainCfg.models.providers) {
      providers = mainCfg.models.providers;
    }
  } catch (e) { /* skip */ }

  // Models.json has per-provider apiKeys — merge into providers
  try {
    var modRaw = fs.readFileSync(modelsPath, 'utf8');
    var modCfg = JSON.parse(modRaw);
    if (modCfg.providers) {
      if (!providers) providers = {};
      for (var name in modCfg.providers) {
        if (!providers[name]) providers[name] = {};
        Object.assign(providers[name], modCfg.providers[name]);
      }
    }
  } catch (e) { /* skip */ }

  if (!providers) {
    _cache = { providers: {}, primaryModel: null };
    return _cache;
  }

  _cache = { providers: providers, primaryModel: primaryModel };
  return _cache;
}

// Resolve LLM config: env vars > openclaw config
function resolveLLMConfig() {
  var endpoint = process.env.STP_FORGE_LLM_ENDPOINT
    || process.env.SPARK_PROMOTE_LLM_ENDPOINT
    || process.env.LLM_ENDPOINT;
  var apiKey = process.env.STP_FORGE_LLM_API_KEY
    || process.env.SPARK_PROMOTE_LLM_API_KEY
    || process.env.LLM_API_KEY;
  var model = process.env.STP_FORGE_LLM_MODEL
    || process.env.SPARK_PROMOTE_LLM_MODEL
    || process.env.LLM_MODEL;

  if (endpoint) {
    return { baseUrl: endpoint, apiKey: apiKey || '', model: model || 'gpt-4o-mini', api: 'openai' };
  }

  var cfg = loadOpenClawConfig();

  // Prefer the primary model's provider
  var primaryProvider = null;
  if (cfg.primaryModel) {
    var parts = cfg.primaryModel.split('/');
    if (parts.length >= 2) primaryProvider = parts[0];
  }

  var names = Object.keys(cfg.providers);
  if (primaryProvider && names.indexOf(primaryProvider) >= 0) {
    names = [primaryProvider].concat(names.filter(function (n) { return n !== primaryProvider; }));
  }

  for (var i = 0; i < names.length; i++) {
    var p = cfg.providers[names[i]];
    if (p.baseUrl && p.apiKey) {
      var modelId = (p.models && p.models.length > 0) ? p.models[0].id : 'default';
      return {
        baseUrl: p.baseUrl,
        apiKey: p.apiKey,
        model: modelId,
        api: p.api || 'openai',
        provider: names[i],
      };
    }
  }
  return null;
}

// Resolve Embedding config: env vars > openclaw config
function resolveEmbeddingConfig() {
  var endpoint = process.env.STP_EMBEDDING_ENDPOINT
    || process.env.SPARK_EMBEDDING_ENDPOINT;
  var apiKey = process.env.STP_EMBEDDING_API_KEY
    || process.env.SPARK_EMBEDDING_API_KEY;
  var model = process.env.STP_EMBEDDING_MODEL;

  if (endpoint) {
    return { endpoint: endpoint, apiKey: apiKey || '', model: model || 'default' };
  }

  var cfg = loadOpenClawConfig();
  var names = Object.keys(cfg.providers);

  // Prefer the primary provider for embeddings too
  var primaryProvider = null;
  if (cfg.primaryModel) {
    var parts = cfg.primaryModel.split('/');
    if (parts.length >= 2) primaryProvider = parts[0];
  }
  if (primaryProvider && names.indexOf(primaryProvider) >= 0) {
    names = [primaryProvider].concat(names.filter(function (n) { return n !== primaryProvider; }));
  }

  // Prefer doubao/volcengine for embeddings (has native embedding models)
  var ordered = names.slice();
  var doubaoIdx = ordered.indexOf('doubao');
  if (doubaoIdx > 0) {
    ordered.splice(doubaoIdx, 1);
    ordered.unshift('doubao');
  }

  for (var i = 0; i < ordered.length; i++) {
    var p = cfg.providers[ordered[i]];
    if (p.baseUrl && p.apiKey) {
      var base = p.baseUrl.replace(/\/$/, '');

      // Doubao / Volcengine ARK: use multimodal embedding endpoint
      if (base.indexOf('volces.com') >= 0 || ordered[i] === 'doubao') {
        base = base.replace(/\/api\/v3$/, '').replace(/\/v1$/, '');
        return {
          endpoint: base + '/api/v3/embeddings/multimodal',
          apiKey: p.apiKey,
          model: process.env.STP_EMBEDDING_MODEL || 'doubao-embedding-vision-251215',
          provider: ordered[i],
          derived: true,
        };
      }

      base = base.replace(/\/anthropic$/, '').replace(/\/v1$/, '');
      return {
        endpoint: base + '/v1/embeddings',
        apiKey: p.apiKey,
        model: 'default',
        provider: ordered[i],
        derived: true,
      };
    }
  }
  return null;
}

// Generic LLM call that handles both OpenAI and Anthropic formats
async function callLLM(prompt, opts) {
  var cfg = opts || resolveLLMConfig();
  if (!cfg) return null;

  var isAnthropic = cfg.api && cfg.api.indexOf('anthropic') >= 0;
  var url, headers, body;

  if (isAnthropic) {
    url = cfg.baseUrl.replace(/\/$/, '') + '/v1/messages';
    headers = {
      'Content-Type': 'application/json',
      'x-api-key': cfg.apiKey,
      'anthropic-version': '2023-06-01',
    };
    body = JSON.stringify({
      model: cfg.model,
      max_tokens: opts && opts.max_tokens || 2000,
      messages: [{ role: 'user', content: prompt }],
      temperature: opts && opts.temperature !== undefined ? opts.temperature : 0.3,
    });
  } else {
    url = cfg.baseUrl.replace(/\/$/, '');
    if (url.indexOf('/chat/completions') === -1) url += '/v1/chat/completions';
    headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + cfg.apiKey,
    };
    body = JSON.stringify({
      model: cfg.model,
      messages: [{ role: 'user', content: prompt }],
      temperature: opts && opts.temperature !== undefined ? opts.temperature : 0.3,
      max_tokens: opts && opts.max_tokens || 2000,
    });
  }

  try {
    var res = await fetch(url, {
      method: 'POST',
      headers: headers,
      body: body,
      signal: AbortSignal.timeout(60000),
    });
    var data = await res.json();

    if (isAnthropic) {
      var blocks = data.content || [];
      for (var i = 0; i < blocks.length; i++) {
        if (blocks[i].type === 'text') return blocks[i].text;
      }
      return null;
    } else {
      return data.choices && data.choices[0] && data.choices[0].message
        && data.choices[0].message.content;
    }
  } catch (e) {
    return null;
  }
}

module.exports = {
  loadOpenClawConfig,
  resolveLLMConfig,
  resolveEmbeddingConfig,
  callLLM,
};
