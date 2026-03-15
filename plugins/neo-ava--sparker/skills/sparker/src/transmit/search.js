// Knowledge search — local TF-IDF + optional vector hybrid + remote SparkHub.
// When embedding is configured and vectors are in the index, uses hybrid scoring
// (vector * 0.6 + TF-IDF * 0.4). Falls back to pure TF-IDF when no embeddings.

var { readRawSparks, readRefinedSparks, readEmbers } = require('../core/storage');
var { computeSimilarities, sparkToText, tokenize, buildTfVector } = require('../core/similarity');
var { loadSearchIndex, rebuildSearchIndex } = require('../core/search-index');
var { hubSearch, getHubUrl } = require('./hub-client');

var RELEVANCE_THRESHOLD = 0.10;
var MAX_RESULTS = 10;
var VECTOR_WEIGHT = 0.6;
var TFIDF_WEIGHT = 0.4;

function formatResult(spark, sparkType, score, searchMethod) {
  var displaySummary = '';
  if (spark.when && spark.when.trigger && spark.how && spark.how.summary) {
    displaySummary = spark.when.trigger + ' → ' + spark.how.summary;
  } else {
    displaySummary = spark.summary || spark.content || (spark.card && spark.card.heuristic) || '';
  }

  var result = {
    id: spark.id,
    type: sparkType,
    domain: spark.domain,
    summary: displaySummary,
    score: parseFloat(score.toFixed(4)),
    confidence: spark.confidence || (spark.credibility && spark.credibility.composite) || 0,
    source: 'local',
  };

  if (searchMethod) result.search_method = searchMethod;
  if (spark.when) result.when = spark.when;
  if (spark.how) result.how = spark.how;
  if (spark.why) result.why = spark.why;
  if (spark.not && spark.not.length > 0) result.not = spark.not;

  return result;
}

function vectorCosine(a, b) {
  if (!a || !b || a.length !== b.length) return 0;
  var dot = 0, normA = 0, normB = 0;
  for (var i = 0; i < a.length; i++) {
    dot += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }
  if (normA === 0 || normB === 0) return 0;
  return dot / (Math.sqrt(normA) * Math.sqrt(normB));
}

function computeTfidfScores(entries, query, index) {
  var queryTokens = tokenize(query);
  var queryTf = buildTfVector(queryTokens);
  var n = index.corpus_size + 1;
  var storedDf = index.df;

  var queryDfBump = {};
  for (var qt in queryTf) queryDfBump[qt] = true;

  var queryVec = {};
  var queryNormSq = 0;
  for (var term in queryTf) {
    var termDf = (storedDf[term] || 0) + 1;
    var idf = Math.log((n + 1) / (termDf + 1)) + 1;
    var val = queryTf[term] * idf;
    queryVec[term] = val;
    queryNormSq += val * val;
  }
  var queryNorm = Math.sqrt(queryNormSq);
  if (queryNorm === 0) return new Array(entries.length).fill(0);

  var scores = [];
  for (var i = 0; i < entries.length; i++) {
    var docTf = entries[i].tf;
    var dot = 0, docNormSq = 0;
    for (var dt in docTf) {
      var dtDf = (storedDf[dt] || 0) + (queryDfBump[dt] ? 1 : 0);
      var dIdf = Math.log((n + 1) / (dtDf + 1)) + 1;
      var dVal = docTf[dt] * dIdf;
      docNormSq += dVal * dVal;
      if (queryVec[dt]) dot += queryVec[dt] * dVal;
    }
    var docNorm = Math.sqrt(docNormSq);
    scores.push(dot === 0 || docNorm === 0 ? 0 : dot / (queryNorm * docNorm));
  }
  return scores;
}

function searchWithIndex(query, index, opts, queryEmbedding) {
  var o = opts || {};
  var threshold = typeof o.threshold === 'number' ? o.threshold : RELEVANCE_THRESHOLD;
  var maxResults = o.maxResults || o.max_results || MAX_RESULTS;
  var domain = o.domain || null;

  var entries = index.entries;
  if (domain) {
    entries = entries.filter(function (e) {
      return e.domain === domain || e.domain.indexOf(domain + '.') === 0;
    });
  }
  if (entries.length === 0) return { results: [], method: 'none' };

  var tfidfScores = computeTfidfScores(entries, query, index);

  var useVector = !!queryEmbedding && index.has_embeddings;
  var vectorScores = null;
  var vectorHits = 0;

  if (useVector) {
    vectorScores = [];
    for (var i = 0; i < entries.length; i++) {
      var vs = entries[i].embedding ? vectorCosine(queryEmbedding, entries[i].embedding) : 0;
      vectorScores.push(vs);
      if (vs > 0) vectorHits++;
    }
    if (vectorHits === 0) useVector = false;
  }

  var method = useVector ? 'hybrid' : 'tfidf';
  var results = [];

  for (var j = 0; j < entries.length; j++) {
    var score;
    if (useVector && vectorScores[j] > 0) {
      score = vectorScores[j] * VECTOR_WEIGHT + tfidfScores[j] * TFIDF_WEIGHT;
    } else {
      score = tfidfScores[j];
    }
    if (score >= threshold) {
      results.push({ entry: entries[j], score: score });
    }
  }

  results.sort(function (a, b) { return b.score - a.score; });
  results = results.slice(0, maxResults);

  return {
    results: results.map(function (r) {
      return formatResult(r.entry.spark, r.entry.type, r.score, method);
    }),
    method: method,
  };
}

function searchLocalFull(query, opts) {
  var o = opts || {};
  var threshold = typeof o.threshold === 'number' ? o.threshold : RELEVANCE_THRESHOLD;
  var maxResults = o.maxResults || o.max_results || MAX_RESULTS;
  var domain = o.domain || null;

  var rawSparks = readRawSparks().filter(function (s) { return s.status !== 'rejected'; });
  var embers = readEmbers();
  var refinedSparks = readRefinedSparks().filter(function (s) { return s.status === 'published' || s.status === 'active'; });
  var candidates = [].concat(rawSparks, embers, refinedSparks);

  if (domain) {
    candidates = candidates.filter(function (c) {
      var d = c.domain || '';
      return d === domain || d.startsWith(domain + '.');
    });
  }

  if (candidates.length === 0) return [];

  var similarities = computeSimilarities(query, candidates);
  var filtered = similarities.filter(function (s) { return s.score >= threshold; });
  filtered = filtered.slice(0, maxResults);

  return filtered.map(function (r) {
    var spark = r.item;
    var sparkType = spark.type || 'unknown';
    if (sparkType === 'unknown') {
      if (spark.card) sparkType = 'RawSpark';
      else if (spark.insight) sparkType = 'RefinedSpark';
      else if (spark.source_refined_id) sparkType = 'Ember';
    }
    return formatResult(spark, sparkType, r.score, 'tfidf');
  });
}

async function searchLocal(query, opts) {
  var index = loadSearchIndex();
  if (!index) {
    try { index = rebuildSearchIndex(); } catch (e) { /* best-effort rebuild */ }
  }
  if (!index) return searchLocalFull(query, opts);

  var queryEmbedding = null;
  if (index.has_embeddings) {
    try {
      var { isEmbeddingAvailable, getEmbedding } = require('../core/embedding');
      if (isEmbeddingAvailable()) {
        queryEmbedding = await getEmbedding(query);
      }
    } catch (e) { /* embedding unavailable, continue with TF-IDF */ }
  }

  var result = searchWithIndex(query, index, opts, queryEmbedding);
  return result.results;
}

async function searchRemote(query, opts) {
  var o = opts || {};
  if (!getHubUrl()) return { results: [], error: null };

  try {
    var result = await hubSearch(query, {
      domain: o.domain,
      threshold: typeof o.threshold === 'number' ? o.threshold : 0.25,
      topK: o.maxResults || o.max_results || 20,
    });
    if (!result.ok) {
      if (result.error === 'insufficient_balance') {
        process.stderr.write('[sparker] Hub search blocked: insufficient points balance' +
          (result.balance !== null && result.balance !== undefined ? ' (balance=' + result.balance + ')' : '') + '\n');
        return {
          results: [],
          error: 'insufficient_balance',
          balance: result.balance,
          message: result.message || 'Points balance is insufficient.',
        };
      }
      process.stderr.write('[sparker] Hub search failed: ' + (result.error || 'unknown') + '\n');
      return { results: [], error: result.error || 'hub_error' };
    }
    return {
      results: result.results || [],
      error: null,
      balance: result.balance,
      purchased_spark_ids: result.purchased_spark_ids,
      insufficient_at: result.insufficient_at || null,
    };
  } catch (e) {
    process.stderr.write('[sparker] Hub search error: ' + e.message + '\n');
    return { results: [], error: 'network_error' };
  }
}

function mergeResults(localResults, hubResults, maxResults) {
  var seen = new Set();
  var merged = [];

  for (var i = 0; i < localResults.length; i++) {
    seen.add(localResults[i].id);
    merged.push(localResults[i]);
  }

  for (var j = 0; j < hubResults.length; j++) {
    if (!seen.has(hubResults[j].id)) {
      seen.add(hubResults[j].id);
      merged.push(hubResults[j]);
    }
  }

  merged.sort(function (a, b) { return b.score - a.score; });
  return merged.slice(0, maxResults || MAX_RESULTS);
}

// Unified search — queries local assets and optionally the remote hub
// mode: 'all' (default) | 'local' | 'hub'
async function searchKnowledge(query, opts) {
  var o = opts || {};
  var mode = o.mode || 'all';
  var maxResults = o.maxResults || o.max_results || MAX_RESULTS;

  var localResults = [];
  var hubRemote = { results: [], error: null };

  if (mode === 'local' || mode === 'all') {
    localResults = await searchLocal(query, o);
  }

  if ((mode === 'hub' || mode === 'all') && getHubUrl()) {
    hubRemote = await searchRemote(query, o);
  }

  var hubResults = hubRemote.results || [];
  var results = mergeResults(localResults, hubResults, maxResults);

  var localMethod = localResults.length > 0 && localResults[0].search_method ? localResults[0].search_method : 'tfidf';

  var output = {
    query: query,
    results: results,
    local_count: localResults.length,
    hub_count: hubResults.length,
    total_candidates: localResults.length + hubResults.length,
    threshold: typeof o.threshold === 'number' ? o.threshold : RELEVANCE_THRESHOLD,
    hub_available: !!getHubUrl(),
    mode: mode,
    search_method: localMethod,
  };

  if (hubRemote.error === 'insufficient_balance') {
    output.insufficient_balance = true;
    output.balance = hubRemote.balance;
    output.balance_message = hubRemote.message || 'Points balance is insufficient for hub search.';
  } else if (hubRemote.error === 'network_error') {
    output.hub_error = 'network';
    output.hub_error_message = 'Hub unreachable. Using local results only.';
  } else if (hubRemote.error && hubRemote.error !== null) {
    output.hub_error = hubRemote.error;
  }

  if (hubRemote.purchased_spark_ids) {
    output.purchased_spark_ids = hubRemote.purchased_spark_ids;
  }

  if (hubRemote.insufficient_at) {
    output.insufficient_at = hubRemote.insufficient_at;
    output.partial_purchase = true;
  }

  if (typeof hubRemote.balance === 'number') {
    output.balance = hubRemote.balance;
  }

  return output;
}

module.exports = {
  searchKnowledge: searchKnowledge,
  searchLocal: searchLocal,
  searchLocalFull: searchLocalFull,
  searchRemote: searchRemote,
  RELEVANCE_THRESHOLD: RELEVANCE_THRESHOLD,
  MAX_RESULTS: MAX_RESULTS,
};
