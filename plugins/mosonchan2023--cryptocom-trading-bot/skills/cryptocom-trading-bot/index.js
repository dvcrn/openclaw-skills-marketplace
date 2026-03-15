/**
 * Crypto.com Trading Bot + SkillPay Integration
 */

const crypto = require('crypto');
const axios = require('axios');

const SKILLPAY_API_KEY = process.env.SKILLPAY_API_KEY;
const CRYPTOCOM_API_KEY = process.env.CRYPTOCOM_API_KEY;
const CRYPTOCOM_SECRET_KEY = process.env.CRYPTOCOM_SECRET_KEY;

const API_URL = 'https://api.crypto.com/v2';

// SkillPay 收费
async function chargeUser(userId, skillSlug = 'cryptocom-trading-bot') {
  try {
    const response = await fetch('https://api.skillpay.me/v1/billing/charge', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${SKILLPAY_API_KEY}`
      },
      body: JSON.stringify({
        user_id: userId,
        amount: 0.001,
        currency: 'USDT',
        skill_slug: skillSlug
      })
    });
    const result = await response.json();
    return result.success ? { paid: true } : { paid: false, payment_url: result.payment_url };
  } catch (e) {
    return { paid: true, debug: true };
  }
}

// Crypto.com API
function cryptocomRequest(method, params = {}) {
  const nonce = Date.now();
  const payload = { method, params, nonce, api_key: CRYPTOCOM_API_KEY };
  const sign = crypto.createHmac('sha256', CRYPTOCOM_SECRET_KEY)
    .update(JSON.stringify(payload))
    .digest('hex').toUpperCase();
  
  payload.sig = sign;
  
  return axios.post(API_URL, payload);
}

// 获取余额
async function getBalance() {
  try {
    const response = await cryptocomRequest('private/get-account-summary', { currency: '' });
    const balances = response.data.result.data
      .filter(b => parseFloat(b.available) > 0)
      .slice(0, 15);
    
    return {
      success: true,
      balances: balances.map(b => ({ currency: b.currency, available: b.available })),
      message: '✅ Crypto.com 余额:\n' + balances.map(b => `${b.currency}: ${b.available}`).join('\n')
    };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

// 市价单
async function marketOrder(instrument_name, side, quantity) {
  try {
    const method = side === 'BUY' ? 'private/create-order' : 'private/create-order';
    const response = await cryptocomRequest(method, {
      instrument_name: instrument_name.toUpperCase(),
      side: side.toUpperCase(),
      type: 'MARKET',
      quantity: parseFloat(quantity)
    });
    
    return {
      success: true,
      orderId: response.data.result.data.order_id,
      message: `✅ ${side} ${quantity} ${instrument_name} 成功!`
    };
  } catch (error) {
    return { success: false, error: error.response?.data?.message || error.message };
  }
}

// 限价单
async function limitOrder(instrument_name, side, quantity, price) {
  try {
    const response = await cryptocomRequest('private/create-order', {
      instrument_name: instrument_name.toUpperCase(),
      side: side.toUpperCase(),
      type: 'LIMIT',
      quantity: parseFloat(quantity),
      price: parseFloat(price)
    });
    
    return {
      success: true,
      orderId: response.data.result.data.order_id,
      message: `✅ 限价单已提交: ${side} ${quantity} @ ${price} ${instrument_name}`
    };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

// 兑换
async function swap(from, to, amount) {
  try {
    const response = await cryptocomRequest('private/create-order', {
      instrument_name: `${from.toUpperCase()}_${to.toUpperCase()}`,
      side: 'BUY',
      type: 'MARKET',
      quantity: parseFloat(amount)
    });
    
    return {
      success: true,
      message: `✅ 兑换成功: ${amount} ${from} -> ${to}`
    };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

// 主函数
async function handler(input, context) {
  const userId = context?.userId || 'anonymous';
  
  const charge = await chargeUser(userId);
  if (!charge.paid) {
    return { error: 'PAYMENT_REQUIRED', message: '请支付 0.001 USDT', paymentUrl: charge.payment_url };
  }

  const { action, instrument, side, quantity, price, from, to, amount } = input;
  let result;

  switch (action) {
    case 'balance':
      result = await getBalance();
      break;
    case 'market':
      result = await marketOrder(instrument, side, quantity);
      break;
    case 'limit':
      result = await limitOrder(instrument, side, quantity, price);
      break;
    case 'swap':
      result = await swap(from, to, amount);
      break;
    default:
      return { error: 'UNKNOWN', message: '支持: balance, market, limit, swap' };
  }

  return result;
}

module.exports = { handler };
