#!/usr/bin/env node

import { readSkillJson, writeSkillJson } from './skill-writer.mjs';

function main() {
  const epId = process.argv[2];
  const pluginRoot = process.argv[3];

  if (!epId || !pluginRoot) {
    console.error('Usage: node delete.mjs <ep-id> <plugin-root>');
    process.exit(1);
  }

  const skillJson = readSkillJson(pluginRoot);
  const idx = skillJson.tools.findIndex(t => t.epId === epId);

  if (idx < 0) {
    console.error(`Skill "${epId}" is not registered.`);
    process.exit(1);
  }

  const deleted = skillJson.tools.splice(idx, 1)[0];
  writeSkillJson(pluginRoot, skillJson);

  console.log(JSON.stringify({
    success: true,
    action: 'deleted',
    epId,
    name: deleted.name,
  }, null, 2));
}

main();
