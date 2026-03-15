/**
 * 配置管理模块
 */

const fs = require('fs');
const path = require('path');

const CONFIG_PATH = path.join(__dirname, '..', 'config.json');

// 默认配置
const DEFAULT_CONFIG = {
  initialized: false,
  location: {
    name: '大理',
    latitude: 25.6069,
    longitude: 100.2679
  },
  notify: {
    distanceThreshold: 300,
    minMagnitude: 3.0,
    enabled: true
  },
  lastEarthquakeIds: {
    CENC: '',
    CWA: '',
    JMA: ''
  }
};

// 常用城市坐标
const CITY_COORDINATES = {
  '大理': { latitude: 25.6069, longitude: 100.2679 },
  '昆明': { latitude: 25.04, longitude: 102.71 },
  '丽江': { latitude: 26.87, longitude: 100.23 },
  '北京': { latitude: 39.90, longitude: 116.40 },
  '上海': { latitude: 31.23, longitude: 121.47 },
  '广州': { latitude: 23.12, longitude: 113.26 },
  '深圳': { latitude: 22.54, longitude: 114.06 },
  '成都': { latitude: 30.57, longitude: 104.07 },
  '台北': { latitude: 25.03, longitude: 121.56 },
  '东京': { latitude: 35.68, longitude: 139.69 },
  '大阪': { latitude: 34.69, longitude: 135.50 }
};

function loadConfig() {
  try {
    if (fs.existsSync(CONFIG_PATH)) {
      return JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
    }
  } catch (e) {
    console.error('[Config] Load error:', e.message);
  }
  return { ...DEFAULT_CONFIG };
}

function saveConfig(config) {
  try {
    const dir = path.dirname(CONFIG_PATH);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
    return true;
  } catch (e) {
    console.error('[Config] Save error:', e.message);
    return false;
  }
}

function parseLocation(cityName) {
  const normalized = cityName.trim();
  if (CITY_COORDINATES[normalized]) {
    return { name: normalized, ...CITY_COORDINATES[normalized] };
  }
  // 模糊匹配
  for (const [city, coords] of Object.entries(CITY_COORDINATES)) {
    if (city.includes(normalized) || normalized.includes(city)) {
      return { name: city, ...coords };
    }
  }
  return null;
}

function isValidCoordinates(lat, lon) {
  return lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180 && !isNaN(lat) && !isNaN(lon);
}

async function getConfig() {
  return loadConfig();
}

async function setConfig(newConfig) {
  const config = loadConfig();
  
  if (newConfig.location) {
    if (typeof newConfig.location === 'string') {
      const parsed = parseLocation(newConfig.location);
      if (parsed) config.location = parsed;
    } else if (newConfig.location.latitude && newConfig.location.longitude) {
      if (isValidCoordinates(newConfig.location.latitude, newConfig.location.longitude)) {
        config.location = {
          name: newConfig.location.name || config.location.name,
          latitude: newConfig.location.latitude,
          longitude: newConfig.location.longitude
        };
      }
    }
  }
  
  if (newConfig.notify) {
    config.notify = { ...config.notify, ...newConfig.notify };
  }
  
  config.initialized = true;
  saveConfig(config);
  return config;
}

async function initConfig(options = {}) {
  const config = loadConfig();
  
  // 设置位置
  if (options.location) {
    if (typeof options.location === 'string') {
      const parsed = parseLocation(options.location);
      if (parsed) config.location = parsed;
    } else if (options.location.latitude && options.location.longitude) {
      if (isValidCoordinates(options.location.latitude, options.location.longitude)) {
        config.location = {
          name: options.location.name || '',
          latitude: options.location.latitude,
          longitude: options.location.longitude
        };
      }
    }
  } else {
    config.location = { name: '大理', latitude: 25.6069, longitude: 100.2679 };
  }
  
  if (options.distanceThreshold) config.notify.distanceThreshold = options.distanceThreshold;
  if (options.minMagnitude) config.notify.minMagnitude = options.minMagnitude;
  
  config.notify.enabled = true;
  config.initialized = true;
  
  saveConfig(config);
  return config;
}

async function updateLastIds(ids) {
  const config = loadConfig();
  config.lastEarthquakeIds = { ...config.lastEarthquakeIds, ...ids };
  saveConfig(config);
}

module.exports = {
  getConfig,
  setConfig,
  initConfig,
  updateLastIds,
  parseLocation,
  DEFAULT_CONFIG
};
