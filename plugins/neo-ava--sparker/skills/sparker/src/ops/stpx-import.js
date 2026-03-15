// .stpx import — restore spark archive into current agent.

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const { appendRawSpark, appendRefinedSpark, appendEmber, appendPracticeRecord, appendExtractionSession, getStpAssetsDir } = require('../core/storage');
const { writeCapabilityMap } = require('../core/capability-map');

function importStpx(archivePath) {
  if (!fs.existsSync(archivePath)) return { ok: false, error: 'file not found' };

  var tmpDir = path.join(getStpAssetsDir(), '.stpx_import_tmp');
  if (fs.existsSync(tmpDir)) fs.rmSync(tmpDir, { recursive: true });
  fs.mkdirSync(tmpDir, { recursive: true });

  // Extract archive
  try {
    execSync('tar -xzf "' + archivePath + '" -C "' + tmpDir + '"');
  } catch (e) {
    fs.rmSync(tmpDir, { recursive: true });
    return { ok: false, error: 'failed to extract archive: ' + e.message };
  }

  // Find the inner directory
  var entries = fs.readdirSync(tmpDir);
  var baseDir = entries.length === 1 ? path.join(tmpDir, entries[0]) : tmpDir;

  var stats = { raw_sparks: 0, refined_sparks: 0, embers: 0, practice_records: 0, sessions: 0 };

  // Import raw sparks
  var rawPath = path.join(baseDir, 'raw_sparks', 'raw_sparks.jsonl');
  if (fs.existsSync(rawPath)) {
    var rawLines = fs.readFileSync(rawPath, 'utf8').split('\n').filter(Boolean);
    for (var i = 0; i < rawLines.length; i++) {
      try { appendRawSpark(JSON.parse(rawLines[i])); stats.raw_sparks++; } catch (e) {}
    }
  }

  // Import refined sparks
  var refinedPath = path.join(baseDir, 'refined_sparks', 'refined_sparks.json');
  if (fs.existsSync(refinedPath)) {
    try {
      var refinedData = JSON.parse(fs.readFileSync(refinedPath, 'utf8'));
      var sparks = Array.isArray(refinedData.sparks) ? refinedData.sparks : [];
      for (var j = 0; j < sparks.length; j++) { appendRefinedSpark(sparks[j]); stats.refined_sparks++; }
    } catch (e) {}
  }

  // Import embers
  var embersPath = path.join(baseDir, 'embers', 'embers.json');
  if (fs.existsSync(embersPath)) {
    try {
      var emberData = JSON.parse(fs.readFileSync(embersPath, 'utf8'));
      var embers = Array.isArray(emberData.embers) ? emberData.embers : [];
      for (var k = 0; k < embers.length; k++) { appendEmber(embers[k]); stats.embers++; }
    } catch (e) {}
  }

  // Import practice records
  var practicePath = path.join(baseDir, 'practice_records', 'practice_records.jsonl');
  if (fs.existsSync(practicePath)) {
    var prLines = fs.readFileSync(practicePath, 'utf8').split('\n').filter(Boolean);
    for (var m = 0; m < prLines.length; m++) {
      try { appendPracticeRecord(JSON.parse(prLines[m])); stats.practice_records++; } catch (e) {}
    }
  }

  // Import extraction sessions
  var sessionsPath = path.join(baseDir, 'extraction_sessions', 'sessions.jsonl');
  if (fs.existsSync(sessionsPath)) {
    var sLines = fs.readFileSync(sessionsPath, 'utf8').split('\n').filter(Boolean);
    for (var n = 0; n < sLines.length; n++) {
      try { appendExtractionSession(JSON.parse(sLines[n])); stats.sessions++; } catch (e) {}
    }
  }

  // Import capability map
  var capMapPath = path.join(baseDir, 'capability_map', 'capability_map.json');
  if (fs.existsSync(capMapPath)) {
    try {
      var capMap = JSON.parse(fs.readFileSync(capMapPath, 'utf8'));
      writeCapabilityMap(capMap);
    } catch (e) {}
  }

  // Read manifest
  var manifest = null;
  var manifestPath = path.join(baseDir, 'manifest.json');
  if (fs.existsSync(manifestPath)) {
    try { manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8')); } catch (e) {}
  }

  // Cleanup
  fs.rmSync(tmpDir, { recursive: true });

  return { ok: true, stats: stats, manifest: manifest };
}

module.exports = { importStpx };
