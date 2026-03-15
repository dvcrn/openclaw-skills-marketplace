/**
 * 天气预报API封装
 * 使用 Open-Meteo（免费）获取气象预报
 */

const OPEN_METEO_API = 'https://api.open-meteo.com/v1';

// 主要城市坐标
const CITY_COORDS = {
  'new york': { lat: 40.71, lon: -74.01, timezone: 'America/New_York' },
  'london': { lat: 51.51, lon: -0.13, timezone: 'Europe/London' },
  'tokyo': { lat: 35.68, lon: 139.69, timezone: 'Asia/Tokyo' },
  'paris': { lat: 48.85, lon: 2.35, timezone: 'Europe/Paris' },
  'sydney': { lat: -33.87, lon: 151.21, timezone: 'Australia/Sydney' },
  'beijing': { lat: 39.90, lon: 116.41, timezone: 'Asia/Shanghai' },
  'shanghai': { lat: 31.23, lon: 121.47, timezone: 'Asia/Shanghai' },
  'hong kong': { lat: 22.32, lon: 114.17, timezone: 'Asia/Hong_Kong' },
  'singapore': { lat: 1.35, lon: 103.82, timezone: 'Asia/Singapore' },
  'dubai': { lat: 25.20, lon: 55.27, timezone: 'Asia/Dubai' },
  'los angeles': { lat: 34.05, lon: -118.24, timezone: 'America/Los_Angeles' },
  'chicago': { lat: 41.88, lon: -87.63, timezone: 'America/Chicago' },
  'miami': { lat: 25.76, lon: -80.19, timezone: 'America/New_York' },
  'houston': { lat: 29.76, lon: -95.37, timezone: 'America/Chicago' },
  'buenos aires': { lat: -34.60, lon: -58.38, timezone: 'America/Argentina/Buenos_Aires' },
  'wellington': { lat: -41.29, lon: 174.78, timezone: 'Pacific/Auckland' }
};

/**
 * 获取城市坐标
 */
function getCityCoords(cityName) {
  const normalized = cityName.toLowerCase().trim();
  return CITY_COORDS[normalized] || null;
}

/**
 * 获取单个气象预报
 */
async function getWeatherForecast(city, dateStr) {
  const coords = getCityCoords(city);
  
  if (!coords) {
    console.log(`⚠️ 未找到城市坐标: ${city}`);
    return null;
  }
  
  try {
    const url = `${OPEN_METEO_API}/forecast?latitude=${coords.lat}&longitude=${coords.lon}&timezone=${coords.timezone}&daily=temperature_2m_max,temperature_2m_min`;
    
    const response = await fetch(url);
    const data = await response.json();
    
    if (!data.daily) {
      return null;
    }
    
    // 找到目标日期
    const targetDate = parseDate(dateStr);
    const dateIndex = data.daily.time.findIndex(t => t === targetDate);
    
    if (dateIndex === -1) {
      // 如果找不到，返回最近的一天
      return {
        city: city,
        date: data.daily.time[0],
        temp: data.daily.temperature_2m_max[0],
        temp_min: data.daily.temperature_2m_min[0],
        source: 'Open-Meteo (GFS)'
      };
    }
    
    return {
      city: city,
      date: data.daily.time[dateIndex],
      temp: data.daily.temperature_2m_max[dateIndex],
      temp_min: data.daily.temperature_2m_min[dateIndex],
      source: 'Open-Meteo (GFS)'
    };
  } catch (error) {
    console.error('获取天气失败:', error.message);
    return null;
  }
}

/**
 * 获取多个气象源的预报（模拟多个模型）
 */
async function getForecasts(city, dateStr) {
  const forecasts = [];
  
  // Open-Meteo (GFS)
  const gfsForecast = await getWeatherForecast(city, dateStr);
  if (gfsForecast) {
    forecasts.push(gfsForecast);
    
    // 模拟ECMWF（通常偏差±2°F）
    forecasts.push({
      ...gfsForecast,
      temp: gfsForecast.temp + (Math.random() - 0.5) * 2,
      source: 'ECMWF (模拟)'
    });
    
    // 模拟NOAA
    forecasts.push({
      ...gfsForecast,
      temp: gfsForecast.temp + (Math.random() - 0.5) * 1.5,
      source: 'NOAA (模拟)'
    });
  }
  
  return forecasts;
}

/**
 * 解析日期字符串
 */
function parseDate(dateStr) {
  // 处理 "March 5", "Mar 5", "3月5日" 等格式
  const now = new Date();
  const year = now.getFullYear();
  
  // 英文月份映射
  const months = {
    'january': '01', 'jan': '01',
    'february': '02', 'feb': '02',
    'march': '03', 'mar': '03',
    'april': '04', 'apr': '04',
    'may': '05',
    'june': '06', 'jun': '06',
    'july': '07', 'jul': '07',
    'august': '08', 'aug': '08',
    'september': '09', 'sep': '09',
    'october': '10', 'oct': '10',
    'november': '11', 'nov': '11',
    'december': '12', 'dec': '12'
  };
  
  const lower = dateStr.toLowerCase();
  
  for (const [month, num] of Object.entries(months)) {
    if (lower.includes(month)) {
      const dayMatch = lower.match(/\d+/);
      if (dayMatch) {
        const day = dayMatch[0].padStart(2, '0');
        return `${year}-${num}-${day}`;
      }
    }
  }
  
  // 默认返回今天
  return now.toISOString().split('T')[0];
}

module.exports = {
  getWeatherForecast,
  getForecasts,
  getCityCoords,
  CITY_COORDS
};
