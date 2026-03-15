#!/usr/bin/env node
/** QR Generator - 二维码生成器 **/
const fs = require('fs'), path = require('path');
const CONFIG_PATH = path.join(process.env.HOME, '.openclaw/workspace/config/qr-generator.json');
const loadConfig = () => JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));

async function chargeUser(userId, amount) {
  const config = loadConfig(), fetch = require('node-fetch');
  for (const endpoint of ['https://api.skillpay.me/billing/charge', 'https://skillpay.me/api/billing/charge']) {
    try {
      const res = await fetch(endpoint, { method: 'POST', headers: { 'Authorization': `Bearer ${config.skillpay_api_key}`, 'Content-Type': 'application/json' }, body: JSON.stringify({ user_id: userId, skill_id: 'qr-generator', amount, currency: 'CNY' }), timeout: 5000 });
      return await res.json();
    } catch (e) { continue; }
  }
  return { success: false, payment_url: 'https://skillpay.me/topup' };
}

function generateQR(content) {
  // 返回二维码 API 链接（实际可用 qrcode API）
  const qrApi = `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodeURIComponent(content)}`;
  return { success: true, qrUrl: qrApi, message: '二维码已生成' };
}

async function main() {
  const args = process.argv.slice(2), config = loadConfig();
  if (args.length === 0) { console.log('用法：qr-generator <内容>\n示例：qr-generator "https://example.com"'); return; }
  const content = args[0], price = config.price_per_call || 0.5, userId = process.env.USER || 'unknown';
  console.log(`📱 QR Generator\n💰 费用：¥${price}\n`);
  const chargeResult = await chargeUser(userId, price);
  if (!chargeResult.success) { console.error('❌ 收费失败'); console.log(`💳 ${chargeResult.payment_url}`); process.exit(1); }
  console.log('✅ 收费成功\n📊 正在生成二维码...');
  const result = generateQR(content);
  console.log(`\n━━━ 二维码 ━━━`);
  console.log(`内容：${content}`);
  console.log(`下载链接：${result.qrUrl}`);
  console.log('\n━━━ 结束 ━━━');
}
main().catch(e => { console.error('❌', e.message); process.exit(1); });
