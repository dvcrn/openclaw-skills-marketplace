/**
 * AI Research Analyst + SkillPay
 * 深度市场分析、项目调研、竞争对比
 */

const axios = require('axios');

const SKILLPAY_API_KEY = process.env.SKILLPAY_API_KEY;

// 收费
async function chargeUser(userId, skillSlug = 'ai-research-analyst') {
  try {
    const res = await fetch('https://api.skillpay.me/v1/billing/charge', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${SKILLPAY_API_KEY}`
      },
      body: JSON.stringify({ user_id: userId, amount: 0.001, currency: 'USDT', skill_slug: skillSlug })
    });
    const data = await res.json();
    return data.success ? { paid: true } : { paid: false, payment_url: data.payment_url };
  } catch (e) {
    return { paid: true, debug: true };
  }
}

// 项目调研
async function researchProject(project) {
  try {
    // 获取 CoinGecko 项目信息
    const response = await axios.get(`https://api.coingecko.com/api/v3/coins/${project.toLowerCase()}?localization=false&tickers=false&community_data=false&developer_data=false`);
    const data = response.data;
    
    const analysis = {
      name: data.name,
      symbol: data.symbol.toUpperCase(),
      price: data.market_data.current_price.usd,
      mc: data.market_data.market_cap.usd,
      volume24h: data.market_data.total_volume.usd,
      ath: data.market_data.ath.usd,
      ath_change: data.market_data.ath_change_percentage.usd,
      description: data.description.en?.substring(0, 500) || 'No description'
    };
    
    // 简单评级
    let rating = 'B';
    if (analysis.volume24h > 1000000000) rating = 'A';
    if (analysis.mc < 10000000) rating = 'C';
    
    return {
      success: true,
      project: analysis,
      rating,
      message: `📊 项目调研: ${analysis.name} (${analysis.symbol})\n\n💰 价格: $${analysis.price}\n市值: $${(analysis.mc/1e9).toFixed(2)}B\n24h交易量: $${(analysis.volume24h/1e9).toFixed(2)}B\nATH: $${analysis.ath}\n从ATH下跌: ${analysis.ath_change.toFixed(2)}%\n\n📝 简介: ${analysis.description}...\n\n⭐ 评级: ${rating}`
    };
  } catch (e) {
    return { success: false, error: `项目未找到: ${project}` };
  }
}

// 市场分析
async function marketAnalysis(category) {
  try {
    // 获取分类数据
    const response = await axios.get(`https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&category=${category}&order=market_cap_desc&per_page=10`);
    const coins = response.data;
    
    const totalMc = coins.reduce((sum, c) => sum + c.market_cap, 0);
    const totalVol = coins.reduce((sum, c) => sum + c.total_volume, 0);
    const avgChange = coins.reduce((sum, c) => sum + c.price_change_percentage_24h, 0) / coins.length;
    
    return {
      success: true,
      category,
      stats: {
        count: coins.length,
        totalMc: totalMc,
        totalVol: totalVol,
        avgChange24h: avgChange
      },
      topCoins: coins.slice(0, 5).map(c => ({ name: c.name, price: c.current_price, change: c.price_change_percentage_24h })),
      message: `📈 ${category} 市场分析:\n\n总市值: $${(totalMc/1e9).toFixed(2)}B\n24h交易量: $${(totalVol/1e9).toFixed(2)}B\n平均24h变化: ${avgChange.toFixed(2)}%\n\n🔥 Top 5:\n${coins.slice(0,5).map((c,i) => `${i+1}. ${c.name}: $${c.current_price} (${c.price_change_percentage_24h.toFixed(2)}%)`).join('\n')}`
    };
  } catch (e) {
    return { success: false, error: e.message };
  }
}

// 竞争对比
async function compareProjects(projects) {
  try {
    const projectList = projects.split(',').map(p => p.trim().toLowerCase());
    const response = await axios.get(`https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=${projectList.join(',')}&order=market_cap_desc`);
    const data = response.data;
    
    const comparison = data.map(p => ({
      name: p.name,
      symbol: p.symbol.toUpperCase(),
      price: p.current_price,
      mc: p.market_cap,
      volume: p.total_volume,
      change24h: p.price_change_percentage_24h
    }));
    
    let msg = '⚖️ 项目对比:\n\n';
    comparison.forEach(p => {
      msg += `【${p.name}】\n`;
      msg += `  价格: $${p.price}\n`;
      msg += `  市值: $${(p.mc/1e9).toFixed(2)}B\n`;
      msg += `  24h: ${p.change24h?.toFixed(2)}%\n\n`;
    });
    
    return { success: true, comparison, message: msg };
  } catch (e) {
    return { success: false, error: e.message };
  }
}

// 投资报告
async function investmentReport(token) {
  try {
    const [priceData, marketData] = await Promise.all([
      axios.get(`https://api.coingecko.com/api/v3/coins/${token.toLowerCase()}?localization=false&tickers=false&community_data=false`),
      axios.get(`https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=${token.toLowerCase()}&order=market_cap_desc&per_page=1`)
    ]);
    
    const data = priceData.data;
    const market = marketData.data[0];
    
    const report = {
      token: data.name,
      price: market.current_price,
      recommendation: market.current_price > market.ath * 0.5 ? 'HOLD' : 'BUY',
      risk: market.market_cap < 10000000 ? 'HIGH' : 'MEDIUM',
      timestamp: new Date().toISOString()
    };
    
    return {
      success: true,
      report,
      message: `📋 投资报告: ${data.name}\n\n💵 当前价格: $${report.price}\n📊 建议: ${report.recommendation}\n⚠️ 风险等级: ${report.risk}\n\n⚠️ 免责声明: 此报告仅供参考,不构成投资建议`
    };
  } catch (e) {
    return { success: false, error: e.message };
  }
}

// 主函数
async function handler(input, context) {
  const userId = context?.userId || 'anonymous';
  
  const charge = await chargeUser(userId);
  if (!charge.paid) {
    return { error: 'PAYMENT_REQUIRED', message: '请支付 0.001 USDT', paymentUrl: charge.payment_url };
  }

  const { action, project, category, projects, token } = input;
  let result;

  switch (action) {
    case 'research':
    case 'analyze':
      result = await researchProject(project);
      break;
    case 'market':
    case 'category':
      result = await marketAnalysis(category);
      break;
    case 'compare':
      result = await compareProjects(projects);
      break;
    case 'report':
    case 'investment':
      result = await investmentReport(token);
      break;
    default:
      return {
        error: 'UNKNOWN',
        message: '支持操作: research, market, compare, report\n示例: { action: "research", project: "bitcoin" }',
        supported: ['research', 'market', 'compare', 'report']
      };
  }

  return result;
}

module.exports = { handler };
