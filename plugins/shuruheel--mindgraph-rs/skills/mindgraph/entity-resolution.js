#!/usr/bin/env node
/**
 * MindGraph Entity Resolution Module
 *
 * Prevents duplicate entity creation during extraction/import.
 * Uses fuzzy resolution and alias matching via the cognitive layer.
 *
 * Usage:
 *   const { resolveEntity, normalizeLabel } = require('./entity-resolution.js');
 *   const uid = await resolveEntity('Thumos Care', 'Organization');
 */

'use strict';

const mg = require('./mindgraph-client.js');

// Cache for resolved entities in this session
const resolutionCache = new Map();

// Common entity aliases and normalizations
const NORMALIZATION_RULES = [
  { pattern: /\s+(Inc\.?|LLC|Ltd\.?|Corp\.?|Corporation|Company|Co\.?)$/i, replacement: '' },
  { pattern: /\s+/g, replacement: ' ' },
  { pattern: /[-–—]/g, replacement: ' ' },
  { pattern: /^[^\w]+|[^\w]+$/g, replacement: '' },
];

const KNOWN_ALIASES = new Map([
  ['thumos', 'Thumos Care'],
  ['thumoscare', 'Thumos Care'],
  ['thumos care inc', 'Thumos Care'],
  ['justads', 'Just Ads'],
  ['just ads llc', 'Just Ads'],
  ['pencil news', 'Pencil News'],
  ['pencil', 'Pencil News'],
  ['openai', 'OpenAI'],
  ['anthropic ai', 'Anthropic'],
  ['google ai', 'Google'],
]);

function normalizeLabel(label) {
  if (!label || typeof label !== 'string') return '';
  let normalized = label.toLowerCase().trim();
  for (const rule of NORMALIZATION_RULES) {
    normalized = normalized.replace(rule.pattern, rule.replacement);
  }
  return normalized.trim();
}

function checkAliases(label) {
  const normalized = normalizeLabel(label);
  return KNOWN_ALIASES.get(normalized);
}

/**
 * Unwrap search/retrieve results that come as {node: {...}, score} or flat objects.
 */
function unwrapNode(item) {
  if (!item) return null;
  return item.node || item;
}

/**
 * Resolve an entity — returns existing UID or null.
 * 
 * Resolution order:
 *   1. Session cache
 *   2. Known aliases map
 *   3. fuzzy_resolve API (server-side fuzzy matching)
 *   4. FTS exact label match via search()
 *   5. Semantic similarity via retrieve('semantic')
 */
async function resolveEntity(label, entityType = 'Person', options = {}) {
  const { 
    createIfMissing = false,
    aliases = [],
    confidence = 0.85,
    agentId = 'entity-resolution'
  } = options;
  
  const cacheKey = `${normalizeLabel(label)}|${entityType}`;
  
  // 1. Session cache
  if (resolutionCache.has(cacheKey)) {
    return resolutionCache.get(cacheKey);
  }
  
  // 2. Known aliases
  const aliasedLabel = checkAliases(label);
  if (aliasedLabel && aliasedLabel !== label) {
    console.error(`  ALIAS-RESOLVE: "${label}" → "${aliasedLabel}"`);
    label = aliasedLabel;
  }
  
  // 3. fuzzy_resolve API
  try {
    const result = await mg.manageEntity({
      action: 'fuzzy_resolve',
      label: label,
      text: label,  // server requires 'text' for fuzzy_resolve
      entityType: entityType,
    });
    
    if (result?.uid) {
      console.error(`  FUZZY-RESOLVED: "${label}" → ${result.uid}`);
      resolutionCache.set(cacheKey, result.uid);
      return result.uid;
    }
  } catch (e) {
    // fuzzy_resolve may fail or return empty — fall through
  }
  
  // 4. FTS exact label match
  try {
    const results = await mg.search(label, { limit: 10 });
    const items = Array.isArray(results) ? results : [];
    
    for (const item of items) {
      const node = unwrapNode(item);
      if (node && node.label && 
          normalizeLabel(node.label) === normalizeLabel(label) &&
          !node.tombstone_at) {
        console.error(`  EXACT-MATCH: "${label}" → ${node.uid} [${node.node_type}]`);
        resolutionCache.set(cacheKey, node.uid);
        return node.uid;
      }
    }
  } catch (e) {
    // FTS may fail — fall through
  }
  
  // 5. Semantic similarity
  try {
    const results = await mg.retrieve('semantic', { query: label, limit: 5 });
    const items = Array.isArray(results) ? results : [];
    
    for (const item of items) {
      const node = unwrapNode(item);
      if (node && !node.tombstone_at && (item.score || node.score || 0) >= confidence) {
        // Only match if it's the same broad category (Entity-like types)
        const entityTypes = ['Entity', 'Person', 'Organization', 'Service', 'Product', 'Location'];
        if (entityTypes.includes(node.node_type) || node.node_type === entityType) {
          console.error(`  SEMANTIC-MATCH: "${label}" → "${node.label}" (${Math.round((item.score || node.score) * 100)}%) [${node.node_type}]`);
          resolutionCache.set(cacheKey, node.uid);
          return node.uid;
        }
      }
    }
  } catch (e) {
    // Semantic search may fail (no OPENAI_API_KEY) — fall through
  }
  
  // Not found — optionally create
  if (createIfMissing) {
    try {
      const newEntity = await mg.manageEntity({
        action: 'create',
        label: label,
        entityType: entityType,
        aliases: aliases,
        agentId: agentId
      });
      
      if (newEntity?.uid) {
        console.error(`  CREATED: "${label}" [${entityType}] → ${newEntity.uid}`);
        resolutionCache.set(cacheKey, newEntity.uid);
        return newEntity.uid;
      }
    } catch (e) {
      console.error(`  CREATE error: ${e.message}`);
    }
  }
  
  return null;
}

async function resolveEntities(entities, options = {}) {
  const results = [];
  for (const entity of entities) {
    const { label, type = 'Person', ...opts } = entity;
    const uid = await resolveEntity(label, type, { ...options, ...opts });
    results.push({ label, type, uid, found: !!uid });
  }
  return results;
}

function clearCache() { resolutionCache.clear(); }

function addAlias(alias, canonicalLabel) {
  KNOWN_ALIASES.set(normalizeLabel(alias), canonicalLabel);
}

async function loadAliasesFromGraph() {
  try {
    const prefs = await mg.search('entity alias', { limit: 20 });
    const items = Array.isArray(prefs) ? prefs : [];
    for (const item of items) {
      const node = unwrapNode(item);
      if (node?.props?.alias && node?.props?.canonical) {
        addAlias(node.props.alias, node.props.canonical);
      }
    }
  } catch (e) {
    // Non-fatal
  }
}

module.exports = {
  resolveEntity,
  resolveEntities,
  normalizeLabel,
  checkAliases,
  addAlias,
  loadAliasesFromGraph,
  clearCache
};

// CLI usage
if (require.main === module) {
  const label = process.argv[2];
  const type = process.argv[3] || 'Entity';
  
  if (!label) {
    console.log('Usage: node entity-resolution.js "<label>" [entityType]');
    process.exit(1);
  }
  
  resolveEntity(label, type, { createIfMissing: false })
    .then(uid => {
      console.log(`\nResult: ${uid || 'NOT FOUND'}`);
      process.exit(uid ? 0 : 1);
    })
    .catch(err => {
      console.error('Error:', err);
      process.exit(1);
    });
}
