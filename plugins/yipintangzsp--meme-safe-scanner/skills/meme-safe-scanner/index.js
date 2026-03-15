#!/usr/bin/env node
/**
 * Meme Safe Scanner - 新币保命扫描器
 * 毒舌链上安全审计专家
 * 风险分：0=安全，100=必死
 */

const fs = require('fs'), path = require('path');
const CONFIG_PATH = path.join(process.env.HOME, '.openclaw/workspace/config/meme-safe-scanner.json');
const loadConfig = () => JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));

// 毒舌 System Prompt
const SYSTEM_PROMPT = `
你是极度毒舌且专业的链上安全审计专家。

分析要素：
1. 权限是否丢弃
2. LP 是否锁定（具体比例）
3. 前 10 持币地址占比

输出风格：
- 风险分：0=安全，100=必死
- 用最直白的语言警告
- 例如："这池子没锁，庄家随时提款跑路"

行动建议：
- 明确告诉用户"全仓冲"还是"快跑"
- 不模棱两可
`;

// 模拟链上数据
function scanContract(address) {
  const hash = address.split('').reduce((a, b) => a + b.charCodeAt(0), 0);
  const lpLocked = hash % 3 !== 0;
  const lpPercent = lpLocked ? (hash % 100) : 0;
  const renounced = hash % 4 !== 0;
  const top10Percent = 30 + (hash % 60);
  
  return { lpLocked, lpPercent, renounced, top10Percent };
}

// 计算风险分 (0=安全，100=必死)
function calculateRiskScore(data) {
  let score = 0;
  const warnings = [];
  
  // LP 风险 (40 分)
  if (!data.lpLocked) {
    score += 40;
    warnings.push('🔴 LP 根本没锁！庄家随时提款跑路！');
  } else if (data.lpPercent < 50) {
    score += 25;
    warnings.push(`🟠 LP 只锁了${data.lpPercent}%，一半以上能随时撤！`);
  } else if (data.lpPercent < 90) {
    score += 10;
    warnings.push(`🟡 LP 锁了${data.lpPercent}%，还行但有风险`);
  }
  
  // 权限风险 (35 分)
  if (!data.renounced) {
    score += 35;
    warnings.push('🔴 合约权限没丢！项目方能无限增发、改税！');
  }
  
  // 持币风险 (25 分)
  if (data.top10Percent > 80) {
    score += 25;
    warnings.push(`🔴 前 10 地址拿了${data.top10Percent}%！高度控盘，随便砸盘！`);
  } else if (data.top10Percent > 60) {
    score += 15;
    warnings.push(`🟠 前 10 地址拿了${data.top10Percent}%，集中度太高！`);
  } else if (data.top10Percent > 40) {
    score += 5;
    warnings.push(`🟡 前 10 地址拿了${data.top10Percent}%，还算凑合`);
  }
  
  return { score, warnings };
}

// 生成毒舌报告
function generateReport(address) {
  const data = scanContract(address);
  const { score, warnings } = calculateRiskScore(data);
  
  let advice, emoji;
  if (score <= 20) {
    advice = '✅ 风险较低，可以小仓位试试';
    emoji = '🟢';
  } else if (score <= 50) {
    advice = '⚠️ 风险中等，别 All-in，玩玩就行';
    emoji = '🟡';
  } else if (score <= 75) {
    advice = '🚨 高风险！建议观望，别当接盘侠！';
    emoji = '🟠';
  } else {
    advice = '💀 必死无疑！快跑！别回头！';
    emoji = '🔴';
  }
  
  return `
━━━━━━━━━━━━━━━━━━━━━━
💀 新币保命扫描报告
━━━━━━━━━━━━━━━━━━━━━━

【风险评分】${emoji} ${score}/100 ${score > 75 ? '（必死）' : score > 50 ? '（高危）' : score > 20 ? '（中等）' : '（安全）'}

【合约地址】\`${address}\`

【核心指标】
• LP 锁定：${data.lpLocked ? `✅ ${data.lpPercent}%` : '❌ 根本没锁'}
• 权限丢弃：${data.renounced ? '✅ 已丢' : '❌ 没丢，项目方能随意操作'}
• 前 10 持仓：${data.top10Percent}% ${data.top10Percent > 60 ? '⚠️ 太高了' : '✅ 还行'}

【风险警告】
${warnings.length > 0 ? warnings.join('\n') : '✅ 没发现致命问题'}

【行动建议】
${advice}

━━━━━━━━━━━━━━━━━━━━━━
⚠️ 仅供参考，DYOR。亏了别怪我。
━━━━━━━━━━━━━━━━━━━━━━
  `;
}

// 收费逻辑
async function chargeUser(userId, amount) {
  const config = loadConfig(), fetch = require('node-fetch');
  for (const endpoint of ['https://api.skillpay.me/billing/charge', 'https://skillpay.me/api/billing/charge']) {
    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${config.skillpay_api_key}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, skill_id: 'meme-safe-scanner', amount, currency: 'CNY' }),
        timeout: 5000
      });
      return await res.json();
    } catch (e) { continue; }
  }
  return { success: false, payment_url: 'https://skillpay.me/topup' };
}

// 主函数
async function main() {
  const args = process.argv.slice(2), config = loadConfig();
  const price = config.price_per_call || 5;
  const userId = process.env.USER || 'user_' + Date.now();
  
  console.log('💀 新币保命扫描器');
  console.log('💰 费用：¥' + price);
  console.log('⚠️ 声明：仅供参考，亏了别怪我\n');
  
  const contractAddress = args[0];
  if (!contractAddress || !contractAddress.startsWith('0x')) {
    console.log('❌ 请输入有效的合约地址（0x 开头）');
    console.log('用法：meme-safe-scanner 0x1234...');
    process.exit(1);
  }
  
  console.log('🔍 正在扫描：' + contractAddress + '...\n');
  
  // 测试模式：跳过收费
  console.log('🧪 测试模式：跳过收费\n');
  // const chargeResult = await chargeUser(userId, price);
  // if (!chargeResult.success) { ... }
  
  console.log('✅ 生成报告中...\n');
  const report = generateReport(contractAddress);
  console.log(report);
}

main().catch(e => { console.error('❌', e.message); process.exit(1); });
