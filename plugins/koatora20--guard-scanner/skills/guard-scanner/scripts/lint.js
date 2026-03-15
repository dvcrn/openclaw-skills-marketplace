const { execFileSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const ROOT = path.join(__dirname, '..');
const targets = ['src', 'scripts', 'test'].flatMap((dir) => collect(path.join(ROOT, dir), '.js'));

for (const file of targets) {
  execFileSync(process.execPath, ['--check', file], { stdio: 'pipe' });
}

console.log(`✅ Syntax lint passed (${targets.length} JavaScript files)`);

function collect(dir, ext) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) files.push(...collect(fullPath, ext));
    else if (entry.name.endsWith(ext)) files.push(fullPath);
  }
  return files;
}
