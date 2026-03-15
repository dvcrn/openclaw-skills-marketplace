#!/usr/bin/env node
/** Password Generator - 密码生成器 **/
const fs = require('fs'), path = require('path');
const CONFIG_PATH = path.join(process.env.HOME, '.openclaw/workspace/config/password-generator.json');
const loadConfig = () => JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));

async function chargeUser(userId, amount) {
  const config = loadConfig(), fetch = require('node-fetch');
  for (const endpoint of ['https://api.skillpay.me/billing/charge', 'https://skillpay.me/api/billing/charge']) {
    try {
      const res = await fetch(endpoint, { method: 'POST', headers: { 'Authorization': `Bearer ${config.skillpay_api_key}`, 'Content-Type': 'application/json' }, body: JSON.stringify({ user_id: userId, skill_id: 'password-generator', amount, currency: 'CNY' }), timeout: 5000 });
      return await res.json();
    } catch (e) { continue; }
  }
  return { success: false, payment_url: 'https://skillpay.me/topup' };
}

function generatePassword(length = 16, options = {}) {
  const chars = { lower: 'abcdefghijklmnopqrstuvwxyz', upper: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', numbers: '0123456789', symbols: '!@#$%^&*()_+-=[]{}|;:,.<>?' };
  let charset = chars.lower + chars.upper + chars.numbers;
  if (options.symbols) charset += chars.symbols;
  let password = '';
  for (let i = 0; i < length; i++) password += charset.charAt(Math.floor(Math.random() * charset.length));
  const strength = length >= 16 && options.symbols ? '强' : length >= 12 ? '中' : '弱';
  return { success: true, password, length, strength, charset: options.symbols ? '字母 + 数字 + 符号' : '字母 + 数字' };
}

async function main() {
  const args = process.argv.slice(2), config = loadConfig();
  if (args.includes('--help') || args.length === 0) { console.log('用法：password-generator [长度] [--symbols]\n示例：password-generator 16 --symbols'); return; }
  const length = parseInt(args[0]) || 16, symbols = args.includes('--symbols'), price = config.price_per_call || 0.5, userId = process.env.USER || 'unknown';
  console.log(`🔐 Password Generator\n🔑 长度：${length}\n🔣 符号：${symbols ? '包含' : '不包含'}\n💰 费用：¥${price}\n`);
  const chargeResult = await chargeUser(userId, price);
  if (!chargeResult.success) { console.error('❌ 收费失败'); console.log(`💳 ${chargeResult.payment_url}`); process.exit(1); }
  console.log('✅ 收费成功\n🔐 正在生成...');
  const result = generatePassword(length, { symbols });
  console.log(`\n━━━ 密码生成 ━━━`);
  console.log(`密码：${result.password}`);
  console.log(`强度：${'⭐'.repeat(result.strength === '强' ? 3 : result.strength === '中' ? 2 : 1)} ${result.strength}`);
  console.log(`字符集：${result.charset}`);
  console.log('\n⚠️ 请安全保存此密码！');
  console.log('\n━━━ 结束 ━━━');
}
main().catch(e => { console.error('❌', e.message); process.exit(1); });
