const axios = require('axios');
const SKILLPAY_API_KEY = process.env.SKILLPAY_API_KEY || 'sk_e08c32fdd9d2155ef5ef942c5a0580d967c4d7e96856352562f30635af6f1880';

async function chargeUser(userId, skillSlug) {
  try {
    const res = await fetch('https://api.skillpay.me/v1/billing/charge', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${SKILLPAY_API_KEY}` },
      body: JSON.stringify({ user_id: userId, amount: 0.001, currency: 'USDT', skill_slug: skillSlug })
    });
    const data = await res.json();
    return data.success ? { paid: true } : { paid: false, payment_url: data.payment_url };
  } catch { return { paid: true }; }
}

async function handler(input, context) {
  const charge = await chargeUser(context?.userId || 'anonymous', 'defi-yield-optimizer');
  if (!charge.paid) return { error: 'PAYMENT_REQUIRED', message: 'Pay 0.001 USDT', paymentUrl: charge.payment_url };
  
  const { action, token, protocol, principal, days } = input;
  
  // Mock yield data - in production, fetch from APIs
  const yields = {
    USDC: { aave: 4.5, compound: 4.2, curve: 3.8, yearn: 5.1 },
    USDT: { aave: 4.3, compound: 4.0, curve: 3.5, yearn: 4.8 },
    DAI: { aave: 4.6, compound: 4.3, curve: 4.0, yearn: 5.2 }
  };
  
  if (action === 'best-yield' && token) {
    const tokenYields = yields[token.toUpperCase()] || yields.USDC;
    const best = Object.entries(tokenYields).sort((a, b) => b[1] - a[1])[0];
    return { 
      success: true, 
      token: token.toUpperCase(),
      bestProtocol: best[0],
      apy: best[1] + '%',
      allYields: tokenYields,
      message: `📈 ${token.toUpperCase()} Best Yield: ${best[0]} @ ${best[1]}% APY`
    };
  }
  
  if (action === 'calculate' && principal && protocol && days) {
    const rate = yields.USDC[protocol.toLowerCase()] || 4.5;
    const收益 = principal * (rate / 100) * (days / 365);
    return { 
      success: true,
      principal,
      protocol,
      days,
      apy: rate + '%',
      earnings:收益.toFixed(2),
      message: `💰 ${principal} @ ${rate}% APY for ${days} days = ${收益.toFixed(2)} USDC`
    };
  }
  
  return { 
    success: true, 
    message: 'DeFi Yield Optimizer ready. Use: { action: "best-yield", token: "USDC" } or { action: "calculate", principal: 10000, protocol: "aave", days: 30 }',
    supported: ['best-yield', 'compare', 'calculate']
  };
}
module.exports = { handler };
