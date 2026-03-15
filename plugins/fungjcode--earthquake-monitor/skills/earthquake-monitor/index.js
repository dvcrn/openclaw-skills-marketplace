/**
 * Earthquake Monitor - 中日地震实时监控
 * 支持 CENC/CWA/JMA 三大数据源，支持主动推送
 */

const { getCENCData } = require('./src/cenc');
const { getCWAData } = require('./src/cwa');
const { getJMAData } = require('./src/jma');
const { calculateDistance, parseLocation } = require('./src/distance');
const { getConfig, setConfig, initConfig } = require('./src/config');
const { startMonitor, stopMonitor, getStatus } = require('./src/monitor');

// 统一字段格式
function normalize(data, source) {
  if (!data || data.length === 0) return [];
  
  return data.map(eq => {
    const normalized = {
      source,
      time: '',
      location: '',
      magnitude: 0,
      latitude: 0,
      longitude: 0,
      depth: 0,
      intensity: ''
    };
    
    if (source === 'CENC') {
      normalized.time = eq.time;
      normalized.location = eq.location || eq.placeName;
      normalized.magnitude = parseFloat(eq.magnitude);
      normalized.latitude = parseFloat(eq.latitude);
      normalized.longitude = parseFloat(eq.longitude);
      normalized.depth = parseFloat(eq.depth);
      normalized.intensity = eq.intensity;
      normalized.id = eq.EventID;
    } else if (source === 'CWA') {
      normalized.time = eq.OriginTime;
      normalized.location = eq.HypoCenter;
      normalized.magnitude = parseFloat(eq.Magunitude);
      normalized.latitude = parseFloat(eq.Latitude);
      normalized.longitude = parseFloat(eq.Longitude);
      normalized.depth = parseFloat(eq.Depth);
      normalized.intensity = eq.MaxIntensity;
      normalized.id = eq.ID;
      normalized.isWarning = true;
    } else if (source === 'JMA') {
      normalized.time = eq.time;
      normalized.location = eq.location;
      normalized.magnitude = parseFloat(eq.magnitude);
      normalized.latitude = parseFloat(eq.latitude);
      normalized.longitude = parseFloat(eq.longitude);
      normalized.depth = eq.depth;
      normalized.intensity = eq.shindo;
      normalized.id = eq.EventID || eq.no;
    }
    
    return normalized;
  });
}

/**
 * 初始化技能配置（首次使用必须调用）
 * @param {Object} options 配置选项
 * @param {string|Object} options.location - 位置，城市名或 {name, latitude, longitude}
 * @param {number} [options.distanceThreshold=300] - 预警距离（公里）
 * @param {number} [options.minMagnitude=3.0] - 最小震级
 * @param {boolean} [options.notifyEnabled=true] - 是否启用推送
 */
async function init(options = {}) {
  const config = await initConfig(options);
  
  let locationInfo = '';
  if (config.location && config.location.name) {
    locationInfo = `\n📍 监控位置: ${config.location.name} (${config.location.latitude}, ${config.location.longitude})`;
  }
  
  return {
    success: true,
    message: `✅ 地震监控技能初始化完成！\n🔔 预警条件: 距离 ${config.notify.distanceThreshold}km 内、震级 ${config.notify.minMagnitude}+ 级${locationInfo}\n\n使用方法:\n- "地震" 或 "getAll()" - 获取最新地震\n- "中国地震" / "getCENC()" - 中国地震台网\n- "日本地震" / "getJMA()" - 日本气象厅\n- "台湾地震" / "getCWA()" - 台湾预警\n- "startMonitor()" - 启动主动推送\n- "config()" - 查看/修改配置`,
    config
  };
}

/**
 * 获取中国地震台网数据
 * @param {number} [limit=10] - 返回条数
 */
async function getCENC(limit = 10) {
  const data = await getCENCData();
  return {
    source: 'CENC',
    sourceName: '中国地震台网',
    count: data.length,
    earthquakes: normalize(data, 'CENC').slice(0, limit)
  };
}

/**
 * 获取台湾 CWA 预警数据
 */
async function getCWA() {
  const data = await getCWAData();
  if (!data) {
    return { source: 'CWA', sourceName: '台湾中央气象署', count: 0, earthquakes: [] };
  }
  return {
    source: 'CWA',
    sourceName: '台湾中央气象署',
    count: 1,
    earthquakes: normalize([data], 'CWA'),
    isWarning: true
  };
}

/**
 * 获取日本气象厅数据
 * @param {number} [limit=10] - 返回条数
 */
async function getJMA(limit = 10) {
  const data = await getJMAData();
  return {
    source: 'JMA',
    sourceName: '日本气象厅',
    count: data.length,
    earthquakes: normalize(data, 'JMA').slice(0, limit)
  };
}

/**
 * 获取所有来源的地震数据
 * @param {Object} options 选项
 * @param {number} [options.limit=5] - 每来源返回条数
 * @param {boolean} [options.checkMyLocation=true] - 是否检查位置
 */
async function getAll(options = {}) {
  const { limit = 5, checkMyLocation = true } = options;
  
  const [cenc, cwa, jma] = await Promise.allSettled([
    getCENC(limit),
    getCWA(),
    getJMA(limit)
  ]);
  
  const results = { timestamp: new Date().toISOString(), sources: [] };
  
  if (cenc.status === 'fulfilled') results.sources.push(cenc.value);
  if (cwa.status === 'fulfilled' && cwa.value.count > 0) results.sources.push(cwa.value);
  if (jma.status === 'fulfilled') results.sources.push(jma.value);
  
  // 合并所有地震
  const allEarthquakes = results.sources
    .flatMap(s => s.earthquakes.map(eq => ({...eq, sourceName: s.sourceName})))
    .sort((a, b) => new Date(b.time) - new Date(a.time))
    .slice(0, 15);
  
  results.earthquakes = allEarthquakes;
  results.totalCount = allEarthquakes.length;
  
  // 检查是否影响设定位置
  if (checkMyLocation) {
    const config = await getConfig();
    if (config.location && config.notify.enabled) {
      const nearby = allEarthquakes.filter(eq => {
        const dist = calculateDistance(
          config.location.latitude, config.location.longitude,
          eq.latitude, eq.longitude
        );
        eq.distance = dist;
        return dist <= config.notify.distanceThreshold && eq.magnitude >= config.notify.minMagnitude;
      });
      
      results.nearbyEarthquakes = nearby;
      results.hasAlert = nearby.length > 0;
      if (nearby.length > 0) {
        results.alertMessage = formatAlertMessage(nearby, config.location.name);
      }
    }
  }
  
  return results;
}

/**
 * 启动主动推送监控
 * @param {Object} options 选项
 * @param {number} [options.interval=60000] - 检查间隔（毫秒）
 */
async function start(options = {}) {
  return await startMonitor(options);
}

/**
 * 停止推送监控
 */
async function stop() {
  return stopMonitor();
}

/**
 * 查看/修改配置
 * @param {Object} [newConfig] - 新配置
 */
async function config(newConfig = null) {
  if (newConfig) {
    const config = await setConfig(newConfig);
    return { success: true, message: '✅ 配置已更新', config };
  }
  return await getConfig();
}

/**
 * 获取监控状态
 */
async function status() {
  return getStatus();
}

// 格式化预警消息
function formatAlertMessage(earthquakes, locationName) {
  const lines = ['⚠️ 地震预警提醒！', `📍 震中距离 ${locationName} 较近：\n`];
  
  earthquakes.forEach((eq, i) => {
    const emoji = eq.magnitude >= 5 ? '🔴' : eq.magnitude >= 4 ? '🟠' : '🟡';
    lines.push(`${i + 1}. ${emoji} M${eq.magnitude} 级`);
    lines.push(`   📍 ${eq.location}`);
    lines.push(`   📏 距离约 ${Math.round(eq.distance)}km`);
    lines.push(`   ⏰ ${eq.time}\n`);
  });
  
  lines.push('请注意安全！');
  return lines.join('\n');
}

module.exports = {
  init,
  getCENC,
  getCWA,
  getJMA,
  getAll,
  start,
  stop,
  config,
  status
};
