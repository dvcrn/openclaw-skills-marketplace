/**
 * 大规模模拟交易
 * 支持100次、1000次模拟
 */

const { getMultiSourceForecast, calculateWeightedForecast, getHistoricalAccuracy, getCityCoords } = require('./weather-multi');
const { calculateLadder } = require('./ladder');

// 城市列表（支持模拟）
const CITIES = ['New York', 'Chicago', 'Miami', 'Phoenix', 'Dallas', 'Los Angeles', 'San Francisco', 'Seattle', 'Denver', 'Boston'];

// 历史数据（预报 vs 实际）
const HISTORICAL_DATA = {
  'new york': [
    { forecast: 45, actual: 43 }, { forecast: 48, actual: 47 }, { forecast: 52, actual: 54 },
    { forecast: 55, actual: 56 }, { forecast: 50, actual: 49 }, { forecast: 47, actual: 45 },
    { forecast: 44, actual: 46 }, { forecast: 46, actual: 45 }, { forecast: 51, actual: 52 },
    { forecast: 55, actual: 53 }, { forecast: 42, actual: 40 }, { forecast: 38, actual: 37 },
    { forecast: 35, actual: 36 }, { forecast: 40, actual: 42 }, { forecast: 44, actual: 43 }
  ],
  'chicago': [
    { forecast: 38, actual: 37 }, { forecast: 42, actual: 43 }, { forecast: 45, actual: 44 },
    { forecast: 48, actual: 49 }, { forecast: 46, actual: 45 }, { forecast: 40, actual: 41 },
    { forecast: 36, actual: 35 }, { forecast: 39, actual: 38 }, { forecast: 44, actual: 46 },
    { forecast: 50, actual: 51 }, { forecast: 52, actual: 53 }, { forecast: 48, actual: 47 },
    { forecast: 42, actual: 41 }, { forecast: 38, actual: 39 }, { forecast: 35, actual: 35 }
  ],
  'miami': [
    { forecast: 78, actual: 79 }, { forecast: 80, actual: 80 }, { forecast: 82, actual: 81 },
    { forecast: 81, actual: 82 }, { forecast: 79, actual: 78 }, { forecast: 77, actual: 78 },
    { forecast: 80, actual: 80 }, { forecast: 83, actual: 82 }, { forecast: 85, actual: 84 },
    { forecast: 84, actual: 85 }, { forecast: 82, actual: 81 }, { forecast: 80, actual: 80 },
    { forecast: 78, actual: 79 }, { forecast: 81, actual: 82 }, { forecast: 83, actual: 83 }
  ],
  'phoenix': [
    { forecast: 75, actual: 76 }, { forecast: 78, actual: 78 }, { forecast: 80, actual: 81 },
    { forecast: 82, actual: 82 }, { forecast: 85, actual: 84 }, { forecast: 83, actual: 83 },
    { forecast: 79, actual: 80 }, { forecast: 77, actual: 76 }, { forecast: 80, actual: 81 },
    { forecast: 84, actual: 85 }, { forecast: 86, actual: 86 }, { forecast: 82, actual: 82 },
    { forecast: 78, actual: 78 }, { forecast: 75, actual: 76 }, { forecast: 72, actual: 73 }
  ],
  'dallas': [
    { forecast: 65, actual: 64 }, { forecast: 68, actual: 69 }, { forecast: 72, actual: 71 },
    { forecast: 75, actual: 76 }, { forecast: 70, actual: 70 }, { forecast: 66, actual: 67 },
    { forecast: 62, actual: 61 }, { forecast: 64, actual: 65 }, { forecast: 70, actual: 72 },
    { forecast: 76, actual: 75 }, { forecast: 78, actual: 77 }, { forecast: 74, actual: 75 },
    { forecast: 68, actual: 68 }, { forecast: 64, actual: 63 }, { forecast: 60, actual: 61 }
  ],
  'los angeles': [
    { forecast: 68, actual: 70 }, { forecast: 70, actual: 69 }, { forecast: 72, actual: 73 },
    { forecast: 71, actual: 70 }, { forecast: 69, actual: 68 }, { forecast: 67, actual: 69 },
    { forecast: 70, actual: 71 }, { forecast: 73, actual: 72 }, { forecast: 75, actual: 74 },
    { forecast: 72, actual: 73 }, { forecast: 70, actual: 69 }, { forecast: 68, actual: 70 },
    { forecast: 66, actual: 65 }, { forecast: 69, actual: 70 }, { forecast: 71, actual: 72 }
  ],
  'san francisco': [
    { forecast: 58, actual: 60 }, { forecast: 60, actual: 58 }, { forecast: 62, actual: 61 },
    { forecast: 59, actual: 61 }, { forecast: 57, actual: 55 }, { forecast: 55, actual: 57 },
    { forecast: 58, actual: 60 }, { forecast: 61, actual: 59 }, { forecast: 63, actual: 62 },
    { forecast: 60, actual: 58 }, { forecast: 56, actual: 58 }, { forecast: 54, actual: 56 },
    { forecast: 58, actual: 57 }, { forecast: 60, actual: 61 }, { forecast: 62, actual: 60 }
  ],
  'seattle': [
    { forecast: 50, actual: 48 }, { forecast: 52, actual: 53 }, { forecast: 48, actual: 47 },
    { forecast: 46, actual: 48 }, { forecast: 49, actual: 50 }, { forecast: 51, actual: 49 },
    { forecast: 47, actual: 46 }, { forecast: 45, actual: 47 }, { forecast: 50, actual: 51 },
    { forecast: 54, actual: 52 }, { forecast: 52, actual: 50 }, { forecast: 48, actual: 49 },
    { forecast: 45, actual: 44 }, { forecast: 49, actual: 50 }, { forecast: 52, actual: 53 }
  ],
  'denver': [
    { forecast: 45, actual: 44 }, { forecast: 50, actual: 52 }, { forecast: 55, actual: 54 },
    { forecast: 48, actual: 46 }, { forecast: 42, actual: 43 }, { forecast: 40, actual: 38 },
    { forecast: 45, actual: 46 }, { forecast: 52, actual: 53 }, { forecast: 58, actual: 56 },
    { forecast: 54, actual: 55 }, { forecast: 48, actual: 49 }, { forecast: 44, actual: 42 },
    { forecast: 40, actual: 41 }, { forecast: 46, actual: 47 }, { forecast: 52, actual: 51 }
  ],
  'boston': [
    { forecast: 42, actual: 40 }, { forecast: 45, actual: 46 }, { forecast: 48, actual: 47 },
    { forecast: 52, actual: 54 }, { forecast: 50, actual: 48 }, { forecast: 46, actual: 45 },
    { forecast: 43, actual: 44 }, { forecast: 45, actual: 43 }, { forecast: 50, actual: 51 },
    { forecast: 54, actual: 53 }, { forecast: 48, actual: 49 }, { forecast: 44, actual: 43 },
    { forecast: 40, actual: 41 }, { forecast: 45, actual: 44 }, { forecast: 50, actual: 52 }
  ]
};

// 模拟市场赔率生成
function generateMarketOdds(actualTemp) {
  const odds = [];
  const baseTemp = Math.floor(actualTemp / 2) * 2;
  
  for (let offset = -2; offset <= 2; offset++) {
    const low = baseTemp + offset * 2;
    const high = low + 1;
    
    const distance = Math.abs(actualTemp - (low + 0.5));
    const baseProb = Math.exp(-distance * distance / 8) * 100;
    
    // 市场偏差（模拟情绪）
    const bias = (Math.random() - 0.5) * 15;
    const prob = Math.max(5, Math.min(50, Math.round(baseProb + bias)));
    
    odds.push({
      outcome: `${low}-${high}°F`,
      probability: prob,
      range: [low, high]
    });
  }
  
  // 归一化
  const total = odds.reduce((sum, o) => sum + o.probability, 0);
  odds.forEach(o => o.probability = Math.round(o.probability / total * 100));
  
  return odds;
}

// 单次模拟交易
function simulateTrade(city, forecastTemp, actualTemp, betAmount = 50) {
  const odds = generateMarketOdds(actualTemp);
  const ladder = calculateLadder(forecastTemp, odds);
  
  let profit = -ladder.totalBet;
  let hitRange = null;
  
  for (const step of ladder.steps) {
    const match = step.range.match(/(\d+)-(\d+)/);
    if (match) {
      const low = parseInt(match[1]);
      const high = parseInt(match[2]);
      
      if (actualTemp >= low && actualTemp <= high) {
        const payout = step.betAmount / step.probability * 100;
        profit += payout;
        hitRange = step.range;
      }
    }
  }
  
  return {
    city,
    forecast: Math.round(forecastTemp),
    actual: Math.round(actualTemp),
    error: Math.abs(forecastTemp - actualTemp),
    bet: ladder.totalBet,
    profit: Math.round(profit),
    roi: Math.round((profit / ladder.totalBet) * 100),
    hit: profit > 0,
    hitRange,
    confidence: ladder.confidence
  };
}

// 运行大规模模拟
function runLargeSimulation(runs = 100) {
  console.log(`\n🎲 运行 ${runs} 次模拟交易...\n`);
  console.log('━'.repeat(70));
  
  const results = [];
  const cityStats = {};
  
  // 初始化城市统计
  CITIES.forEach(city => {
    cityStats[city.toLowerCase()] = {
      trades: 0,
      hits: 0,
      totalProfit: 0,
      totalBet: 0,
      totalError: 0
    };
  });
  
  // 运行模拟
  for (let i = 0; i < runs; i++) {
    // 随机选择城市
    const city = CITIES[Math.floor(Math.random() * CITIES.length)].toLowerCase();
    const history = HISTORICAL_DATA[city];
    
    if (!history || history.length === 0) continue;
    
    // 随机选择一条历史记录
    const record = history[Math.floor(Math.random() * history.length)];
    
    // 添加随机误差（模拟多气象源加权后的结果）
    const forecastNoise = (Math.random() - 0.5) * 3;
    const forecastTemp = record.forecast + forecastNoise;
    const actualTemp = record.actual;
    
    // 模拟交易
    const result = simulateTrade(city, forecastTemp, actualTemp);
    results.push(result);
    
    // 更新统计
    const stats = cityStats[city];
    stats.trades++;
    stats.totalBet += result.bet;
    stats.totalProfit += result.profit;
    stats.totalError += result.error;
    if (result.hit) stats.hits++;
  }
  
  // 打印城市统计
  console.log('\n📊 各城市表现:\n');
  
  const sortedCities = Object.entries(cityStats)
    .filter(([_, s]) => s.trades > 0)
    .sort((a, b) => (b[1].totalProfit / b[1].totalBet) - (a[1].totalProfit / a[1].totalBet));
  
  for (const [city, stats] of sortedCities) {
    if (stats.trades === 0) continue;
    
    const hitRate = Math.round(stats.hits / stats.trades * 100);
    const roi = Math.round(stats.totalProfit / stats.totalBet * 100);
    const avgError = Math.round(stats.totalError / stats.trades * 10) / 10;
    
    const emoji = roi > 50 ? '🔥' : roi > 20 ? '✅' : roi > 0 ? '📈' : '📉';
    
    console.log(`${emoji} ${city.toUpperCase().padEnd(15)} | 交易: ${String(stats.trades).padStart(3)} | 命中: ${hitRate}% | ROI: ${roi}% | 误差: ${avgError}°F`);
  }
  
  // 汇总统计
  const totalStats = {
    trades: results.length,
    hits: results.filter(r => r.hit).length,
    totalBet: results.reduce((sum, r) => sum + r.bet, 0),
    totalProfit: results.reduce((sum, r) => sum + r.profit, 0),
    avgError: results.reduce((sum, r) => sum + r.error, 0) / results.length
  };
  
  const hitRate = Math.round(totalStats.hits / totalStats.trades * 100);
  const avgROI = Math.round(totalStats.totalProfit / totalStats.totalBet * 100);
  
  console.log('\n' + '━'.repeat(70));
  console.log('\n📈 总体统计:\n');
  console.log(`   总交易次数: ${totalStats.trades}`);
  console.log(`   总命中次数: ${totalStats.hits}`);
  console.log(`   命中率: ${hitRate}%`);
  console.log(`   总投入: $${totalStats.totalBet}`);
  console.log(`   总收益: $${totalStats.totalProfit}`);
  console.log(`   平均ROI: ${avgROI}%`);
  console.log(`   平均误差: ${Math.round(totalStats.avgError * 10) / 10}°F`);
  
  // 收益分布
  const profits = results.map(r => r.profit);
  const wins = profits.filter(p => p > 0);
  const losses = profits.filter(p => p < 0);
  
  console.log('\n📊 收益分布:\n');
  console.log(`   盈利交易: ${wins.length} 次 (平均 +$${wins.length > 0 ? Math.round(wins.reduce((a,b) => a+b, 0) / wins.length) : 0})`);
  console.log(`   亏损交易: ${losses.length} 次 (平均 -$${losses.length > 0 ? Math.abs(Math.round(losses.reduce((a,b) => a+b, 0) / losses.length)) : 0})`);
  console.log(`   最大盈利: $${Math.max(...profits)}`);
  console.log(`   最大亏损: $${Math.min(...profits)}`);
  
  // 最佳/最差城市
  const bestCity = sortedCities[0];
  const worstCity = sortedCities[sortedCities.length - 1];
  
  console.log('\n🏆 最佳城市: ' + bestCity[0].toUpperCase());
  console.log('💀 最差城市: ' + worstCity[0].toUpperCase());
  
  // 策略建议
  console.log('\n💡 策略建议:\n');
  
  if (avgROI > 30) {
    console.log('   ✅ 策略有效，建议继续使用');
    console.log('   💰 推荐城市: ' + sortedCities.slice(0, 3).map(c => c[0].toUpperCase()).join(', '));
  } else if (avgROI > 10) {
    console.log('   ⚠️ 策略有潜力，但需优化');
    console.log('   📍 聚焦高命中率城市');
  } else if (avgROI > 0) {
    console.log('   ⚠️ 收益微薄，建议调整参数');
    console.log('   🎯 提高边缘优势阈值');
  } else {
    console.log('   ❌ 当前策略亏损，需要重新设计');
    console.log('   🔧 建议: 提高预报准确率 或 降低单次投入');
  }
  
  console.log('\n' + '━'.repeat(70));
  
  return {
    totalStats,
    cityStats,
    results
  };
}

// 命令行入口
if (require.main === module) {
  const runs = parseInt(process.argv[2]) || 100;
  runLargeSimulation(runs);
}

module.exports = {
  simulateTrade,
  runLargeSimulation,
  CITIES,
  HISTORICAL_DATA
};
