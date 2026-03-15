#!/usr/bin/env node

/**
 * YouTube 标题优化器 - 高 CTR 和高 SEO 排名
 * 定价：¥5/次 | ¥99/月
 */

const fs = require('fs');
const path = require('path');

// YouTube 标题最佳实践
const TITLE_PATTERNS = [
  '{主题} {年份}｜{价值主张}（{附加价值}）',
  '{如何}+{结果}｜{时间框架}',
  '{数字}+{主题}+{承诺}',
  '{问题}？{解决方案}',
  '{主题} 教程｜{从 X 到 Y}',
  '我靠{技能}+{成果}，{教程}',
  '{主题} 新手必看！{警告/建议}',
  '{对比}：{A} vs {B}'
];

// 高 CTR 词汇
const CTR_BOOSTERS = [
  '2026', '完整版', '从零开始', '实战', '附源码',
  '保姆级', '超详细', '建议收藏', '必看', '干货',
  '亲测有效', '太狠了', '绝了', '炸裂', '颠覆'
];

// 关键词数据库（简化版）
const KEYWORD_DATA = {
  'Python': { volume: 50000, competition: '高' },
  '教程': { volume: 80000, competition: '高' },
  '入门': { volume: 40000, competition: '中' },
  '健身': { volume: 60000, competition: '高' },
  '减肥': { volume: 70000, competition: '高' },
  '编程': { volume: 35000, competition: '中' },
  '美食': { volume: 45000, competition: '中' },
  '教程': { volume: 80000, competition: '高' }
};

/**
 * 生成 YouTube 标题
 * @param {string} content - 视频内容
 * @param {string[]} keywords - 关键词列表
 * @param {number} count - 生成数量
 * @returns {Promise<Object>}
 */
async function generateTitles(content, keywords = [], count = 3) {
  const titles = [];
  
  for (let i = 0; i < count; i++) {
    const pattern = TITLE_PATTERNS[i % TITLE_PATTERNS.length];
    const booster = CTR_BOOSTERS[i % CTR_BOOSTERS.length];
    
    const title = generateTitleFromPattern(pattern, content, booster);
    const ctr = predictCTR(title, content);
    
    titles.push({
      text: title,
      ctr: ctr,
      length: title.length,
      seoScore: calculateSEOScore(title, keywords)
    });
  }
  
  titles.sort((a, b) => b.ctr - a.ctr);
  
  return {
    recommended: titles[0],
    alternatives: titles.slice(1),
    keywords: analyzeKeywords(content, keywords),
    tags: generateTags(content),
    description: generateDescriptionTemplate(content)
  };
}

/**
 * 从模板生成标题
 */
function generateTitleFromPattern(pattern, content, booster) {
  const year = new Date().getFullYear();
  
  let title = pattern
    .replace('{主题}', content.substring(0, 10))
    .replace('{年份}', year)
    .replace('{价值主张}', '从入门到精通')
    .replace('{附加价值}', booster)
    .replace('{如何}', '如何')
    .replace('{结果}', '快速掌握')
    .replace('{时间框架}', '7 天搞定')
    .replace('{数字}', '5 个')
    .replace('{承诺}', '让你少走弯路')
    .replace('{问题}', '还在为 XX 烦恼')
    .replace('{解决方案}', '这个方法绝了')
    .replace('{从 X 到 Y}', '从零到能写项目')
    .replace('{技能}', '这个技能')
    .replace('{成果}', '月入 3 万')
    .replace('{教程}', '教程来了')
    .replace('{警告/建议}', '避开这 5 个坑')
    .replace('{对比}', '全面对比')
    .replace('{A}', '方案 A')
    .replace('{B}', '方案 B');
  
  // 确保标题长度在 60 字符以内（YouTube 最佳实践）
  if (title.length > 60) {
    title = title.substring(0, 57) + '...';
  }
  
  return title;
}

/**
 * 预测 CTR
 */
function predictCTR(title, content) {
  let baseCTR = 4.0; // 平均 CTR
  
  // 包含数字加分
  if (/\d/.test(title)) baseCTR += 1.0;
  
  // 包含年份加分
  if (/2026|2025/.test(title)) baseCTR += 0.5;
  
  // 包含括号加分
  if (/[（()]/.test(title)) baseCTR += 0.5;
  
  // 长度适中加分
  if (title.length >= 40 && title.length <= 60) baseCTR += 1.0;
  
  // 包含 CTR  booster 加分
  CTR_BOOSTERS.forEach(word => {
    if (title.includes(word)) baseCTR += 0.3;
  });
  
  return Math.min(baseCTR, 15.0); // 上限 15%
}

/**
 * 计算 SEO 分数
 */
function calculateSEOScore(title, keywords) {
  let score = 70;
  
  keywords.forEach(kw => {
    if (title.toLowerCase().includes(kw.toLowerCase())) {
      score += 5;
    }
  });
  
  return Math.min(score, 100);
}

/**
 * 分析关键词
 */
function analyzeKeywords(content, keywords) {
  const allKeywords = [...keywords, ...extractKeywords(content)];
  
  return allKeywords.map(kw => ({
    keyword: kw,
    volume: KEYWORD_DATA[kw]?.volume || 10000,
    competition: KEYWORD_DATA[kw]?.competition || '中'
  }));
}

/**
 * 提取关键词
 */
function extractKeywords(content) {
  // 简化版关键词提取
  return content.split(/[\s,，]+/).filter(w => w.length >= 2).slice(0, 5);
}

/**
 * 生成标签
 */
function generateTags(content) {
  const baseTags = ['#教程', '#干货', '#学习', '#知识分享'];
  const keywords = extractKeywords(content);
  return [...keywords.map(k => `#${k}`), ...baseTags].slice(0, 10);
}

/**
 * 生成描述模板
 */
function generateDescriptionTemplate(content) {
  return `[前 2 行：包含核心关键词，吸引观众继续观看]

📌 时间戳：
0:00 开场介绍
1:30 核心内容
5:00 实战演示
10:00 总结

🔗 相关资源：
- 源码下载：[链接]
- 参考资料：[链接]

#标签 1 #标签 2 #标签 3`;
}

/**
 * 格式化输出
 */
function formatOutput(result) {
  let output = `## 🎬 YouTube 标题优化方案\n\n`;
  output += `### 🏆 推荐标题（CTR 预测：${result.recommended.ctr}%）\n`;
  output += `"${result.recommended.text}"\n\n`;
  output += `标题长度：${result.recommended.length} 字符 | SEO 分数：${result.recommended.seoScore}/100\n\n`;
  
  output += `### 📋 备选方案\n`;
  result.alternatives.forEach((alt, i) => {
    output += `${i + 1}. "${alt.text}" (CTR: ${alt.ctr}%, SEO: ${alt.seoScore})\n`;
  });
  
  output += `\n### 🔍 SEO 分析\n`;
  result.keywords.forEach((kw, i) => {
    if (i < 3) {
      output += `- ${kw.keyword}: 搜索量 ${kw.volume}/月，竞争${kw.competition}\n`;
    }
  });
  
  output += `\n### 🏷️ 标签建议\n`;
  output += result.tags.join(' ');\n\n`;
  
  output += `### 📝 描述模板\n`;
  output += `\`\`\`\n${result.description}\n\`\`\`\n`;
  
  return output;
}

/**
 * CLI 入口
 */
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('用法：youtube-title "内容描述" [--keywords "关键词 1，关键词 2"] [--count 数量]');
    process.exit(1);
  }
  
  const content = args.find(arg => !arg.startsWith('--'));
  const keywordsIndex = args.indexOf('--keywords');
  const countIndex = args.indexOf('--count');
  
  let keywords = [];
  if (keywordsIndex > -1) {
    keywords = args[keywordsIndex + 1].split(/[,,]/).map(k => k.trim());
  }
  
  const count = countIndex > -1 ? parseInt(args[countIndex + 1]) : 3;
  
  console.log('正在生成 YouTube 标题优化方案...\n');
  
  const result = await generateTitles(content.replace(/"/g, ''), keywords, count);
  console.log(formatOutput(result));
}

module.exports = { generateTitles, formatOutput };

if (require.main === module) {
  main().catch(console.error);
}
