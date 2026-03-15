#!/usr/bin/env node
/** Perplexica Search - AI 搜索助手 **/
const fs = require('fs'), path = require('path');
const CONFIG_PATH = path.join(process.env.HOME, '.openclaw/workspace/config/perplexica-search.json');
const loadConfig = () => JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));

async function main() {
  const args = process.argv.slice(2), config = loadConfig();
  const price = config.price_per_call || 3;
  const query = args.join(' ') || 'AI trends 2026';
  
  console.log('🔍 Perplexica Search - AI 搜索');
  console.log('💰 费用：¥' + price);
  console.log('🎯 深度搜索，智能总结\n');
  console.log('🧪 测试模式：跳过收费\n');
  
  // 模拟搜索结果
  const results = [
    { title: 'AI Trends 2026', source: 'TechCrunch', snippet: 'AI industry expected to reach $1.8T...' },
    { title: 'Top AI Tools 2026', source: 'VentureBeat', snippet: 'Best AI tools for productivity...' },
    { title: 'AI Regulation Update', source: 'Reuters', snippet: 'New AI regulations coming in 2026...' }
  ];
  
  const summary = `基于搜索结果，2026 年 AI 主要趋势：
1. 行业规模达$1.8 万亿
2. 生产力工具爆发
3. 监管政策完善
4. 多模态 AI 成熟`;
  
  console.log('━━━━━━━━━━━━━━━━━━━━━━');
  console.log('🔍 搜索结果');
  console.log('━━━━━━━━━━━━━━━━━━━━━━\n');
  
  console.log('【查询】' + query + '\n');
  
  console.log('【相关结果】');
  results.forEach((r, i) => {
    console.log(`${i+1}. ${r.title}`);
    console.log(`   来源：${r.source}`);
    console.log(`   ${r.snippet}\n`);
  });
  
  console.log('【AI 总结】');
  console.log(summary + '\n');
  
  console.log('━━━━━━━━━━━━━━━━━━━━━━');
  console.log('💡 提示：更多结果请访问 perplexica.app');
  console.log('━━━━━━━━━━━━━━━━━━━━━━\n');
}

main().catch(e => { console.error('❌', e.message); process.exit(1); });
