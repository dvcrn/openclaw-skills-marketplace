/**
 * 地震监控推送模块
 * 定时检查并推送地震预警
 */

const { getCENCData, getCachedData: getCENCCached } = require('./cenc');
const { getCWAData, getCachedWarning: getCWACached } = require('./cwa');
const { getJMAData, getCachedData: getJMACached } = require('./jma');
const { calculateDistance, parseLocation } = require('./distance');
const { getConfig, setConfig } = require('./config');

let monitorInterval = null;
let lastNotificationTime = 0;
const NOTIFICATION_COOLDOWN = 300000; // 5分钟内不重复通知同一级别地震

/**
 * 启动地震监控
 * @param {Object} options 选项
 * @param {Function} onAlert 预警回调函数
 * @param {number} interval 检查间隔（毫秒），默认 60000 (1分钟)
 */
async function startMonitor(options = {}, onAlert = null, interval = 60000) {
  const config = await getConfig();
  
  if (!config.notify.enabled) {
    console.log('[Earthquake Monitor] 预警未启用');
    return { success: false, message: '预警未启用，请在配置中开启' };
  }
  
  if (!config.location || !config.location.latitude) {
    return { success: false, message: '请先设置监控位置，使用 init() 函数' };
  }
  
  // 如果已有监控在运行，先停止
  if (monitorInterval) {
    stopMonitor();
  }
  
  console.log(`[Earthquake Monitor] 启动监控: ${config.location.name}`);
  console.log(`[Earthquake Monitor] 预警条件: 距离 ${config.notify.distanceThreshold}km 内、震级 ${config.notify.minMagnitude}+`);
  
  // 立即执行一次检查
  await checkAndNotify(onAlert);
  
  // 设置定时检查
  monitorInterval = setInterval(async () => {
    await checkAndNotify(onAlert);
  }, interval);
  
  return { 
    success: true, 
    message: `✅ 地震监控已启动！\n📍 监控位置: ${config.location.name}\n🔔 预警条件: 距离 ${config.notify.distanceThreshold}km 内、震级 ${config.notify.minMagnitude}+ 级\n⏰ 检查间隔: ${interval/1000}秒` 
  };
}

/**
 * 停止地震监控
 */
function stopMonitor() {
  if (monitorInterval) {
    clearInterval(monitorInterval);
    monitorInterval = null;
    console.log('[Earthquake Monitor] 监控已停止');
  }
  return { success: true, message: '✅ 地震监控已停止' };
}

/**
 * 检查并通知
 */
async function checkAndNotify(onAlert) {
  const config = await getConfig();
  if (!config.notify.enabled) return;
  
  try {
    // 获取最新数据
    const [cencData, cwaData, jmaData] = await Promise.allSettled([
      getCENCCached(),
      getCWACached(),
      getJMACached()
    ]);
    
    const earthquakes = [];
    const now = Date.now();
    
    // 处理 CENC 数据
    if (cencData.status === 'fulfilled' && cencData.value.length > 0) {
      for (const eq of cencData.value) {
        const id = eq.EventID || `${eq.time}-${eq.location}`;
        if (id !== config.lastEarthquakeIds?.CENC) {
          earthquakes.push({
            source: 'CENC',
            sourceName: '中国地震台网',
            id: id,
            time: eq.time,
            location: eq.location,
            magnitude: parseFloat(eq.magnitude),
            latitude: parseFloat(eq.latitude),
            longitude: parseFloat(eq.longitude),
            depth: parseFloat(eq.depth),
            intensity: eq.intensity
          });
        }
      }
    }
    
    // 处理 JMA 数据
    if (jmaData.status === 'fulfilled' && jmaData.value.length > 0) {
      for (const eq of jmaData.value) {
        const id = eq.EventID || eq.no;
        if (id !== config.lastEarthquakeIds?.JMA) {
          earthquakes.push({
            source: 'JMA',
            sourceName: '日本气象厅',
            id: id,
            time: eq.time,
            location: eq.location,
            magnitude: parseFloat(eq.magnitude),
            latitude: parseFloat(eq.latitude),
            longitude: parseFloat(eq.longitude),
            depth: eq.depth,
            intensity: eq.shindo
          });
        }
      }
    }
    
    // 检查是否有新地震且符合预警条件
    if (earthquakes.length === 0) return;
    
    // 按时间排序
    earthquakes.sort((a, b) => new Date(b.time) - new Date(a.time));
    
    // 更新 lastEarthquakeIds
    const newConfig = { ...config };
    newConfig.lastEarthquakeIds = {
      CENC: earthquakes.find(e => e.source === 'CENC')?.id || config.lastEarthquakeIds?.CENC || '',
      JMA: earthquakes.find(e => e.source === 'JMA')?.id || config.lastEarthquakeIds?.JMA || '',
      CWA: config.lastEarthquakeIds?.CWA || ''
    };
    await setConfig(newConfig);
    
    // 检查是否符合预警条件
    const alerts = earthquakes.filter(eq => {
      const dist = calculateDistance(
        config.location.latitude,
        config.location.longitude,
        eq.latitude,
        eq.longitude
      );
      eq.distance = dist;
      return dist <= config.notify.distanceThreshold && 
             eq.magnitude >= config.notify.minMagnitude;
    });
    
    // 发送通知
    if (alerts.length > 0 && now - lastNotificationTime > NOTIFICATION_COOLDOWN) {
      lastNotificationTime = now;
      const message = formatAlertMessage(alerts, config.location.name);
      
      if (onAlert) {
        onAlert({ alerts, message });
      }
      
      console.log(`[Earthquake Monitor] 发送预警: ${alerts.length} 条`);
    }
    
  } catch (e) {
    console.error('[Earthquake Monitor] 检查失败:', e.message);
  }
}

/**
 * 格式化预警消息
 */
function formatAlertMessage(earthquakes, locationName) {
  const lines = ['⚠️ 地震预警提醒！'];
  lines.push(`📍 震中距离 ${locationName} 较近：\n`);
  
  earthquakes.forEach((eq, i) => {
    const emoji = eq.magnitude >= 5 ? '🔴' : eq.magnitude >= 4 ? '🟠' : '🟡';
    lines.push(`${i + 1}. ${emoji} M${eq.magnitude} 级`);
    lines.push(`   📍 ${eq.location}`);
    lines.push(`   📏 距离约 ${Math.round(eq.distance)}km`);
    lines.push(`   ⏰ ${eq.time}`);
    lines.push('');
  });
  
  lines.push('请注意安全！');
  return lines.join('\n');
}

/**
 * 获取监控状态
 */
function getStatus() {
  return {
    isRunning: monitorInterval !== null,
    lastNotification: lastNotificationTime > 0 ? new Date(lastNotificationTime).toISOString() : null
  };
}

module.exports = {
  startMonitor,
  stopMonitor,
  checkAndNotify,
  getStatus
};
