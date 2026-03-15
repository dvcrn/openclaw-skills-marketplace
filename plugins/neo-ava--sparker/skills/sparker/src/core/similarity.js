// TF-IDF based similarity engine for spark search and chain detection.
// CJK-aware tokenization with character bigrams.

function tokenize(text) {
  if (!text) return [];
  var tokens = [];
  var words = String(text).toLowerCase().split(/[\s,，。.!！?？；;：:、\n\r\t()\[\]{}（）【】「」]+/);

  for (var i = 0; i < words.length; i++) {
    var w = words[i].trim();
    if (!w) continue;

    var cjkRanges = /[\u4e00-\u9fff\u3400-\u4dbf\u3000-\u303f]/;
    if (cjkRanges.test(w)) {
      var cjkChars = w.match(/[\u4e00-\u9fff\u3400-\u4dbf]+/g);
      if (cjkChars) {
        for (var c = 0; c < cjkChars.length; c++) {
          var seg = cjkChars[c];
          for (var ci = 0; ci < seg.length; ci++) {
            tokens.push(seg[ci]);
          }
          for (var bi = 0; bi < seg.length - 1; bi++) {
            tokens.push(seg[bi] + seg[bi + 1]);
          }
        }
      }
      var nonCjk = w.replace(/[\u4e00-\u9fff\u3400-\u4dbf]+/g, '').trim();
      if (nonCjk.length >= 2) tokens.push(nonCjk);
    } else if (w.length >= 2) {
      tokens.push(w);
    }
  }
  return tokens;
}

function buildTfVector(tokens) {
  var tf = {};
  for (var i = 0; i < tokens.length; i++) {
    tf[tokens[i]] = (tf[tokens[i]] || 0) + 1;
  }
  var maxFreq = 0;
  for (var t in tf) {
    if (tf[t] > maxFreq) maxFreq = tf[t];
  }
  if (maxFreq > 0) {
    for (var t2 in tf) {
      tf[t2] = tf[t2] / maxFreq;
    }
  }
  return tf;
}

function computeIdf(tokenizedDocs) {
  var n = tokenizedDocs.length;
  var df = {};
  for (var i = 0; i < n; i++) {
    var seen = {};
    for (var j = 0; j < tokenizedDocs[i].length; j++) {
      var token = tokenizedDocs[i][j];
      if (!seen[token]) {
        df[token] = (df[token] || 0) + 1;
        seen[token] = true;
      }
    }
  }
  var idf = {};
  for (var term in df) {
    idf[term] = Math.log((n + 1) / (df[term] + 1)) + 1;
  }
  return idf;
}

function cosineSimilarity(vecA, vecB) {
  var dot = 0;
  var normA = 0;
  var normB = 0;
  var allTerms = {};
  for (var a in vecA) allTerms[a] = true;
  for (var b in vecB) allTerms[b] = true;

  for (var term in allTerms) {
    var va = vecA[term] || 0;
    var vb = vecB[term] || 0;
    dot += va * vb;
    normA += va * va;
    normB += vb * vb;
  }

  if (normA === 0 || normB === 0) return 0;
  return dot / (Math.sqrt(normA) * Math.sqrt(normB));
}

function sparkToText(spark) {
  var parts = [];

  // V2 six-dimension fields (preferred)
  if (spark.when && spark.when.trigger) parts.push(spark.when.trigger);
  if (spark.where) {
    if (spark.where.domain) parts.push(spark.where.domain);
    if (spark.where.sub_domain) parts.push(spark.where.sub_domain);
    if (spark.where.scenario) parts.push(spark.where.scenario);
    if (spark.where.audience) parts.push(spark.where.audience);
  }
  if (spark.how && spark.how.summary) parts.push(spark.how.summary);
  if (spark.why) parts.push(spark.why);

  // V1 fallback fields (for old data without six dimensions)
  if (parts.length === 0) {
    if (spark.domain) parts.push(spark.domain);
    if (spark.content) parts.push(spark.content);
    if (spark.card && spark.card.heuristic) parts.push(spark.card.heuristic);
  }

  // Shared fields
  if (spark.summary) parts.push(spark.summary);
  if (spark.insight) {
    if (typeof spark.insight === 'string') {
      parts.push(spark.insight);
    } else if (spark.insight.rules) {
      parts.push(spark.insight.rules.join(' '));
    }
  }
  if (Array.isArray(spark.tags)) parts.push(spark.tags.join(' '));
  if (Array.isArray(spark.keywords)) parts.push(spark.keywords.join(' '));
  return parts.join(' ');
}

function computeSimilarities(queryText, items) {
  if (!items || items.length === 0) return [];

  var queryTokens = tokenize(queryText);
  var docTokensList = items.map(function (item) {
    return tokenize(sparkToText(item));
  });

  var allDocs = [queryTokens].concat(docTokensList);
  var idf = computeIdf(allDocs);

  var queryTf = buildTfVector(queryTokens);
  var queryVec = {};
  for (var qt in queryTf) {
    queryVec[qt] = queryTf[qt] * (idf[qt] || 1);
  }

  var results = [];
  for (var i = 0; i < items.length; i++) {
    var docTf = buildTfVector(docTokensList[i]);
    var docVec = {};
    for (var dt in docTf) {
      docVec[dt] = docTf[dt] * (idf[dt] || 1);
    }
    var score = cosineSimilarity(queryVec, docVec);
    results.push({ item: items[i], score: score });
  }

  results.sort(function (a, b) { return b.score - a.score; });
  return results;
}

module.exports = {
  sparkToText: sparkToText,
  computeSimilarities: computeSimilarities,
  tokenize: tokenize,
  buildTfVector: buildTfVector,
  computeIdf: computeIdf,
  cosineSimilarity: cosineSimilarity,
};
