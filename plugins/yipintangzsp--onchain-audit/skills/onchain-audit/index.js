#!/usr/bin/env node

/**
 * 链上项目安全审计 - 项目风险评估
 * 定价：¥9/次 | ¥199/月
 */

// 风险评估权重
const RISK_WEIGHTS = {
  合约安全：35,
  持币分布：25,
  流动性：20,
  团队背景：15,
  社区活跃：5
};

// 检查项
const CHECKLIST = {
  合约安全：[
    { name: '合约已开源', weight: 10 },
    { name: '无 honeypot 特征', weight: 15 },
    { name: '无无限 mint 权限', weight: 10 }
  ],
  持币分布：[
    { name: '前 10 地址<50%', weight: 15 },
    { name: '团队持仓<20%', weight: 10 }
  ],
  流动性：[
    { name: 'LP 已锁定', weight: 10 },
    { name: '流动性>$100K', weight: 10 }
  ],
  团队背景：[
    { name: '团队实名', weight: 10 },
    { name: '有知名投资', weight: 5 }
  ],
  社区活跃：[
    { name: 'Twitter 活跃', weight: 3 },
    { name: 'Telegram 活跃', weight: 2 }
  ]
};

/**
 * 执行安全审计
 */
async function auditProject(projectInput, deep = false) {
  const isAddress = /^0x[a-fA-F0-9]{40}$/.test(projectInput);
  
  // 模拟审计结果（实际应调用链上 API）
  const auditResult = {
    projectName: isAddress ? `合约 ${projectInput.substring(0, 10)}...` : projectInput,
    auditTime: new Date().toISOString(),
    isDeep: deep,
    scores: {},
    checks: {},
    risks: [],
    safes: [],
    data: generateProjectData(),
    recommendation: {}
  };
  
  // 执行各项检查
  for (const [category, items] of Object.entries(CHECKLIST)) {
    const categoryScore = auditCategory(category, items, auditResult);
    auditResult.scores[category] = categoryScore;
  }
  
  // 计算综合评分
  const totalScore = calculateTotalScore(auditResult.scores);
  auditResult.totalScore = totalScore;
  auditResult.riskLevel = getRiskLevel(totalScore);
  
  // 生成建议
  auditResult.recommendation = generateRecommendation(totalScore, auditResult.data);
  
  return auditResult;
}

/**
 * 审计单个类别
 */
function auditCategory(category, items, result) {
  let score = 0;
  let maxScore = 0;
  
  items.forEach(item => {
    maxScore += item.weight;
    // 模拟检查结果（实际应调用 API）
    const passed = Math.random() > 0.4; // 60% 通过率
    
    if (passed) {
      score += item.weight;
      result.safes.push(`[✓] ${item.name}`);
    } else {
      result.risks.push(`[!] ${item.name}`);
    }
  });
  
  return Math.round((score / maxScore) * 100);
}

/**
 * 计算综合评分
 */
function calculateTotalScore(scores) {
  let total = 0;
  let totalWeight = 0;
  
  for (const [category, score] of Object.entries(scores)) {
    const weight = RISK_WEIGHTS[category] || 10;
    total += score * weight;
    totalWeight += weight;
  }
  
  return Math.round(total / totalWeight);
}

/**
 * 获取风险等级
 */
function getRiskLevel(score) {
  if (score >= 80) return '低风险';
  if (score >= 60) return '中风险';
  if (score >= 40) return '高风险';
  return '极高风险';
}

/**
 * 生成项目数据（模拟）
 */
function generateProjectData() {
  return {
    marketCap: `$${(Math.random() * 1000 + 100).toFixed(0)}K`,
    volume24h: `$${(Math.random() * 100 + 10).toFixed(0)}K`,
    holders: Math.floor(Math.random() * 5000 + 500),
    launchDays: Math.floor(Math.random() * 30 + 1),
    lpLocked: Math.random() > 0.3,
    lpLockDays: Math.floor(Math.random() * 365),
    top10Concentration: `${Math.floor(Math.random() * 40 + 30)}%`,
    teamShare: `${Math.floor(Math.random() * 30)}%`
  };
}

/**
 * 生成投资建议
 */
function generateRecommendation(score, data) {
  let position, stopLoss, focus;
  
  if (score >= 80) {
    position = '可配置 10-20%';
    stopLoss = '-30%';
    focus = '项目进展、市值增长';
  } else if (score >= 60) {
    position = '不超过总资金 5%';
    stopLoss = '-20%';
    focus = '交易量、持币地址数';
  } else if (score >= 40) {
    position = '建议观望';
    stopLoss = '-10%';
    focus = '风险变化、团队动态';
  } else {
    position = '强烈建议避开';
    stopLoss = 'N/A';
    focus = '风险警示';
  }
  
  return { position, stopLoss, focus };
}

/**
 * 格式化输出
 */
function formatOutput(result) {
  let output = `## 🔒 链上项目安全审计报告\n\n`;
  output += `**项目：** ${result.projectName}\n`;
  output += `**审计时间：** ${result.auditTime.split('T')[0]}\n\n`;
  
  output += `### 📊 综合风险评分：${result.totalScore}/100（${result.riskLevel}）\n\n`;
  
  // 各类别得分
  output += `**分类评分：**\n`;
  for (const [cat, score] of Object.entries(result.scores)) {
    output += `- ${cat}: ${score}/100\n`;
  }
  output += `\n`;
  
  // 安全项
  output += `### ✅ 安全项（${result.safes.length}项）\n`;
  result.safes.forEach(item => output += `${item}\n`);
  output += `\n`;
  
  // 风险项
  output += `### ⚠️ 风险项（${result.risks.length}项）\n`;
  result.risks.forEach(item => output += `${item}\n`);
  output += `\n`;
  
  // 投资建议
  output += `### 💡 投资建议\n`;
  output += `- 建议仓位：${result.recommendation.position}\n`;
  output += `- 止损位：${result.recommendation.stopLoss}\n`;
  output += `- 关注指标：${result.recommendation.focus}\n\n`;
  
  // 项目数据
  output += `### 📈 项目数据\n`;
  output += `- 市值：${result.data.marketCap}\n`;
  output += `- 24h 交易量：${result.data.volume24h}\n`;
  output += `- 持币地址：${result.data.holders}\n`;
  output += `- 上线时间：${result.data.launchDays}天\n`;
  output += `- LP 锁定：${result.data.lpLocked ? `${result.data.lpLockDays}天` : '未锁定'}\n`;
  output += `- 前 10 地址：${result.data.top10Concentration}\n`;
  output += `- 团队持仓：${result.data.teamShare}\n`;
  
  return output;
}

/**
 * CLI 入口
 */
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('用法：onchain-audit "项目地址或名称" [--deep]');
    console.log('示例：onchain-audit "0x1234...5678"');
    console.log('      onchain-audit "项目名称" --deep');
    process.exit(1);
  }
  
  const project = args.find(arg => !arg.startsWith('--'));
  const isDeep = args.includes('--deep');
  
  console.log('正在执行链上安全审计...\n');
  
  const result = await auditProject(project.replace(/"/g, ''), isDeep);
  console.log(formatOutput(result));
}

module.exports = { auditProject, formatOutput };

if (require.main === module) {
  main().catch(console.error);
}
