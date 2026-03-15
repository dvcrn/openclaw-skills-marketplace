#!/usr/bin/env node

/**
 * wip-release/cli.mjs
 * Release tool CLI. Bumps version, updates docs, publishes.
 */

import { release, detectCurrentVersion } from './core.mjs';

const args = process.argv.slice(2);
const level = args.find(a => ['patch', 'minor', 'major'].includes(a));

function flag(name) {
  const prefix = `--${name}=`;
  const found = args.find(a => a.startsWith(prefix));
  return found ? found.slice(prefix.length) : null;
}

const dryRun = args.includes('--dry-run');
const noPublish = args.includes('--no-publish');
const skipProductCheck = args.includes('--skip-product-check');
const skipStaleCheck = args.includes('--skip-stale-check');
const notesFilePath = flag('notes-file');
let notes = flag('notes');
let notesSource = notes ? 'flag' : 'none'; // track where notes came from

// Auto-detect RELEASE-NOTES-v{version}.md if no --notes or --notes-file provided.
// Also supports explicit --notes-file for custom paths.
{
  const { readFileSync, existsSync } = await import('node:fs');
  const { resolve, join } = await import('node:path');

  if (notesFilePath) {
    // Explicit --notes-file
    const resolved = resolve(notesFilePath);
    if (!existsSync(resolved)) {
      console.error(`  ✗ Notes file not found: ${resolved}`);
      process.exit(1);
    }
    notes = readFileSync(resolved, 'utf8').trim();
    notesSource = 'file';
  } else if (!notes && level) {
    // Auto-detect: compute the next version and look for RELEASE-NOTES-v{version}.md
    try {
      const { detectCurrentVersion, bumpSemver } = await import('./core.mjs');
      const cwd = process.cwd();
      const currentVersion = detectCurrentVersion(cwd);
      const newVersion = bumpSemver(currentVersion, level);
      const dashed = newVersion.replace(/\./g, '-');
      const autoFile = join(cwd, `RELEASE-NOTES-v${dashed}.md`);
      if (existsSync(autoFile)) {
        notes = readFileSync(autoFile, 'utf8').trim();
        notesSource = 'file';
        console.log(`  ✓ Found RELEASE-NOTES-v${dashed}.md`);
      }
    } catch {}
  }

  // Auto-detect dev update from ai/dev-updates/ if notes are missing or thin
  if (level && (!notes || notes.length < 100)) {
    try {
      const { readdirSync } = await import('node:fs');
      const devUpdatesDir = join(process.cwd(), 'ai', 'dev-updates');
      if (existsSync(devUpdatesDir)) {
        const today = new Date().toISOString().split('T')[0];
        const todayFiles = readdirSync(devUpdatesDir)
          .filter(f => f.startsWith(today) && f.endsWith('.md'))
          .sort()
          .reverse();

        if (todayFiles.length > 0) {
          const devUpdatePath = join(devUpdatesDir, todayFiles[0]);
          const devUpdateContent = readFileSync(devUpdatePath, 'utf8').trim();
          if (devUpdateContent.length > (notes || '').length) {
            notes = devUpdateContent;
            notesSource = 'dev-update';
            console.log(`  ✓ Found dev update: ai/dev-updates/${todayFiles[0]}`);
          }
        }
      }
    } catch {}
  }
}

if (!level || args.includes('--help') || args.includes('-h')) {
  const cwd = process.cwd();
  let current = '';
  try { current = ` (current: ${detectCurrentVersion(cwd)})`; } catch {}

  console.log(`wip-release ... local release tool${current}

Usage:
  wip-release patch                    1.0.0 -> 1.0.1
  wip-release minor                    1.0.0 -> 1.1.0
  wip-release major                    1.0.0 -> 2.0.0

Flags:
  --notes="description"    Release narrative (what was built and why)
  --notes-file=path        Read release narrative from a markdown file
  --dry-run                Show what would happen, change nothing
  --no-publish             Bump + tag only, skip npm/GitHub
  --skip-product-check     Skip product docs check (dev update, roadmap, readme-first)
  --skip-stale-check       Skip stale remote branch check

Release notes:
  Auto-detects notes from three sources (first match wins):
  1. --notes-file=path          Explicit file path
  2. RELEASE-NOTES-v{ver}.md    In repo root (e.g. RELEASE-NOTES-v1-7-4.md)
  3. ai/dev-updates/YYYY-MM-DD* Today's dev update files (most recent first)
  Write dev updates as you work. wip-release picks them up automatically.

Pipeline:
  1. Bump package.json version
  2. Sync SKILL.md version (if exists)
  3. Update CHANGELOG.md
  4. Git commit + tag
  5. Push to remote
  6. npm publish (via 1Password)
  7. GitHub Packages publish
  8. GitHub release create`);
  process.exit(level ? 0 : 1);
}

release({
  repoPath: process.cwd(),
  level,
  notes,
  notesSource,
  dryRun,
  noPublish,
  skipProductCheck,
  skipStaleCheck,
}).catch(err => {
  console.error(`  ✗ ${err.message}`);
  process.exit(1);
});
