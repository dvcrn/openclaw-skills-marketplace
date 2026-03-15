const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const filePath = process.argv[2];
if (!filePath) {
  console.error('Usage: node process-intel.js <file_path>');
  process.exit(1);
}

const baseName = path.basename(filePath);
const workspace = '/home/node/.openclaw/workspace';

try {
  console.log(`🧠 Processing intelligence: ${baseName}`);

  // 1. Extract
  console.log('--- Step 1: Extracting nodes ---');
  execSync(`node skills/mindgraph/extract.js ${filePath}`, { stdio: 'inherit' });

  // 2. Find the JSON output
  // extract.js saves to extracted/<basename>.<date>.json
  const extractedDir = path.join(workspace, 'skills/mindgraph/extracted');
  const files = fs.readdirSync(extractedDir);
  const match = files.find(f => f.startsWith(baseName) && f.endsWith('.json'));
  
  if (!match) {
    throw new Error(`Could not find extracted JSON for ${baseName}`);
  }

  const jsonPath = path.join(extractedDir, match);

  // 3. Import
  console.log('--- Step 2: Importing to MindGraph ---');
  execSync(`node skills/mindgraph/import.js ${jsonPath}`, { stdio: 'inherit' });

  // 4. Sync Markets
  console.log('--- Step 3: Syncing to Polymarket TimeSeries ---');
  execSync(`node sync-markets.js`, { stdio: 'inherit' });

  console.log('✅ Intelligence fully processed and synced.');
} catch (err) {
  console.error(`❌ Error processing intelligence: ${err.message}`);
  process.exit(1);
}
