#!/usr/bin/env node

// Sparker CLI — STP knowledge extraction, refinement, search, and lifecycle.
// Usage: node index.js <command> --file=<json_path> [options]
//    or: echo '<json>' | node index.js <command> [options]
// Commands: kindle, teach, digest, search, publish, forge, ingest, profile, review,
//           status, plan, post-task, report, strategy, login, register, bind, whoami, hub-url

var fs = require('fs');
var path = require('path');

var SKILL_ROOT = path.resolve(__dirname);

function readStdin() {
  try {
    return fs.readFileSync(0, 'utf8').trim();
  } catch (e) {
    return '';
  }
}

// Read JSON input: prefer --file flag over stdin to avoid shell escaping issues.
// If --file is given, read from that path and optionally delete the temp file.
function readJsonInput(flags) {
  var filePath = flags.file || flags.input;
  if (filePath) {
    try {
      var content = fs.readFileSync(path.resolve(filePath), 'utf8').trim();
      var resolvedDir = path.dirname(path.resolve(filePath));
      if (flags['cleanup'] !== false && (resolvedDir === '/tmp' || /^[A-Za-z]:\\tmp$/i.test(resolvedDir))) {
        try { fs.unlinkSync(path.resolve(filePath)); } catch (e) { /* best-effort cleanup */ }
      }
      return content;
    } catch (e) {
      process.stderr.write('[sparker] Error reading --file=' + filePath + ': ' + e.message + '\n');
      return '';
    }
  }
  return readStdin();
}

function parseArgs() {
  var args = process.argv.slice(2);
  var command = args[0] || '';
  var rest = args.slice(1);
  var flags = {};
  var positional = [];
  for (var i = 0; i < rest.length; i++) {
    if (rest[i].startsWith('--')) {
      var kv = rest[i].slice(2).split('=');
      flags[kv[0]] = kv.length > 1 ? kv.slice(1).join('=') : true;
    } else {
      positional.push(rest[i]);
    }
  }
  return { command: command, flags: flags, positional: positional };
}

var CORRECTION_SIGNALS = [
  /改成/, /不对/, /太.了/, /应该是/, /错了/, /不是.*而是/,
  /把.*换成/, /修改/, /纠正/, /更正/,
];

function inferSource(params) {
  if (params.source !== 'human_teaching') return params.source;
  var content = String(params.content || '');
  for (var i = 0; i < CORRECTION_SIGNALS.length; i++) {
    if (CORRECTION_SIGNALS[i].test(content)) {
      return 'human_feedback';
    }
  }
  return params.source;
}

function getConfidenceForSource(source) {
  var map = {
    human_teaching: 0.70,
    iterative_refinement: 0.50,
    human_feedback: 0.40,
    micro_probe: 0.40,
    task_negotiation: 0.35,
    human_choice: 0.30,
    casual_mining: 0.25,
    agent_exchange: 0.25,
    web_exploration: 0.20,
    self_diagnosis: 0.20,
    post_task: 0.15,
  };
  return map[source] || 0.20;
}

async function handleKindle(stdinData) {
  var params;
  try {
    params = JSON.parse(stdinData);
  } catch (e) {
    process.stderr.write('Error: invalid JSON input\n');
    process.exit(1);
  }

  var originalSource = params.source || 'human_teaching';
  params.source = inferSource(params);
  if (params.source !== originalSource) {
    process.stderr.write('[sparker] Source auto-reclassified: ' + originalSource + ' → ' + params.source + '\n');
  }

  // V2 format: validate six-dimension fields
  if (params.how && params.how.summary) {
    // New format — no need for card.heuristic warning
  } else if (params.card && (!params.card.heuristic || !String(params.card.heuristic).trim())) {
    process.stderr.write('[sparker] Warning: card.heuristic / how.summary is empty. Spark may have low search relevance.\n');
  }

  if (typeof params.confidence !== 'number') {
    params.confidence = getConfidenceForSource(params.source);
  }

  var extractor = require('./src/kindle/extractor');
  var { appendRawSpark } = require('./src/core/storage');

  var spark;
  switch (params.source) {
    case 'human_teaching':
      spark = await extractor.extractFromTeaching(params);
      break;
    case 'human_feedback':
      spark = await extractor.extractFromFeedback(params);
      break;
    case 'human_choice':
      params.is_choice = true;
      spark = await extractor.extractFromFeedback(params);
      break;
    case 'task_negotiation':
      spark = await extractor.extractFromTaskNegotiation(params);
      break;
    case 'iterative_refinement':
      spark = await extractor.extractFromIterativeRefinement(params);
      break;
    case 'casual_mining':
    case 'post_task':
    case 'self_diagnosis':
      spark = await extractor.extractFromObservation(params);
      break;
    case 'web_exploration':
      spark = await extractor.extractFromExploration(params);
      break;
    case 'agent_exchange':
      spark = await extractor.extractFromAgentExchange(params);
      break;
    case 'micro_probe':
      spark = await extractor.extractFromFeedback(params);
      break;
    default:
      spark = extractor.createRawSpark(params);
      break;
  }

  appendRawSpark(spark);
  try {
    require('./src/core/search-index').rebuildSearchIndex();
    await require('./src/core/search-index').computeIndexEmbeddings();
  } catch (e) { /* best-effort */ }
  console.log(JSON.stringify(spark));
}

async function handleTeach(args) {
  var domain = args.positional[0] || 'general';
  var { appendExtractionSession } = require('./src/core/storage');
  var { generateId } = require('./src/core/asset-id');

  var session = {
    id: generateId('session'),
    type: 'ExtractionSession',
    domain: domain,
    method: 'structured_extraction',
    status: 'active',
    sparks_created: [],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  };

  appendExtractionSession(session);
  console.log(JSON.stringify(session));
}

async function handleDigest(args) {
  var { runDigest } = require('./src/temper/digest');
  var opts = {};
  if (args.flags.hours) opts.hours = Number(args.flags.hours);
  if (args.flags.days) opts.days = Number(args.flags.days);
  if (args.flags['dry-run'] || args.flags.dryRun) opts.dryRun = true;
  var report = await runDigest(opts);
  if (!opts.dryRun) {
    try {
      require('./src/core/search-index').rebuildSearchIndex();
      await require('./src/core/search-index').computeIndexEmbeddings();
    } catch (e) { /* best-effort */ }
  }
  console.log(JSON.stringify(report));
}

async function handleSearch(stdinData, args) {
  var query = stdinData || args.positional.join(' ');
  if (!query) {
    process.stderr.write('Usage: echo "query" | node index.js search\n       node index.js search "your query" [--hub] [--local] [--domain=X]\n');
    process.exit(1);
  }
  var { searchKnowledge } = require('./src/transmit/search');
  var opts = {};
  if (args.flags.domain) opts.domain = args.flags.domain;
  if (args.flags.threshold) opts.threshold = Number(args.flags.threshold);
  if (args.flags.max) opts.maxResults = Number(args.flags.max);
  if (args.flags.hub) opts.mode = 'hub';
  else if (args.flags.local) opts.mode = 'local';
  var results = await searchKnowledge(query, opts);
  console.log(JSON.stringify(results));
}

async function handlePublish(args) {
  var sparkId = args.positional[0];
  if (!sparkId) {
    process.stderr.write('Usage: node index.js publish <refined_spark_id> [--category-id=X] [--category-path=industry/domain/sub_direction]\n');
    process.exit(1);
  }
  var { publishEmber } = require('./src/transmit/publisher');
  var opts = {};
  if (args.flags.visibility) opts.visibility = args.flags.visibility;
  if (args.flags['owner-confirmed']) opts.ownerConfirmed = true;
  if (args.flags['category-id']) opts.category_id = args.flags['category-id'];
  if (args.flags['category-path']) {
    var parts = args.flags['category-path'].split('/');
    if (parts.length === 3) {
      opts.category_path = { industry: parts[0], domain: parts[1], sub_direction: parts[2] };
    }
  }
  var result = await publishEmber(sparkId, opts);
  console.log(JSON.stringify(result));
}

async function handleCategories() {
  var { hubGetCategoryTree, formatCategoryTree, getHubUrl } = require('./src/transmit/hub-client');
  if (!getHubUrl()) {
    process.stderr.write('[sparker] Hub URL not configured; cannot fetch categories.\n');
    console.log(JSON.stringify({ ok: false, error: 'hub_not_configured', tree: [] }));
    return;
  }
  var result = await hubGetCategoryTree();
  if (!result.ok) {
    console.log(JSON.stringify(result));
    return;
  }
  var text = formatCategoryTree(result.tree, 0, result.level_semantics);
  console.log(JSON.stringify({ ok: true, tree: result.tree, level_semantics: result.level_semantics || null, display: text }));
}

async function handleForge(args) {
  var { forgeAll } = require('./src/forge/forge-engine');
  var opts = {};
  if (args.flags.force) opts.force = true;
  if (args.flags.domain) opts.domain = args.flags.domain;
  var result = await forgeAll(opts);
  console.log(JSON.stringify(result));
}

async function handleIngest(args) {
  var targetPath = args.positional[0];
  if (!targetPath) {
    process.stderr.write('Usage: node index.js ingest <file_or_directory>\n');
    process.exit(1);
  }
  var { ingestPath } = require('./src/kindle/ingest');
  var opts = {};
  if (args.flags.domain) opts.domain = args.flags.domain;
  if (args.flags['auto-confirm']) opts.auto_confirm = true;
  if (args.flags['dry-run']) opts.dry_run = true;
  var result = await ingestPath(targetPath, opts);
  console.log(JSON.stringify(result));
}

async function handleProfile(args) {
  var domain = args.positional[0] || 'general';
  var { generateProfile, readPreferenceMap } = require('./src/core/preference-map');
  if (args.flags.read) {
    var map = readPreferenceMap(domain);
    console.log(JSON.stringify(map));
  } else {
    var profile = await generateProfile(domain);
    console.log(JSON.stringify(profile));
  }
}

async function handleFeedback(stdinData, args) {
  var { hubVote, getHubUrl } = require('./src/transmit/hub-client');
  var { enqueueRetry } = require('./src/transmit/publisher');
  if (!getHubUrl()) {
    process.stderr.write('[sparker] Hub URL not configured; feedback skipped.\n');
    console.log(JSON.stringify({ ok: false, error: 'hub_not_configured' }));
    return;
  }
  var params = {};
  var pos = (args && args.positional) || [];
  if (stdinData && stdinData.trim()) {
    try {
      params = JSON.parse(stdinData);
    } catch (e) {
      process.stderr.write('Usage: node index.js feedback <spark_id> [positive|negative] [reason]\n');
      process.stderr.write('   or: node index.js feedback --file=<json_path>\n');
      process.exit(1);
    }
  } else if (pos.length >= 1) {
    params.emberIdsUsed = [pos[0]];
    var p2 = (pos[1] || 'positive').toLowerCase();
    params.type = (p2 === 'downvote' || p2 === 'negative') ? 'negative' : 'positive';
    if (pos[2]) params.reason = pos.slice(2).join(' ');
  }
  var type = (params.type || 'positive').toLowerCase();
  var voteType = type === 'negative' ? 'downvote' : 'upvote';
  var ids = params.emberIdsUsed || params.sparkIdsUsed || (params.spark_id ? [params.spark_id] : []);
  if (!Array.isArray(ids)) ids = [ids];
  if (ids.length === 0) {
    process.stderr.write('Usage: node index.js feedback <spark_id> [positive|negative] [reason]\n');
    process.stderr.write('   or: node index.js feedback --file=<json_path>\n');
    process.exit(1);
  }
  var results = [];
  for (var i = 0; i < ids.length; i++) {
    try {
      var r = await hubVote(ids[i], voteType, { reason: params.reason });
      var httpOk = r && r.ok;
      var responsePayload = (r && r.response) || {};
      var voteResult = {
        id: ids[i],
        vote: voteType,
        ok: httpOk,
        is_new_vote: responsePayload.is_new_vote !== undefined ? responsePayload.is_new_vote : null,
        credibility_after: responsePayload.credibility_score !== undefined ? responsePayload.credibility_score : null,
        already_voted: responsePayload.already_voted || false,
      };
      if (!httpOk) {
        voteResult.error = (r && r.error) || 'hub_error';
        enqueueRetry({
          type: 'vote',
          spark_id: ids[i],
          vote_type: voteType,
          reason: params.reason || null,
          error: voteResult.error,
        });
        process.stderr.write('[sparker] Vote failed for ' + ids[i] + ', queued for retry.\n');
      }
      results.push(voteResult);
    } catch (e) {
      results.push({ id: ids[i], vote: voteType, ok: false, error: e.message });
      enqueueRetry({
        type: 'vote',
        spark_id: ids[i],
        vote_type: voteType,
        reason: params.reason || null,
        error: e.message,
      });
    }
  }
  console.log(JSON.stringify({ ok: results.every(function (x) { return x.ok; }), results: results }));
}

function handleStatus() {
  var storage = require('./src/core/storage');
  var { readCapabilityMap } = require('./src/core/capability-map');
  var { getIdentity } = require('./src/transmit/auth');

  var raw = storage.readRawSparks();
  var refined = storage.readRefinedSparks();
  var embers = storage.readEmbers();
  var practice = storage.readPracticeRecords();
  var digests = storage.readDigestReports();
  var capMap = readCapabilityMap();

  var trustedRaw = raw.filter(function (s) {
    return s.confirmation_status === 'human_confirmed' || s.confidence >= 0.40;
  });

  var identity = getIdentity();

  var status = {
    total_raw_sparks: raw.length,
    active_raw_sparks: raw.filter(function (s) { return s.status === 'active'; }).length,
    trusted_raw: trustedRaw.length,
    total_refined_sparks: refined.length,
    total_embers: embers.length,
    total_practice_records: practice.length,
    total_digest_reports: digests.length,
    domains: Object.keys(capMap.domains || {}),
    capability_map_updated: capMap.updated_at || null,
    fast_path_ready: trustedRaw.length >= 3,
    ready: raw.length >= 5,
    hub: {
      url: identity.hub_url,
      bound: identity.bound,
      node_id: identity.node_id,
      agent_name: identity.agent_name,
    },
  };

  console.log(JSON.stringify(status));
}

async function handleReview(stdinData) {
  var storage = require('./src/core/storage');
  var params;
  try {
    params = JSON.parse(stdinData);
  } catch (e) {
    var embers = storage.readEmbers();
    var candidates = embers
      .filter(function (e) { return e.status === 'candidate'; })
      .slice(0, 5);
    console.log(JSON.stringify({
      review_candidates: candidates.map(function (e) {
        return { id: e.id, domain: e.domain, summary: e.summary };
      }),
    }));
    return;
  }

  var { applyExternalVote } = require('./src/core/credibility');
  var ember = storage.readEmbers().find(function (e) { return e.id === params.ember_id; });
  if (!ember) {
    console.log(JSON.stringify({ error: 'ember_not_found' }));
    return;
  }
  applyExternalVote(ember.credibility, params.vote || 'upvote', params.voter_reputation || 1.0);
  storage.updateEmber(ember.id, { credibility: ember.credibility });
  console.log(JSON.stringify({ ok: true, ember_id: ember.id, credibility: ember.credibility }));
}

async function handlePlan(args) {
  var storage = require('./src/core/storage');
  var { generateId } = require('./src/core/asset-id');
  var { readCapabilityMap, writeCapabilityMap } = require('./src/core/capability-map');

  var domain = args.positional[0] || 'general';
  var goal = args.positional[1] || '';

  var capMap = readCapabilityMap();
  var rootDomain = domain.split('.')[0];
  var isNewDomain = !capMap.domains[rootDomain];

  if (isNewDomain) {
    capMap.domains[rootDomain] = {
      status: 'blind_spot',
      score: 0,
      sub_domains: {},
      spark_count: 0,
      refined_count: 0,
      practice_count: 0,
      last_activity: new Date().toISOString(),
    };
    writeCapabilityMap(capMap);
  }

  var plan = {
    id: generateId('plan'),
    domain: domain,
    goal: goal,
    phase: 'research',
    status: 'active',
    sub_skills: [],
    is_new_domain: isNewDomain,
    created_at: new Date().toISOString(),
  };

  var planPath = storage.resolvePath('cold_start_plans.json');
  var plans = storage.readJson(planPath, []);
  if (!Array.isArray(plans)) plans = [];
  plans.push(plan);
  storage.writeJson(planPath, plans);

  console.log(JSON.stringify(plan));
}

function handlePostTask(stdinData) {
  var params;
  try {
    params = JSON.parse(stdinData);
  } catch (e) {
    process.stderr.write('Error: invalid JSON input for post-task\n');
    process.exit(1);
  }

  var { appendRawSpark, appendPracticeRecord } = require('./src/core/storage');
  var { generateId } = require('./src/core/asset-id');
  var extractor = require('./src/kindle/extractor');

  var results = { extracted: 0, sparks: [], practice_recorded: false };

  if (params.user_correction) {
    var spark = extractor.extractFromFeedback({
      source: 'human_feedback',
      trigger: 'user_corrected_output',
      extraction_method: 'feedback',
      content: 'User corrected: ' + params.user_correction,
      domain: params.domain || 'general',
      card: params.card || { heuristic: params.user_correction, heuristic_type: 'rule' },
    });
    appendRawSpark(spark);
    results.extracted++;
    results.sparks.push(spark);
  }

  if (params.sparks_used && params.sparks_used.length > 0) {
    for (var i = 0; i < params.sparks_used.length; i++) {
      var usage = params.sparks_used[i];
      var record = {
        type: 'PracticeRecord',
        id: generateId('practice'),
        spark_id: usage.spark_id,
        spark_type: usage.spark_type || 'RawSpark',
        task_id: params.task_id || generateId('task'),
        agent_id: require('./src/core/asset-id').getNodeId(),
        applied: true,
        outcome: params.outcome || 'accepted',
        usage_type: usage.usage_type || 'soft_constraint',
        estimated_impact: usage.estimated_impact || 'medium',
        counterfactual: usage.counterfactual || '',
        domain: params.domain || 'general',
        created_at: new Date().toISOString(),
      };
      appendPracticeRecord(record);
      results.practice_recorded = true;
    }
  }

  console.log(JSON.stringify(results));
}

function handleReport() {
  var storage = require('./src/core/storage');
  var { readCapabilityMap } = require('./src/core/capability-map');

  var raw = storage.readRawSparks();
  var refined = storage.readRefinedSparks();
  var embers = storage.readEmbers();
  var capMap = readCapabilityMap();

  var report = {
    capability_map: capMap,
    statistics: {
      raw_sparks: raw.length,
      refined_sparks: refined.length,
      embers: embers.length,
      active_raw: raw.filter(function (s) { return s.status === 'active'; }).length,
      mastered_domains: 0,
      learning_domains: 0,
      blind_spots: 0,
    },
  };

  for (var d in capMap.domains) {
    var st = capMap.domains[d].status;
    if (st === 'mastered') report.statistics.mastered_domains++;
    else if (st === 'learning' || st === 'proficient') report.statistics.learning_domains++;
    else if (st === 'blind_spot') report.statistics.blind_spots++;
  }

  console.log(JSON.stringify(report));
}

function handleStrategy(args) {
  var domain = args.positional[0] || 'general';
  var { readCapabilityMap } = require('./src/core/capability-map');
  var storage = require('./src/core/storage');

  var capMap = readCapabilityMap();
  var rootDomain = domain.split('.')[0];
  var entry = capMap.domains[rootDomain];
  var raw = storage.readRawSparks().filter(function (s) {
    return (s.domain || '').startsWith(rootDomain);
  });

  var mode = 'cold_start';
  if (entry) {
    if (entry.status === 'mastered' || entry.status === 'proficient') mode = 'cruise';
    else if (entry.spark_count >= 5 || entry.practice_count >= 2) mode = 'active';
  }

  console.log(JSON.stringify({
    domain: domain,
    mode: mode,
    status: entry ? entry.status : 'blind_spot',
    spark_count: raw.length,
    probe_budget: mode === 'cold_start' ? 3 : (mode === 'active' ? 2 : 1),
  }));
}

// --- Hub identity commands ---

async function handleLogin(args) {
  var { loginToHub } = require('./src/transmit/auth');
  var email = args.flags.email || args.positional[0];
  var password = args.flags.password || args.positional[1];
  if (!email || !password) {
    process.stderr.write('Usage: node index.js login --email=you@example.com --password=xxx\n');
    process.exit(1);
  }
  var result = await loginToHub(email, password);
  console.log(JSON.stringify(result));
}

async function handleRegister(args) {
  var { registerOnHub } = require('./src/transmit/auth');
  var email = args.flags.email || args.positional[0];
  var password = args.flags.password || args.positional[1];
  var invite = args.flags.invite || args.flags['invite-code'] || args.positional[2];
  if (!email || !password || !invite) {
    process.stderr.write('Usage: node index.js register --email=you@example.com --password=xxx --invite=CODE\n');
    process.exit(1);
  }
  var result = await registerOnHub(email, password, invite);
  console.log(JSON.stringify(result));
}

async function handleBind(args) {
  var { saveBindingKey, getIdentity, validateBindingKey } = require('./src/transmit/auth');
  var key = args.positional[0] || args.flags.key;
  if (!key) {
    process.stderr.write('Usage: node index.js bind <binding_key>\n');
    process.stderr.write('  Get your binding key from SparkLand dashboard or via: node index.js login\n');
    process.exit(1);
  }
  saveBindingKey(key);
  var identity = getIdentity();

  // Validate connectivity after saving
  var validation = await validateBindingKey();
  var result = { ok: true, message: 'Binding key saved', identity: identity };
  if (!validation.ok && validation.error === 'binding_key_invalid') {
    result.warning = 'Binding key saved but hub returned ' + validation.status + '. The key may be invalid.';
  } else if (!validation.ok && validation.error === 'network_error') {
    result.warning = 'Binding key saved but hub is unreachable. Will validate on next request.';
  }
  console.log(JSON.stringify(result));
}

async function handleWhoami(args) {
  var { getIdentity, validateBindingKey } = require('./src/transmit/auth');
  var identity = getIdentity();
  if (args && args.flags.check) {
    var validation = await validateBindingKey();
    identity.hub_reachable = validation.ok || validation.reachable || false;
    identity.validation = validation;
  }
  console.log(JSON.stringify(identity));
}

function handleHubUrl(args) {
  var { saveHubUrl, getHubUrl } = require('./src/transmit/auth');
  var url = args.positional[0];
  if (!url) {
    var current = getHubUrl();
    console.log(JSON.stringify({ hub_url: current || '(not set)' }));
    return;
  }
  saveHubUrl(url);
  console.log(JSON.stringify({ ok: true, hub_url: url }));
}

async function handleDailyReport() {
  var storage = require('./src/core/storage');
  var { readCapabilityMap } = require('./src/core/capability-map');
  var { runDigest } = require('./src/temper/digest');

  var report = await runDigest({ hours: 24 });
  var capMap = readCapabilityMap();
  var raw = storage.readRawSparks();
  var refined = storage.readRefinedSparks();

  var today = new Date().toISOString().split('T')[0];
  var todayRaw = raw.filter(function (s) {
    return s.created_at && s.created_at.startsWith(today);
  });

  var atRisk = raw.filter(function (s) {
    return s.status === 'active' &&
      s.confirmation_status === 'human_confirmed' &&
      s.confidence < 0.35 && s.confidence > 0.10;
  });

  var capLines = [];
  for (var d in capMap.domains) {
    var dm = capMap.domains[d];
    var bar = '';
    var score = dm.score || 0;
    var filled = Math.round(score * 10);
    for (var i = 0; i < 10; i++) bar += i < filled ? '\u2588' : '\u2591';
    capLines.push('  ' + d + '  ' + bar + ' ' + dm.status + ' (' + score.toFixed(2) + ')');
    if (dm.sub_domains) {
      for (var sd in dm.sub_domains) {
        var sub = dm.sub_domains[sd];
        var sbar = '';
        var sscore = sub.score || 0;
        var sfilled = Math.round(sscore * 10);
        for (var si = 0; si < 10; si++) sbar += si < sfilled ? '\u2588' : '\u2591';
        capLines.push('  \u251C\u2500\u2500 ' + sd + '  ' + sbar + ' ' + sub.status + ' (' + sscore.toFixed(2) + ')');
      }
    }
  }

  var newRefinedLines = [];
  if (report && report.new_refined_sparks) {
    for (var ri = 0; ri < report.new_refined_sparks.length; ri++) {
      var rs = report.new_refined_sparks[ri];
      newRefinedLines.push((ri + 1) + '. [' + rs.domain + '] ' + rs.summary);
    }
  }

  var atRiskLines = [];
  for (var ai = 0; ai < atRisk.length && ai < 5; ai++) {
    var ar = atRisk[ai];
    var heuristic = (ar.card && ar.card.heuristic) || ar.content || '';
    var age = Math.round((Date.now() - new Date(ar.created_at).getTime()) / 86400000);
    atRiskLines.push('- [' + ar.domain + '] "' + heuristic.slice(0, 60) + '" \u2014 ' + age + '\u5929\u672a\u4f7f\u7528');
  }

  var output = {
    type: 'daily_report',
    date: today,
    summary: {
      new_raw_today: todayRaw.length,
      new_refined: newRefinedLines.length,
      total_raw: raw.length,
      total_refined: refined.length,
      at_risk_count: atRisk.length,
    },
    new_refined: newRefinedLines,
    capability_map: capLines,
    at_risk: atRiskLines,
    digest_skipped: report && report.skipped ? true : false,
  };

  console.log(JSON.stringify(output));
}

function handleMigrate(args) {
  var { migrateAllToV2 } = require('./src/ops/migration');
  var result = migrateAllToV2();
  console.log(JSON.stringify(result));
}

async function handleRebuildIndex(args) {
  var { rebuildSearchIndex, computeIndexEmbeddings } = require('./src/core/search-index');
  var { isEmbeddingAvailable } = require('./src/core/embedding');
  var index = rebuildSearchIndex();
  var embResult = null;
  var skipEmb = args && args.flags && args.flags['no-embeddings'];
  if (!skipEmb && isEmbeddingAvailable()) {
    embResult = await computeIndexEmbeddings();
  }
  console.log(JSON.stringify({
    ok: true,
    entries: index.entries.length,
    df_terms: Object.keys(index.df).length,
    built_at: index.built_at,
    embeddings: embResult || { skipped: true, reason: skipEmb ? 'flag' : 'no_config' },
  }));
}

async function handleRetry() {
  var { processRetryQueue, readRetryQueue } = require('./src/transmit/publisher');
  var queue = readRetryQueue();
  if (queue.length === 0) {
    console.log(JSON.stringify({ ok: true, message: 'Retry queue is empty', processed: 0, remaining: 0 }));
    return;
  }
  process.stderr.write('[sparker] Processing ' + queue.length + ' retry queue entries...\n');
  var result = await processRetryQueue();
  console.log(JSON.stringify(result));
}

async function main() {
  var args = parseArgs();
  var stdinData = '';

  var jsonInputCommands = ['kindle', 'search', 'review', 'post-task'];
  if (jsonInputCommands.indexOf(args.command) !== -1) {
    stdinData = readJsonInput(args.flags);
  } else if (args.command === 'feedback' && (!args.positional || args.positional.length === 0)) {
    stdinData = readJsonInput(args.flags);
  }

  switch (args.command) {
    case 'kindle':
      await handleKindle(stdinData);
      break;
    case 'teach':
      await handleTeach(args);
      break;
    case 'digest':
      await handleDigest(args);
      break;
    case 'search':
      await handleSearch(stdinData, args);
      break;
    case 'publish':
      await handlePublish(args);
      break;
    case 'categories':
      await handleCategories();
      break;
    case 'forge':
      await handleForge(args);
      break;
    case 'ingest':
      await handleIngest(args);
      break;
    case 'profile':
      await handleProfile(args);
      break;
    case 'review':
      await handleReview(stdinData);
      break;
    case 'feedback':
      await handleFeedback(stdinData, args);
      break;
    case 'status':
      handleStatus();
      break;
    case 'plan':
      await handlePlan(args);
      break;
    case 'post-task':
      handlePostTask(stdinData);
      break;
    case 'report':
      handleReport();
      break;
    case 'strategy':
      handleStrategy(args);
      break;
    case 'login':
      await handleLogin(args);
      break;
    case 'register':
      await handleRegister(args);
      break;
    case 'bind':
      await handleBind(args);
      break;
    case 'whoami':
      await handleWhoami(args);
      break;
    case 'daily-report':
      await handleDailyReport();
      break;
    case 'hub-url':
      handleHubUrl(args);
      break;
    case 'migrate':
      handleMigrate(args);
      break;
    case 'retry':
      await handleRetry();
      break;
    case 'rebuild-index':
      await handleRebuildIndex(args);
      break;
    default:
      process.stderr.write('Sparker CLI — STP knowledge engine\n\n');
      process.stderr.write('Hub Identity:\n');
      process.stderr.write('  login       Login to SparkLand and obtain binding key\n');
      process.stderr.write('  register    Register a new SparkLand account (invite required)\n');
      process.stderr.write('  bind <key>  Save a binding key locally\n');
      process.stderr.write('  whoami      Show current identity (node_id, agent, hub status)\n');
      process.stderr.write('  hub-url     Show or set SparkLand URL\n\n');
      process.stderr.write('Knowledge:\n');
      process.stderr.write('  kindle      Capture a spark (--file=<json_path> or stdin)\n');
      process.stderr.write('  teach       Start structured extraction session\n');
      process.stderr.write('  ingest      Import from file/directory\n');
      process.stderr.write('  search      Search local + hub knowledge\n');
      process.stderr.write('  publish     Publish RefinedSpark as Ember to hub\n');
      process.stderr.write('  categories  Fetch category tree from SparkHub (for pre-classification)\n');
      process.stderr.write('  feedback    Send vote (positive/negative) to hub for used sparks\n');
      process.stderr.write('  digest      Run periodic review\n');
      process.stderr.write('  forge       Crystallize Ember into Gene\n\n');
      process.stderr.write('Info:\n');
      process.stderr.write('  status        Show STP status and hub connection\n');
      process.stderr.write('  report        Generate capability report\n');
      process.stderr.write('  daily-report    Daily learning summary (for cron)\n');
      process.stderr.write('  profile         View domain preference profile\n');
      process.stderr.write('  strategy        Show adaptive learning strategy\n');
      process.stderr.write('  review          Review pending embers\n');
      process.stderr.write('  rebuild-index   Rebuild search index for faster queries\n');
      process.exit(1);
  }
}

main().catch(function (e) {
  process.stderr.write('Error: ' + e.message + '\n');
  process.exit(1);
});
