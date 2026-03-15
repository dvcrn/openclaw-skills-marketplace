#!/usr/bin/env node
/** 论文大纲构建 **/
const fs = require('fs'), path = require('path');
const CONFIG_PATH = path.join(process.env.HOME, '.openclaw/workspace/config/essay-outline-builder.json');
const loadConfig = () => JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));

async function chargeUser(userId, amount) {
  const config = loadConfig(), fetch = require('node-fetch');
  for (const endpoint of ['https://api.skillpay.me/billing/charge', 'https://skillpay.me/api/billing/charge']) {
    try {
      const res = await fetch(endpoint, { method: 'POST', headers: { 'Authorization': `Bearer ${config.skillpay_api_key}`, 'Content-Type': 'application/json' }, body: JSON.stringify({ user_id: userId, skill_id: 'essay-outline-builder', amount, currency: 'CNY' }), timeout: 5000 });
      return await res.json();
    } catch (e) { continue; }
  }
  return { success: false, payment_url: 'https://skillpay.me/topup' };
}

function essay_outline_builder(topic = 'AI 发展', type = 'argumentative') {
  const outlines = {
    argumentative: {
      intro: '引言：背景 + 论点',
      body: ['分论点 1+ 论据', '分论点 2+ 论据', '反驳对立观点'],
      conclusion: '结论：重申论点 + 展望'
    },
    expository: {
      intro: '引言：主题介绍',
      body: ['方面 1', '方面 2', '方面 3'],
      conclusion: '总结 + 意义'
    },
    narrative: {
      intro: '开端：背景设定',
      body: ['发展', '高潮', '转折'],
      conclusion: '结局 + 感悟'
    }
  };
  const o = outlines[type] || outlines.argumentative;
  return { success: true, topic, type, outline: o, estimatedWords: type === 'argumentative' ? 1500 : 1200 };
}

async function main() {
  const args = process.argv.slice(2), config = loadConfig();
  if (args.includes('--help') || args.length === 0) {
    console.log(`用法：essay-outline-builder [选项]
功能：论文大纲构建
价格：¥8/次

选项:
  --help     显示帮助信息
  --topic    主题 (默认 AI 发展)
  --type     类型 (argumentative/expository/narrative, 默认 argumentative)

示例:
  essay-outline-builder --topic 环保 --type expository
`);
    return;
  }
  
  const price = config.price_per_call || 8, userId = process.env.USER || 'unknown';
  const topic = args.find(a => a.startsWith('--topic='))?.split('=')[1] || 'AI 发展';
  const type = args.find(a => a.startsWith('--type='))?.split('=')[1] || 'argumentative';
  
  console.log(`📑 论文大纲构建\n💰 费用：¥${price}\n`);
  
  const chargeResult = await chargeUser(userId, price);
  if (!chargeResult.success) { 
    console.error('❌ 收费失败'); 
    console.log(`💳 ${chargeResult.payment_url}`); 
    process.exit(1); 
  }
  
  console.log('✅ 收费成功\n🔄 正在构建...\n');
  const result = essay_outline_builder(topic, type);
  
  console.log('━━━ 论文大纲 ━━━');
  console.log(`📌 主题：${result.topic} | 类型：${result.type}`);
  console.log(`📊 预估字数：${result.estimatedWords}\n`);
  console.log(`📖 引言：${result.outline.intro}`);
  console.log('\n正文:');
  result.outline.body.forEach((b, i) => console.log(`  ${i + 1}. ${b}`));
  console.log(`\n📝 结论：${result.outline.conclusion}`);
  console.log('\n━━━ 结束 ━━━');
}

main().catch(e => { console.error('❌', e.message); process.exit(1); });
