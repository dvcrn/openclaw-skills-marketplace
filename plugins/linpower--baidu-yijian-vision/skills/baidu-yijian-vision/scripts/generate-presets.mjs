#!/usr/bin/env node

import { httpsRequest, getApiKey, metadataUrl, runUrl } from './utils.mjs';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PRESETS_FILE = path.join(__dirname, '../preset-skills.json');

/**
 * Fetch skill metadata from Yijian API
 */
async function fetchSkillMetadata(epId, apiKey) {
  const url = metadataUrl(epId);
  const response = await httpsRequest(url, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Accept': 'application/json',
    },
  });

  if (response.statusCode !== 200) {
    throw new Error(`Metadata request failed with status ${response.statusCode}: ${response.body}`);
  }

  let parsed;
  try {
    parsed = JSON.parse(response.body);
  } catch (err) {
    throw new Error(`Failed to parse metadata response: ${err.message}`);
  }

  if (!parsed.success || !parsed.result) {
    throw new Error(`Metadata response indicates failure: ${response.body}`);
  }

  return parsed.result;
}

/**
 * Build preset skill entry from metadata (same structure as registered tools)
 */
function buildPresetEntry(epId, metadata) {
  // Simplified inputs — one entry per schema field inside each DataSet input
  const inputs = [];
  for (const inp of metadata.inputs || []) {
    for (const field of inp.schema || []) {
      inputs.push({
        name: field.name,
        type: field.type,
        description: field.description || field.displayName || field.name,
        required: !field.optional,
      });
    }
  }

  // Simplified outputs
  const outputs = [];
  for (const out of metadata.outputs || []) {
    for (const field of out.schema || []) {
      outputs.push({
        name: field.name,
        type: field.type,
        description: field.description || field.displayName || field.name,
      });
    }
  }

  return {
    epId,
    name: metadata.displayName || metadata.name || epId,
    description: metadata.description || '',
    scope: '',
    version: metadata.version || '1.0',
    runUrl: runUrl(epId),
    inputs,
    outputs,
    rawInputs: metadata.inputs || [],
    rawOutputs: metadata.outputs || [],
    registeredAt: new Date().toISOString(),
  };
}

/**
 * Read existing presets
 */
function readPresets() {
  if (fs.existsSync(PRESETS_FILE)) {
    try {
      const content = fs.readFileSync(PRESETS_FILE, 'utf-8');
      return JSON.parse(content);
    } catch (err) {
      console.error(`Failed to read presets file: ${err.message}`);
      return { version: '1.0', description: 'Yijian preset skills library', lastUpdated: new Date().toISOString().split('T')[0], presetSkills: [] };
    }
  }
  return { version: '1.0', description: 'Yijian preset skills library', lastUpdated: new Date().toISOString().split('T')[0], presetSkills: [] };
}

/**
 * Write presets to file
 */
function writePresets(data) {
  fs.writeFileSync(PRESETS_FILE, JSON.stringify(data, null, 2) + '\n');
}

async function main() {
  const epIds = process.argv.slice(2);

  if (epIds.length === 0) {
    console.error('Usage: node generate-presets.mjs <ep-id> [<ep-id> ...]');
    console.error('Example: YIJIAN_API_KEY=xxx node generate-presets.mjs ep-public-0rgd8bq9 ep-public-inqm15aq');
    process.exit(1);
  }

  let apiKey;
  try {
    apiKey = getApiKey();
  } catch (err) {
    console.error(err.message);
    process.exit(1);
  }

  const presets = readPresets();
  const newSkills = [];

  for (const epId of epIds) {
    try {
      console.log(`Fetching metadata for ${epId}...`);
      const metadata = await fetchSkillMetadata(epId, apiKey);

      const entry = buildPresetEntry(epId, metadata);

      // Check if already exists
      const existingIdx = presets.presetSkills.findIndex(s => s.epId === epId);
      if (existingIdx >= 0) {
        presets.presetSkills[existingIdx] = entry;
        console.log(`✓ Updated: ${epId}`);
      } else {
        presets.presetSkills.push(entry);
        console.log(`✓ Added: ${epId}`);
      }

      newSkills.push({ epId, name: entry.name });
    } catch (err) {
      console.error(`✗ Failed to process ${epId}: ${err.message}`);
      // Continue processing other skills instead of exiting
    }
  }

  // Update timestamp
  presets.lastUpdated = new Date().toISOString().split('T')[0];

  // Write back
  writePresets(presets);

  // Output result
  const result = {
    success: true,
    addedCount: newSkills.length,
    skills: newSkills,
  };
  console.log(JSON.stringify(result, null, 2));
}

main();
