// .stpx export — portable spark archive for agent migration.

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const { getNodeId } = require('../core/asset-id');
const {
  readRawSparks, readRefinedSparks, readEmbers,
  readPracticeRecords, readExtractionSessions, getStpAssetsDir,
} = require('../core/storage');
const { readCapabilityMap } = require('../core/capability-map');

function exportStpx(outputPath, opts) {
  var o = opts || {};
  var agentName = o.agentName || process.env.AGENT_NAME || 'agent';
  var tmpDir = path.join(getStpAssetsDir(), '.stpx_tmp');

  // Clean up any previous tmp
  if (fs.existsSync(tmpDir)) fs.rmSync(tmpDir, { recursive: true });
  fs.mkdirSync(tmpDir, { recursive: true });

  var rawSparks = readRawSparks();
  var refinedSparks = readRefinedSparks();
  var embers = readEmbers();
  var practiceRecords = readPracticeRecords();
  var sessions = readExtractionSessions();
  var capMap = readCapabilityMap();

  // Write manifest
  var manifest = {
    stp_version: '1.0.0',
    schema_version: '1.0.0',
    created_at: new Date().toISOString(),
    agent_id: getNodeId(),
    agent_name: agentName,
    owner_id: o.ownerId || 'unknown',
    statistics: {
      total_raw_sparks: rawSparks.length,
      total_refined_sparks: refinedSparks.length,
      total_embers_published: embers.length,
      total_practice_records: practiceRecords.length,
      total_extraction_sessions: sessions.length,
      domains_covered: Object.keys(capMap.domains || {}).length,
      avg_composite_credibility: computeAvgCredibility(refinedSparks),
      mastered_domains: countByStatus(capMap, 'mastered'),
      learning_domains: countByStatus(capMap, 'learning'),
      blind_spots: countByStatus(capMap, 'blind_spot'),
    },
  };

  // Create subdirectories and write files
  var dirs = ['raw_sparks', 'refined_sparks', 'embers', 'practice_records', 'extraction_sessions', 'capability_map'];
  for (var i = 0; i < dirs.length; i++) {
    fs.mkdirSync(path.join(tmpDir, dirs[i]), { recursive: true });
  }

  fs.writeFileSync(path.join(tmpDir, 'manifest.json'), JSON.stringify(manifest, null, 2));
  writeJsonl(path.join(tmpDir, 'raw_sparks', 'raw_sparks.jsonl'), rawSparks);
  fs.writeFileSync(path.join(tmpDir, 'refined_sparks', 'refined_sparks.json'), JSON.stringify({ version: 1, sparks: refinedSparks }, null, 2));
  writeJsonl(path.join(tmpDir, 'refined_sparks', 'refined_sparks.jsonl'), refinedSparks);
  fs.writeFileSync(path.join(tmpDir, 'embers', 'embers.json'), JSON.stringify({ version: 1, embers: embers }, null, 2));
  writeJsonl(path.join(tmpDir, 'practice_records', 'practice_records.jsonl'), practiceRecords);
  writeJsonl(path.join(tmpDir, 'extraction_sessions', 'sessions.jsonl'), sessions);
  fs.writeFileSync(path.join(tmpDir, 'capability_map', 'capability_map.json'), JSON.stringify(capMap, null, 2));

  // Compute checksum
  var checksumData = JSON.stringify(manifest) + rawSparks.length + refinedSparks.length;
  var crypto = require('crypto');
  var checksum = crypto.createHash('sha256').update(checksumData).digest('hex');
  fs.writeFileSync(path.join(tmpDir, 'checksum.sha256'), checksum);

  // Create tar.gz
  var out = outputPath || path.join(process.cwd(), agentName + '.stpx');
  try {
    execSync('tar -czf "' + out + '" -C "' + path.dirname(tmpDir) + '" "' + path.basename(tmpDir) + '"');
  } catch (e) {
    // Fallback: just copy the directory
    var fallbackDir = out.replace('.stpx', '_stpx');
    fs.cpSync(tmpDir, fallbackDir, { recursive: true });
    fs.rmSync(tmpDir, { recursive: true });
    return { ok: true, path: fallbackDir, format: 'directory' };
  }

  // Cleanup
  fs.rmSync(tmpDir, { recursive: true });

  return { ok: true, path: out, format: 'tar.gz', manifest: manifest };
}

function writeJsonl(filePath, records) {
  var content = records.map(r => JSON.stringify(r)).join('\n');
  if (content) content += '\n';
  fs.writeFileSync(filePath, content, 'utf8');
}

function computeAvgCredibility(refinedSparks) {
  if (refinedSparks.length === 0) return 0;
  var total = refinedSparks.reduce((acc, s) => {
    return acc + (s.credibility ? s.credibility.composite : 0);
  }, 0);
  return parseFloat((total / refinedSparks.length).toFixed(3));
}

function countByStatus(capMap, status) {
  var count = 0;
  for (var d in capMap.domains || {}) {
    if (capMap.domains[d].status === status) count++;
  }
  return count;
}

module.exports = { exportStpx };
