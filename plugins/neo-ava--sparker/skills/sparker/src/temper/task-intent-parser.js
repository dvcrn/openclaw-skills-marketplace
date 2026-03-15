// Task Intent Parser — extracts structured search keys from user's task description.
// Runs BEFORE TF-IDF similarity to dramatically improve Spark recall.
//
// DESIGN: During user interaction, ONLY uses zero-cost rule-based parsing.
// The Agent's own LLM call (the one generating the reply) already understands
// the task — SKILL.md instructs the Agent to pass intent tags to the search
// command. LLM-based parsing is reserved for background/digest contexts only.

var { callLLM } = require('../core/openclaw-config');

var INTENT_PROMPT = [
  'Extract structured search tags from the user task description.',
  'Return ONLY a JSON object with these fields (omit unknown):',
  '  domain, sub_domain, task_phase, objective, implicit_dimensions',
  'Example input: "帮我写一段吸引观众停留的开头"',
  'Example output: {"domain":"直播策划","sub_domain":"开场策略","task_phase":"pre_stream","objective":"提升观众停留","implicit_dimensions":["hook_strategy","pacing"]}',
  'Keep values concise (2-6 Chinese characters per field). Return valid JSON only.',
].join('\n');

// Lightweight LLM call — a few dozen output tokens at most
async function parseIntentWithLLM(taskDescription) {
  try {
    var result = await callLLM({
      messages: [
        { role: 'system', content: INTENT_PROMPT },
        { role: 'user', content: taskDescription },
      ],
      max_tokens: 120,
      temperature: 0,
    });
    var text = (result && (result.content || result.text || result)) || '';
    if (typeof text !== 'string') text = JSON.stringify(text);
    var jsonMatch = text.match(/\{[\s\S]*\}/);
    if (jsonMatch) return JSON.parse(jsonMatch[0]);
  } catch (e) { /* LLM unavailable — fall through to rule-based */ }
  return null;
}

// Rule-based fallback: keyword → domain/sub_domain mapping
var KEYWORD_RULES = [
  { keywords: ['直播', '开场', '开播', '暖场'], domain: '直播策划', sub_domain: '开场策略' },
  { keywords: ['直播', '互动', '弹幕', '点赞'], domain: '直播策划', sub_domain: '互动策略' },
  { keywords: ['直播', '选品', '品类', '排品'], domain: '直播策划', sub_domain: '选品策略' },
  { keywords: ['标题', '封面', '缩略图'], domain: '内容运营', sub_domain: '标题策略' },
  { keywords: ['短剧', '剧本', '分镜'], domain: '短剧制作', sub_domain: '剧本创作' },
  { keywords: ['报告', '分析', '数据'], domain: '数据分析', sub_domain: '报告撰写' },
  { keywords: ['文案', '文章', '推文'], domain: '内容创作', sub_domain: '文案撰写' },
  { keywords: ['代码', '编程', '函数', '接口'], domain: '软件开发', sub_domain: '代码编写' },
];

function parseIntentByRules(taskDescription) {
  var text = (taskDescription || '').toLowerCase();
  for (var i = 0; i < KEYWORD_RULES.length; i++) {
    var rule = KEYWORD_RULES[i];
    var matchCount = 0;
    for (var j = 0; j < rule.keywords.length; j++) {
      if (text.indexOf(rule.keywords[j]) >= 0) matchCount++;
    }
    if (matchCount >= 1) {
      return { domain: rule.domain, sub_domain: rule.sub_domain };
    }
  }
  return null;
}

// Match intent tags against a spark's context_envelope
function matchIntentToEnvelope(intent, spark) {
  if (!intent || !spark) return 0;
  var envelope = (spark.card && spark.card.context_envelope) || {};
  var sparkDomain = spark.domain || envelope.domain || '';
  var score = 0;
  var checks = 0;

  if (intent.domain) {
    checks++;
    if (sparkDomain.indexOf(intent.domain) >= 0 || (envelope.domain || '').indexOf(intent.domain) >= 0) score++;
  }
  if (intent.sub_domain) {
    checks++;
    var sd = envelope.sub_domain || sparkDomain.split('.')[1] || '';
    if (sd.indexOf(intent.sub_domain) >= 0 || sparkDomain.indexOf(intent.sub_domain) >= 0) score++;
  }
  if (intent.task_phase) {
    checks++;
    if ((envelope.task_phase || '') === intent.task_phase) score++;
  }
  if (intent.objective) {
    checks++;
    var heuristic = (spark.card && spark.card.heuristic) || spark.content || '';
    if (heuristic.indexOf(intent.objective) >= 0) score += 0.5;
  }

  return checks > 0 ? score / checks : 0;
}

// Main entry: parse task → return intent + pre-filter function.
// By default uses rules only (zero LLM cost, no latency).
// Set opts.useLLM=true explicitly for background/digest contexts.
// Set opts.intent to pass pre-parsed intent from Agent's own LLM call.
async function parseTaskIntent(taskDescription, opts) {
  var o = opts || {};

  // Fast path: Agent already parsed intent in its own LLM call and passes it
  if (o.intent) {
    return { intent: o.intent, raw_query: taskDescription, method: 'agent_passthrough' };
  }

  var intent = null;

  // Only call LLM when explicitly requested (background/digest contexts)
  if (o.useLLM === true) {
    intent = await parseIntentWithLLM(taskDescription);
  }
  if (!intent) {
    intent = parseIntentByRules(taskDescription);
  }

  return {
    intent: intent,
    raw_query: taskDescription,
    method: intent ? (o.useLLM ? 'llm' : 'rules') : 'none',
  };
}

// Pre-filter candidates using intent matching; boost matching ones
function boostByIntent(candidates, intent, boostWeight) {
  if (!intent) return candidates;
  var weight = typeof boostWeight === 'number' ? boostWeight : 0.3;

  return candidates.map(function (c) {
    var intentScore = matchIntentToEnvelope(intent, c);
    return {
      item: c,
      intentScore: intentScore,
      intentBoost: intentScore * weight,
    };
  });
}

module.exports = {
  parseTaskIntent,
  parseIntentWithLLM,
  parseIntentByRules,
  matchIntentToEnvelope,
  boostByIntent,
  KEYWORD_RULES,
};
