// Credibility decay engine — time-based and inactivity decay.

const { applyTimeDecay, applyInactiveDecay, shouldReject } = require('../core/credibility');

// Apply time-based decay to a spark's confidence/credibility
function decayRawSpark(spark, now) {
  if (spark.status !== 'active') return spark;
  var created = new Date(spark.created_at).getTime();
  var current = (now || Date.now());
  var ageDays = (current - created) / (24 * 60 * 60 * 1000);
  var halfLife = spark.freshness_half_life_days || 60;

  var factor = Math.pow(0.5, ageDays / halfLife);
  spark.confidence = (spark.confidence || 0.5) * factor;

  if (spark.confidence <= 0.10) {
    spark.status = 'rejected';
  }

  return spark;
}

function decayRefinedSpark(spark, now) {
  if (spark.status !== 'active' && spark.status !== 'published') return spark;
  var created = new Date(spark.created_at).getTime();
  var current = (now || Date.now());
  var ageDays = (current - created) / (24 * 60 * 60 * 1000);
  var halfLife = spark.freshness_half_life_days || 90;

  if (spark.credibility) {
    applyTimeDecay(spark.credibility, ageDays, halfLife);
    if (shouldReject(spark.credibility)) {
      spark.status = 'rejected';
    }
  }

  return spark;
}

// Apply inactivity decay to sparks not practiced within period
function applyInactivityDecay(sparks, practiceRecords, periodDays) {
  var period = (periodDays || 7) * 24 * 60 * 60 * 1000;
  var now = Date.now();
  var practicedIds = new Set();

  for (var i = 0; i < practiceRecords.length; i++) {
    var pr = practiceRecords[i];
    var prTime = new Date(pr.created_at).getTime();
    if (now - prTime <= period) {
      practicedIds.add(pr.spark_id);
    }
  }

  var decayed = 0;
  for (var j = 0; j < sparks.length; j++) {
    var s = sparks[j];
    if (s.status !== 'active') continue;
    if (!practicedIds.has(s.id)) {
      var created = new Date(s.created_at).getTime();
      if (now - created > period) {
        if (s.credibility) {
          applyInactiveDecay(s.credibility);
        } else {
          s.confidence = Math.max(0, (s.confidence || 0.5) - 0.05);
        }
        decayed++;
      }
    }
  }

  return { decayed: decayed };
}

module.exports = {
  decayRawSpark,
  decayRefinedSpark,
  applyInactivityDecay,
};
