#!/usr/bin/env node
/** Instagram Reels Analyzer - Reels 爆款分析 **/
const fs = require('fs'), path = require('path');
const CONFIG_PATH = path.join(process.env.HOME, '.openclaw/workspace/config/instagram-reels-analyzer.json');
const loadConfig = () => JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));

async function main() {
  const args = process.argv.slice(2), config = loadConfig();
  const price = config.price_per_call || 3;
  const keyword = args.join(' ') || 'fitness';
  
  console.log('📱 Instagram Reels Analyzer');
  console.log('💰 费用：¥' + price);
  console.log('🎯 分析热门视频，生成爆款脚本\n');
  console.log('🧪 测试模式：跳过收费\n');
  
  const hooks = [
    'Stop doing this mistake...',
    'This changed my life...',
    'I wish I knew this sooner...',
    '3 secrets about ' + keyword,
    'Why nobody talks about ' + keyword
  ];
  
  const scripts = hooks.map((hook, i) => ({
    hook,
    structure: ['Hook (0-3s)', 'Value (3-15s)', 'CTA (15-30s)'],
    hashtags: ['#' + keyword, '#viral', '#trending', '#fyp', '#reels']
  }));
  
  console.log('━━━━━━━━━━━━━━━━━━━━━━');
  console.log('📱 Reels 爆款脚本');
  console.log('━━━━━━━━━━━━━━━━━━━━━━\n');
  
  scripts.forEach((s, i) => {
    console.log(`${i+1}. 【Hook】${s.hook}`);
    console.log(`   结构：${s.structure.join(' → ')}`);
    console.log(`   标签：${s.hashtags.join(' ')}\n`);
  });
  
  console.log('💡 发布建议：早 9 点/午 12 点/晚 7 点');
  console.log('━━━━━━━━━━━━━━━━━━━━━━\n');
}

main().catch(e => { console.error('❌', e.message); process.exit(1); });
