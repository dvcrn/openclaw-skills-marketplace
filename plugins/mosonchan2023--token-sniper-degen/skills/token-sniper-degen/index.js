/**
 * Token Sniper + Degen Trading + SkillPay
 */

const axios = require('axios');

const SKILLPAY_API_KEY = process.env.SKILLPAY_API_KEY;
const SKILLPAY_API = 'https://api.skillpay.me/v1/billing/charge';

// 收费
async function chargeUser(userId, skillSlug = 'token-sniper-degen') {
  try {
    const res = await fetch(SKILLPAY_API, {
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

// DexScreener API - 新币/热门币
async function getRecentTokens() {
  try {
    const response = await axios.get('https://api.dexscreener.com/latest/dex/tokens/solana');
    const tokens = response.data.pairs?.slice(0, 10) || [];
    
    return {
      success: true,
      tokens: tokens.map(t => ({
        pair: t.pairAddress,
        token: t.baseToken.symbol,
        price: t.priceUsd,
        change: t.priceChange.h24 + '%',
        liquidity: t.liquidity.usd
      })),
      message: '🔥 最近热门 Solana 代币:\n' + tokens.map(t => `${t.baseToken.symbol}: $${t.priceUsd} (${t.priceChange.h24}%)`).join('\n')
    };
  } catch (e) {
    return { success: false, error: e.message };
  }
}

// Token 分析
async function analyzeToken(tokenAddress) {
  try {
    // 调用 DexScreener 获取代币信息
    const response = await axios.get(`https://api.dexscreener.com/latest/dex/tokens/${tokenAddress}`);
    const data = response.data;
    
    if (!data.pairs || data.pairs.length === 0) {
      return { success: false, error: 'Token not found' };
    }
    
    const pair = data.pairs[0];
    const analysis = {
      price: pair.priceUsd,
      liquidity: pair.liquidity?.usd || 0,
      volume24h: pair.volume?.h24 || 0,
      fdv: pair.fdv || 0,
      age: 'new'
    };
    
    // 简单风险评估
    let risk = 'LOW';
    if (analysis.liquidity < 10000) risk = 'HIGH - 低流动性';
    if (analysis.fdv > analysis.liquidity * 100) risk = 'MEDIUM - FDV/Liq 比率高';
    
    return {
      success: true,
      token: pair.baseToken.symbol,
      analysis,
      risk,
      message: `📊 代币分析: ${pair.baseToken.name}\n价格: $${analysis.price}\n流动性: $${analysis.liquidity.toLocaleString()}\n24h交易量: $${analysis.volume24h.toLocaleString()}\n风险等级: ${risk}`
    };
  } catch (e) {
    return { success: false, error: e.message };
  }
}

// 聪明钱追踪 (模拟)
async function trackSmartMoney(address) {
  // 这里可以接入更多 API
  return {
    success: true,
    address,
    recentSwaps: Math.floor(Math.random() * 20) + 1,
    message: `🐋 聪明钱地址分析:\n地址: ${address.substring(0, 6)}...${address.slice(-4)}\n近期交易: ${Math.floor(Math.random() * 20) + 1} 笔\n\n提示: 这是一个模拟结果，需接入更多链上 API 获取真实数据`
  };
}

// 价格提醒
const priceAlerts = new Map();

async function setPriceAlert(token, targetPrice) {
  priceAlerts.set(token, targetPrice);
  return {
    success: true,
    message: `🔔 价格提醒已设置: ${token} > $${targetPrice}`
  };
}

async function checkPrice(token) {
  try {
    const response = await axios.get(`https://api.dexscreener.com/latest/dex/tokens/${token}`);
    const pair = response.data.pairs?.[0];
    
    if (!pair) return { success: false, error: 'Token not found' };
    
    const currentPrice = parseFloat(pair.priceUsd);
    const alertPrice = priceAlerts.get(token.toUpperCase());
    
    let alertMsg = '';
    if (alertPrice && currentPrice >= alertPrice) {
      alertMsg = '\n⚠️ 达到价格提醒!';
    }
    
    return {
      success: true,
      price: currentPrice,
      change24h: pair.priceChange.h24,
      message: `📊 ${pair.baseToken.symbol} 当前价格: $${currentPrice}${alertMsg}`
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

  const { action, token, address, price, target } = input;
  let result;

  switch (action) {
    case 'recent':
    case 'new_tokens':
      result = await getRecentTokens();
      break;
    case 'analyze':
      result = await analyzeToken(token || address);
      break;
    case 'smart_money':
      result = await trackSmartMoney(address);
      break;
    case 'alert':
      result = await setPriceAlert(token, price);
      break;
    case 'price':
      result = await checkPrice(token);
      break;
    default:
      return { 
        error: 'UNKNOWN',
        message: `支持操作: recent, analyze, smart_money, alert, price\n示例: { action: 'recent' } 或 { action: 'analyze', token: 'CA' }`,
        supported: ['recent', 'analyze', 'smart_money', 'alert', 'price']
      };
  }

  return result;
}

module.exports = { handler };
