// Boundary Auto-Discovery — mines practice_records to find conditions
// where a Spark fails, and proposes new boundary_conditions automatically.
//
// Logic: for each Spark with mixed outcomes, compare the task_context_envelope
// of rejected records vs. accepted records. Features present in rejected but
// absent in accepted are candidate boundaries.

var { readPracticeRecords, readRawSparksWithSnapshot, writeRawSparksSnapshot } = require('../core/storage');

// Extract flat key-value pairs from a context envelope (one level deep)
function flattenEnvelope(envelope) {
  if (!envelope || typeof envelope !== 'object') return {};
  var flat = {};
  for (var k in envelope) {
    var v = envelope[k];
    if (v === null || v === undefined) continue;
    if (Array.isArray(v)) {
      for (var i = 0; i < v.length; i++) flat[k + '=' + v[i]] = true;
    } else if (typeof v === 'object') {
      for (var sk in v) flat[k + '.' + sk + '=' + v[sk]] = true;
    } else {
      flat[k + '=' + v] = true;
    }
  }
  return flat;
}

// Find candidate boundaries for a single Spark from its practice history
function discoverBoundariesForSpark(sparkId, practiceRecords) {
  var records = practiceRecords.filter(function (r) {
    return r.spark_id === sparkId && r.task_context_envelope;
  });
  if (records.length < 3) return []; // need enough data points

  var accepted = records.filter(function (r) {
    return r.outcome === 'accepted' || r.outcome === 'positive';
  });
  var rejected = records.filter(function (r) {
    return r.outcome === 'rejected' || r.outcome === 'negative';
  });

  if (accepted.length === 0 || rejected.length === 0) return [];

  // Count feature frequency in accepted vs rejected
  var acceptedFeatures = {};
  var rejectedFeatures = {};

  for (var ai = 0; ai < accepted.length; ai++) {
    var af = flattenEnvelope(accepted[ai].task_context_envelope);
    for (var ak in af) acceptedFeatures[ak] = (acceptedFeatures[ak] || 0) + 1;
  }
  for (var ri = 0; ri < rejected.length; ri++) {
    var rf = flattenEnvelope(rejected[ri].task_context_envelope);
    for (var rk in rf) rejectedFeatures[rk] = (rejectedFeatures[rk] || 0) + 1;
  }

  // Features present in majority of rejected but minority of accepted → candidate boundary
  var candidates = [];
  var rejThreshold = rejected.length * 0.5;
  var accThreshold = accepted.length * 0.3;

  for (var feat in rejectedFeatures) {
    if (rejectedFeatures[feat] >= rejThreshold &&
        (acceptedFeatures[feat] || 0) < accThreshold) {
      candidates.push({
        feature: feat,
        rejected_count: rejectedFeatures[feat],
        accepted_count: acceptedFeatures[feat] || 0,
        confidence: rejectedFeatures[feat] / rejected.length,
      });
    }
  }

  // Convert to boundary_condition format
  return candidates.map(function (c) {
    var parts = c.feature.split('=');
    return {
      condition: parts[0] + ' = ' + parts[1],
      effect: 'do_not_apply',
      reason: 'Auto-discovered: Spark rejected in ' + c.rejected_count + '/' + rejected.length +
              ' cases with this context, accepted in only ' + c.accepted_count + '/' + accepted.length,
      status: 'pending_verification',
      discovered_at: new Date().toISOString(),
      confidence: c.confidence,
    };
  });
}

// Run boundary discovery across all Sparks (called during digest)
function discoverAllBoundaries() {
  var practiceRecords = readPracticeRecords();
  var allSparks = readRawSparksWithSnapshot();
  var discoveries = [];

  // Group practice records by spark_id
  var bySparkId = {};
  for (var i = 0; i < practiceRecords.length; i++) {
    var pr = practiceRecords[i];
    if (!pr.spark_id) continue;
    if (!bySparkId[pr.spark_id]) bySparkId[pr.spark_id] = [];
    bySparkId[pr.spark_id].push(pr);
  }

  for (var sparkId in bySparkId) {
    var candidates = discoverBoundariesForSpark(sparkId, bySparkId[sparkId]);
    if (candidates.length === 0) continue;

    var spark = allSparks.find(function (s) { return s.id === sparkId; });
    if (!spark) continue;

    // Add new boundaries (avoid duplicates)
    // V2: also populate spark.not array
    if (!spark.card) spark.card = {};
    if (!spark.card.boundary_conditions) spark.card.boundary_conditions = [];
    if (!spark.not) spark.not = [];
    var existingConds = spark.card.boundary_conditions.map(function (bc) {
      return (bc.condition || '').toLowerCase();
    });
    var existingNotConds = spark.not.map(function (n) {
      return (n.condition || '').toLowerCase();
    });

    var added = [];
    for (var ci = 0; ci < candidates.length; ci++) {
      var candCond = (candidates[ci].condition || '').toLowerCase();
      if (existingConds.indexOf(candCond) === -1) {
        spark.card.boundary_conditions.push(candidates[ci]);
        existingConds.push(candCond);
        added.push(candidates[ci]);
      }
      // V2: sync to spark.not array
      if (existingNotConds.indexOf(candCond) === -1) {
        spark.not.push({
          condition: candidates[ci].condition,
          effect: candidates[ci].effect || 'do_not_apply',
          reason: candidates[ci].reason || ''
        });
        existingNotConds.push(candCond);
      }
    }

    if (added.length > 0) {
      discoveries.push({ spark_id: sparkId, domain: spark.domain, new_boundaries: added });
    }
  }

  if (discoveries.length > 0) {
    writeRawSparksSnapshot(allSparks);
  }

  return discoveries;
}

module.exports = {
  discoverBoundariesForSpark,
  discoverAllBoundaries,
  flattenEnvelope,
};
