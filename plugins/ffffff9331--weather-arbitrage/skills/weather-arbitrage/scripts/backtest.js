/**
 * 模拟盘/回测模块
 * 用历史数据测试策略效果
 */

const { celsiusToFahrenheit } = require('./weather-multi');
const { calculateLadder } = require('./ladder');

// 历史数据：预报 vs 实际温度
const HISTORICAL_DATA = {
  'new york': [
    { date: '2024-03-01', forecast: 45, actual: 43, error: 2 },
    { date: '2024-03-02', forecast: 48, actual: 47, error: 1 },
    { date: '2024-03-03', forecast: 52, actual: 54, error: -2 },
    { date: '2024-03-04', forecast: 55, actual: 56, error: -1 },
    { date: '2024-03-05', forecast: 50, actual: 49, error: 1 },
    { date: '2024-03-06', forecast: 47, actual: 45, error: 2 },
    { date: '2024-03-07', forecast: 44, actual: 46, error: -2 },
    { date: '2024-03-08', forecast: 46, actual: 45, error: 1 },
    { date: '2024-03-09', forecast: 51, actual: 52, error: -1 },
    { date: '2024-03-10', forecast: 55, actual: 53, error: 2 }
  ],
  'chicago': [
    { date: '2024-03-01', forecast: 38, actual: 37, error: 1 },
    { date: '2024-03-02', forecast: 42, actual: 43, error: -1 },
    { date: '2024-03-03', forecast: 45, actual: 44, error: 1 },
    { date: '2024-03-04', forecast: 48, actual: 49, error: -1 },
    { date: '2024-03-05', forecast: 46, actual: 45, error: 1 },
    { date: '2024-03-06', forecast: 40, actual: 41, error: -1 },
    { date: '2024-03-07', forecast: 36, actual: 35, error: 1 },
    { date: '2024-03-08', forecast: 39, actual: 38, error: 1 },
    { date: '2024-03-09', forecast: 44, actual: 46, error: -2 },
    { date: '2024-03-10', forecast: 50, actual: 51, error: -1 }
  ],
  'miami': [
    { date: '2024-03-01', forecast: 78, actual: 79, error: -1 },
    { date: '2024-03-02', forecast: 80, actual: 80, error: 0 },
    { date: '2024-03-03', forecast: 82, actual: 81, error: 1 },
    { date: '2024-03-04', forecast: 81, actual: 82, error: -1 },
    { date: '2024-03-05', forecast: 79, actual: 78, error: 1 },
    { date: '2024-03-06', forecast: 77, actual: 78, error: -1 },
    { date: '2024-03-07', forecast: 80, actual: 80, error: 0 },
    { date: '2024-03-08', forecast: 83, actual: 82, error: 1 },
    { date: '2024-03-09', forecast: 85, actual: 84, error: 1 },
    { date: '2024-03-10', forecast: 84, actual: 85, error: -1 }
  ]
};

// 模拟市场赔率
function generateMockOdds(actualTemp) {
  const odds = [];
  const baseTemp = Math.floor(actualTemp / 2) * 2;
  
  // 生成5个温度区间
  for (let offset = -2; offset <= 2; offset++) {
    const low = baseTemp + offset * 2;
    const high = low + 1;
    
    // 计算市场赔率（基于正态分布，但有人为偏差）
    const distance = Math.abs(actualTemp - (low + 0.5));
    const baseProb = Math.exp(-distance * distance / 8) * 100;
    
    // 添加人为偏差（市场情绪）
    const bias = (Math.random() - 0.5) * 10;
    const prob = Math.max(5, Math.min(60, Math.round(baseProb + bias)));
    
    odds.push({
      outcome: `${low}-${high}°F`,
      probability: prob
    });
  }
  
  // 归一化
  const total = odds.reduce((sum, o) => sum + o.probability, 0);
  odds.forEach(o => {
    o.probability = Math.round(o.probability / total * 100);
  });
  
  return odds;
}

/**
 * 回测单个交易日
 */
function backtestDay(city, day, betAmount = 50) {
  const actual = day.actual;
  const forecast = day.forecast;
  
  // 生成模拟市场赔率
  const odds = generateMockOdds(actual);
  
  // 用预报计算策略
  const ladder = calculateLadder(forecast, odds);
  
  // 检查是否命中
  let totalProfit = -ladder.totalBet;
  
  for (const step of ladder.steps) {
    const match = step.range.match(/(\d+)-(\d+)/);
    if (match) {
      const low = parseInt(match[1]);
      const high = parseInt(match[2]);
      
      if (actual >= low && actual <= high) {
        // 命中！
        const payout = step.betAmount / step.probability * 100;
        totalProfit += payout;
      }
    }
  }
  
  return {
    date: day.date,
    city,
    forecast,
    actual,
    error: day.error,
    bet: ladder.totalBet,
    profit: Math.round(totalProfit),
    roi: Math.round((totalProfit / ladder.totalBet - 1) * 100),
    hit: totalProfit > 0
  };
}

/**
 * 回测整个城市
 */
function backtestCity(city, days = null) {
  const history = HISTORICAL_DATA[city.toLowerCase()];
  
  if (!history || history.length === 0) {
    return null;
  }
  
  const testData = days ? history.slice(0, days) : history;
  const results = [];
  
  let totalProfit = 0;
  let totalBet = 0;
  let hits = 0;
  
  for (const day of testData) {
    const result = backtestDay(city, day);
    results.push(result);
    
    totalProfit += result.profit;
    totalBet += result.bet;
    if (result.hit) hits++;
  }
  
  return {
    city,
    days: testData.length,
    total_profit: totalProfit,
    total_bet: totalBet,
    roi: Math.round((totalProfit / totalBet) * 100),
    hit_rate: Math.round(hits / testData.length * 100),
    avg_error: Math.round(history.reduce((sum, d) => sum + Math.abs(d.error), 0) / history.length * 10) / 10,
    results
  };
}

/**
 * 运行完整回测
 */
function runFullBacktest() {
  console.log('📊 天气套利策略回测\n');
  console.log('━'.repeat(70));
  
  const allResults = [];
  
  for (const city of Object.keys(HISTORICAL_DATA)) {
    const result = backtestCity(city);
    allResults.push(result);
    
    console.log(`\n📍 ${city.toUpperCase()}`);
    console.log(`   测试天数: ${result.days}`);
    console.log(`   命中率: ${result.hit_rate}%`);
    console.log(`   总投入: $${result.total_bet}`);
    console.log(`   总收益: $${result.total_profit}`);
    console.log(`   ROI: ${result.roi}%`);
    console.log(`   平均误差: ${result.avg_error}°F`);
  }
  
  console.log('\n' + '━'.repeat(70));
  
  // 汇总
  const summary = {
    cities: allResults.length,
    total_days: allResults.reduce((sum, r) => sum + r.days, 0),
    total_profit: allResults.reduce((sum, r) => sum + r.total_profit, 0),
    total_bet: allResults.reduce((sum, r) => sum + r.total_bet, 0),
    avg_hit_rate: Math.round(allResults.reduce((sum, r) => sum + r.hit_rate, 0) / allResults.length),
    avg_roi: Math.round(allResults.reduce((sum, r) => sum + r.roi, 0) / allResults.length)
  };
  
  console.log('\n📈 汇总统计');
  console.log(`   总测试天数: ${summary.total_days}`);
  console.log(`   平均命中率: ${summary.avg_hit_rate}%`);
  console.log(`   总投入: $${summary.total_bet}`);
  console.log(`   总收益: $${summary.total_profit}`);
  console.log(`   平均ROI: ${summary.avg_roi}%`);
  
  return { summary, cities: allResults };
}

/**
 * 模拟单次交易
 */
function simulateTrade(city, forecastTemp, actualTemp = null) {
  // 如果没有提供实际温度，模拟一个
  if (!actualTemp) {
    const error = (Math.random() - 0.5) * 4; // ±2°F误差
    actualTemp = forecastTemp + error;
  }
  
  const odds = generateMockOdds(actualTemp);
  const ladder = calculateLadder(forecastTemp, odds);
  
  let profit = -ladder.totalBet;
  
  for (const step of ladder.steps) {
    const match = step.range.match(/(\d+)-(\d+)/);
    if (match) {
      const low = parseInt(match[1]);
      const high = parseInt(match[2]);
      
      if (actualTemp >= low && actualTemp <= high) {
        const payout = step.betAmount / step.probability * 100;
        profit += payout;
      }
    }
  }
  
  return {
    city,
    forecast: Math.round(forecastTemp),
    actual: Math.round(actualTemp),
    error: Math.round(Math.abs(forecastTemp - actualTemp) * 10) / 10,
    bet: ladder.totalBet,
    profit: Math.round(profit),
    roi: Math.round((profit / ladder.totalBet) * 100),
    ladder: ladder.steps
  };
}

module.exports = {
  backtestDay,
  backtestCity,
  runFullBacktest,
  simulateTrade,
  HISTORICAL_DATA
};
