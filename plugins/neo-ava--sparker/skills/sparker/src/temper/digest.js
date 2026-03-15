// Periodic digest (temper cycle) — the 9-step review process.
// Aggregates raw sparks, promotes to refined, updates credibility,
// runs preference profiling, pushes review cards, generates report.

const { readRawSparksWithSnapshot, writeRawSparksSnapshot, readRefinedSparks, readPracticeRecords, appendDigestReport, writeRefinedSparks, readEmbers } = require('../core/storage');
const { rebuildCapabilityMap, writeCapabilityMap } = require('../core/capability-map');
const { meetsRefinementThreshold, shouldReject } = require('../core/credibility');
const { promoteEligibleRawSparks } = require('./promoter');
const { decayRawSpark, decayRefinedSpark, applyInactivityDecay } = require('./decay');
const { detectRelations } = require('./chain-detector');
const { rebuildClusterCache } = require('./spark-cluster');
const { discoverAllBoundaries } = require('./boundary-discovery');
const { discoverAllContextDimensions } = require('./context-discovery');
const { shouldProfile, generateProfile, generatePersonaText, readAllPreferenceMaps } = require('../core/preference-map');
const { withFileLock } = require('../core/file-lock');

function buildSkippedDigestReport(opts, reason) {
  var o = opts || {};
  var hours = o.hours || Number(process.env.STP_DIGEST_INTERVAL_HOURS) || 12;
  if (o.days) hours = o.days * 24;
  var now = Date.now();
  var cutoff = now - hours * 60 * 60 * 1000;
  return {
    type: 'DigestReport',
    skipped: true,
    skip_reason: reason || 'locked',
    period_start: new Date(cutoff).toISOString(),
    period_end: new Date(now).toISOString(),
    digest_hours: hours,
    summary: {
      new_raw_sparks: 0,
      domains_active: 0,
      practice_records: 0,
      practice_accepted: 0,
      practice_rejected: 0,
      promoted_to_refined: 0,
      publish_ready: 0,
      rejected: 0,
      decayed: 0,
      profiles_updated: 0,
      review_cards_pushed: 0,
    },
    new_refined_sparks: [],
    publish_ready: [],
    preference_profiles: [],
    review_cards: [],
    capability_changes: {},
    blind_spots: [],
    learning_suggestions: [],
    created_at: new Date().toISOString(),
  };
}

async function runDigestUnlocked(opts) {
  var o = opts || {};
  var hours = o.hours || Number(process.env.STP_DIGEST_INTERVAL_HOURS) || 12;
  if (o.days) hours = o.days * 24;
  var now = Date.now();
  var cutoff = now - hours * 60 * 60 * 1000;

  // Step 1: Gather recent raw sparks (with snapshot overlay for practice stats)
  var allRawSparks = readRawSparksWithSnapshot();
  var recentRaw = allRawSparks.filter(s => new Date(s.created_at).getTime() >= cutoff);

  // Step 2: Group by domain
  var byDomain = {};
  for (var i = 0; i < recentRaw.length; i++) {
    var d = recentRaw[i].domain || 'general';
    if (!byDomain[d]) byDomain[d] = [];
    byDomain[d].push(recentRaw[i]);
  }

  // Step 3: Analyze practice records and aggregate onto RawSparks
  var practiceRecords = readPracticeRecords();
  var recentPractice = practiceRecords.filter(p => new Date(p.created_at).getTime() >= cutoff);

  var practiceBySparkId = {};
  for (var pi = 0; pi < practiceRecords.length; pi++) {
    var pr = practiceRecords[pi];
    if (!pr.spark_id) continue;
    if (!practiceBySparkId[pr.spark_id]) practiceBySparkId[pr.spark_id] = { count: 0, success: 0 };
    practiceBySparkId[pr.spark_id].count++;
    var out = pr.outcome;
    if (out === 'positive' || out === 'accepted') practiceBySparkId[pr.spark_id].success++;
    else if (out === 'partial') practiceBySparkId[pr.spark_id].success += 0.5;
  }

  for (var ai = 0; ai < allRawSparks.length; ai++) {
    var agg = practiceBySparkId[allRawSparks[ai].id];
    if (agg) {
      allRawSparks[ai].practice_count = Math.max(allRawSparks[ai].practice_count || 0, agg.count);
      allRawSparks[ai].success_count = Math.max(allRawSparks[ai].success_count || 0, agg.success);
    }
  }

  writeRawSparksSnapshot(allRawSparks);

  // Step 4: Promote eligible RawSparks to RefinedSparks
  var promotionResult = await promoteEligibleRawSparks(allRawSparks.filter(s => s.status === 'active'), practiceRecords);

  // Step 3.5: Boundary auto-discovery from practice_record patterns
  var boundaryDiscoveries = discoverAllBoundaries();

  // Step 5: Update credibility with decay
  for (var j = 0; j < allRawSparks.length; j++) {
    decayRawSpark(allRawSparks[j], now);
  }

  var refinedSparks = readRefinedSparks();

  // Step 4.5: Rebuild Spark clusters from chain relations (after refinedSparks loaded)
  var allActiveSparks = allRawSparks.filter(function (s) { return s.status === 'active' || s.status === 'published'; });
  var allRelations = [];
  for (var ri = 0; ri < allActiveSparks.length; ri++) {
    var sparkRels = allActiveSparks[ri].relations || [];
    for (var rj = 0; rj < sparkRels.length; rj++) {
      allRelations.push(Object.assign({ source_id: allActiveSparks[ri].id }, sparkRels[rj]));
    }
  }
  var clusterData = rebuildClusterCache(allActiveSparks.concat(refinedSparks), allRelations);
  for (var k = 0; k < refinedSparks.length; k++) {
    decayRefinedSpark(refinedSparks[k], now);
  }

  // Apply inactivity decay
  var inactivityResult = applyInactivityDecay(refinedSparks, practiceRecords, 7);

  // Step 6: Promotion decisions
  var publishReady = [];
  var rejected = [];
  for (var m = 0; m < refinedSparks.length; m++) {
    var rs = refinedSparks[m];
    if (rs.status === 'active' && rs.credibility) {
      if (meetsRefinementThreshold(rs.credibility, rs.credibility.internal.practice_count)) {
        if (rs.credibility.internal.score >= 0.75 &&
            rs.credibility.internal.practice_count >= 3) {
          rs.status = 'published';
          publishReady.push(rs);
        }
      }
      if (shouldReject(rs.credibility)) {
        rs.status = 'rejected';
        rejected.push(rs);
      }
    }
  }

  writeRefinedSparks(refinedSparks);

  // Step 7: Preference Profiling — auto-summarize preferences per domain
  var profileUpdates = [];
  var allDomains = Object.keys(byDomain);
  for (var di = 0; di < allDomains.length; di++) {
    var dom = allDomains[di];
    if (shouldProfile(dom)) {
      try {
        var profile = await generateProfile(dom);
        if (profile && !profile.error) {
          profileUpdates.push({ domain: dom, dimensions: profile.dimensions || [], signal_count: profile.signal_count || 0 });
        }
      } catch (e) { /* profiling is best-effort */ }
    }
  }

  // Step 7.2: Generate persona text for all profiled domains (cached, zero LLM)
  var allMaps = readAllPreferenceMaps();
  for (var pd in allMaps) {
    try { generatePersonaText(pd); } catch (e) { /* best-effort */ }
  }

  // Step 7.5: Context dimension discovery — find domain-specific envelope fields
  var contextDiscoveries = discoverAllContextDimensions();

  // Step 8: Rebuild capability map, detect blind spots
  var capabilityMap = rebuildCapabilityMap(allRawSparks, refinedSparks, practiceRecords);
  writeCapabilityMap(capabilityMap);

  var blindSpots = [];
  for (var domain in capabilityMap.domains) {
    if (capabilityMap.domains[domain].status === 'blind_spot') {
      blindSpots.push(domain);
    }
  }

  // Step 9: Identify review card candidates from community embers
  var reviewCandidates = [];
  try {
    var embers = readEmbers();
    var candidateEmbers = embers.filter(function (e) {
      return e.status === 'candidate' && e.credibility && e.credibility.composite < 0.80;
    });
    var domainSet = {};
    for (var dj = 0; dj < allDomains.length; dj++) domainSet[allDomains[dj]] = true;
    reviewCandidates = candidateEmbers
      .filter(function (e) { return domainSet[e.domain]; })
      .slice(0, 3)
      .map(function (e) {
        return { id: e.id, domain: e.domain, summary: e.summary, credibility: e.credibility.composite };
      });
  } catch (e) { /* review cards are best-effort */ }

  // Generate digest report
  var report = {
    type: 'DigestReport',
    period_start: new Date(cutoff).toISOString(),
    period_end: new Date(now).toISOString(),
    digest_hours: hours,
    summary: {
      new_raw_sparks: recentRaw.length,
      domains_active: Object.keys(byDomain).length,
      practice_records: recentPractice.length,
      practice_accepted: recentPractice.filter(p => p.outcome === 'accepted').length,
      practice_rejected: recentPractice.filter(p => p.outcome === 'rejected').length,
      boundaries_discovered: boundaryDiscoveries.length,
      clusters_built: clusterData.clusters ? clusterData.clusters.length : 0,
      promoted_to_refined: promotionResult.promoted,
      publish_ready: publishReady.length,
      rejected: rejected.length,
      decayed: inactivityResult.decayed,
      profiles_updated: profileUpdates.length,
      context_dimensions_discovered: contextDiscoveries.length,
      review_cards_pushed: reviewCandidates.length,
    },
    new_refined_sparks: promotionResult.refined_sparks.map(r => ({
      id: r.id,
      domain: r.domain,
      summary: r.summary,
      credibility: r.credibility ? r.credibility.composite : 0,
    })),
    publish_ready: publishReady.map(r => ({
      id: r.id,
      domain: r.domain,
      summary: r.summary,
    })),
    preference_profiles: profileUpdates,
    review_cards: reviewCandidates,
    capability_changes: capabilityMap.domains,
    blind_spots: blindSpots,
    learning_suggestions: blindSpots.map(d => ({
      domain: d,
      suggestions: [
        'Search SparkHub for ' + d + ' embers',
        'Ask owner for ' + d + ' expertise',
        'Explore web resources about ' + d,
      ],
    })),
    created_at: new Date().toISOString(),
  };

  if (!o.dryRun) {
    appendDigestReport(report);
  }

  return report;
}

async function runDigest(opts) {
  var staleMs = Number(process.env.STP_DIGEST_LOCK_STALE_MS || 2 * 60 * 60 * 1000);
  var result = await withFileLock('digest', function () {
    return runDigestUnlocked(opts);
  }, { staleMs: staleMs });
  if (result && result.__lock_skipped) {
    return buildSkippedDigestReport(opts, 'already_running');
  }
  return result;
}

module.exports = { runDigest };
