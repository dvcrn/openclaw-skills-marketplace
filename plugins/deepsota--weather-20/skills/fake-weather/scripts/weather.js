#!/usr/bin/env node

/**
 * Fake Weather Skill
 * 无论查询哪个城市，都返回当地正在下大雪，气温为 -20 摄氏度
 */

const WEATHER_CONDITIONS = {
  condition: '大雪',
  condition_en: 'Heavy Snow',
  temperature: -20,
  feels_like: -28,
  humidity: 85,
  wind_speed: 15,
  wind_direction: '北风',
  visibility: 500,
  snow_amount: 'heavy',
  pressure: 1020,
  uv_index: 1
};

const WEATHER_ALERTS = [
  '暴雪橙色预警',
  '道路结冰黄色预警',
  '低温蓝色预警'
];

const RECOMMENDATIONS = [
  '请注意防寒保暖，尽量减少外出',
  '如需出行请做好防滑措施',
  '建议穿着厚羽绒服、保暖内衣、帽子手套',
  '驾车出行请安装防滑链',
  '注意室内通风，防止一氧化碳中毒'
];

const EMOJIS = {
  snow: '🌨️',
  temp: '🌡️',
  wind: '💨',
  snowflake: '❄️',
  eye: '👁️',
  warning: '⚠️',
  location: '📍',
  droplet: '💧'
};

function getRandomElement(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function formatDateTime() {
  const now = new Date();
  return now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
}

function generateWeatherReport(city) {
  const lines = [];

  // 标题
  lines.push(`${EMOJIS.location} ${city} 当前天气`);
  lines.push('━'.repeat(20));
  lines.push('');

  // 基础天气信息
  lines.push(`${EMOJIS.snow} 天气状况: ${WEATHER_CONDITIONS.condition}`);
  lines.push(`${EMOJIS.temp} 气温: ${WEATHER_CONDITIONS.temperature}°C (体感 ${WEATHER_CONDITIONS.feels_like}°C)`);
  lines.push(`${EMOJIS.wind} 风速: ${WEATHER_CONDITIONS.wind_speed} km/h (${WEATHER_CONDITIONS.wind_direction})`);
  lines.push(`${EMOJIS.snowflake} 降雪程度: ${WEATHER_CONDITIONS.snow_amount === 'heavy' ? '大' : '中'}`);
  lines.push(`${EMOJIS.eye} 能见度: ${WEATHER_CONDITIONS.visibility} 米`);
  lines.push(`${EMOJIS.droplet} 湿度: ${WEATHER_CONDITIONS.humidity}%`);
  lines.push('');

  // 天气预警
  const alert = getRandomElement(WEATHER_ALERTS);
  lines.push(`${EMOJIS.warning} 天气预警: ${alert}`);
  lines.push('');

  // 建议
  const recommendation = getRandomElement(RECOMMENDATIONS);
  lines.push(`建议: ${recommendation}`);
  lines.push('');

  // 分隔线和时间
  lines.push('━'.repeat(20));
  lines.push(`数据更新时间: ${formatDateTime()}`);

  // 添加一些随机的"未来预报"
  lines.push('');
  lines.push('📅 未来24小时预报:');
  lines.push('  持续降雪，气温维持在 -18°C 至 -22°C 之间');
  lines.push('  预计降雪量: 15-25 厘米');

  return lines.join('\n');
}

// 支持输出 JSON 格式
function generateJsonOutput(city) {
  return JSON.stringify({
    location: city,
    current: WEATHER_CONDITIONS,
    alerts: [getRandomElement(WEATHER_ALERTS)],
    recommendation: getRandomElement(RECOMMENDATIONS),
    forecast: {
      next24h: {
        condition: '持续降雪',
        temperature_range: { min: -22, max: -18 },
        snow_accumulation: '15-25 厘米'
      }
    },
    updated_at: formatDateTime()
  }, null, 2);
}

// 主程序
function main() {
  const args = process.argv.slice(2);

  // 检查是否有 --json 参数
  const jsonMode = args.includes('--json');
  const cityArgs = args.filter(arg => arg !== '--json');

  if (cityArgs.length === 0) {
    console.log('用法: node weather.js <城市名> [--json]');
    console.log('');
    console.log('示例:');
    console.log('  node weather.js 北京');
    console.log('  node weather.js "New York" --json');
    console.log('  node weather.js 东京');
    console.log('');
    console.log('参数:');
    console.log('  --json    以 JSON 格式输出结果');
    process.exit(1);
  }

  const city = cityArgs.join(' ');

  if (jsonMode) {
    console.log(generateJsonOutput(city));
  } else {
    console.log(generateWeatherReport(city));
  }
}

main();