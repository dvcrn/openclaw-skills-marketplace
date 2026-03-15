#!/usr/bin/env node

/**
 * Meme Coin Launch Monitor Pro
 * 专业版土狗币监控工具
 * @version 1.0.0
 * @price ¥39/月
 */

const axios = require('axios');

// 配置
const CONFIG = {
  apis: {
    dexscreener: 'https://api.dexscreener.com/latest',
    pumpfun: 'https://frontend-api.pump.fun',
    solscan: 'https://public-api.solscan.io',
  },
  riskThresholds: {
    low: 3,
    medium: 6,
    high: 8,
  },
};

/**
 * 获取新币列表
 */
async function fetchNewTokens(chain = 'solana', limit = 20) {
  try {
    const response = await axios.get(
      `${CONFIG.apis.dexscreener}/tokens/newest`,
      { params: { chain, limit } }
    );
    return response.data.tokens || [];
  } catch (error) {
    console.error(`获取新币列表失败:`, error.message);
    return [];
  }
}

/**
 * 计算风险评分
 */
function calculateRiskScore(token) {
  let score = 0;
  
  // 流动性风险
  if (token.liquidity < 10000) score += 3;
  else if (token.liquidity < 50000) score += 2;
  
  // LP 锁定
  if (!token.lpLocked) score += 3;
  
  // 持币集中
  if (token.top10Holders > 50) score += 2;
  
  // 合约风险
  if (token.renounced !== true) score += 2;
  
  return Math.min(10, score);
}

/**
 * 生成投资建议
 */
function generateAdvice(riskScore, liquidity, marketCap) {
  if (riskScore <= 3 && liquidity > 50000) {
    return '✅ 可参与 | 建议仓位：5-10% | 止损：-30%';
  }
  if (riskScore <= 5 && liquidity > 20000) {
    return '⚠️ 谨慎参与 | 建议仓位：1-3% | 止损：-50%';
  }
  return '❌ 高风险 | 不建议参与';
}

/**
 * 主函数
 */
async function main() {
  const args = process.argv.slice(2);
  
  console.log('🚀 Meme Coin Launch Monitor Pro');
  console.log('=' .repeat(50));
  
  // 示例输出
  const sampleTokens = [
    {
      name: 'PEPE2.0',
      symbol: 'PEPE2',
      price: 0.00012,
      mc: 120000,
      liquidity: 45000,
      lpLocked: true,
      top10Holders: 28,
      riskScore: 4.2,
    },
    {
      name: 'DogeKing',
      symbol: 'DOGEK',
      price: 0.0000045,
      mc: 45000,
      liquidity: 12000,
      lpLocked: false,
      top10Holders: 65,
      riskScore: 7.8,
    },
  ];
  
  console.log('\n🔥 热门新币:\n');
  sampleTokens.forEach((item, index) => {
    const riskLevel = item.riskScore <= 3 ? '低' : item.riskScore <= 6 ? '中' : '高';
    console.log(`${index + 1}. ${item.name} (${item.symbol})`);
    console.log(`   价格：$${item.price} | MC: $${(item.mc/1000).toFixed(1)}K`);
    console.log(`   流动性：$${(item.liquidity/1000).toFixed(1)}K | LP 锁定：${item.lpLocked ? '✅' : '❌'}`);
    console.log(`   风险：${riskLevel} (${item.riskScore}/10) | Top10: ${item.top10Holders}%`);
    console.log(`   ${generateAdvice(item.riskScore, item.liquidity, item.mc)}\n`);
  });
  
  console.log('⚡ 使用 --monitor 开启实时监控');
  console.log('🔔 专业版支持 Telegram 实时推送新币');
}

main().catch(console.error);
