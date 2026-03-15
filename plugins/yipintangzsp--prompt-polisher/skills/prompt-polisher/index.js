#!/usr/bin/env node
/**
 * Prompt Polisher - Prompt 降维打击工具
 * 把你的烂描述变成专业级 System Prompt
 */

const fs = require('fs'), path = require('path');
const CONFIG_PATH = path.join(process.env.HOME, '.openclaw/workspace/config/prompt-polisher.json');
const loadConfig = () => JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));

// CoT + Role-Play 框架
function polishPrompt(original) {
  const role = '你是一名该领域的顶级专家，拥有 10 年以上实战经验';
  
  const constraints = [
    '必须分步骤思考，展示推理过程',
    '输出必须结构化，使用标题和列表',
    '必须给出具体可执行的建议',
    '如有不确定，明确说明假设条件'
  ];
  
  const format = `
输出格式：
1. 【问题分析】- 理解用户需求
2. 【核心思路】- 解决框架
3. 【详细方案】- 分步骤执行
4. 【注意事项】- 风险提示
5. 【延伸建议】- 额外价值
`;
  
  const optimized = `
# Role
${role}

# Task
${original}

# Constraints
${constraints.map(c => `- ${c}`).join('\n')}

# Output Format
${format}

# Quality Standards
- 专业准确，不胡说
- 逻辑清晰，不啰嗦
- 实用可执行，不空泛
- 如有数据，注明来源或估算依据
`;
  
  return { role, constraints, format, optimized };
}

// 收费逻辑
async function chargeUser(userId, amount) {
  const config = loadConfig(), fetch = require('node-fetch');
  for (const endpoint of ['https://api.skillpay.me/billing/charge', 'https://skillpay.me/api/billing/charge']) {
    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${config.skillpay_api_key}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, skill_id: 'prompt-polisher', amount, currency: 'CNY' }),
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
  
  console.log('🤖 Prompt 降维打击工具');
  console.log('💰 费用：¥' + price);
  console.log('✨ 把你的烂描述变成专业级 System Prompt\n');
  
  const original = args.join(' ');
  if (!original) {
    console.log('❌ 请输入你的 Prompt 需求');
    console.log('用法：prompt-polisher "帮我写个文案"');
    process.exit(1);
  }
  
  console.log('📝 原始 Prompt：');
  console.log(`"${original}"\n`);
  console.log('⚡ 正在优化...\n');
  
  // 测试模式：跳过收费
  console.log('🧪 测试模式：跳过收费\n');
  console.log('✅ 优化中...\n');
  const result = polishPrompt(original);
  
  console.log('━━━━━━━━━━━━━━━━━━━━━━');
  console.log('📊 优化对比');
  console.log('━━━━━━━━━━━━━━━━━━━━━━\n');
  
  console.log('【优化前】');
  console.log(`"${original}"`);
  console.log('❌ 问题：缺少人设/无约束/无格式/质量不可控\n');
  
  console.log('【优化后】');
  console.log(result.optimized);
  
  console.log('\n━━━━━━━━━━━━━━━━━━━━━━');
  console.log('💡 使用说明：');
  console.log('• 复制优化后的 Prompt 到 AI 对话框');
  console.log('• 效果提升：准确性↑ 逻辑性↑ 实用性↑');
  console.log('• 适用场景：文案/分析/策划/编程等');
  console.log('━━━━━━━━━━━━━━━━━━━━━━\n');
}

main().catch(e => { console.error('❌', e.message); process.exit(1); });
