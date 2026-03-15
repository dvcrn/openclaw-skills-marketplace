#!/usr/bin/env node
/**
 * 收入监控 - 监控 SkillPay 收入数据
 * 每晚 10 点推送日报
 */

const fs = require('fs');
const path = require('path');

// 模拟收入数据（实际应接入 SkillPay API）
const SKILL_DATA = [
  { name: '新币保命扫描器', price: 5, downloads: 10 },
  { name: '空投资格检测', price: 5, downloads: 8 },
  { name: 'Whale 地址追踪', price: 5, downloads: 5 },
  { name: '爆款标题魔法师', price: 3, downloads: 12 },
  { name: '亚马逊选品助手', price: 8, downloads: 3 },
  { name: 'Prompt 降维打击', price: 5, downloads: 6 },
  { name: '名校文书润色', price: 15, downloads: 2 },
  { name: 'NFT 地板价监控', price: 3, downloads: 4 },
  { name: 'Perplexica AI 搜索', price: 3, downloads: 5 }
];

// 计算收入
function calculateRevenue() {
  const today = new Date().toLocaleDateString('zh-CN');
  
  const totalDownloads = SKILL_DATA.reduce((sum, s) => sum + s.downloads, 0);
  const totalRevenue = SKILL_DATA.reduce((sum, s) => sum + (s.price * s.downloads), 0);
  
  const topSkill = SKILL_DATA.reduce((max, s) => s.downloads > max.downloads ? s : max, SKILL_DATA[0]);
  
  return {
    date: today,
    totalDownloads,
    totalRevenue,
    topSkill,
    breakdown: SKILL_DATA
  };
}

// 生成日报
function generateReport() {
  const data = calculateRevenue();
  
  const report = `
💰 SkillPay 收入日报 - ${data.date}

📊 今日总计
- 总下载：${data.totalDownloads} 次
- 总收入：¥${data.totalRevenue}
- 平均单价：¥${(data.totalRevenue / data.totalDownloads).toFixed(2)}

🏆 热门 Skill
${data.topSkill.name} - ${data.topSkill.downloads} 次 (¥${data.topSkill.price})

📋 详细数据
${data.breakdown.map(s => `• ${s.name}: ${s.downloads}次 × ¥${s.price} = ¥${s.price * s.downloads}`).join('\n')}

📈 月度累计
- 本月下载：待统计
- 本月收入：待统计
- 目标完成：${((data.totalRevenue / 5000) * 100).toFixed(1)}%

---
继续优化，坐等收钱！🐾
  `;
  
  return report.trim();
}

// 主函数
if (require.main === module) {
  console.log(generateReport());
}

module.exports = { generateReport, calculateRevenue };
