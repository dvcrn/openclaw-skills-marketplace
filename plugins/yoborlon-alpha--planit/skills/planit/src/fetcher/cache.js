'use strict';

/**
 * File-based JSON cache with TTL.
 * Stores all entries in a single cache.json file under the planit data dir.
 * No external dependencies required.
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

const CACHE_FILE = path.join(os.homedir(), '.openclaw', 'data', 'planit', 'cache.json');

// Default TTLs (milliseconds)
const TTL = {
  trains: 30 * 60 * 1000,      // 30 minutes — schedules stable within a day
  hotels: 60 * 60 * 1000,      // 1 hour
  attractions: 24 * 60 * 60 * 1000, // 24 hours — rarely changes
};

function loadCache() {
  try {
    if (fs.existsSync(CACHE_FILE)) {
      return JSON.parse(fs.readFileSync(CACHE_FILE, 'utf8'));
    }
  } catch {
    // corrupted cache — start fresh
  }
  return {};
}

function saveCache(data) {
  const dir = path.dirname(CACHE_FILE);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(CACHE_FILE, JSON.stringify(data), 'utf8');
}

/**
 * Get a cached value. Returns null if missing or expired.
 * @param {string} key
 * @returns {any|null}
 */
function get(key) {
  const cache = loadCache();
  const entry = cache[key];
  if (!entry) return null;
  if (Date.now() > entry.expiresAt) {
    // Expired — clean up lazily
    delete cache[key];
    saveCache(cache);
    return null;
  }
  return entry.value;
}

/**
 * Set a cached value with a TTL.
 * @param {string} key
 * @param {any} value
 * @param {number} ttlMs - milliseconds
 */
function set(key, value, ttlMs) {
  const cache = loadCache();
  cache[key] = {
    value,
    expiresAt: Date.now() + ttlMs,
    cachedAt: new Date().toISOString(),
  };
  saveCache(cache);
}

/**
 * Build a cache key.
 */
function key(...parts) {
  return parts.join('::');
}

/**
 * Remove all expired entries (maintenance).
 */
function prune() {
  const cache = loadCache();
  const now = Date.now();
  let changed = false;
  for (const k of Object.keys(cache)) {
    if (now > cache[k].expiresAt) {
      delete cache[k];
      changed = true;
    }
  }
  if (changed) saveCache(cache);
}

module.exports = { get, set, key, TTL, prune };
