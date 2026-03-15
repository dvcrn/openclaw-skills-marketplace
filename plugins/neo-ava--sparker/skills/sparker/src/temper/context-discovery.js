// Context Envelope Progressive Discovery — automatically identifies which
// context dimensions matter for each domain, based on practice record patterns.
//
// When practice_records frequently carry certain extra fields in their
// task_context_envelope, those fields become "recommended" for that domain.
// extractor.js can then explicitly request these fields during Spark creation.

var { readPracticeRecords } = require('../core/storage');
var { readPreferenceMap, writePreferenceMap } = require('../core/preference-map');

var PROMOTION_THRESHOLD = 0.3; // field must appear in >30% of records to be promoted

// Analyze practice records for a domain, find frequently-used context fields
function discoverContextDimensions(domain) {
  var records = readPracticeRecords();
  var domainRecords = records.filter(function (r) {
    return r.domain === domain && r.task_context_envelope;
  });

  if (domainRecords.length < 5) return { domain: domain, recommended_fields: [], sample_size: domainRecords.length };

  // Standard fields that are always present — don't count these
  var standardFields = { domain: true, sub_domain: true };

  // Count field occurrences — check both V1 (task_context_envelope) and V2 (where)
  var fieldCounts = {};
  var fieldValues = {};
  for (var i = 0; i < domainRecords.length; i++) {
    var env = domainRecords[i].task_context_envelope;
    // V2: merge where fields into the envelope for analysis
    var whereObj = domainRecords[i].where;
    if (whereObj && typeof whereObj === 'object') {
      if (!env) env = {};
      if (whereObj.scenario && !env.scenario) env.scenario = whereObj.scenario;
      if (whereObj.audience && !env.audience) env.audience = whereObj.audience;
    }
    if (!env) continue;
    for (var key in env) {
      if (standardFields[key]) continue;
      if (env[key] === null || env[key] === undefined) continue;
      fieldCounts[key] = (fieldCounts[key] || 0) + 1;
      if (!fieldValues[key]) fieldValues[key] = {};
      var val = Array.isArray(env[key]) ? env[key].join(',') : String(env[key]);
      fieldValues[key][val] = (fieldValues[key][val] || 0) + 1;
    }
  }

  var recommended = [];
  var total = domainRecords.length;
  for (var field in fieldCounts) {
    var freq = fieldCounts[field] / total;
    if (freq >= PROMOTION_THRESHOLD) {
      var values = Object.keys(fieldValues[field] || {});
      recommended.push({
        field: field,
        frequency: Math.round(freq * 100) / 100,
        unique_values: values.length,
        sample_values: values.slice(0, 5),
      });
    }
  }

  recommended.sort(function (a, b) { return b.frequency - a.frequency; });

  return {
    domain: domain,
    recommended_fields: recommended,
    sample_size: total,
    discovered_at: new Date().toISOString(),
  };
}

// Update the domain's preference map with recommended context fields
function updateDomainContextFields(domain) {
  var discovery = discoverContextDimensions(domain);
  if (discovery.recommended_fields.length === 0) return discovery;

  try {
    var map = readPreferenceMap(domain);
    map.recommended_context_fields = discovery.recommended_fields;
    map.context_discovery_at = discovery.discovered_at;
    writePreferenceMap(domain, map);
  } catch (e) { /* best-effort */ }

  return discovery;
}

// Run for all domains that have enough practice data (called during digest)
function discoverAllContextDimensions() {
  var records = readPracticeRecords();
  var domains = {};
  for (var i = 0; i < records.length; i++) {
    if (records[i].domain) domains[records[i].domain] = true;
  }

  var results = [];
  for (var d in domains) {
    var r = updateDomainContextFields(d);
    if (r.recommended_fields.length > 0) results.push(r);
  }
  return results;
}

module.exports = {
  discoverContextDimensions,
  updateDomainContextFields,
  discoverAllContextDimensions,
  PROMOTION_THRESHOLD,
};
