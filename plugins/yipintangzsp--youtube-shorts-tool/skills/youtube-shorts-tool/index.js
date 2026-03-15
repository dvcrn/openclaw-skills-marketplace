#!/usr/bin/env node
/** YouTube Shorts Tool - Shorts 爆款生成器 **/
const fs = require('fs'), path = require('path');
const CONFIG_PATH = path.join(process.env.HOME, '.openclaw/workspace/config/youtube-shorts-tool.json');
const loadConfig = () => JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));

async function main() {
  const args = process.argv.slice(2), config = loadConfig();
  const price = config.price_per_call || 3;
  const topic = args.join(' ') || 'fitness';
  
  console.log('📹 YouTube Shorts Tool');
  console.log('💰 费用：¥' + price);
  console.log('🎯 生成爆款脚本和标题\n');
  console.log('🧪 测试模式：跳过收费\n');
  
  const titles = [
    'I tried ' + topic + ' for 30 days...',
    'This ' + topic + ' hack changed my life!',
    'Stop doing this ' + topic + ' mistake!',
    '3 ' + topic + ' secrets nobody tells you',
    'Why your ' + topic + ' isnt working'
  ];
  
  const script = `0-3s: Hook - 吸引注意
3-15s: Problem - 提出问题
15-45s: Solution - 给出方案
45-60s: CTA - 行动号召`;
  
  console.log('━━━━━━━━━━━━━━━━━━━━━━');
  console.log('📹 Shorts 爆款方案');
  console.log('━━━━━━━━━━━━━━━━━━━━━━\n');
  
  console.log('【主题】' + topic + '\n');
  
  console.log('【标题建议】');
  titles.forEach((t, i) => console.log(`${i+1}. ${t}`));
  console.log();
  
  console.log('【脚本结构】');
  console.log(script + '\n');
  
  console.log('💡 发布建议：短于 60 秒，前 3 秒关键');
  console.log('━━━━━━━━━━━━━━━━━━━━━━\n');
}

main().catch(e => { console.error('❌', e.message); process.exit(1); });
