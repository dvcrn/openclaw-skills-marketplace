// Promoter — synthesizes groups of related RawSparks into RefinedSparks.
// Called by digest Step 4 to merge domain-grouped raw knowledge into
// consolidated, higher-confidence refined entries.

var { generateId, computeAssetId, STP_SCHEMA_VERSION } = require('../core/asset-id');
var { createCredibility, computeComposite } = require('../core/credibility');
var { appendRefinedSpark } = require('../core/storage');
var { mergeSixDimensions } = require('../core/spark-card-schema');

var MIN_GROUP_SIZE = 1;

function groupBySubDomain(sparks) {
  var groups = {};
  for (var i = 0; i < sparks.length; i++) {
    var s = sparks[i];
    var domain = s.domain || 'general';
    if (!groups[domain]) groups[domain] = [];
    groups[domain].push(s);
  }
  return groups;
}

// Derive contributor role from raw spark source — pure rule, no LLM
function deriveContributorRole(spark) {
  var ctype = spark.contributor ? spark.contributor.type : 'unknown';
  if (ctype === 'agent') return 'extractor';
  var source = spark.source || spark.extraction_method || '';
  switch (source) {
    case 'human_teaching': return 'practitioner';
    case 'human_feedback': case 'human_choice': return 'reviewer';
    case 'task_negotiation': return 'collaborator';
    case 'iterative_refinement': return 'refiner';
    case 'micro_probe': return 'informant';
    case 'post_task': case 'self_diagnosis': return 'analyst';
    default: return 'contributor';
  }
}

// Derive contributor focus from the raw sparks they contributed.
// Sources: explicit contributor.focus, context_envelope.extra values, sub_domain
function deriveContributorFocus(contributorSparks, groupDomain) {
  var focusSet = {};
  for (var i = 0; i < contributorSparks.length; i++) {
    var spark = contributorSparks[i];
    // 1) Explicit focus from extraction
    if (spark.contributor && Array.isArray(spark.contributor.focus)) {
      for (var fi = 0; fi < spark.contributor.focus.length; fi++) {
        focusSet[spark.contributor.focus[fi]] = (focusSet[spark.contributor.focus[fi]] || 0) + 3;
      }
    }
    // 2) From context_envelope.extra — reveals what aspect the contributor cares about
    var ce = (spark.card || {}).context_envelope || {};
    if (ce.extra && typeof ce.extra === 'object') {
      for (var ek in ce.extra) {
        var val = ce.extra[ek];
        if (typeof val === 'string' && val.length > 0 && val.length < 30) {
          focusSet[val] = (focusSet[val] || 0) + 1;
        }
      }
    }
    // 3) Sub-domain that differs from the group domain — indicates specialization
    if (ce.sub_domain && ce.sub_domain !== groupDomain) {
      focusSet[ce.sub_domain] = (focusSet[ce.sub_domain] || 0) + 1;
    }
    // 4) From preference_dimensions — explicit priorities
    var prefs = (spark.card || {}).preference_dimensions || [];
    for (var pi = 0; pi < prefs.length; pi++) {
      var pref = prefs[pi];
      var label = typeof pref === 'string' ? pref : (pref.name || pref.dimension || '');
      if (label) focusSet[label] = (focusSet[label] || 0) + 2;
    }
  }
  // Sort by weight, return top focus areas
  var entries = Object.keys(focusSet);
  if (entries.length === 0) return [];
  entries.sort(function (a, b) { return focusSet[b] - focusSet[a]; });
  return entries.slice(0, 3);
}

// Build applicable_when from context_envelope — these fields answer
// "面向谁/什么情况下" without overlapping with do_list/rules (which answer "怎么做")
function deriveApplicableWhen(contextEnvelope, allBoundaries) {
  var conditions = [];

  // From boundary_conditions with positive effects
  for (var i = 0; i < allBoundaries.length; i++) {
    var b = allBoundaries[i];
    if (b.effect === 'apply' || b.effect === 'best_practice' || b.effect === 'recommended') {
      var text = b.condition || b.reason;
      if (text) conditions.push(text);
    }
  }

  // From context_envelope — only fields that add WHO/WHEN context (not WHAT)
  if (!contextEnvelope) return conditions;
  if (contextEnvelope.audience_type) {
    conditions.push('面向' + contextEnvelope.audience_type);
  }
  if (contextEnvelope.task_phase) {
    conditions.push(contextEnvelope.task_phase + '阶段');
  }
  if (contextEnvelope.experience_level) {
    conditions.push('适合' + contextEnvelope.experience_level + '水平');
  }
  if (Array.isArray(contextEnvelope.prerequisites) && contextEnvelope.prerequisites.length > 0) {
    conditions.push('前提: ' + contextEnvelope.prerequisites.join(', '));
  }
  if (contextEnvelope.platform && Array.isArray(contextEnvelope.platform) && contextEnvelope.platform.length > 0) {
    conditions.push('平台: ' + contextEnvelope.platform.join(', '));
  }

  return conditions;
}

function synthesizeRefinedSpark(group, domain) {
  var summaryParts = [];
  var allHeuristics = [];
  var doList = [];
  var dontList = [];
  var rules = [];
  var allBoundaries = [];
  var evidenceSparks = [];
  var totalConfidence = 0;
  var humanConfirmations = 0;
  var totalPractice = 0;
  var totalSuccess = 0;
  var contributors = {};

  for (var i = 0; i < group.length; i++) {
    var spark = group[i];
    evidenceSparks.push(spark.id);
    totalConfidence += spark.confidence || 0;
    totalPractice += spark.practice_count || 0;
    totalSuccess += spark.success_count || 0;

    if (spark.confirmation_status === 'human_confirmed') humanConfirmations++;

    var card = spark.card || {};
    if (card.heuristic) {
      allHeuristics.push(card.heuristic);
      summaryParts.push(card.heuristic);
    }

    if (card.heuristic_type === 'rule') {
      rules.push(card.heuristic);
      doList.push(card.heuristic);
    } else if (card.heuristic_type === 'boundary') {
      dontList.push(card.heuristic);
    }

    if (card.boundary_conditions) {
      allBoundaries = allBoundaries.concat(card.boundary_conditions);
    }

    var ctype = spark.contributor ? spark.contributor.type : 'unknown';
    var cid = spark.contributor ? spark.contributor.id : 'unknown';
    var ckey = ctype + ':' + cid;
    if (!contributors[ckey]) {
      contributors[ckey] = { type: ctype, id: cid, role: deriveContributorRole(spark), contributions: 0, weight: 1.0, _sparks: [] };
    }
    contributors[ckey].contributions++;
    contributors[ckey]._sparks.push(spark);
  }

  var avgConfidence = group.length > 0 ? totalConfidence / group.length : 0;

  var summaryText = domain + ' 经验 (' + group.length + '条): ' +
    allHeuristics.slice(0, 3).join('; ') +
    (allHeuristics.length > 3 ? '...' : '');

  var primaryHeuristic = allHeuristics.length > 0 ? allHeuristics[0] : summaryText;
  var contextEnvelope = {};
  for (var j = 0; j < group.length; j++) {
    var ce = (group[j].card || {}).context_envelope;
    if (ce) {
      for (var k in ce) {
        if (!contextEnvelope[k]) contextEnvelope[k] = ce[k];
      }
    }
  }

  var credibility = createCredibility(avgConfidence);
  credibility.internal.practice_count = totalPractice;
  credibility.internal.success_count = totalSuccess;
  credibility.internal.human_confirmations = humanConfirmations;

  var notApplicableWhen = [];
  for (var bi = 0; bi < allBoundaries.length; bi++) {
    if (allBoundaries[bi].effect === 'do_not_apply') {
      notApplicableWhen.push(allBoundaries[bi].condition || allBoundaries[bi].reason);
    }
  }

  // Derive task_type from domain hierarchy (e.g. "手冲咖啡.冲煮参数" → "冲煮参数")
  var domainParts = domain.split('.');
  var taskType = domainParts.length > 1 ? domainParts[domainParts.length - 1] : (contextEnvelope.sub_domain || null);

  // Derive applicable_when — answers "面向谁/什么场景" (no overlap with rules/do_list)
  var applicableWhen = deriveApplicableWhen(contextEnvelope, allBoundaries);

  // Build contributor chain with focus derivation
  var contributorChain = Object.keys(contributors).map(function (k) {
    var c = contributors[k];
    var focus = deriveContributorFocus(c._sparks, domain);
    var entry = { type: c.type, id: c.id, role: c.role, contributions: c.contributions, weight: c.weight };
    if (focus.length > 0) entry.focus = focus;
    return entry;
  });

  // Inject contributor focus into applicable_when as perspective signal
  for (var ci = 0; ci < contributorChain.length; ci++) {
    var cFocus = contributorChain[ci].focus;
    if (cFocus && cFocus.length > 0 && contributorChain[ci].type === 'human') {
      applicableWhen.push('来自注重' + cFocus.join('/') + '的实践者');
    }
  }

  // Derive expected_outcome from practice evidence (no LLM, pure stats)
  var expectedOutcome = '';
  if (totalPractice > 0) {
    var successRate = totalPractice > 0 ? Math.round(totalSuccess / totalPractice * 100) : 0;
    expectedOutcome = '实践验证: ' + totalPractice + '次应用, 成功率' + successRate + '%';
  }

  // Merge six-dimension fields from all sparks in the group
  var mergedDims = mergeSixDimensions(group);

  var refined = {
    type: 'RefinedSpark',
    schema_version: STP_SCHEMA_VERSION,
    id: generateId('refined_' + domain.replace(/[^a-zA-Z0-9_]/g, '_')),
    domain: domain,
    task_type: taskType,

    // ── Core Layer: six dimensions (merged from raw sparks) ──
    knowledge_type: mergedDims.knowledge_type,
    when: mergedDims.when,
    where: mergedDims.where,
    why: mergedDims.why,
    how: mergedDims.how,
    result: {
      expected_outcome: mergedDims.result.expected_outcome || expectedOutcome,
      practice_count: totalPractice,
      success_rate: totalPractice > 0 ? totalSuccess / totalPractice : null,
      confidence: parseFloat(avgConfidence.toFixed(2)),
      feedback_log: mergedDims.result.feedback_log,
    },
    not: mergedDims.not,

    // ── Compatibility Layer (auto-generated) ──
    summary: mergedDims.when.trigger
      ? (mergedDims.when.trigger + ' → ' + mergedDims.how.summary)
      : summaryText,
    card: {
      heuristic: primaryHeuristic,
      heuristics: allHeuristics,
      heuristic_type: rules.length >= allHeuristics.length / 2 ? 'rule' : 'pattern',
      context_envelope: contextEnvelope,
      boundary_conditions: allBoundaries,
      preference_dimensions: [],
      evidence: {
        practice_count: totalPractice,
        success_rate: totalPractice > 0 ? totalSuccess / totalPractice : null,
        last_practiced: null,
        notable_cases: [],
        context_diversity: 0,
      },
    },
    insight: {
      do_list: doList.slice(0, 5),
      dont_list: dontList.slice(0, 5),
      rules: rules,
      expected_outcome: mergedDims.result.expected_outcome || expectedOutcome,
      confidence_note: 'Synthesized from ' + group.length + ' raw sparks with avg confidence ' + avgConfidence.toFixed(2),
    },
    applicable_when: applicableWhen,
    not_applicable_when: notApplicableWhen,
    evidence_sparks: evidenceSparks,
    contributor_chain: contributorChain,
    credibility: credibility,
    practice_results: [],
    visibility: 'private',
    relations: [],
    status: 'active',
    created_at: new Date().toISOString(),
    promoted_at: new Date().toISOString(),
  };

  refined.asset_id = computeAssetId(refined);
  return refined;
}

function promoteEligibleRawSparks(activeSparks, practiceRecords) {
  var groups = groupBySubDomain(activeSparks);
  var promoted = 0;
  var refinedSparks = [];

  for (var domain in groups) {
    var group = groups[domain];
    if (group.length < MIN_GROUP_SIZE) continue;

    var refined = synthesizeRefinedSpark(group, domain);
    appendRefinedSpark(refined);
    refinedSparks.push(refined);
    promoted++;
  }

  return {
    promoted: promoted,
    refined_sparks: refinedSparks,
  };
}

module.exports = {
  promoteEligibleRawSparks: promoteEligibleRawSparks,
  synthesizeRefinedSpark: synthesizeRefinedSpark,
};
