#!/usr/bin/env node

import { readSkillJson, writeSkillJson } from './skill-writer.mjs';

function main() {
  const epId = process.argv[2];
  const pluginRoot = process.argv[3];

  if (!epId || !pluginRoot) {
    console.error('Usage: node update.mjs <ep-id> <plugin-root> --scope "description"');
    process.exit(1);
  }

  const skillJson = readSkillJson(pluginRoot);
  const toolIdx = skillJson.tools.findIndex(t => t.epId === epId);

  if (toolIdx === -1) {
    console.error(`Tool not found: ${epId}`);
    process.exit(1);
  }

  // Parse --scope flag
  const scopeIdx = process.argv.indexOf('--scope');
  if (scopeIdx !== -1 && scopeIdx + 1 < process.argv.length) {
    skillJson.tools[toolIdx].scope = process.argv[scopeIdx + 1];
  }

  // Write back to skill.json
  writeSkillJson(pluginRoot, skillJson);

  const tool = skillJson.tools[toolIdx];
  console.log(JSON.stringify({
    success: true,
    action: 'updated',
    skill: { epId, name: tool.name, scope: tool.scope || '' },
  }, null, 2));
}

main();
