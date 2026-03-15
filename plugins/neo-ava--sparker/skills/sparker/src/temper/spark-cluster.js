// Spark Cluster — aggregates relationship-connected Sparks into knowledge units.
//
// A cluster = one core Spark + all directly related Sparks.
// Relation types:
//   supports    → evidence, increases cluster confidence
//   refines     → adds detail / boundary conditions
//   contradicts → NOT merged in, surfaced as risk warning
//   supersedes  → replaces core, original becomes historical

var { readJson, writeJson, resolvePath } = require('../core/storage');
var { mergeCards } = require('../core/spark-card-schema');

function getClustersPath() {
  return resolvePath('clusters/clusters.json');
}

function readClusters() {
  return readJson(getClustersPath(), { clusters: [], built_at: null });
}

function writeClusters(data) {
  writeJson(getClustersPath(), data);
}

// Build a single cluster around a core Spark
function buildCluster(coreSpark, allSparks, relations) {
  var cluster = {
    core_id: coreSpark.id,
    core: coreSpark,
    refinements: [],
    supporting: [],
    contradictions: [],
    composite_envelope: null,
    composite_boundaries: [],
  };

  var sparkMap = {};
  for (var i = 0; i < allSparks.length; i++) {
    sparkMap[allSparks[i].id] = allSparks[i];
  }

  for (var ri = 0; ri < relations.length; ri++) {
    var rel = relations[ri];
    var isSource = rel.source_id === coreSpark.id || rel.source === coreSpark.id;
    var isTarget = rel.target_id === coreSpark.id || rel.target === coreSpark.id;
    if (!isSource && !isTarget) continue;

    var relatedId = isSource
      ? (rel.target_id || rel.target)
      : (rel.source_id || rel.source);
    var related = sparkMap[relatedId];
    if (!related) continue;

    var type = rel.type || rel.relation_type;
    switch (type) {
      case 'refines':
        cluster.refinements.push(related);
        var bc = (related.card && related.card.boundary_conditions) || [];
        for (var bci = 0; bci < bc.length; bci++) cluster.composite_boundaries.push(bc[bci]);
        // V2: also collect boundaries from spark.not
        var notArr = related.not || [];
        for (var ni = 0; ni < notArr.length; ni++) {
          cluster.composite_boundaries.push({
            condition: notArr[ni].condition || '',
            effect: notArr[ni].effect || 'do_not_apply',
            reason: notArr[ni].reason || ''
          });
        }
        break;
      case 'supports':
        cluster.supporting.push(related);
        break;
      case 'contradicts':
        cluster.contradictions.push(related);
        break;
      case 'supersedes':
        if (isSource) {
          // coreSpark supersedes related → core stays, related is historical
          cluster.supporting.push(related);
        } else {
          // related supersedes coreSpark → swap
          cluster.supporting.push(cluster.core);
          cluster.core = related;
          cluster.core_id = related.id;
        }
        break;
    }
  }

  // Merge core's envelope with refinements' envelopes
  // V2: also consider spark.where as context envelope source
  var coreEnv = (cluster.core.card && cluster.core.card.context_envelope) || null;
  if (!coreEnv && cluster.core.where) {
    coreEnv = cluster.core.where;
  }
  var envelopes = [coreEnv].filter(Boolean);
  for (var ei = 0; ei < cluster.refinements.length; ei++) {
    var env = (cluster.refinements[ei].card && cluster.refinements[ei].card.context_envelope)
      || cluster.refinements[ei].where || null;
    if (env) envelopes.push(env);
  }
  cluster.composite_envelope = envelopes.length > 0 ? envelopes[0] : {};

  // Deduplicate boundary conditions
  var coreBc = (cluster.core.card && cluster.core.card.boundary_conditions) || [];
  // V2: also include core's not array
  var coreNot = cluster.core.not || [];
  for (var cni = 0; cni < coreNot.length; cni++) {
    coreBc.push({
      condition: coreNot[cni].condition || '',
      effect: coreNot[cni].effect || 'do_not_apply',
      reason: coreNot[cni].reason || ''
    });
  }
  var allBc = coreBc.concat(cluster.composite_boundaries);
  var seen = {};
  cluster.composite_boundaries = [];
  for (var di = 0; di < allBc.length; di++) {
    var key = (allBc[di].condition || '') + '|' + (allBc[di].effect || '');
    if (!seen[key]) {
      seen[key] = true;
      cluster.composite_boundaries.push(allBc[di]);
    }
  }

  return cluster;
}

// Build all clusters from a set of active Sparks and their relations.
// Each Spark belongs to at most one cluster (as core). Sparks with no
// relations form a trivial cluster of size 1.
function buildAllClusters(sparks, relations) {
  var activeSparks = sparks.filter(function (s) {
    return s.status === 'active' || s.status === 'published';
  });

  // Index: spark_id → list of relations involving it
  var relIndex = {};
  for (var ri = 0; ri < relations.length; ri++) {
    var r = relations[ri];
    var src = r.source_id || r.source;
    var tgt = r.target_id || r.target;
    if (src) { if (!relIndex[src]) relIndex[src] = []; relIndex[src].push(r); }
    if (tgt) { if (!relIndex[tgt]) relIndex[tgt] = []; relIndex[tgt].push(r); }
  }

  // Find sparks that have been superseded — they shouldn't be cluster cores
  var superseded = {};
  for (var si = 0; si < relations.length; si++) {
    if (relations[si].type === 'supersedes') {
      var oldId = relations[si].target_id || relations[si].target;
      if (oldId) superseded[oldId] = true;
    }
  }

  var clusters = [];
  for (var i = 0; i < activeSparks.length; i++) {
    var sp = activeSparks[i];
    if (superseded[sp.id]) continue;
    var sparkRels = relIndex[sp.id] || [];
    if (sparkRels.length === 0) continue; // skip trivial clusters
    clusters.push(buildCluster(sp, activeSparks, sparkRels));
  }

  return clusters;
}

// Rebuild and cache clusters (called during digest step 4.5)
function rebuildClusterCache(sparks, relations) {
  var clusters = buildAllClusters(sparks, relations);
  var data = {
    clusters: clusters.map(function (c) {
      return {
        core_id: c.core_id,
        refinement_ids: c.refinements.map(function (r) { return r.id; }),
        supporting_ids: c.supporting.map(function (r) { return r.id; }),
        contradiction_ids: c.contradictions.map(function (r) { return r.id; }),
        composite_boundaries: c.composite_boundaries,
        size: 1 + c.refinements.length + c.supporting.length,
      };
    }),
    built_at: new Date().toISOString(),
  };
  writeClusters(data);
  return data;
}

// Look up the cluster containing a given spark_id
function findClusterForSpark(sparkId) {
  var data = readClusters();
  for (var i = 0; i < data.clusters.length; i++) {
    var c = data.clusters[i];
    if (c.core_id === sparkId ||
        (c.refinement_ids && c.refinement_ids.indexOf(sparkId) >= 0) ||
        (c.supporting_ids && c.supporting_ids.indexOf(sparkId) >= 0)) {
      return c;
    }
  }
  return null;
}

// Expand search results: for each hit, pull its cluster members
function expandWithClusters(selectedSparks, allSparks) {
  var data = readClusters();
  if (!data.clusters || data.clusters.length === 0) return selectedSparks;

  var sparkMap = {};
  for (var i = 0; i < allSparks.length; i++) sparkMap[allSparks[i].id] = allSparks[i];

  var expanded = [];
  var seen = {};
  for (var si = 0; si < selectedSparks.length; si++) {
    var sp = selectedSparks[si];
    if (seen[sp.id]) continue;
    seen[sp.id] = true;

    var cluster = findClusterForSpark(sp.id);
    if (cluster) {
      var entry = {
        type: 'cluster',
        core: sparkMap[cluster.core_id] || sp,
        refinements: (cluster.refinement_ids || []).map(function (id) { return sparkMap[id]; }).filter(Boolean),
        contradictions: (cluster.contradiction_ids || []).map(function (id) { return sparkMap[id]; }).filter(Boolean),
        composite_boundaries: cluster.composite_boundaries || [],
      };
      // Mark all cluster members as seen
      if (cluster.refinement_ids) cluster.refinement_ids.forEach(function (id) { seen[id] = true; });
      if (cluster.supporting_ids) cluster.supporting_ids.forEach(function (id) { seen[id] = true; });
      expanded.push(entry);
    } else {
      expanded.push({ type: 'single', core: sp, refinements: [], contradictions: [], composite_boundaries: [] });
    }
  }

  return expanded;
}

module.exports = {
  buildCluster,
  buildAllClusters,
  rebuildClusterCache,
  findClusterForSpark,
  expandWithClusters,
  readClusters,
};
