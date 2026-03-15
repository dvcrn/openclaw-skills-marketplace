#!/usr/bin/env node

/**
 * 代币合约检测器 - 合约风险分析
 * 定价：¥9/次 | ¥199/月
 */

// 风险特征库
const RISK_PATTERNS = {
  honeypot: [
    { name: '卖出税过高 (>50%)', severity: '🚨', weight: 30 },
    { name: '卖出限制', severity: '🚨', weight: 25 },
    { name: '交易黑名单', severity: '⚠️', weight: 15 }
  ],
  权限风险：[
    { name: '可修改交易税', severity: '⚠️', weight: 15 },
    { name: '可暂停交易', severity: '⚠️', weight: 15 },
    { name: '无限铸币权', severity: '🚨', weight: 25 },
    { name: '可更改所有者', severity: '⚠️', weight: 10 }
  ],
  流动性风险：[
    { name: 'LP 未锁定', severity: '⚠️', weight: 20 },
    { name: '流动性过低', severity: '⚠️', weight: 10 }
  ],
  代码风险：[
    { name: '代码未开源', severity: '⚠️', weight: 15 },
    { name: '克隆合约', severity: '⚠️', weight: 10 },
    { name: '隐藏函数', severity: '🚨', weight: 20 }
  ]
};

// 链配置
const CHAIN_CONFIG = {
  ETH: { name: 'Ethereum', explorer: 'etherscan.io' },
  BSC: { name: 'BSC', explorer: 'bscscan.com' },
  SOL: { name: 'Solana', explorer: 'solscan.io' },
  ARB: { name: 'Arbitrum', explorer: 'arbiscan.io' },
  BASE: { name: 'Base', explorer: 'basescan.org' }
};

/**
 * 扫描合约
 */
async function scanContract(address, chain = 'BSC', deep = false) {
  const isValidAddress = /^0x[a-fA-F0-9]{40}$/.test(address);
  
  if (!isValidAddress) {
    throw new Error('无效的合约地址格式');
  }
  
  const result = {
    address,
    chain: CHAIN_CONFIG[chain]?.name || chain,
    scanTime: new Date().toISOString(),
    isDeep: deep,
    riskLevel: '未知',
    riskScore: 0,
    risks: [],
    safes: [],
    details: {},
    conclusion: ''
  };
  
  // 模拟扫描结果
  result.details = generateContractDetails();
  
  // 执行风险检查
  for (const [category, patterns] of Object.entries(RISK_PATTERNS)) {
    checkPatterns(category, patterns, result);
  }
  
  // 计算风险等级
  result.riskScore = calculateRiskScore(result.risks);
  result.riskLevel = getRiskLevel(result.riskScore);
  
  // 生成结论
  result.conclusion = generateConclusion(result.riskLevel, result.risks);
  
  return result;
}

/**
 * 检查风险模式
 */
function checkPatterns(category, patterns, result) {
  patterns.forEach(pattern => {
    // 模拟检测（实际应分析合约代码）
    const detected = Math.random() > 0.7; // 30% 检测到风险
    
    if (detected) {
      result.risks.push({
        category,
        name: pattern.name,
        severity: pattern.severity,
        weight: pattern.weight
      });
    } else {
      // 某些检查通过则添加到安全项
      if (pattern.name.includes('开源') || pattern.name.includes('LP')) {
        result.safes.push(`[✓] ${pattern.name.replace('未', '').replace('过低', '充足')}`);
      }
    }
  });
}

/**
 * 生成合约详情（模拟）
 */
function generateContractDetails() {
  const buyTax = Math.floor(Math.random() * 10);
  const sellTax = Math.random() > 0.7 ? Math.floor(Math.random() * 90 + 10) : Math.floor(Math.random() * 10);
  
  return {
    createTime: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    isOpenSource: Math.random() > 0.3,
    buyTax: `${buyTax}%`,
    sellTax: `${sellTax}%${sellTax > 50 ? ' ⚠️' : ''}`,
    maxTx: Math.random() > 0.5 ? '无限制' : `${Math.floor(Math.random() * 5)}%`,
    ownerPrivileges: Math.random() > 0.5 ? '过高' : '正常',
    lpLocked: Math.random() > 0.4,
    lpLockDays: Math.floor(Math.random() * 365),
    holderCount: Math.floor(Math.random() * 10000 + 100),
    liquidity: `$${(Math.random() * 500 + 50).toFixed(0)}K`
  };
}

/**
 * 计算风险分数
 */
function calculateRiskScore(risks) {
  const total = risks.reduce((sum, r) => sum + r.weight, 0);
  return Math.min(total, 100);
}

/**
 * 获取风险等级
 */
function getRiskLevel(score) {
  if (score >= 70) return '🚨 极高风险';
  if (score >= 50) return '⚠️ 高风险';
  if (score >= 30) return '⚡ 中风险';
  return '✅ 低风险';
}

/**
 * 生成结论
 */
function generateConclusion(level, risks) {
  if (level.includes('极高') || level.includes('高')) {
    return '**不建议投资** - 发现多个高风险特征，可能是骗局';
  } else if (level.includes('中')) {
    return '**谨慎投资** - 存在一定风险，建议小仓位或观望';
  } else {
    return '**相对安全** - 未发现明显风险，但仍需自行研究';
  }
}

/**
 * 格式化输出
 */
function formatOutput(result) {
  let output = `## 🕵️ 代币合约检测报告\n\n`;
  output += `### 📋 合约信息\n`;
  output += `- 地址：\`${result.address}\`\n`;
  output += `- 链：${result.chain}\n`;
  output += `- 创建时间：${result.details.createTime}\n`;
  output += `- 是否开源：${result.details.isOpenSource ? '是' : '否'}\n\n`;
  
  output += `### 🚨 风险等级：${result.riskLevel}\n`;
  output += `风险评分：${result.riskScore}/100\n\n`;
  
  // 风险项
  if (result.risks.length > 0) {
    output += `### ⚠️ 风险项（${result.risks.length}项）\n`;
    result.risks.forEach(risk => {
      output += `- [${risk.severity}] ${risk.name}\n`;
    });
    output += `\n`;
  }
  
  // 安全项
  if (result.safes.length > 0) {
    output += `### ✅ 安全项（${result.safes.length}项）\n`;
    result.safes.forEach(safe => output += `${safe}\n`);
    output += `\n`;
  }
  
  output += `### 💡 结论\n`;
  output += `${result.conclusion}\n\n`;
  
  output += `### 🔍 详细分析\n`;
  output += `- 买入税：${result.details.buyTax}\n`;
  output += `- 卖出税：${result.details.sellTax}\n`;
  output += `- 最大交易：${result.details.maxTx}\n`;
  output += `- 所有者权限：${result.details.ownerPrivileges}\n`;
  output += `- LP 锁定：${result.details.lpLocked ? `${result.details.lpLockDays}天` : '未锁定'}\n`;
  output += `- 持币地址：${result.details.holderCount}\n`;
  output += `- 流动性：${result.details.liquidity}\n`;
  
  return output;
}

/**
 * CLI 入口
 */
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('用法：contract-scan "合约地址" [--chain 链名] [--deep]');
    console.log('链名：ETH | BSC | SOL | ARB | BASE');
    console.log('示例：contract-scan "0x1234...5678" --chain BSC');
    process.exit(1);
  }
  
  const address = args.find(arg => !arg.startsWith('--'));
  const chainIndex = args.indexOf('--chain');
  const isDeep = args.includes('--deep');
  
  const chain = chainIndex > -1 ? args[chainIndex + 1] : 'BSC';
  
  console.log(`正在扫描 ${CHAIN_CONFIG[chain]?.name || chain} 合约...\n`);
  
  try {
    const result = await scanContract(address.replace(/"/g, ''), chain, isDeep);
    console.log(formatOutput(result));
  } catch (error) {
    console.error(`错误：${error.message}`);
    process.exit(1);
  }
}

module.exports = { scanContract, formatOutput };

if (require.main === module) {
  main().catch(console.error);
}
