// Spark Card Schema — unified structure across the full lifecycle:
//   RawSpark.card → RefinedSpark.card → Ember.card → Gene
//
// Design principles:
// 1. RawSpark.card = single experience capture
// 2. RefinedSpark.card = merged synthesis of multiple RawSpark.cards
// 3. Ember.card = sanitized RefinedSpark.card (PII stripped, professional context retained)
// 4. Gene = format-converted from Ember.card (semantics preserved)

function createSparkCard(params) {
  var p = params || {};
  return {
    heuristic: p.heuristic || '',
    heuristics: p.heuristics || [],
    heuristic_type: p.heuristic_type || 'rule',

    context_envelope: Object.assign({
      domain: '',
      sub_domain: '',
      platform: [],
      audience_type: '',
      task_phase: '',
      prerequisites: [],
      contributor_role: '',
      contributor_industry: '',
      experience_level: '',
      extra: {},
    }, p.context_envelope || {}),

    boundary_conditions: (p.boundary_conditions || []).map(normalizeBoundary),

    preference_dimensions: p.preference_dimensions || [],

    evidence: Object.assign({
      practice_count: 0,
      success_rate: null,
      last_practiced: null,
      notable_cases: [],
      context_diversity: 0,
    }, p.evidence || {}),
  };
}

function normalizeBoundary(b) {
  if (typeof b === 'string') {
    return { condition: b, effect: 'do_not_apply', reason: '' };
  }
  return {
    condition: b.condition || '',
    effect: b.effect || 'do_not_apply',
    reason: b.reason || '',
  };
}

// Merge multiple RawSpark cards into a single RefinedSpark card.
// context_envelope → intersection (strictest common context)
// boundary_conditions → union (all known exceptions, deduplicated)
// heuristics → all raw heuristics collected; caller may LLM-summarize
// preference_dimensions → union, deduplicated
// evidence → aggregated from practice records
function mergeCards(cards, practiceStats) {
  if (!cards || cards.length === 0) return createSparkCard({});

  var allHeuristics = [];
  var allBoundaries = [];
  var allPrefDims = [];
  var allPlatforms = [];
  var allPrereqs = [];
  var envelopes = [];

  for (var i = 0; i < cards.length; i++) {
    var c = cards[i];
    if (!c) continue;
    if (c.heuristic) allHeuristics.push(c.heuristic);
    if (c.heuristics) allHeuristics = allHeuristics.concat(c.heuristics);
    if (c.boundary_conditions) {
      allBoundaries = allBoundaries.concat(c.boundary_conditions.map(normalizeBoundary));
    }
    if (c.preference_dimensions) {
      allPrefDims = allPrefDims.concat(c.preference_dimensions);
    }
    if (c.context_envelope) envelopes.push(c.context_envelope);
  }

  var mergedEnvelope = intersectEnvelopes(envelopes);

  var boundarySet = {};
  var dedupedBoundaries = [];
  for (var bi = 0; bi < allBoundaries.length; bi++) {
    var key = (allBoundaries[bi].condition || '').toLowerCase().trim();
    if (key && !boundarySet[key]) {
      boundarySet[key] = true;
      dedupedBoundaries.push(allBoundaries[bi]);
    }
  }

  var dimSet = {};
  var dedupedDims = allPrefDims.filter(function (d) {
    if (!d || dimSet[d]) return false;
    dimSet[d] = true;
    return true;
  });

  var dedupedHeuristics = [];
  var hSet = {};
  for (var hi = 0; hi < allHeuristics.length; hi++) {
    var hKey = (allHeuristics[hi] || '').toLowerCase().trim();
    if (hKey && !hSet[hKey]) {
      hSet[hKey] = true;
      dedupedHeuristics.push(allHeuristics[hi]);
    }
  }

  var ps = practiceStats || {};
  return createSparkCard({
    heuristic: dedupedHeuristics[0] || '',
    heuristics: dedupedHeuristics,
    heuristic_type: detectDominantType(cards),
    context_envelope: mergedEnvelope,
    boundary_conditions: dedupedBoundaries,
    preference_dimensions: dedupedDims,
    evidence: {
      practice_count: ps.practice_count || 0,
      success_rate: ps.success_rate != null ? ps.success_rate : null,
      last_practiced: ps.last_practiced || null,
      notable_cases: ps.notable_cases || [],
      context_diversity: ps.context_diversity || 0,
    },
  });
}

function intersectEnvelopes(envelopes) {
  if (envelopes.length === 0) return {};
  if (envelopes.length === 1) return Object.assign({}, envelopes[0]);

  var result = {};

  var stringFields = ['domain', 'sub_domain', 'audience_type', 'task_phase',
    'contributor_role', 'contributor_industry', 'experience_level'];
  for (var fi = 0; fi < stringFields.length; fi++) {
    var field = stringFields[fi];
    var values = envelopes.map(function (e) { return e[field] || ''; }).filter(Boolean);
    if (values.length === 0) continue;
    var counts = {};
    for (var vi = 0; vi < values.length; vi++) {
      counts[values[vi]] = (counts[values[vi]] || 0) + 1;
    }
    var best = Object.keys(counts).sort(function (a, b) { return counts[b] - counts[a]; })[0];
    if (counts[best] >= Math.ceil(envelopes.length * 0.5)) {
      result[field] = best;
    }
  }

  var allPlatforms = {};
  for (var pi = 0; pi < envelopes.length; pi++) {
    var plats = envelopes[pi].platform || [];
    for (var pj = 0; pj < plats.length; pj++) {
      allPlatforms[plats[pj]] = (allPlatforms[plats[pj]] || 0) + 1;
    }
  }
  result.platform = Object.keys(allPlatforms).filter(function (k) {
    return allPlatforms[k] > envelopes.length / 2;
  });

  result.extra = {};
  return result;
}

function detectDominantType(cards) {
  var counts = {};
  for (var i = 0; i < cards.length; i++) {
    var t = (cards[i] && cards[i].heuristic_type) || 'rule';
    counts[t] = (counts[t] || 0) + 1;
  }
  var best = 'rule';
  var bestCount = 0;
  for (var k in counts) {
    if (counts[k] > bestCount) { best = k; bestCount = counts[k]; }
  }
  return best;
}

// Merge six-dimension fields from multiple sparks.
// Used by promoter to aggregate RawSparks into a RefinedSpark.
function mergeSixDimensions(sparks) {
  var allTriggers = [];
  var allConditions = {};
  var bestTriggerSpark = null;
  var bestTriggerConf = -1;
  var allWhys = [];
  var allSummaries = [];
  var allDetails = [];
  var allOutcomes = [];
  var allFeedback = [];
  var allNots = [];
  var notSet = {};
  var whereDomain = '';
  var whereSubDomain = '';
  var whereScenarios = [];
  var whereAudiences = [];
  var knowledgeTypeCounts = {};

  for (var i = 0; i < sparks.length; i++) {
    var s = sparks[i];

    // WHEN: collect triggers, pick highest-confidence one
    if (s.when && s.when.trigger) {
      allTriggers.push(s.when.trigger);
      var conf = s.confidence || 0;
      if (conf > bestTriggerConf) {
        bestTriggerConf = conf;
        bestTriggerSpark = s;
      }
      if (Array.isArray(s.when.conditions)) {
        for (var ci = 0; ci < s.when.conditions.length; ci++) {
          allConditions[s.when.conditions[ci]] = true;
        }
      }
    }

    // WHERE: collect, pick most frequent domain
    if (s.where) {
      if (s.where.domain) whereDomain = whereDomain || s.where.domain;
      if (s.where.sub_domain) whereSubDomain = whereSubDomain || s.where.sub_domain;
      if (s.where.scenario) whereScenarios.push(s.where.scenario);
      if (s.where.audience) whereAudiences.push(s.where.audience);
    }

    // WHY: collect all
    if (s.why) allWhys.push(s.why);

    // HOW: collect summaries and details
    if (s.how) {
      if (s.how.summary) allSummaries.push(s.how.summary);
      if (s.how.detail) allDetails.push(s.how.detail);
    }

    // RESULT: collect outcomes and feedback
    if (s.result) {
      if (s.result.expected_outcome) allOutcomes.push(s.result.expected_outcome);
      if (Array.isArray(s.result.feedback_log)) {
        allFeedback = allFeedback.concat(s.result.feedback_log);
      }
    }

    // NOT: union with dedup
    if (Array.isArray(s.not)) {
      for (var ni = 0; ni < s.not.length; ni++) {
        var nKey = (s.not[ni].condition || '').toLowerCase().trim();
        if (nKey && !notSet[nKey]) {
          notSet[nKey] = true;
          allNots.push(s.not[ni]);
        }
      }
    }

    // knowledge_type: majority vote
    var kt = s.knowledge_type || 'rule';
    knowledgeTypeCounts[kt] = (knowledgeTypeCounts[kt] || 0) + 1;
  }

  // Pick dominant knowledge_type
  var bestKt = 'rule';
  var bestKtCount = 0;
  for (var ktk in knowledgeTypeCounts) {
    if (knowledgeTypeCounts[ktk] > bestKtCount) {
      bestKt = ktk;
      bestKtCount = knowledgeTypeCounts[ktk];
    }
  }

  // Pick best trigger
  var mergedTrigger = bestTriggerSpark ? bestTriggerSpark.when.trigger : (allTriggers[0] || '');

  // Pick best summary (from highest-confidence spark)
  var mergedSummary = bestTriggerSpark && bestTriggerSpark.how ? bestTriggerSpark.how.summary : (allSummaries[0] || '');

  // Merge details: concatenate unique ones
  var detailSet = {};
  var mergedDetails = [];
  for (var di = 0; di < allDetails.length; di++) {
    var dKey = allDetails[di].trim().slice(0, 50);
    if (!detailSet[dKey]) {
      detailSet[dKey] = true;
      mergedDetails.push(allDetails[di]);
    }
  }

  // Dedup scenarios and audiences
  var scenarioSet = {};
  var uniqueScenarios = whereScenarios.filter(function(s) {
    if (!s || scenarioSet[s]) return false;
    scenarioSet[s] = true;
    return true;
  });
  var audienceSet = {};
  var uniqueAudiences = whereAudiences.filter(function(a) {
    if (!a || audienceSet[a]) return false;
    audienceSet[a] = true;
    return true;
  });

  return {
    knowledge_type: bestKt,
    when: {
      trigger: mergedTrigger,
      conditions: Object.keys(allConditions),
    },
    where: {
      domain: whereDomain,
      sub_domain: whereSubDomain,
      scenario: uniqueScenarios.join('；'),
      audience: uniqueAudiences.join('、'),
    },
    why: allWhys.join('\n\n'),
    how: {
      summary: mergedSummary,
      detail: mergedDetails.join('\n\n'),
    },
    result: {
      expected_outcome: allOutcomes.join('；'),
      feedback_log: allFeedback,
    },
    not: allNots,
  };
}

module.exports = {
  createSparkCard,
  mergeCards,
  mergeSixDimensions,
  normalizeBoundary,
  intersectEnvelopes,
};
