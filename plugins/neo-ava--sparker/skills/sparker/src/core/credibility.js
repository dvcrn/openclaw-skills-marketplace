// Dual-dimension credibility engine for STP.
// Internal (owner/agent) + External (community) + Composite + Trend.

const SOURCE_INITIAL_CONFIDENCE = {
  human_teaching: 0.50,
  iterative_refinement: 0.45,
  human_feedback: 0.40,
  task_negotiation: 0.35,
  human_choice: 0.30,
  agent_exchange: 0.25,
  web_exploration: 0.20,
  self_diagnosis: 0.20,
  post_task: 0.15,
};

const BOOST_RULES = {
  human_confirmed: 0.20,
  practice_accepted: 0.15,
  cross_validated: 0.10,
  refined_promotion: 0.10,
  practice_partial: 0.05,
};

const DECAY_RULES = {
  practice_rejected: -0.20,
  superseded: -0.15,
  inactive_per_period: -0.05,
};

function getInitialConfidence(source) {
  return SOURCE_INITIAL_CONFIDENCE[source] || 0.20;
}

function createInternalCredibility(initialScore) {
  return {
    score: typeof initialScore === 'number' ? initialScore : 0.5,
    practice_count: 0,
    success_count: 0,
    human_confirmations: 0,
    last_validated_at: null,
  };
}

function createExternalCredibility() {
  return {
    score: 0.5,
    citations: 0,
    upvotes: 0,
    downvotes: 0,
    weighted_upvotes: 0,
    weighted_downvotes: 0,
    unique_agents: 0,
    unique_domains: 0,
  };
}

function createCredibility(initialInternal) {
  return {
    internal: createInternalCredibility(initialInternal),
    external: createExternalCredibility(),
    composite: typeof initialInternal === 'number' ? initialInternal : 0.5,
    trend: 'stable',
  };
}

// Compute composite credibility with dynamic alpha
function computeComposite(internal, external) {
  var intScore = internal.score;
  var extScore = external.score;
  var citations = external.citations || 0;
  var alpha;
  if (citations < 3) {
    alpha = 1.0;
  } else if (citations <= 10) {
    alpha = 0.8 - (citations - 3) * (0.2 / 7);
  } else {
    alpha = 0.6;
  }
  return alpha * intScore + (1 - alpha) * extScore;
}

// Apply external score using Laplace smoothing
function computeExternalScore(external) {
  var wp = external.weighted_upvotes || external.upvotes || 0;
  var wn = external.weighted_downvotes || external.downvotes || 0;
  return (wp + 1) / (wp + wn + 2);
}

// Update internal credibility after a practice result.
// impactWeight (0-1): how much this Spark contributed to the task output.
//   hard_constraint → 1.0, soft_constraint → 0.6, preference_guide → 0.3,
//   background_reference → 0.1. Default 1.0 for backward compatibility.
function applyPracticeResult(credibility, outcome, impactWeight) {
  var w = typeof impactWeight === 'number' ? impactWeight : 1.0;
  var internal = credibility.internal;
  internal.practice_count += 1;
  internal.last_validated_at = new Date().toISOString();

  if (outcome === 'accepted') {
    internal.success_count += 1;
    internal.score = Math.min(1.0, internal.score + BOOST_RULES.practice_accepted * w);
  } else if (outcome === 'rejected') {
    internal.score = Math.max(0.0, internal.score + DECAY_RULES.practice_rejected * w);
  } else if (outcome === 'partial') {
    internal.success_count += 0.5;
    internal.score = Math.min(1.0, internal.score + BOOST_RULES.practice_partial * w);
  }

  credibility.composite = computeComposite(credibility.internal, credibility.external);
  return credibility;
}

// Apply human confirmation boost
function applyHumanConfirmation(credibility) {
  credibility.internal.human_confirmations += 1;
  credibility.internal.score = Math.min(1.0, credibility.internal.score + BOOST_RULES.human_confirmed);
  credibility.internal.last_validated_at = new Date().toISOString();
  credibility.composite = computeComposite(credibility.internal, credibility.external);
  return credibility;
}

// Apply cross-validation boost
function applyCrossValidation(credibility) {
  credibility.internal.score = Math.min(1.0, credibility.internal.score + BOOST_RULES.cross_validated);
  credibility.composite = computeComposite(credibility.internal, credibility.external);
  return credibility;
}

// Apply time-based decay
function applyTimeDecay(credibility, ageDays, halfLifeDays) {
  if (!halfLifeDays || halfLifeDays <= 0) return credibility;
  var factor = Math.pow(0.5, ageDays / halfLifeDays);
  credibility.internal.score = credibility.internal.score * factor;
  credibility.composite = computeComposite(credibility.internal, credibility.external);
  return credibility;
}

// Apply inactive decay (for sparks not practiced within period)
function applyInactiveDecay(credibility) {
  credibility.internal.score = Math.max(0.0, credibility.internal.score + DECAY_RULES.inactive_per_period);
  credibility.composite = computeComposite(credibility.internal, credibility.external);
  return credibility;
}

// Apply external vote with reputation weighting
function applyExternalVote(credibility, voteType, voterReputation) {
  var rep = typeof voterReputation === 'number' ? voterReputation : 1.0;
  var baseCred = Number(process.env.STP_CRED_BOOST) || 0.05;
  var basePenalty = Number(process.env.STP_CRED_PENALTY) || 0.03;

  if (voteType === 'upvote') {
    credibility.external.upvotes += 1;
    credibility.external.weighted_upvotes += rep;
    credibility.external.citations += 1;
  } else if (voteType === 'downvote') {
    credibility.external.downvotes += 1;
    credibility.external.weighted_downvotes += rep;
  } else if (voteType === 'cite') {
    credibility.external.citations += 1;
  }

  credibility.external.score = computeExternalScore(credibility.external);
  credibility.composite = computeComposite(credibility.internal, credibility.external);
  return credibility;
}

// Compute trend from recent score history
function computeTrend(scoreHistory) {
  if (!scoreHistory || scoreHistory.length < 3) return 'stable';
  var n = scoreHistory.length;
  var sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0;
  for (var i = 0; i < n; i++) {
    sumX += i;
    sumY += scoreHistory[i];
    sumXY += i * scoreHistory[i];
    sumX2 += i * i;
  }
  var slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
  var meanY = sumY / n;
  var ssRes = 0;
  for (var j = 0; j < n; j++) {
    var predicted = meanY + slope * (j - (n - 1) / 2);
    ssRes += Math.pow(scoreHistory[j] - predicted, 2);
  }
  var variance = ssRes / n;

  if (variance > 0.02) return 'volatile';
  if (slope > 0.01) return 'rising';
  if (slope < -0.01) return 'declining';
  return 'stable';
}

// Check if spark meets refinement promotion threshold
function meetsRefinementThreshold(credibility, practiceCount) {
  var threshold = Number(process.env.STP_CONFIDENCE_THRESHOLD) || 0.60;
  var minPractice = Number(process.env.STP_MIN_PRACTICE_COUNT) || 2;
  var successRate = practiceCount > 0 ? (credibility.internal.success_count / practiceCount) : 0;
  return (
    credibility.internal.score >= threshold &&
    practiceCount >= minPractice &&
    successRate >= 0.60
  );
}

// Compute context diversity: ratio of unique contexts to total practices
function computeContextDiversity(practiceRecords, sparkId) {
  var relevant = practiceRecords.filter(function (p) { return p.spark_id === sparkId; });
  if (relevant.length === 0) return 0;
  var contexts = {};
  for (var i = 0; i < relevant.length; i++) {
    var ctx = relevant[i].context_snapshot;
    var key = ctx ? JSON.stringify({
      task_type: ctx.task_type || '',
      scenario: ctx.scenario || '',
      platform: (ctx.environment && ctx.environment.platform) || '',
    }) : 'no_context_' + i;
    contexts[key] = true;
  }
  return Object.keys(contexts).length / relevant.length;
}

// Apply diversity bonus to composite credibility
function applyDiversityBonus(composite, contextDiversity) {
  var beta = 0.15;
  return composite * (1 + beta * contextDiversity);
}

// Check if ember meets forge threshold (now includes diversity check)
function meetsForgeThreshold(credibility, contextDiversity) {
  var threshold = Number(process.env.STP_FORGE_THRESHOLD) || 0.85;
  var minCitations = Number(process.env.STP_FORGE_MIN_CITATIONS) || 8;
  var ext = credibility.external;
  var total = ext.upvotes + ext.downvotes;
  var ratio = total > 0 ? ext.weighted_upvotes / (ext.weighted_upvotes + ext.weighted_downvotes) : 0;

  var diversityOk = typeof contextDiversity === 'number' ? contextDiversity >= 0.40 : true;

  return (
    credibility.composite >= threshold &&
    ext.citations >= minCitations &&
    ratio >= 0.80 &&
    ext.unique_agents >= 5 &&
    diversityOk
  );
}

// Check if spark should be rejected
function shouldReject(credibility) {
  return credibility.internal.score <= 0.10;
}

module.exports = {
  SOURCE_INITIAL_CONFIDENCE,
  BOOST_RULES,
  DECAY_RULES,
  getInitialConfidence,
  createInternalCredibility,
  createExternalCredibility,
  createCredibility,
  computeComposite,
  computeExternalScore,
  applyPracticeResult,
  applyHumanConfirmation,
  applyCrossValidation,
  applyTimeDecay,
  applyInactiveDecay,
  applyExternalVote,
  computeTrend,
  meetsRefinementThreshold,
  meetsForgeThreshold,
  shouldReject,
  computeContextDiversity,
  applyDiversityBonus,
};
