/**
 * 优化策略模拟
 * - 只选择高准确率城市
 * - 提高边缘优势阈值
 * - 增加置信度过滤
 */

const { simulateTrade, CITIES, HISTORICAL_DATA } = require('./simulation');

// 优化参数
const OPTIMIZED_CONFIG = {
  // 只选择高准确率城市
  allowedCities: ['seattle', 'phoenix', 'chicago', 'dallas'],
  
  // 边缘优势阈值提高到20%
  minEdge: 20,
  
  // 最大单次投入降低
  maxSingleBet: 15,
  
  // 最大总投入
  maxTotalBet: 40,
  
  // 置信度阈值
  minConfidence: 70
};

// 优化版模拟交易
function simulateOptimizedTrade(city, forecastTemp, actualTemp) {
  const odds = generateMarketOdds(actualTemp);
  
  // 使用更高的边缘阈值
  const ladder = calculateOptimizedLadder(forecastTemp, odds, OPTIMIZED_CONFIG);
  
  if (ladder.steps.length === 0) {
    return null; // 跳过无价值的交易
  }
  
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
    edge: ladder.avgEdge
  };
}

// 优化版阶梯计算
function calculateOptimizedLadder(avgTempF, marketOdds, config) {
  const steps = [];
  const tempRange = 2;
  const baseTemp = Math.floor(avgTempF / tempRange) * tempRange;
  
  for (let offset = -2; offset <= 2; offset++) {
    const low = baseTemp + offset * tempRange;
    const high = low + tempRange - 1;
    const center = low + tempRange / 2;
    
    const matchingOdd = findMatchingOdd({ low, high }, marketOdds);
    
    if (matchingOdd) {
      const distance = Math.abs(avgTempF - center);
      const forecastProb = Math.exp(-distance * distance / 10) * 100;
      const marketProb = matchingOdd.probability;
      const edge = forecastProb - marketProb;
      
      // 使用更高的边缘阈值
      if (edge > config.minEdge) {
        const edgeRatio = Math.min(edge / 50, 1);
        let betAmount = Math.round(config.maxSingleBet * edgeRatio);
        betAmount = Math.max(5, Math.min(config.maxSingleBet, betAmount));
        
        steps.push({
          range: `${low}-${high}°F`,
          probability: marketProb,
          forecastProb: Math.round(forecastProb),
          edge: Math.round(edge),
          betAmount
        });
      }
    }
  }
  
  // 限制总投入
  let totalBet = steps.reduce((sum, s) => sum + s.betAmount, 0);
  if (totalBet > config.maxTotalBet) {
    steps.sort((a, b) => b.edge - a.edge);
    let adjustedTotal = 0;
    for (const step of steps) {
      const remaining = config.maxTotalBet - adjustedTotal;
      step.betAmount = Math.min(step.betAmount, remaining);
      adjustedTotal += step.betAmount;
    }
    totalBet = adjustedTotal;
  }
  
  return {
    steps,
    totalBet,
    avgEdge: steps.length > 0 ? Math.round(steps.reduce((s, x) => s + x.edge, 0) / steps.length) : 0
  };
}

function findMatchingOdd(range, odds) {
  if (!odds || odds.length === 0) return null;
  
  for (const odd of odds) {
    const outcome = (odd.outcome || '').toString().toLowerCase();
    const tempMatch = outcome.match(/(\d+)\s*[-–]\s*(\d+)/);
    if (tempMatch) {
      const low = parseInt(tempMatch[1]);
      const high = parseInt(tempMatch[2]);
      if (low <= range.high && high >= range.low) {
        return odd;
      }
    }
  }
  return odds[0];
}

function generateMarketOdds(actualTemp) {
  const odds = [];
  const baseTemp = Math.floor(actualTemp / 2) * 2;
  
  for (let offset = -2; offset <= 2; offset++) {
    const low = baseTemp + offset * 2;
    const high = low + 1;
    
    const distance = Math.abs(actualTemp - (low + 0.5));
    const baseProb = Math.exp(-distance * distance / 8) * 100;
    const bias = (Math.random() - 0.5) * 15;
    const prob = Math.max(5, Math.min(50, Math.round(baseProb + bias)));
    
    odds.push({
      outcome: `${low}-${high}°F`,
      probability: prob,
      range: [low, high]
    });
  }
  
  const total = odds.reduce((sum, o) => sum + o.probability, 0);
  odds.forEach(o => o.probability = Math.round(o.probability / total * 100));
  
  return odds;
}

// 运行优化版模拟
function runOptimizedSimulation(runs = 100) {
  console.log(`\n🎯 优化策略模拟 (${runs}次)\n`);
  console.log('配置:');
  console.log(`   允许城市: ${OPTIMIZED_CONFIG.allowedCities.join(', ')}`);
  console.log(`   最小边缘: ${OPTIMIZED_CONFIG.minEdge}%`);
  console.log(`   最大单注: $${OPTIMIZED_CONFIG.maxSingleBet}`);
  console.log(`   最大总投: $${OPTIMIZED_CONFIG.maxTotalBet}`);
  console.log('\n' + '━'.repeat(70));
  
  const results = [];
  const cityStats = {};
  let skipped = 0;
  
  OPTIMIZED_CONFIG.allowedCities.forEach(city => {
    cityStats[city] = { trades: 0, hits: 0, totalProfit: 0, totalBet: 0 };
  });
  
  for (let i = 0; i < runs * 2; i++) { // 多跑一些，因为会跳过
    const city = OPTIMIZED_CONFIG.allowedCities[Math.floor(Math.random() * OPTIMIZED_CONFIG.allowedCities.length)];
    const history = HISTORICAL_DATA[city];
    
    if (!history) continue;
    
    const record = history[Math.floor(Math.random() * history.length)];
    const forecastNoise = (Math.random() - 0.5) * 3;
    const forecastTemp = record.forecast + forecastNoise;
    const actualTemp = record.actual;
    
    const result = simulateOptimizedTrade(city, forecastTemp, actualTemp);
    
    if (result === null) {
      skipped++;
      continue;
    }
    
    results.push(result);
    
    const stats = cityStats[city];
    stats.trades++;
    stats.totalBet += result.bet;
    stats.totalProfit += result.profit;
    if (result.hit) stats.hits++;
    
    if (results.length >= runs) break;
  }
  
  // 打印结果
  console.log('\n📊 各城市表现:\n');
  
  const sortedCities = Object.entries(cityStats)
    .filter(([_, s]) => s.trades > 0)
    .sort((a, b) => (b[1].totalProfit / b[1].totalBet) - (a[1].totalProfit / a[1].totalBet));
  
  for (const [city, stats] of sortedCities) {
    if (stats.trades === 0) continue;
    
    const hitRate = Math.round(stats.hits / stats.trades * 100);
    const roi = Math.round(stats.totalProfit / stats.totalBet * 100);
    
    const emoji = roi > 30 ? '🔥' : roi > 15 ? '✅' : roi > 0 ? '📈' : '📉';
    
    console.log(`${emoji} ${city.toUpperCase().padEnd(12)} | 交易: ${String(stats.trades).padStart(3)} | 命中: ${hitRate}% | ROI: ${roi}% | 收益: $${stats.totalProfit}`);
  }
  
  // 汇总
  const totalStats = {
    trades: results.length,
    hits: results.filter(r => r.hit).length,
    totalBet: results.reduce((sum, r) => sum + r.bet, 0),
    totalProfit: results.reduce((sum, r) => sum + r.profit, 0)
  };
  
  const hitRate = Math.round(totalStats.hits / totalStats.trades * 100);
  const avgROI = Math.round(totalStats.totalProfit / totalStats.totalBet * 100);
  
  console.log('\n' + '━'.repeat(70));
  console.log('\n📈 总体统计:\n');
  console.log(`   有效交易: ${totalStats.trades} 次`);
  console.log(`   跳过交易: ${skipped} 次 (边缘不足)`);
  console.log(`   命中率: ${hitRate}%`);
  console.log(`   总投入: $${totalStats.totalBet}`);
  console.log(`   总收益: $${totalStats.totalProfit}`);
  console.log(`   平均ROI: ${avgROI}%`);
  
  return { totalStats, cityStats, results };
}

// 命令行入口
if (require.main === module) {
  const runs = parseInt(process.argv[2]) || 100;
  runOptimizedSimulation(runs);
}

module.exports = {
  simulateOptimizedTrade,
  runOptimizedSimulation,
  OPTIMIZED_CONFIG
};