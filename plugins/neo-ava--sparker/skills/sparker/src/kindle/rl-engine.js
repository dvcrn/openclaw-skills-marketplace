// RL (Reinforcement Learning from Human Feedback) engine.
// Decides when to present multi-option choices and infers preferences from selections.

const { readJson, writeJson, resolvePath } = require('../core/storage');

function getRlStatePath() {
  return resolvePath('rl_state.json');
}

function readRlState() {
  return readJson(getRlStatePath(), {
    last_rl_timestamp: null,
    rl_count_today: 0,
    rl_date: null,
    total_rl_sessions: 0,
    preferences: {},
    patience_score: 0,
  });
}

function writeRlState(state) {
  writeJson(getRlStatePath(), state);
}

function getRlConfig() {
  var freq = process.env.STP_RL_FREQUENCY || process.env.STP_LEARNER_STRATEGY || 'balanced';
  return {
    frequency: freq,
    max_per_day: Number(process.env.STP_MAX_RL_PER_DAY) || 3,
    cooldown_minutes: Number(process.env.STP_RL_COOLDOWN_MINUTES) || 60,
  };
}

// RL trigger scoring function — determines whether to present multi-option choice.
// Now capability-map aware: learns more aggressively in blind_spot/learning domains
// and eases off in proficient/mastered domains.
function computeRlScore(params) {
  var p = params || {};
  var score = 0;

  if (p.is_first_time_task_type) score += 0.5;
  if (p.recent_correction_exists) score += 0.3;
  if (p.multiple_valid_approaches) score += 0.4;
  if (p.domain_preference_sparse) score += 0.2;

  // Adaptive boost from capability map
  if (p.domain) {
    try {
      var { getDomainStrategy } = require('../core/adaptive-strategy');
      var strategy = getDomainStrategy(p.domain);
      score += strategy.rl_boost;
    } catch (e) { /* ignore */ }
  }

  var config = getRlConfig();
  var state = readRlState();
  var now = Date.now();
  var today = new Date().toISOString().slice(0, 10);

  if (state.rl_date !== today) {
    state.rl_count_today = 0;
    state.rl_date = today;
  }

  // Use adaptive max_per_day if domain strategy provides one
  var effectiveMaxPerDay = config.max_per_day;
  if (p.domain) {
    try {
      var { getDomainStrategy: gds } = require('../core/adaptive-strategy');
      effectiveMaxPerDay = gds(p.domain).max_rl_per_day;
    } catch (e) { /* ignore */ }
  }

  if (state.rl_count_today >= effectiveMaxPerDay) score -= 1.0;

  if (state.last_rl_timestamp) {
    var elapsed = (now - new Date(state.last_rl_timestamp).getTime()) / 60000;
    if (elapsed < config.cooldown_minutes) score -= 0.5;
  }

  if (p.user_busy_signal) score -= 0.3;

  // Patience-based budget adjustment
  var patience = state.patience_score || 0;
  if (patience >= 3) score += 0.15;
  else if (patience <= -3) score -= 0.3;
  else if (patience <= -6) score -= 0.8;

  if (config.frequency === 'intensive' || config.frequency === 'aggressive') score += 0.2;
  if (config.frequency === 'consolidate' || config.frequency === 'conservative') score -= 0.2;
  if (config.frequency === 'manual') score -= 2.0;

  return score;
}

function shouldTriggerRl(params) {
  return computeRlScore(params) > 0.6;
}

function recordRlTriggered() {
  var state = readRlState();
  var today = new Date().toISOString().slice(0, 10);
  if (state.rl_date !== today) {
    state.rl_count_today = 0;
    state.rl_date = today;
  }
  state.rl_count_today += 1;
  state.last_rl_timestamp = new Date().toISOString();
  state.total_rl_sessions += 1;
  writeRlState(state);
}

// Infer preferences from user's choice among options
function inferPreferences(options, chosenIndex, domain) {
  if (!Array.isArray(options) || chosenIndex < 0 || chosenIndex >= options.length) return null;
  var chosen = options[chosenIndex];
  var rejected = options.filter((_, i) => i !== chosenIndex);

  var state = readRlState();
  if (!state.preferences[domain]) state.preferences[domain] = {};

  var inference = {
    chosen_features: chosen.features || chosen.label || String(chosen),
    rejected_features: rejected.map(r => r.features || r.label || String(r)),
    domain: domain,
    inferred_at: new Date().toISOString(),
  };

  if (!state.preferences[domain].history) state.preferences[domain].history = [];
  state.preferences[domain].history.push(inference);
  if (state.preferences[domain].history.length > 50) {
    state.preferences[domain].history = state.preferences[domain].history.slice(-50);
  }

  writeRlState(state);
  return inference;
}

function getPreferences(domain) {
  var state = readRlState();
  return state.preferences[domain] || null;
}

// Update patience score based on user's response to probes/questions.
// response_type:
//   'detailed'  → +1 (user is willing to teach)
//   'brief'     →  0 (neutral)
//   'ignored'   → -2 (user skipped the question)
//   'rejected'  → -5 (user explicitly said "don't ask me")
function updatePatience(response_type) {
  var deltas = { detailed: 1, brief: 0, ignored: -2, rejected: -5 };
  var delta = deltas[response_type];
  if (delta == null) return;

  var state = readRlState();
  state.patience_score = Math.max(-10, Math.min(10, (state.patience_score || 0) + delta));
  writeRlState(state);
  return state.patience_score;
}

function getPatience() {
  var state = readRlState();
  return state.patience_score || 0;
}

module.exports = {
  readRlState,
  getRlConfig,
  computeRlScore,
  shouldTriggerRl,
  recordRlTriggered,
  inferPreferences,
  getPreferences,
  updatePatience,
  getPatience,
};
