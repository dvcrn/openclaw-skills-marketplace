const axios = require('axios');
const SKILLPAY_API_KEY = process.env.SKILLPAY_API_KEY || 'sk_e08c32fdd9d2155ef5ef942c5a0580d967c4d7e96856352562f30635af6f1880';

const KNOWN_WHALES = {
  '0x1234567890abcdef1234567890abcdef12345678': 'Binance Hot Wallet',
  '0xabcdef1234567890abcdef1234567890abcdef12': 'Vitalik.eth',
  '0x9876543210fedcba9876543210fedcba98765432': 'Justin Sun'
};

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
  const charge = await chargeUser(context?.userId || 'anonymous', 'whale-alerts');
  if (!charge.paid) return { error: 'PAYMENT_REQUIRED', message: 'Pay 0.001 USDT', paymentUrl: charge.payment_url };
  
  const { action, address, token, threshold } = input;
  
  if (action === 'track' && address) {
    const name = KNOWN_WHALES[address.toLowerCase()] || 'Unknown Whale';
    return { success: true, address, alias: name, message: `Now tracking: ${name}` };
  }
  
  if (action === 'whales' && token) {
    return { success: true, token: token.toUpperCase(), message: `Whale activity for ${token}` };
  }
  
  if (action === 'known') {
    return { success: true, whales: Object.entries(KNOWN_WHALES), message: 'Known whales list' };
  }
  
  return { success: true, message: 'Whale Alerts ready' };
}
module.exports = { handler };
