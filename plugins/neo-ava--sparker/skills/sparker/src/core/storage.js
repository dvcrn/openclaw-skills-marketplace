// STP asset storage — file-backed persistence for sparks, embers, practice records,
// extraction sessions, digest reports, and capability maps.
// Uses __dirname-relative paths so CLI works from any working directory.

var fs = require('fs');
var path = require('path');

var SKILL_ROOT = path.resolve(__dirname, '..', '..');

function getStpAssetsDir() {
  if (process.env.SPARK_ASSETS_DIR) return path.resolve(process.env.SPARK_ASSETS_DIR);
  if (process.env.STP_ASSETS_DIR) return path.resolve(process.env.STP_ASSETS_DIR);
  var sparkDir = path.join(SKILL_ROOT, 'assets', 'spark');
  var stpDir = path.join(SKILL_ROOT, 'assets', 'stp');
  if (fs.existsSync(stpDir) && !fs.existsSync(sparkDir)) return stpDir;
  return sparkDir;
}

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function resolvePath() {
  var segments = [getStpAssetsDir()];
  for (var i = 0; i < arguments.length; i++) {
    segments.push(arguments[i]);
  }
  return path.join.apply(path, segments);
}

function readJson(filePath, defaultValue) {
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch (e) {
    if (typeof defaultValue === 'function') return defaultValue();
    return defaultValue !== undefined ? defaultValue : {};
  }
}

function writeJson(filePath, data) {
  ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf8');
}

var PATHS = {
  capabilityMap: function () { return resolvePath('capability_map', 'capability_map.json'); },
  domains: function () { return resolvePath('capability_map', 'domains.json'); },
  rawSparks: function () { return resolvePath('raw_sparks', 'raw_sparks.jsonl'); },
  rawSparksSnapshot: function () { return resolvePath('raw_sparks', 'raw_sparks_snapshot.json'); },
  refinedSparks: function () { return resolvePath('refined_sparks', 'refined_sparks.json'); },
  embers: function () { return resolvePath('embers', 'embers.json'); },
  practiceRecords: function () { return resolvePath('practice_records', 'practice_records.jsonl'); },
  extractionSessions: function () { return resolvePath('extraction_sessions', 'sessions.jsonl'); },
  digestReports: function () { return resolvePath('digest_reports', 'digest_reports.jsonl'); },
};

// --- JSONL helpers ---

function readJsonl(filePath) {
  try {
    return fs.readFileSync(filePath, 'utf8')
      .split('\n')
      .filter(Boolean)
      .map(function (line) { return JSON.parse(line); });
  } catch (e) {
    return [];
  }
}

function appendJsonl(filePath, record) {
  ensureDir(path.dirname(filePath));
  fs.appendFileSync(filePath, JSON.stringify(record) + '\n', 'utf8');
}

// --- Raw Sparks ---

function readRawSparks() {
  return readJsonl(PATHS.rawSparks());
}

function readRawSparksWithSnapshot() {
  var snapshotPath = PATHS.rawSparksSnapshot();
  var snapshot = readJson(snapshotPath, null);
  var rawSparks = readRawSparks();

  if (snapshot && Array.isArray(snapshot.sparks)) {
    var snapshotMap = {};
    for (var i = 0; i < snapshot.sparks.length; i++) {
      snapshotMap[snapshot.sparks[i].id] = snapshot.sparks[i];
    }
    for (var j = 0; j < rawSparks.length; j++) {
      var overlay = snapshotMap[rawSparks[j].id];
      if (overlay) {
        Object.assign(rawSparks[j], overlay);
      }
    }
  }
  return rawSparks;
}

function writeRawSparksSnapshot(sparks) {
  writeJson(PATHS.rawSparksSnapshot(), {
    sparks: sparks,
    updated_at: new Date().toISOString(),
  });
}

function appendRawSpark(spark) {
  appendJsonl(PATHS.rawSparks(), spark);
  if (spark.domain) {
    _registerDomain(spark.domain);
  }
}

function _registerDomain(domain) {
  var rootDomain = domain.split('.')[0];

  var domainsPath = PATHS.domains();
  var domains = readJson(domainsPath, []);
  if (!Array.isArray(domains)) domains = [];
  if (domains.indexOf(rootDomain) === -1) {
    domains.push(rootDomain);
    writeJson(domainsPath, domains);
  }

  var capMapPath = PATHS.capabilityMap();
  var capMap = readJson(capMapPath, { domains: {}, updated_at: null });
  if (!capMap.domains) capMap.domains = {};
  if (!capMap.domains[rootDomain]) {
    capMap.domains[rootDomain] = {
      status: 'learning',
      score: 0,
      spark_count: 1,
      refined_count: 0,
      practice_count: 0,
      last_activity: new Date().toISOString(),
    };
  } else {
    capMap.domains[rootDomain].spark_count = (capMap.domains[rootDomain].spark_count || 0) + 1;
    capMap.domains[rootDomain].last_activity = new Date().toISOString();
  }
  capMap.updated_at = new Date().toISOString();
  writeJson(capMapPath, capMap);
}

// --- Refined Sparks ---

function readRefinedSparks() {
  var data = readJson(PATHS.refinedSparks(), { version: 1, sparks: [] });
  return Array.isArray(data.sparks) ? data.sparks : [];
}

function writeRefinedSparks(sparks) {
  writeJson(PATHS.refinedSparks(), { version: 1, sparks: sparks });
}

function appendRefinedSpark(spark) {
  var sparks = readRefinedSparks();
  sparks.push(spark);
  writeRefinedSparks(sparks);
}

function updateRefinedSpark(id, updates) {
  var sparks = readRefinedSparks();
  for (var i = 0; i < sparks.length; i++) {
    if (sparks[i].id === id) {
      Object.assign(sparks[i], updates);
      writeRefinedSparks(sparks);
      return sparks[i];
    }
  }
  return null;
}

// --- Embers ---

function readEmbers() {
  var data = readJson(PATHS.embers(), { version: 1, embers: [] });
  return Array.isArray(data.embers) ? data.embers : [];
}

function appendEmber(ember) {
  var data = readJson(PATHS.embers(), { version: 1, embers: [] });
  if (!Array.isArray(data.embers)) data.embers = [];
  data.embers.push(ember);
  writeJson(PATHS.embers(), data);
}

function updateEmber(id, updates) {
  var data = readJson(PATHS.embers(), { version: 1, embers: [] });
  if (!Array.isArray(data.embers)) data.embers = [];
  for (var i = 0; i < data.embers.length; i++) {
    if (data.embers[i].id === id) {
      Object.assign(data.embers[i], updates);
      writeJson(PATHS.embers(), data);
      return data.embers[i];
    }
  }
  return null;
}

// --- Practice Records ---

function readPracticeRecords() {
  return readJsonl(PATHS.practiceRecords());
}

function appendPracticeRecord(record) {
  appendJsonl(PATHS.practiceRecords(), record);
}

// --- Extraction Sessions ---

function readExtractionSessions() {
  return readJsonl(PATHS.extractionSessions());
}

function appendExtractionSession(session) {
  appendJsonl(PATHS.extractionSessions(), session);
}

// --- Digest Reports ---

function readDigestReports() {
  return readJsonl(PATHS.digestReports());
}

function appendDigestReport(report) {
  appendJsonl(PATHS.digestReports(), report);
}

module.exports = {
  getStpAssetsDir: getStpAssetsDir,
  ensureDir: ensureDir,
  resolvePath: resolvePath,
  readJson: readJson,
  writeJson: writeJson,
  PATHS: PATHS,
  readRawSparks: readRawSparks,
  readRawSparksWithSnapshot: readRawSparksWithSnapshot,
  writeRawSparksSnapshot: writeRawSparksSnapshot,
  appendRawSpark: appendRawSpark,
  readRefinedSparks: readRefinedSparks,
  writeRefinedSparks: writeRefinedSparks,
  appendRefinedSpark: appendRefinedSpark,
  updateRefinedSpark: updateRefinedSpark,
  readEmbers: readEmbers,
  appendEmber: appendEmber,
  updateEmber: updateEmber,
  readPracticeRecords: readPracticeRecords,
  appendPracticeRecord: appendPracticeRecord,
  readExtractionSessions: readExtractionSessions,
  appendExtractionSession: appendExtractionSession,
  readDigestReports: readDigestReports,
  appendDigestReport: appendDigestReport,
};
