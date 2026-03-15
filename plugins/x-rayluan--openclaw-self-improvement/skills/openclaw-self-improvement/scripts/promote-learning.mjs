#!/usr/bin/env node
import fs from 'fs';
import path from 'path';

const [,, target, text] = process.argv;
if (!target || !text) {
  console.error('Usage: node promote-learning.mjs <workflow|tools|behavior|obsidian> <text>');
  process.exit(2);
}
const workspace = process.env.WORKSPACE || path.join(process.env.HOME, '.openclaw/workspace');
const targets = {
  workflow: path.join(workspace, 'AGENTS.md'),
  tools: path.join(workspace, 'TOOLS.md'),
  behavior: path.join(workspace, 'SOUL.md')
};
if (target === 'obsidian') {
  const outDir = '/Users/m1/Desktop/obsidianvault/ClawLite/Operations/Learnings';
  fs.mkdirSync(outDir, { recursive: true });
  const outPath = path.join(outDir, `${new Date().toISOString().slice(0,10)}-learning.md`);
  fs.appendFileSync(outPath, `\n- ${text}\n`);
  console.log(outPath);
  process.exit(0);
}
const file = targets[target];
if (!file) {
  console.error('target must be workflow|tools|behavior|obsidian');
  process.exit(2);
}
fs.appendFileSync(file, `\n- ${text}\n`);
console.log(file);
