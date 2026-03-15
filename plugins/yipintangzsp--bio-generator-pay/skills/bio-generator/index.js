#!/usr/bin/env node
/** Bio Generator - 个人简介生成器 **/
const fs = require('fs'), path = require('path');
const CONFIG_PATH = path.join(process.env.HOME, '.openclaw/workspace/config/bio-generator.json');
const loadConfig = () => JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));

async function chargeUser(userId, amount) {
  const config = loadConfig(), fetch = require('node-fetch');
  for (const endpoint of ['https://api.skillpay.me/billing/charge', 'https://skillpay.me/api/billing/charge']) {
    try {
      const res = await fetch(endpoint, { method: 'POST', headers: { 'Authorization': `Bearer ${config.skillpay_api_key}`, 'Content-Type': 'application/json' }, body: JSON.stringify({ user_id: userId, skill_id: 'bio-generator', amount, currency: 'CNY' }), timeout: 5000 });
      return await res.json();
    } catch (e) { continue; }
  }
  return { success: false, payment_url: 'https://skillpay.me/topup' };
}

function generateBio(name, profession, style = 'professional') {
  const styles = {
    professional: `我是${name}，一名${profession}。专注于提供高质量的专业服务，帮助客户实现目标。`,
    casual: `嗨，我是${name}！平时喜欢${profession}，热爱生活，乐于分享。`,
    creative: `${name} | ${profession} | 用创意改变世界 ✨`,
    minimal: `${name} - ${profession}`
  };
  return { success: true, name, profession, style, bio: styles[style] || styles.professional };
}

async function main() {
  const args = process.argv.slice(2), config = loadConfig();
  if (args.length < 2) { console.log('用法：bio-generator <名字> <职业> [风格]\n风格：professional|casual|creative|minimal'); return; }
  const name = args[0], profession = args[1], style = args[2] || 'professional', price = config.price_per_call || 1, userId = process.env.USER || 'unknown';
  console.log(`✍️ Bio Generator\n👤 名字：${name}\n💼 职业：${profession}\n🎨 风格：${style}\n💰 费用：¥${price}\n`);
  const chargeResult = await chargeUser(userId, price);
  if (!chargeResult.success) { console.error('❌ 收费失败'); console.log(`💳 ${chargeResult.payment_url}`); process.exit(1); }
  console.log('✅ 收费成功\n✍️ 正在生成...');
  const result = generateBio(name, profession, style);
  console.log(`\n━━━ 个人简介 ━━━`);
  console.log(result.bio);
  console.log('\n━━━ 结束 ━━━');
}
main().catch(e => { console.error('❌', e.message); process.exit(1); });
