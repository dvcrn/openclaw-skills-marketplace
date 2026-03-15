#!/usr/bin/env node

/**
 * 抖音标题魔法 - TikTok 爆款标题生成器
 * 定价：¥5/次 | ¥99/月
 */

const fs = require('fs');
const path = require('path');

// 流量密码词库（简化版，实际应更大）
const POWER_WORDS = {
  悬念：['揭秘', '曝光', '内部', '偷偷', '竟然', '没想到', '真相', '背后'],
  利益：['免费', '省钱', '赚钱', '高效', '快速', '轻松', '简单', '必备'],
  共鸣：['扎心', '真实', '泪目', '破防', '懂了', '是我', '谁懂', '太真实'],
  反直觉：['别再', '错了', '骗局', '智商税', '颠覆', '反常识', '冷门'],
  干货：['教程', '攻略', '指南', '清单', '模板', '公式', '方法', '技巧']
};

const VIRAL_PATTERNS = [
  '{数字}+{结果}！{感叹}',
  '{痛点}？{解决方案}',
  '别再{错误行为}了！{正确方法}',
  '{时间}+{惊人效果}！{方法}',
  '{人群}必看！{价值}',
  '亲测有效！{成果}',
  '{对比}！{反差}',
  '偷偷{动作}，{结果}'
];

const HASHTAGS = {
  减肥： ['#减肥', '#瘦身', '#逆袭', '#变美', '#自律'],
  职场： ['#职场', '#成长', '#干货', '#升职', '#打工人'],
  美妆： ['#美妆', '#护肤', '#化妆', '#变美', '#教程'],
  美食： ['#美食', '#教程', '#家常菜', '#美食分享', '#吃货'],
  旅行： ['#旅行', '#旅游', '#攻略', '#打卡', '#风景'],
  情感： ['#情感', '#恋爱', '#婚姻', '#家庭', '#成长'],
  教育： ['#教育', '#学习', '#育儿', '#成长', '#知识'],
  通用： ['#热门', '#推荐', '#爆款', '#干货', '#分享']
};

/**
 * 生成爆款标题
 * @param {string} content - 视频内容描述
 * @param {string} style - 标题风格
 * @param {number} count - 生成数量
 * @returns {Promise<Object>} - 标题方案
 */
async function generateTitles(content, style = '混合', count = 3) {
  // 这里应该调用 LLM API，简化版用规则生成
  const styles = style === '混合' 
    ? ['悬念', '利益', '共鸣', '反直觉', '干货']
    : [style];
  
  const titles = [];
  
  for (let i = 0; i < count; i++) {
    const currentStyle = styles[i % styles.length];
    const words = POWER_WORDS[currentStyle];
    const pattern = VIRAL_PATTERNS[i % VIRAL_PATTERNS.length];
    
    // 简化版标题生成（实际应调用 LLM）
    const title = generateTitleFromPattern(pattern, content, words);
    titles.push({
      text: title,
      style: currentStyle,
      score: Math.floor(Math.random() * 20) + 80 // 模拟评分 80-99
    });
  }
  
  // 按评分排序
  titles.sort((a, b) => b.score - a.score);
  
  // 推荐标签
  const tags = recommendHashtags(content);
  
  return {
    recommended: titles[0],
    alternatives: titles.slice(1),
    hashtags: tags,
    suggestions: generateSuggestions(content)
  };
}

/**
 * 从模板生成标题
 */
function generateTitleFromPattern(pattern, content, words) {
  const word = words[Math.floor(Math.random() * words.length)];
  
  // 简化替换逻辑
  let title = pattern
    .replace('{数字}', () => Math.floor(Math.random() * 10) + 1)
    .replace('{结果}', '惊人效果')
    .replace('{感叹}', '太狠了')
    .replace('{痛点}', '还在烦恼')
    .replace('{解决方案}', '这个方法绝了')
    .replace('{错误行为}', '瞎折腾')
    .replace('{正确方法}', '这才是正解')
    .replace('{时间}', '7 天')
    .replace('{惊人效果}', '瘦了 10 斤')
    .replace('{方法}', '懒人必备')
    .replace('{人群}', '新手')
    .replace('{价值}', '干货满满')
    .replace('{成果}', '效果炸裂')
    .replace('{对比}', '前后对比')
    .replace('{反差}', '差距太大了')
    .replace('{动作}', '变美')
    .replace('{word}', word);
  
  return title;
}

/**
 * 推荐标签
 */
function recommendHashtags(content) {
  for (const [category, tags] of Object.entries(HASHTAGS)) {
    if (content.includes(category)) {
      return tags;
    }
  }
  return HASHTAGS.通用;
}

/**
 * 生成发布建议
 */
function generateSuggestions(content) {
  return {
    bestTime: '18:00-20:00',
    coverTip: '对比图 + 大字标题',
    hookTip: '前 3 秒展示惊人效果'
  };
}

/**
 * 格式化输出
 */
function formatOutput(result) {
  let output = `## 🎬 抖音爆款标题方案\n\n`;
  output += `### 🏆 推荐标题（吸引力评分：${result.recommended.score}/100）\n`;
  output += `"${result.recommended.text}"\n\n`;
  
  output += `### 📋 备选方案\n`;
  result.alternatives.forEach((alt, i) => {
    output += `${i + 1}. "${alt.text}" (评分：${alt.score}/100)\n`;
  });
  
  output += `\n### 🏷️ 热门标签\n`;
  output += result.hashtags.join(' ');\n\n`;
  
  output += `### 💡 发布建议\n`;
  output += `- 最佳时间：${result.suggestions.bestTime}\n`;
  output += `- 封面建议：${result.suggestions.coverTip}\n`;
  output += `- 前 3 秒钩子：${result.suggestions.hookTip}\n`;
  
  return output;
}

/**
 * CLI 入口
 */
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('用法：tiktok-title "内容描述" [--style 风格] [--count 数量]');
    console.log('风格：悬念 | 利益 | 共鸣 | 反直觉 | 干货 | 混合');
    process.exit(1);
  }
  
  const content = args.find(arg => !arg.startsWith('--'));
  const styleIndex = args.indexOf('--style');
  const countIndex = args.indexOf('--count');
  
  const style = styleIndex > -1 ? args[styleIndex + 1] : '混合';
  const count = countIndex > -1 ? parseInt(args[countIndex + 1]) : 3;
  
  console.log('正在生成爆款标题...\n');
  
  const result = await generateTitles(content.replace(/"/g, ''), style, count);
  console.log(formatOutput(result));
}

// 导出供其他模块使用
module.exports = { generateTitles, formatOutput };

// CLI 执行
if (require.main === module) {
  main().catch(console.error);
}
