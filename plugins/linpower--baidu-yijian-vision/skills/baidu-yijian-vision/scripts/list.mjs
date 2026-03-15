#!/usr/bin/env node

import { readSkillJson } from './skill-writer.mjs';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const pluginRoot = path.resolve(__dirname, '../..');

/**
 * List all available skills (preset + registered)
 *
 * Reads from:
 * - skill/skill.json (registered skills)
 * - skill/preset-skills.json (preset skills)
 */

function readPresets() {
  const presetPath = path.join(pluginRoot, 'skill/preset-skills.json');
  if (!fs.existsSync(presetPath)) {
    return { presetSkills: [] };
  }
  try {
    return JSON.parse(fs.readFileSync(presetPath, 'utf-8'));
  } catch (err) {
    console.error(`Warning: Failed to read presets: ${err.message}`);
    return { presetSkills: [] };
  }
}

function main() {
  try {
    // Read registered skills
    const skillJson = readSkillJson(pluginRoot);
    const registered = (skillJson.tools || []).map(s => ({ ...s, source: 'registered' }));

    // Read preset skills
    const presetData = readPresets();
    const presets = (presetData.presetSkills || []).map(s => ({ ...s, source: 'preset' }));

    // Combine: registered skills take priority if epId duplicates
    const skillMap = new Map();
    presets.forEach(s => skillMap.set(s.epId, s));
    registered.forEach(s => skillMap.set(s.epId, s));
    const allSkills = Array.from(skillMap.values());

    if (allSkills.length === 0) {
      console.log('📭 No skills available.\n');
      console.log('Available preset skills are ready to use:');
      console.log('  YIJIAN_API_KEY=$KEY node scripts/invoke.mjs <ep-id> ...\n');
      console.log('To register a custom skill from Yijian:');
      console.log('  YIJIAN_API_KEY=$KEY node scripts/register.mjs <ep-id>\n');
      return;
    }

    console.log('Available Skills:\n');

    // Sort by source, then by name
    const sortedSkills = allSkills.sort((a, b) => {
      if (a.source !== b.source) {
        return a.source === 'registered' ? -1 : 1;
      }
      return (a.name || a.epId).localeCompare(b.name || b.epId);
    });

    let currentSource = '';
    sortedSkills.forEach(skill => {
      if (skill.source !== currentSource) {
        currentSource = skill.source;
        const header = currentSource === 'registered' ? '📌 REGISTERED SKILLS' : '📚 PRESET SKILLS';
        console.log(header);
      }

      const icon = skill.source === 'registered' ? '📍' : '⭐';
      console.log(`  ${icon} ${skill.epId.padEnd(25)} ${skill.name || '(no name)'}`);
      if (skill.description) {
        console.log(`     ${skill.description}`);
      }
    });

    console.log();
    const regCount = registered.length;
    const presetCount = presets.length - registered.filter(r => presets.find(p => p.epId === r.epId)).length;
    console.log(`Total: ${allSkills.length} skill${allSkills.length !== 1 ? 's' : ''} (${regCount} registered, ${presetCount} preset)\n`);

    // Show sample invocation
    if (allSkills.length > 0) {
      const firstSkill = allSkills[0];
      console.log('Example - invoke a skill:');
      console.log(`  echo '{"input0":{"image":"photo.jpg"}}' | node scripts/invoke.mjs ${firstSkill.epId}\n`);
    }
  } catch (err) {
    console.error('❌ Error:', err.message);
    process.exit(1);
  }
}

main();
