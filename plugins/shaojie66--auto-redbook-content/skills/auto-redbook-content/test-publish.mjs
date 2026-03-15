import { readdir, readFile } from 'fs/promises';
import { join, relative, resolve, sep } from 'path';

const TEXT_FILE_EXTENSION_SET = new Set(['md', 'mdx', 'txt', 'json', 'json5', 'yaml', 'yml', 'toml', 'js', 'cjs', 'mjs', 'ts', 'tsx', 'jsx', 'py', 'sh', 'rb', 'go', 'rs', 'swift', 'kt', 'java', 'cs', 'cpp', 'c', 'h', 'hpp', 'sql', 'csv', 'ini', 'cfg', 'env', 'xml', 'html', 'css', 'scss', 'sass', 'svg']);

function normalizePath(p) {
  return p.split(sep).join('/');
}

async function listTextFiles(root) {
  const files = [];
  const absRoot = resolve(root);
  
  async function walk(dir) {
    const entries = await readdir(dir, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.name.startsWith('.')) continue;
      if (entry.name === 'node_modules') continue;
      
      const full = join(dir, entry.name);
      
      if (entry.isDirectory()) {
        await walk(full);
        continue;
      }
      
      if (!entry.isFile()) continue;
      
      const relPath = normalizePath(relative(absRoot, full));
      if (!relPath) continue;
      
      const ext = relPath.split('.').at(-1)?.toLowerCase() ?? '';
      if (!ext || !TEXT_FILE_EXTENSION_SET.has(ext)) continue;
      
      const buffer = await readFile(full);
      files.push({ relPath, bytes: new Uint8Array(buffer) });
    }
  }
  
  await walk(absRoot);
  return files;
}

const folder = process.cwd();
const filesOnDisk = await listTextFiles(folder);

console.log('Total files:', filesOnDisk.length);
console.log('Files:', filesOnDisk.map(f => f.relPath).join('\n'));

const hasSkill = filesOnDisk.some((file) => {
  const lower = file.relPath.toLowerCase();
  return lower === 'skill.md' || lower === 'skills.md';
});

console.log('\nHas SKILL.md:', hasSkill);

if (!hasSkill) {
  console.error('ERROR: SKILL.md required');
  process.exit(1);
}

console.log('\n✅ Validation passed - SKILL.md found');
