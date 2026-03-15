// Precomputed search index — avoids repeated file I/O, tokenization, and TF
// computation on every search call. Index is rebuilt when data files change.
// Optionally stores embedding vectors for hybrid (TF-IDF + vector) search.

var fs = require('fs');
var path = require('path');
var { PATHS, readRawSparks, readRefinedSparks, readEmbers, readJson, ensureDir } = require('./storage');
var { tokenize, buildTfVector, sparkToText } = require('./similarity');

var SKILL_ROOT = path.resolve(__dirname, '..', '..');

function getIndexPath() {
  return path.join(SKILL_ROOT, 'assets', 'stp', 'search_index.json');
}

function getSourceMtimes() {
  var mtimes = {};
  var files = {
    raw_sparks: PATHS.rawSparks(),
    embers: PATHS.embers(),
    refined_sparks: PATHS.refinedSparks(),
  };
  for (var key in files) {
    try {
      mtimes[key] = fs.statSync(files[key]).mtimeMs;
    } catch (e) {
      mtimes[key] = 0;
    }
  }
  return mtimes;
}

function writeIndex(index) {
  var indexPath = getIndexPath();
  ensureDir(path.dirname(indexPath));
  fs.writeFileSync(indexPath, JSON.stringify(index), 'utf8');
}

function rebuildSearchIndex() {
  var rawSparks = readRawSparks().filter(function (s) { return s.status !== 'rejected'; });
  var embers = readEmbers();
  var refinedSparks = readRefinedSparks().filter(function (s) {
    return s.status === 'published' || s.status === 'active';
  });

  var allSparks = [].concat(rawSparks, embers, refinedSparks);

  // Load old index to preserve existing embeddings
  var oldEmbeddings = {};
  try {
    var oldIndex = readJson(getIndexPath(), null);
    if (oldIndex && Array.isArray(oldIndex.entries)) {
      for (var oi = 0; oi < oldIndex.entries.length; oi++) {
        var oe = oldIndex.entries[oi];
        if (oe.embedding) oldEmbeddings[oe.id] = oe.embedding;
      }
    }
  } catch (e) { /* no old index */ }

  var df = {};
  var entries = [];
  var embeddingCount = 0;

  for (var i = 0; i < allSparks.length; i++) {
    var spark = allSparks[i];
    var text = sparkToText(spark);
    var tokens = tokenize(text);
    var tf = buildTfVector(tokens);

    for (var term in tf) {
      df[term] = (df[term] || 0) + 1;
    }

    var sparkType = spark.type || 'unknown';
    if (sparkType === 'unknown') {
      if (spark.card) sparkType = 'RawSpark';
      else if (spark.insight) sparkType = 'RefinedSpark';
      else if (spark.source_refined_id) sparkType = 'Ember';
    }

    var existingEmb = oldEmbeddings[spark.id] || null;
    if (existingEmb) embeddingCount++;

    entries.push({
      id: spark.id,
      type: sparkType,
      domain: spark.domain || '',
      status: spark.status || 'active',
      tf: tf,
      embedding: existingEmb,
      spark: spark,
    });
  }

  var index = {
    version: 2,
    built_at: new Date().toISOString(),
    source_mtimes: getSourceMtimes(),
    corpus_size: entries.length,
    has_embeddings: embeddingCount > 0,
    embedding_count: embeddingCount,
    df: df,
    entries: entries,
  };

  writeIndex(index);
  return index;
}

// Incrementally compute embeddings for entries that don't have them yet.
// Preserves all existing index data; only adds/updates embedding fields.
async function computeIndexEmbeddings() {
  var { isEmbeddingAvailable, getEmbeddings } = require('./embedding');
  if (!isEmbeddingAvailable()) {
    return { ok: false, reason: 'no_embedding_config', computed: 0 };
  }

  var indexPath = getIndexPath();
  var index = readJson(indexPath, null);
  if (!index || !Array.isArray(index.entries)) {
    return { ok: false, reason: 'no_index', computed: 0 };
  }

  var missing = [];
  var missingIdx = [];
  for (var i = 0; i < index.entries.length; i++) {
    if (!index.entries[i].embedding) {
      missing.push(sparkToText(index.entries[i].spark));
      missingIdx.push(i);
    }
  }

  if (missing.length === 0) {
    return { ok: true, reason: 'all_present', computed: 0, total: index.entries.length };
  }

  process.stderr.write('[search-index] Computing embeddings for ' + missing.length + ' entries...\n');

  var vectors = await getEmbeddings(missing);
  var computed = 0;
  for (var j = 0; j < vectors.length; j++) {
    if (vectors[j]) {
      index.entries[missingIdx[j]].embedding = vectors[j];
      computed++;
    }
  }

  var embCount = 0;
  for (var k = 0; k < index.entries.length; k++) {
    if (index.entries[k].embedding) embCount++;
  }
  index.has_embeddings = embCount > 0;
  index.embedding_count = embCount;
  index.embeddings_updated_at = new Date().toISOString();

  writeIndex(index);
  process.stderr.write('[search-index] Embeddings computed: ' + computed + '/' + missing.length + ' (total: ' + embCount + '/' + index.entries.length + ')\n');

  return { ok: true, computed: computed, failed: missing.length - computed, total: index.entries.length, embedded: embCount };
}

function loadSearchIndex() {
  var indexPath = getIndexPath();
  var index;
  try {
    index = readJson(indexPath, null);
  } catch (e) {
    return null;
  }
  if (!index || !index.entries) return null;
  if (index.version !== 1 && index.version !== 2) return null;

  var currentMtimes = getSourceMtimes();
  var stored = index.source_mtimes || {};

  if (stored.raw_sparks !== currentMtimes.raw_sparks ||
      stored.embers !== currentMtimes.embers ||
      stored.refined_sparks !== currentMtimes.refined_sparks) {
    return null;
  }

  return index;
}

function invalidateSearchIndex() {
  var indexPath = getIndexPath();
  try { fs.unlinkSync(indexPath); } catch (e) { /* no-op */ }
}

module.exports = {
  rebuildSearchIndex: rebuildSearchIndex,
  computeIndexEmbeddings: computeIndexEmbeddings,
  loadSearchIndex: loadSearchIndex,
  invalidateSearchIndex: invalidateSearchIndex,
  getIndexPath: getIndexPath,
};
