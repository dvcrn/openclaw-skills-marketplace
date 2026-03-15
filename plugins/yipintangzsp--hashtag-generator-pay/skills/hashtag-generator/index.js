#!/usr/bin/env node
/** Hashtag Generator - 标签生成器 **/
const fs = require('fs'), path = require('path');
const CONFIG_PATH = path.join(process.env.HOME, '.openclaw/workspace/config/hashtag-generator.json');
const loadConfig = () => JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));

async function chargeUser(userId, amount) {
  const config = loadConfig(), fetch = require('node-fetch');
  for (const endpoint of ['https://api.skillpay.me/billing/charge', 'https://skillpay.me/api/billing/charge']) {
    try {
      const res = await fetch(endpoint, { method: 'POST', headers: { 'Authorization': `Bearer ${config.skillpay_api_key}`, 'Content-Type': 'application/json' }, body: JSON.stringify({ user_id: userId, skill_id: 'hashtag-generator', amount, currency: 'CNY' }), timeout: 5000 });
      return await res.json();
    } catch (e) { continue; }
  }
  return { success: false, payment_url: 'https://skillpay.me/topup' };
}

function generateHashtags(topic, platform = 'instagram') {
  const base = topic.replace(/\s+/g, '');
  const tags = {
    instagram: [`#${base}`, `#${base}Life`, `#${base}Love`, `#${base}Style`, `#Insta${base}`, `#${base}OfTheDay`, `#${base}Gram`, `#${base}Vibes`, `#${base}Addict`, `#${base}Community`],
    twitter: [`#${base}`, `#${base}News`, `#${base}Tips`, `#${base}Thread`],
    tiktok: [`#${base}`, `#${base}Tok`, `#${base}Challenge`, `#${base}Trend`, `#ForYou`]
  };
  return { success: true, topic, platform, tags: tags[platform] || tags.instagram };
}

async function main() {
  const args = process.argv.slice(2), config = loadConfig();
  if (args.length === 0) { console.log('用法：hashtag-generator <主题> [平台]\n平台：instagram|twitter|tiktok'); return; }
  const topic = args[0], platform = args[1] || 'instagram', price = config.price_per_call || 1, userId = process.env.USER || 'unknown';
  console.log(`#️⃣ Hashtag Generator\n📝 主题：${topic}\n📱 平台：${platform}\n💰 费用：¥${price}\n`);
  const chargeResult = await chargeUser(userId, price);
  if (!chargeResult.success) { console.error('❌ 收费失败'); console.log(`💳 ${chargeResult.payment_url}`); process.exit(1); }
  console.log('✅ 收费成功\n#️⃣ 正在生成...');
  const result = generateHashtags(topic, platform);
  console.log(`\n━━━ 标签推荐 ━━━`);
  console.log(result.tags.join(' '));
  console.log('\n━━━ 结束 ━━━');
}
main().catch(e => { console.error('❌', e.message); process.exit(1); });
