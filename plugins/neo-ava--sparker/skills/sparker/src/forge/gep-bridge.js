// GEP bridge — bidirectional interop between STP and GEP.
// Forward: Ember -> Gene (via forge-engine)
// Reverse: Gene execution results -> Ember credibility updates

const { readEmbers, updateEmber } = require('../core/storage');

// Reverse channel: update ember credibility based on Gene execution results
function handleGeneExecutionResult(params) {
  var p = params || {};
  var emberId = p.ember_id;
  var success = p.success;

  if (!emberId) return { ok: false, error: 'ember_id required' };

  var embers = readEmbers();
  var ember = embers.find(e => e.id === emberId);
  if (!ember) return { ok: false, error: 'ember_not_found' };

  if (success) {
    ember.credibility.internal.score = Math.min(1.0, ember.credibility.internal.score + 0.05);
  } else {
    ember.credibility.internal.score = Math.max(0.0, ember.credibility.internal.score - 0.10);
    // If gene was rejected, revert ember to candidate
    if (p.gene_rejected) {
      ember.status = 'candidate';
    }
  }

  // Recompute composite
  var alpha = ember.credibility.external.citations < 3 ? 1.0 :
    ember.credibility.external.citations <= 10 ? 0.8 - (ember.credibility.external.citations - 3) * (0.2 / 7) : 0.6;
  ember.credibility.composite = alpha * ember.credibility.internal.score + (1 - alpha) * ember.credibility.external.score;

  updateEmber(emberId, ember);

  return {
    ok: true,
    ember_id: emberId,
    new_composite: ember.credibility.composite,
    new_status: ember.status,
  };
}

// Inject spark relevance into GEP selection scoring
function computeSparkRelevance(sparkResults, threshold) {
  if (!sparkResults || sparkResults.length === 0) return 0;
  var t = threshold || 0.25;
  var relevant = sparkResults.filter(r => r.score >= t);
  if (relevant.length === 0) return 0;

  var total = relevant.reduce((acc, r) => {
    var credScore = r.item && r.item.credibility ? r.item.credibility.composite : 0.5;
    return acc + r.score * credScore;
  }, 0);

  return total / relevant.length;
}

module.exports = {
  handleGeneExecutionResult,
  computeSparkRelevance,
};
