// Capability Map — tracks agent's knowledge coverage across domains.
// Four levels: mastered > proficient > learning > blind_spot.

const { readJson, writeJson, PATHS } = require('./storage');

function createCapabilityMap() {
  return { domains: {}, updated_at: new Date().toISOString() };
}

function readCapabilityMap() {
  return readJson(PATHS.capabilityMap(), createCapabilityMap());
}

function writeCapabilityMap(map) {
  map.updated_at = new Date().toISOString();
  writeJson(PATHS.capabilityMap(), map);
}

function getStatus(score, practiceCount, hasRefined) {
  if (hasRefined && score >= 0.80 && practiceCount >= 5) return 'mastered';
  if (hasRefined && score >= 0.60) return 'proficient';
  if (score > 0 || practiceCount > 0) return 'learning';
  return 'blind_spot';
}

// Rebuild capability map from raw+refined sparks and practice records
function rebuildCapabilityMap(rawSparks, refinedSparks, practiceRecords) {
  var map = createCapabilityMap();
  var domainStats = {};

  function ensureDomain(domain) {
    if (!domainStats[domain]) {
      domainStats[domain] = {
        rawCount: 0,
        refinedCount: 0,
        totalScore: 0,
        practiceCount: 0,
        successCount: 0,
        hasRefined: false,
        lastActivity: null,
        subDomains: {},
      };
    }
    return domainStats[domain];
  }

  for (var i = 0; i < rawSparks.length; i++) {
    var rs = rawSparks[i];
    var domain = (rs.domain || 'general').split('.')[0];
    var sub = (rs.domain || '').includes('.') ? rs.domain.split('.').slice(1).join('.') : null;
    var ds = ensureDomain(domain);
    ds.rawCount++;
    ds.totalScore += rs.confidence || 0;
    if (rs.created_at && (!ds.lastActivity || rs.created_at > ds.lastActivity)) {
      ds.lastActivity = rs.created_at;
    }
    if (sub) {
      if (!ds.subDomains[sub]) ds.subDomains[sub] = { rawCount: 0, refinedCount: 0, score: 0 };
      ds.subDomains[sub].rawCount++;
    }
  }

  for (var j = 0; j < refinedSparks.length; j++) {
    var ref = refinedSparks[j];
    var rdomain = (ref.domain || 'general').split('.')[0];
    var rsub = (ref.domain || '').includes('.') ? ref.domain.split('.').slice(1).join('.') : null;
    var rds = ensureDomain(rdomain);
    rds.refinedCount++;
    rds.hasRefined = true;
    var refScore = ref.credibility ? ref.credibility.composite || ref.credibility.internal.score : 0;
    rds.totalScore += refScore;
    if (ref.created_at && (!rds.lastActivity || ref.created_at > rds.lastActivity)) {
      rds.lastActivity = ref.created_at;
    }
    if (rsub) {
      if (!rds.subDomains[rsub]) rds.subDomains[rsub] = { rawCount: 0, refinedCount: 0, score: 0 };
      rds.subDomains[rsub].refinedCount++;
      rds.subDomains[rsub].score = refScore;
    }
  }

  for (var k = 0; k < practiceRecords.length; k++) {
    var pr = practiceRecords[k];
    var sparkDomain = pr.domain || 'general';
    var pdomain = sparkDomain.split('.')[0];
    var pds = ensureDomain(pdomain);
    pds.practiceCount++;
    if (pr.outcome === 'accepted') pds.successCount++;
  }

  for (var d in domainStats) {
    var st = domainStats[d];
    var total = st.rawCount + st.refinedCount;
    var avgScore = total > 0 ? st.totalScore / total : 0;
    var status = getStatus(avgScore, st.practiceCount, st.hasRefined);

    var subDomains = {};
    for (var sd in st.subDomains) {
      var sds = st.subDomains[sd];
      subDomains[sd] = {
        status: getStatus(sds.score, 0, sds.refinedCount > 0),
        score: sds.score,
      };
    }

    map.domains[d] = {
      status: status,
      score: parseFloat(avgScore.toFixed(3)),
      sub_domains: subDomains,
      spark_count: st.rawCount,
      refined_count: st.refinedCount,
      practice_count: st.practiceCount,
      last_activity: st.lastActivity,
    };
  }

  return map;
}

// Detect blind spots: domains mentioned in tasks but absent from map
function detectBlindSpots(taskDomains, capabilityMap) {
  var blindSpots = [];
  for (var i = 0; i < taskDomains.length; i++) {
    var d = taskDomains[i];
    var entry = capabilityMap.domains[d];
    if (!entry || entry.status === 'blind_spot' || entry.status === 'learning') {
      blindSpots.push({ domain: d, status: entry ? entry.status : 'blind_spot' });
    }
  }
  return blindSpots;
}

module.exports = {
  createCapabilityMap,
  readCapabilityMap,
  writeCapabilityMap,
  getStatus,
  rebuildCapabilityMap,
  detectBlindSpots,
};
