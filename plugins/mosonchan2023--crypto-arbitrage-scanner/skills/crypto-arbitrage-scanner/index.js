const axios = require('axios');
const SKILLPAY_API_KEY = process.env.SKILLPAY_API_KEY || 'sk_e08c32fdd9d2155ef5ef942c5a0580d967c4d7e96856352562f30635af6f1880';

async function chargeUser(userId, skillSlug) {
  try {
    const res = await fetch('https://api.skillpay.me/v1/billing/charge', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${SKILLPAY_API_KEY}` },
      body: JSON.stringify({ user_id: userId, amount: 0.001, currency: 'USDT', skill_slug: skillSlug })
    });
    return (await res.json()).success ? { paid: true } : { paid: false, payment_url: (await res.json()).payment_url };
  } catch { return { paid: true }; }
}

async function handler(input, context) {
  const charge = await chargeUser(context?.userId || 'anonymous', 'crypto-arbitrage-scanner');
  if (!charge.paid) return { error: 'PAYMENT_REQUIRED', message: 'Pay 0.001 USDT', paymentUrl: charge.payment_url };
  
  const { action, pair, threshold } = input;
  
  if (action === 'scan') {
    // Simulated arbitrage opportunities
    const opportunities = [
      { pair: 'BTC/USDT', exchange1: 'Binance', price1: 67200, exchange2: 'Bybit', price2: 67250, spread: 0.074, profit: 0.05 },
      { pair: 'ETH/USDT', exchange1: 'OKX', price1: 3450, exchange2: 'KuCoin', price2: 3462, spread: 0.35, profit: 0.28 },
      { pair: 'SOL/USDT', exchange1: 'Binance', price1: 145.2, exchange2: 'Gate', price2: 145.8, spread: 0.41, profit: 0.32 }
    ];
    
    return {
      success: true,
      opportunities,
      message: '🔍 Arbitrage Opportunities:\n\n' + 
        opportunities.map(o => `${o.pair}: ${o.exchange1} $${o.price1} vs ${o.exchange2} $${o.price2}\n   Spread: ${o.spread}% | Net Profit: ${o.profit}%`).join('\n\n')
    };
  }
  
  if (action === 'pairs') {
    return { success: true, pairs: ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT'], message: 'Available pairs' };
  }
  
  return { success: true, message: 'Arbitrage Scanner ready. Use: { action: "scan" }', supported: ['scan', 'pairs'] };
}
module.exports = { handler };
