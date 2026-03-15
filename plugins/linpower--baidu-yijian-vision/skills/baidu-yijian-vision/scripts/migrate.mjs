#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import { readRegistry, REGISTRY_FILENAME } from './utils.mjs';
import { readSkillJson, writeSkillJson } from './skill-writer.mjs';

function main() {
  const projectDir = process.argv[2];
  const pluginRoot = process.argv[3];

  if (!projectDir || !pluginRoot) {
    console.error('Usage: node migrate.mjs <project-dir> <plugin-root>');
    console.error('  <project-dir>  — project root containing .claude/yijian-skills.local.md');
    console.error('  <plugin-root>  — plugin root containing skill/');
    process.exit(1);
  }

  const oldFile = path.join(projectDir, REGISTRY_FILENAME);
  if (!fs.existsSync(oldFile)) {
    console.error(`Old registry not found: ${oldFile}`);
    process.exit(1);
  }

  // Read old registry
  const registry = readRegistry(projectDir);
  const skills = registry.skills || {};
  const epIds = Object.keys(skills);

  if (epIds.length === 0) {
    console.log(JSON.stringify({ success: true, action: 'migrate', migrated: 0, message: 'No skills to migrate.' }));
    return;
  }

  // Read current skill.json (may already have tools)
  const skillJson = readSkillJson(pluginRoot);

  let migrated = 0;
  for (const epId of epIds) {
    const old = skills[epId];

    // Skip if already exists in skill.json
    if (skillJson.tools.some(t => t.epId === epId)) {
      continue;
    }

    // Build simplified inputs from old format
    const inputs = [];
    for (const inp of old.inputs || []) {
      for (const field of inp.schema || []) {
        inputs.push({
          name: field.name,
          type: field.type,
          description: field.description || field.displayName || field.name,
          required: !field.optional,
        });
      }
    }

    // Build simplified outputs from old format
    const outputs = [];
    for (const out of old.outputs || []) {
      for (const field of out.schema || []) {
        outputs.push({
          name: field.name,
          type: field.type,
          description: field.description || field.displayName || field.name,
        });
      }
    }

    skillJson.tools.push({
      epId,
      name: old.displayName || old.name || epId,
      description: old.description || '',
      scope: '',
      version: old.version || '1.0',
      runUrl: old.runUrl,
      inputs,
      outputs,
      rawInputs: old.inputs || [],
      rawOutputs: old.outputs || [],
      registeredAt: old.registeredAt || new Date().toISOString(),
    });
    migrated++;
  }

  // Write skill.json
  writeSkillJson(pluginRoot, skillJson);

  // Rename old file to .bak
  const bakFile = oldFile + '.bak';
  fs.renameSync(oldFile, bakFile);

  console.log(JSON.stringify({
    success: true,
    action: 'migrate',
    migrated,
    total: skillJson.tools.length,
    backupFile: bakFile,
  }, null, 2));
}

main();
