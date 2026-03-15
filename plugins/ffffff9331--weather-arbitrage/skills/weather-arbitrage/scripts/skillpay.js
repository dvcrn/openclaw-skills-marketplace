/**
 * SkillPay 收费接口
 */

const BILLING_API_URL = 'https://skillpay.me/api/v1/billing';
const BILLING_API_KEY = process.env.SKILLPAY_API_KEY || 'sk_a267a27a1eb8381a762a9a6cdb1ea7d722f9f45f345b7319cfd3cccd9fae35c5';
const SKILL_ID = '2ad7fab2-e33f-4999-b253-c90a4b7ce8f3'; // 天气套利助手

/**
 * 查询用户余额
 */
async function checkBalance(userId) {
  try {
    const response = await fetch(
      `${BILLING_API_URL}/balance?user_id=${userId}`,
      {
        headers: {
          'X-API-Key': BILLING_API_KEY
        }
      }
    );
    const data = await response.json();
    return data.balance || 0;
  } catch (error) {
    console.error('查询余额失败:', error.message);
    return 0;
  }
}

/**
 * 扣费
 */
async function chargeUser(userId, amount) {
  try {
    const response = await fetch(`${BILLING_API_URL}/charge`, {
      method: 'POST',
      headers: {
        'X-API-Key': BILLING_API_KEY,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: userId,
        skill_id: SKILL_ID,
        amount: amount
      })
    });
    
    const data = await response.json();
    
    if (data.success) {
      return {
        ok: true,
        balance: data.balance
      };
    }
    
    // 余额不足，返回充值链接
    return {
      ok: false,
      balance: data.balance,
      paymentUrl: data.payment_url
    };
  } catch (error) {
    console.error('扣费失败:', error.message);
    return {
      ok: false,
      error: error.message
    };
  }
}

/**
 * 生成充值链接
 */
async function getPaymentLink(userId, amount) {
  try {
    const response = await fetch(`${BILLING_API_URL}/payment-link`, {
      method: 'POST',
      headers: {
        'X-API-Key': BILLING_API_KEY,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: userId,
        amount: amount
      })
    });
    
    const data = await response.json();
    return data.payment_url;
  } catch (error) {
    console.error('生成充值链接失败:', error.message);
    return null;
  }
}

module.exports = {
  checkBalance,
  chargeUser,
  getPaymentLink
};