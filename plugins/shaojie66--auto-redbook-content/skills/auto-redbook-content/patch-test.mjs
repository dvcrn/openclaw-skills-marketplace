import { readdir, readFile, stat } from 'fs/promises';
import { join, relative, resolve, sep, basename } from 'path';

const TEXT_FILE_EXTENSION_SET = new Set(['md', 'mdx', 'txt', 'json', 'json5', 'yaml', 'yml', 'toml', 'js', 'cjs', 'mjs', 'ts', 'tsx', 'jsx', 'py', 'sh', 'rb', 'go', 'rs', 'swift', 'kt', 'java', 'cs', 'cpp', 'c', 'h', 'hpp', 'sql', 'csv', 'ini', 'cfg', 'env', 'xml', 'html', 'css', 'scss', 'sass', 'svg']);

function normalizePath(p) {
  return p.split(sep).join('/');
}

async function listTextFiles(root) {
  const files = [];
  const absRoot = resolve(root);
  
  console.log('listTextFiles called with root:', root);
  console.log('absRoot:', absRoot);
  
  async function walk(dir) {
    console.log('Walking dir:', dir);
    const entries = await readdir(dir, { withFileTypes: true });
    console.log('Entries in', dir, ':', entries.map(e => e.name).join(', '));
    
    for (const entry of entries) {
      if (entry.name.startsWith('.')) {
        console.log('Skipping dotfile:', entry.name);
        continue;
      }
      if (entry.name === 'node_modules') {
        console.log('Skipping node_modules');
        continue;
      }
      
      const full = join(dir, entry.name);
      
      if (entry.isDirectory()) {
        await walk(full);
        continue;
      }
      
      if (!entry.isFile()) continue;
      
      const relPath = normalizePath(relative(absRoot, full));
      console.log('Processing file:', entry.name, '-> relPath:', relPath);
      
      if (!relPath) continue;
      
      const ext = relPath.split('.').at(-1)?.toLowerCase() ?? '';
      console.log('  ext:', ext, 'in set:', TEXT_FILE_EXTENSION_SET.has(ext));
      
      if (!ext || !TEXT_FILE_EXTENSION_SET.has(ext)) continue;
      
      const buffer = await readFile(full);
      files.push({ relPath, bytes: new Uint8Array(buffer) });
      console.log('  ✅ Added:', relPath);
    }
  }
  
  await walk(absRoot);
  return files;
}

// Simulate cmdPublish logic
const workdir = process.cwd();
const folderArg = '.';
const folder = folderArg ? resolve(workdir, folderArg) : null;

console.log('=== Simulating cmdPublish ===');
console.log('workdir:', workdir);
console.log('folderArg:', folderArg);
console.log('folder:', folder);

const folderStat = await stat(folder).catch(() => null);
console.log('folderStat:', folderStat ? 'exists, isDirectory=' + folderStat.isDirectory() : 'null');

const filesOnDisk = await listTextFiles(folder);
console.log('\n=== Results ===');
console.log('Total files:', filesOnDisk.length);

const hasSkill = filesOnDisk.some((file) => {
  const lower = file.relPath.toLowerCase();
  return lower === 'skill.md' || lower === 'skills.md';
});

console.log('Has SKILL.md:', hasSkill);
