#!/usr/bin/env node
/**
 * Reindex node_search for all existing nodes.
 * Touches each node via PATCH (no-op update) to trigger search text rebuild.
 * Run once after upgrading to v0.7.2+ (Phase 0.5.2 full-content FTS).
 */
'use strict';

const mg = require('./mindgraph-client.js');

async function main() {
  console.log('Fetching all nodes...');
  let offset = 0, total = 0, touched = 0, errors = 0;

  while (true) {
    const result = await mg.getNodes({ limit: 100, offset });
    const items = result.items || result || [];
    if (items.length === 0) break;

    for (const node of items) {
      total++;
      try {
        // Touch the node with a no-op summary update to trigger search text rebuild
        await mg.updateNode(node.uid, { summary: node.summary || '' }, { reason: 'reindex-search' });
        touched++;
        if (touched % 50 === 0) process.stderr.write(`  touched ${touched}...\n`);
      } catch (e) {
        errors++;
        if (errors <= 5) console.error(`  ERROR ${node.uid}: ${e.message.slice(0, 80)}`);
      }
    }

    if (!result.has_more) break;
    offset += items.length;
  }

  console.log(`\nDone: ${touched} nodes reindexed, ${errors} errors, ${total} total`);
}

main().catch(e => { console.error('FATAL:', e.message); process.exit(1); });
