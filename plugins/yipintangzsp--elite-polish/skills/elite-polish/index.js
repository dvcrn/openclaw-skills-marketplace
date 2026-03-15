#!/usr/bin/env node
/**
 * Elite Polish - 名校大厂文书润色
 * 哈佛/斯坦福招生官或麦肯锡高级合伙人级别润色
 */

const fs = require('fs'), path = require('path');
const CONFIG_PATH = path.join(process.env.HOME, '.openclaw/workspace/config/elite-polish.json');
const loadConfig = () => JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));

// Action Verbs 库
const ACTION_VERBS = {
  leadership: ['Led', 'Spearheaded', 'Orchestrated', 'Championed', 'Pioneered'],
  achievement: ['Achieved', 'Attained', 'Accomplished', 'Secured', 'Earned'],
  improvement: ['Improved', 'Enhanced', 'Optimized', 'Streamlined', 'Revolutionized'],
  creation: ['Created', 'Developed', 'Designed', 'Engineered', 'Architected'],
  analysis: ['Analyzed', 'Evaluated', 'Assessed', 'Diagnosed', 'Investigated']
};

// STAR 法则框架
function polishWithSTAR(original) {
  const star = {
    situation: '【Situation】- 描述背景和挑战',
    task: '【Task】- 说明你的职责和目标',
    action: '【Action】- 详述你采取的具体行动（使用 Action Verbs）',
    result: '【Result】- 量化成果和影响'
  };
  
  const tips = [
    '用具体数字量化成果（提升 30%、节省$50K、管理 10 人团队）',
    '使用强动词开头，避免"负责/参与"等弱表达',
    '突出个人贡献，不是团队功劳',
    '展示成长和学习，不只是结果'
  ];
  
  return { star, tips };
}

// 模拟润色示例
function demonstratePolish(original) {
  const before = original || '我负责了一个项目，帮助公司提高了销售额';
  
  const after = `
【优化前】
"${before}"
❌ 问题：动词弱（负责）、无数值、无具体行动

【优化后】
"Spearheaded a cross-functional sales optimization project, analyzing customer 
data to identify 3 key growth opportunities. Implemented targeted marketing 
strategies that increased quarterly revenue by 35% ($2.3M) and expanded market 
share by 8 percentage points within 6 months."

✅ 改进：
• 强动词：Spearheaded（而非 Responsible for）
• 量化成果：35% 增长、$2.3M、8 个百分点
• 时间框架：6 个月内
• 具体行动：数据分析、精准营销策略
  `;
  
  return { before, after };
}

// 收费逻辑
async function chargeUser(userId, amount) {
  const config = loadConfig(), fetch = require('node-fetch');
  for (const endpoint of ['https://api.skillpay.me/billing/charge', 'https://skillpay.me/api/billing/charge']) {
    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${config.skillpay_api_key}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, skill_id: 'elite-polish', amount, currency: 'CNY' }),
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
  const price = config.price_per_call || 15;
  const userId = process.env.USER || 'user_' + Date.now();
  
  console.log('🎓 Elite Polish - 名校大厂文书润色');
  console.log('💰 费用：¥' + price);
  console.log('✨ 哈佛/斯坦福招生官级别润色\n');
  
  const original = args.join(' ');
  
  console.log('⚡ 正在生成润色指南...\n');
  
  // 测试模式：跳过收费
  console.log('🧪 测试模式：跳过收费\n');
  console.log('✅ 生成润色指南...\n');
  
  const { star, tips } = polishWithSTAR(original);
  const demo = demonstratePolish(original);
  
  console.log('━━━━━━━━━━━━━━━━━━━━━━');
  console.log('📝 STAR 法则框架');
  console.log('━━━━━━━━━━━━━━━━━━━━━━\n');
  
  console.log('【写作框架】');
  Object.values(star).forEach(s => console.log('• ' + s));
  console.log();
  
  console.log('【关键技巧】');
  tips.forEach(t => console.log('✅ ' + t));
  console.log();
  
  console.log('━━━━━━━━━━━━━━━━━━━━━━');
  console.log('📊 润色示例');
  console.log('━━━━━━━━━━━━━━━━━━━━━━\n');
  
  console.log(demo.after);
  
  console.log('\n━━━━━━━━━━━━━━━━━━━━━━');
  console.log('💡 Action Verbs 推荐：');
  console.log('领导力：Led, Spearheaded, Orchestrated');
  console.log('成就：Achieved, Attained, Secured');
  console.log('改进：Improved, Optimized, Revolutionized');
  console.log('创造：Created, Developed, Architected');
  console.log('分析：Analyzed, Evaluated, Diagnosed');
  console.log('━━━━━━━━━━━━━━━━━━━━━━\n');
  
  if (original) {
    console.log('📮 如需具体润色你的文书，请发送完整内容，我将逐句优化。');
  }
}

main().catch(e => { console.error('❌', e.message); process.exit(1); });
