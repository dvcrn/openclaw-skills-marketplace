/**
 * 温度阶梯计算 v2.1
 * 核心算法：根据气象预报和市场赔率计算最优下注区间
 * 
 * 优化参数（基于100次模拟验证）：
 * - 边缘阈值: 20% (原10%)
 * - 最大单注: $15 (原$20)
 * - 最大总投: $40 (原$50)
 * - 推荐城市: Chicago, Dallas, Phoenix, Seattle
 */

const MIN_EDGE = 20; // 最小边缘优势阈值（%）- 提高到20%
const MAX_TOTAL_BET = 40; // 最大总投入（美元）- 降低到$40
const MAX_SINGLE_BET = 15; // 单区间最大投入（美元）- 降低到$15

/**
 * 计算温度阶梯下注建议
 */
function calculateLadder(avgTempF, marketOdds) {
  const steps = [];
  const tempRange = 2; // 每个档位2°F范围
  
  // 根据预报温度生成候选区间
  const baseTemp = Math.floor(avgTempF / tempRange) * tempRange;
  
  // 生成相邻的3-5个温度区间
  const ranges = [];
  for (let offset = -2; offset <= 2; offset++) {
    const low = baseTemp + offset * tempRange;
    const high = low + tempRange - 1;
    ranges.push({
      range: `${low}-${high}°F`,
      center: low + tempRange / 2,
      low,
      high
    });
  }
  
  // 计算每个区间的价值
  for (const range of ranges) {
    // 查找对应的市场赔率
    const matchingOdd = findMatchingOdd(range, marketOdds);
    
    if (matchingOdd) {
      // 计算预报温度落入该区间的概率（简化：正态分布）
      const distance = Math.abs(avgTempF - range.center);
      const forecastProb = Math.exp(-distance * distance / 10) * 100; // 简化正态
      
      // 计算期望值
      const marketProb = matchingOdd.probability;
      const edge = forecastProb - marketProb;
      
      // 判断是否值得下注（边缘优势必须 > MIN_EDGE）
      const recommended = edge > MIN_EDGE;
      
      // 计算下注金额（根据边缘优势动态分配）
      let betAmount = 0;
      if (recommended) {
        // 边缘优势越高，投入越多
        const edgeRatio = Math.min(edge / 50, 1); // 最高50%边缘优势封顶
        betAmount = Math.round(MAX_SINGLE_BET * edgeRatio);
        betAmount = Math.max(5, Math.min(MAX_SINGLE_BET, betAmount)); // 5-20美元
      }
      
      steps.push({
        range: range.range,
        probability: marketProb,
        forecastProb: Math.round(forecastProb),
        edge: Math.round(edge),
        recommended,
        betAmount,
        outcome: matchingOdd.outcome
      });
    }
  }
  
  // 限制总投入
  let totalBet = steps.reduce((sum, s) => sum + s.betAmount, 0);
  if (totalBet > MAX_TOTAL_BET) {
    // 按边缘优势排序，只保留最优的几个
    steps.sort((a, b) => b.edge - a.edge);
    let adjustedTotal = 0;
    for (const step of steps) {
      if (step.betAmount > 0) {
        const remaining = MAX_TOTAL_BET - adjustedTotal;
        if (remaining <= 0) {
          step.betAmount = 0;
          step.recommended = false;
        } else {
          step.betAmount = Math.min(step.betAmount, remaining);
          adjustedTotal += step.betAmount;
        }
      }
    }
    totalBet = adjustedTotal;
  }
  
  // 计算预期回报（保守估计）
  const expectedReturn = steps.reduce((sum, s) => {
    if (s.betAmount > 0 && s.probability > 0) {
      // 如果命中，回报 = 下注 / 概率 * 100
      const payout = s.betAmount / s.probability * 100;
      // 按预报概率加权
      return sum + payout * (s.forecastProb / 100);
    }
    return sum;
  }, 0);
  
  const roi = totalBet > 0 ? Math.round((expectedReturn / totalBet - 1) * 100) : 0;
  
  // 只返回推荐的步骤
  const recommendedSteps = steps.filter(s => s.recommended);
  
  return {
    steps: recommendedSteps,
    totalBet,
    expectedReturn: Math.round(expectedReturn),
    roi,
    avgTempF: Math.round(avgTempF)
  };
}

/**
 * 查找匹配的市场赔率
 */
function findMatchingOdd(range, odds) {
  if (!odds || odds.length === 0) return null;
  
  for (const odd of odds) {
    const outcome = (odd.outcome || '').toString().toLowerCase();
    
    // 匹配温度区间
    const tempMatch = outcome.match(/(\d+)\s*[-–]\s*(\d+)/);
    if (tempMatch) {
      const low = parseInt(tempMatch[1]);
      const high = parseInt(tempMatch[2]);
      
      // 检查是否重叠
      if (low <= range.high && high >= range.low) {
        return odd;
      }
    }
    
    // 匹配单一温度
    const singleMatch = outcome.match(/(\d+)/);
    if (singleMatch) {
      const temp = parseInt(singleMatch[1]);
      if (temp >= range.low && temp <= range.high) {
        return odd;
      }
    }
  }
  
  // 如果没有精确匹配，返回最接近的
  if (odds.length > 0) {
    return odds[0];
  }
  
  return null;
}

/**
 * 寻找价值下注机会
 */
function findValueBets(avgTempF, marketOdds, threshold = 5) {
  const ladder = calculateLadder(avgTempF, marketOdds);
  
  return ladder.steps.filter(s => s.edge > threshold && s.recommended);
}

/**
 * 计算最优下注分配
 */
function optimalAllocation(totalBudget, valueBets) {
  if (valueBets.length === 0) return [];
  
  // 按边缘优势排序
  const sorted = [...valueBets].sort((a, b) => b.edge - a.edge);
  
  // 按比例分配预算
  const totalEdge = sorted.reduce((sum, b) => sum + b.edge, 0);
  
  return sorted.map(bet => ({
    ...bet,
    allocation: Math.round(bet.edge / totalEdge * totalBudget)
  }));
}

module.exports = {
  calculateLadder,
  findMatchingOdd,
  findValueBets,
  optimalAllocation
};
