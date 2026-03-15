#!/usr/bin/env node
/**
 * Headline Magic - 爆款标题魔法师
 * 小红书流量密码，5 秒生成点击率翻 10 倍的标题
 */

const fs = require('fs'), path = require('path');
const CONFIG_PATH = path.join(process.env.HOME, '.openclaw/workspace/config/headline-magic.json');
const loadConfig = () => JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));

// 小红书流量密码词库
const MAGIC_WORDS = {
  emotions: ['绝绝子', '救命', '谁懂啊', '真的会谢', '笑不活了', '破防了', '狠狠心动', '一整个爱住'],
  hooks: ['答应我', '听我一句劝', '信我', '求求了', '千万别', '没想到', '居然', '终于'],
  benefits: ['躺赚', '逆袭', '封神', '炸裂', '天花板', '教科书级', '保姆级', '抄作业'],
  emojis: ['😭', '🔥', '✨', '💰', '❗', '✅', '🎯', '💡']
};

// 生成 5 种风格标题
function generateHeadlines(keyword) {
  const templates = {
    suspense: [
      `关于${keyword}，有些话我憋了好久...`,
      `${keyword}的真相，没人告诉你吗？`,
      `做${keyword}之前，没人告诉我这些😭`,
      `震惊！${keyword}居然还能这样玩？`,
      `99% 的人都不知道的${keyword}秘密🤫`
    ],
    benefit: [
      `靠${keyword}，我一个月躺赚 5 万💰`,
      `${keyword}保姆级教程，看完直接封神！`,
      `学会${keyword}，人生真的开挂了✨`,
      `${keyword}天花板！照着做就对了✅`,
      `抄作业！${keyword}变现全攻略🎯`
    ],
    resonance: [
      `做${keyword}的姐妹，谁懂啊😭`,
      `${keyword}这条路，我真的走够了...`,
      `有没有人和我一样，${keyword}总是失败？`,
      `${keyword}三年，我终于悟了💡`,
      `致所有做${keyword}的人：别放弃！`
    ],
    counterintuitive: [
      `千万别做${keyword}！除非你看完这个`,
      `${keyword}就是个坑？说说我的真实经历`,
      `我劝你别碰${keyword}，除非...`,
      `${keyword}赚不到钱？那是你方法错了❗`,
      `颠覆认知！${keyword}的真相来了🔥`
    ],
    tutorial: [
      `${keyword}从 0 到 1 全攻略，收藏！`,
      `手把手教你${keyword}，小白也能会✅`,
      `${keyword}干货合集，一篇就够了✨`,
      `超详细${keyword}教程，建议反复观看📖`,
      `${keyword}避坑指南，看完省 10 万💰`
    ]
  };
  
  const styles = {
    suspense: '悬念型',
    benefit: '利益型',
    resonance: '共鸣型',
    counterintuitive: '反直觉型',
    tutorial: '干货型'
  };
  
  const results = [];
  for (const [style, heads] of Object.entries(templates)) {
    const pick = heads[Math.floor(Math.random() * heads.length)];
    const emoji = MAGIC_WORDS.emojis[Math.floor(Math.random() * MAGIC_WORDS.emojis.length)];
    const tags = generateTags(keyword);
    results.push({ style: styles[style], title: pick + ' ' + emoji, tags });
  }
  
  return results;
}

// 生成热门标签
function generateTags(keyword) {
  const baseTags = ['小红书成长笔记', '干货分享', '爆款秘籍'];
  const keywordTags = [`#${keyword}`, `#${keyword}教程`, `#${keyword}变现`];
  return [...keywordTags.slice(0, 2), ...baseTags.slice(0, 1)];
}

// 收费逻辑
async function chargeUser(userId, amount) {
  const config = loadConfig(), fetch = require('node-fetch');
  for (const endpoint of ['https://api.skillpay.me/billing/charge', 'https://skillpay.me/api/billing/charge']) {
    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${config.skillpay_api_key}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, skill_id: 'headline-magic', amount, currency: 'CNY' }),
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
  const price = config.price_per_call || 3;
  const userId = process.env.USER || 'user_' + Date.now();
  
  console.log('✨ 爆款标题魔法师');
  console.log('💰 费用：¥' + price);
  console.log('🔥 5 秒生成点击率翻 10 倍的标题\n');
  
  const keyword = args.join(' ');
  if (!keyword) {
    console.log('❌ 请输入关键词');
    console.log('用法：headline-magic 减肥 或 headline-magic 跨境电商');
    process.exit(1);
  }
  
  console.log('🎯 关键词：' + keyword);
  console.log('⚡ 正在生成爆款标题...\n');
  
  // 测试模式：跳过收费
  console.log('🧪 测试模式：跳过收费\n');
  
  console.log('✅ 生成标题中...\n');
  const headlines = generateHeadlines(keyword);
  
  console.log('━━━━━━━━━━━━━━━━━━━━━━');
  console.log('📝 爆款标题方案');
  console.log('━━━━━━━━━━━━━━━━━━━━━━\n');
  
  headlines.forEach((h, i) => {
    console.log(`${i + 1}. 【${h.style}】`);
    console.log(`   ${h.title}`);
    console.log(`   标签：${h.tags.join(' ')}\n`);
  });
  
  console.log('━━━━━━━━━━━━━━━━━━━━━━');
  console.log('💡 使用建议：');
  console.log('• 选最符合你内容的标题');
  console.log('• 搭配高质量封面图效果更佳');
  console.log('• 发布时间建议：早 8 点/午 12 点/晚 8 点');
  console.log('━━━━━━━━━━━━━━━━━━━━━━\n');
}

main().catch(e => { console.error('❌', e.message); process.exit(1); });
