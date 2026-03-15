#!/usr/bin/env node

import { httpsRequest, getApiKey, metadataUrl, runUrl } from './utils.mjs';
import { readSkillJson, writeSkillJson, buildToolEntry, tryAutoMigrate } from './skill-writer.mjs';

async function main() {
  const epId = process.argv[2];
  const pluginRoot = process.argv[3];

  if (!epId || !pluginRoot) {
    console.error('Usage: node register.mjs <ep-id> <plugin-root> [--scope "description"]');
    process.exit(1);
  }

  // Parse optional --scope flag
  let scope = '';
  const scopeIdx = process.argv.indexOf('--scope');
  if (scopeIdx !== -1 && process.argv[scopeIdx + 1]) {
    scope = process.argv[scopeIdx + 1];
  }

  let apiKey;
  try {
    apiKey = getApiKey();
  } catch (err) {
    console.error(err.message);
    process.exit(1);
  }

  // Fetch metadata
  const url = metadataUrl(epId);
  let response;
  try {
    response = await httpsRequest(url, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Accept': 'application/json',
      },
    });
  } catch (err) {
    console.error(`Failed to fetch metadata: ${err.message}`);
    process.exit(1);
  }

  if (response.statusCode !== 200) {
    console.error(`Metadata request failed with status ${response.statusCode}: ${response.body}`);
    process.exit(1);
  }

  let parsed;
  try {
    parsed = JSON.parse(response.body);
  } catch (err) {
    console.error(`Failed to parse metadata response: ${err.message}`);
    process.exit(1);
  }

  if (!parsed.success || !parsed.result) {
    console.error(`Metadata response indicates failure: ${response.body}`);
    process.exit(1);
  }

  const metadata = parsed.result;

  // Build tool entry and update skill.json
  const toolEntry = buildToolEntry(epId, metadata, runUrl(epId), { scope });
  const skillJson = tryAutoMigrate(pluginRoot, readSkillJson(pluginRoot));

  const existingIdx = skillJson.tools.findIndex(t => t.epId === epId);
  const isUpdate = existingIdx >= 0;
  if (isUpdate) {
    skillJson.tools[existingIdx] = toolEntry;
  } else {
    skillJson.tools.push(toolEntry);
  }

  writeSkillJson(pluginRoot, skillJson);

  const result = {
    success: true,
    action: isUpdate ? 'updated' : 'registered',
    skill: { epId, name: toolEntry.name, description: toolEntry.description, version: toolEntry.version },
  };
  console.log(JSON.stringify(result, null, 2));
}

main();
