'use strict';

/**
 * Config loader — reads API keys from ~/.openclaw/data/planit/config.json
 * Keys are NEVER stored in source code.
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

const CONFIG_FILE = path.join(os.homedir(), '.openclaw', 'data', 'planit', 'config.json');

let _config = null;

function loadConfig() {
  if (_config) return _config;
  try {
    _config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
  } catch {
    _config = {};
  }
  return _config;
}

function getAmapKey() {
  return loadConfig()?.amap?.key || null;
}

function getProxyUrl() {
  return loadConfig()?.proxy?.url || process.env.PLANIT_PROXY_URL || null;
}

module.exports = { getAmapKey, getProxyUrl, loadConfig };
