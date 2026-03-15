#!/usr/bin/env node
/**
 * Warrior System - 战车系统核心代码
 * 版本：1.0.0（Phase 1 基础版）
 * 功能：多模型并行调用 + 4D 压缩汇总
 * 
 * 集成技能：
 * - gemini: Gemini CLI
 * - grok-search: Grok 搜索/聊天
 * - summarize: 基础汇总
 * - uptef-4d-compression-smart-router: 4D 压缩
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

/**
 * 主函数：多模型咨询
 * @param {string} query - 用户问题
 */
function consult(query) {
  console.log('🛡️ 战车系统启动...\n');
  console.log(`问题：${query}\n`);
  
  const startTime = Date.now();
  
  // Step 1: 调用 Neo（本地 - 通过 sessions_send 或模拟）
  console.log('🤖 Neo 思考中...');
  const neoResponse = callNeo(query);
  
  // Step 2: 调用 Gemini（CLI）
  console.log('💎 Gemini 思考中...');
  const geminiResponse = callGemini(query);
  
  // Step 3: 调用 Grok（CLI）
  console.log('🛠️ Grok 思考中...');
  const grokResponse = callGrok(query);
  
  // Step 4: 基础汇总
  console.log('\n📊 汇总中...');
  const summary = summarize(neoResponse, geminiResponse, grokResponse);
  
  // Step 5: 4D 压缩汇总
  console.log('🌀 4D 压缩中...\n');
  const compressed = compress4d(summary);
  
  // Step 6: 输出结果
  printResult(neoResponse, geminiResponse, grokResponse, summary, compressed);
  
  const endTime = Date.now();
  console.log(`\n⏱️ 总耗时：${((endTime - startTime) / 1000).toFixed(2)} 秒`);
}

/**
 * 调用 Neo（本地）
 * Phase 1: 模拟调用
 * Phase 2: 通过 sessions_send 调用
 */
function callNeo(query) {
  try {
    // Phase 1: 模拟（实际应调用 OpenClaw sessions_send）
    return `【Neo 视角】基于 4D 压缩和 UPTEF 框架，建议从选择力入手，明确方向后再执行影响力。${query} 可以通过三赢原则来评估：你好、我好、世界好。`;
  } catch (error) {
    return `【Neo 视角】暂时无法调用，稍后重试。`;
  }
}

/**
 * 调用 Gemini（CLI）
 */
function callGemini(query) {
  try {
    // 调用 gemini CLI
    const output = execSync(`gemini "${escapeShell(query)}"`, {
      encoding: 'utf-8',
      timeout: 30000 // 30 秒超时
    });
    return output.trim();
  } catch (error) {
    // 如果 gemini CLI 不可用，返回模拟响应
    console.log('  ⚠️ Gemini CLI 不可用，使用模拟响应');
    return `【Gemini 视角】从 Google AI 趋势来看，${query} 需要关注多模态和 Agent 能力，建议快速 MVP 验证。`;
  }
}

/**
 * 调用 Grok（CLI）
 */
function callGrok(query) {
  try {
    // 调用 grok-search CLI（chat 模式）
    const scriptPath = '/Users/abc/skills/grok-search/scripts/chat.mjs';
    const output = execSync(`node "${scriptPath}" "${escapeShell(query)}"`, {
      encoding: 'utf-8',
      timeout: 30000 // 30 秒超时
    });
    return output.trim();
  } catch (error) {
    // 如果 grok CLI 不可用，返回模拟响应
    console.log('  ⚠️ Grok CLI 不可用，使用模拟响应');
    return `【Grok 视角】工程师角度，${query} 的技术实现不难，关键是产品定位和商业化路径。`;
  }
}

/**
 * 基础汇总
 */
function summarize(neo, gemini, grok) {
  try {
    // 调用 summarize CLI（如果有）
    const combinedText = `Neo: ${neo}\n\nGemini: ${gemini}\n\nGrok: ${grok}`;
    const tempFile = '/tmp/warrior_combined.txt';
    fs.writeFileSync(tempFile, combinedText);
    
    const output = execSync(`summarize "${tempFile}" --length short`, {
      encoding: 'utf-8',
      timeout: 30000
    });
    fs.unlinkSync(tempFile);
    return output.trim();
  } catch (error) {
    // 如果 summarize 不可用，手动汇总
    return `三方共识：${neo.substring(0, 100)}... | ${gemini.substring(0, 100)}... | ${grok.substring(0, 100)}...`;
  }
}

/**
 * 4D 压缩汇总
 */
function compress4d(summary) {
  // Phase 1: 简单 4D 结构（实际应调用 4D 压缩技能）
  return {
    choice: `【选择力】${summary.substring(0, 50)}...`,
    impact: `【影响力】可立即执行的行动`,
    feedback: `【反馈力】需要注意的风险`,
    experience: `【体验力】核心洞察`
  };
}

/**
 * 打印结果
 */
function printResult(neo, gemini, grok, summary, compressed) {
  console.log('\n' + '═'.repeat(50));
  console.log('🛡️ 战车系统 · 多模型咨询结果');
  console.log('═'.repeat(50) + '\n');
  
  console.log('┌─────────────────────────────────────────────┐');
  console.log('│  🤖 Neo 回复                                │');
  console.log('├─────────────────────────────────────────────┤');
  printWrapped(neo, 50);
  console.log('└─────────────────────────────────────────────┘\n');
  
  console.log('┌─────────────────────────────────────────────┐');
  console.log('│  💎 Gemini 回复                             │');
  console.log('├─────────────────────────────────────────────┤');
  printWrapped(gemini, 50);
  console.log('└─────────────────────────────────────────────┘\n');
  
  console.log('┌─────────────────────────────────────────────┐');
  console.log('│  🛠️ Grok 回复                               │');
  console.log('├─────────────────────────────────────────────┤');
  printWrapped(grok, 50);
  console.log('└─────────────────────────────────────────────┘\n');
  
  console.log('┌─────────────────────────────────────────────┐');
  console.log('│  📊 基础汇总                                │');
  console.log('├─────────────────────────────────────────────┤');
  printWrapped(summary, 50);
  console.log('└─────────────────────────────────────────────┘\n');
  
  console.log('┌─────────────────────────────────────────────┐');
  console.log('│  🌀 4D 压缩汇总                              │');
  console.log('├─────────────────────────────────────────────┤');
  console.log(`│  ${compressed.choice}`.padEnd(50) + '│');
  console.log(`│  ${compressed.impact}`.padEnd(50) + '│');
  console.log(`│  ${compressed.feedback}`.padEnd(50) + '│');
  console.log(`│  ${compressed.experience}`.padEnd(50) + '│');
  console.log('└─────────────────────────────────────────────┘\n');
}

/**
 * 打印自动换行的文本
 */
function printWrapped(text, maxWidth) {
  const words = text.split(' ');
  let line = '│  ';
  
  for (const word of words) {
    if ((line + word).length > maxWidth - 2) {
      console.log(line.padEnd(maxWidth - 1) + '│');
      line = '│  ' + word;
    } else {
      line += (line === '│  ' ? '' : ' ') + word;
    }
  }
  
  if (line.trim()) {
    console.log(line.padEnd(maxWidth - 1) + '│');
  }
}

/**
 * 转义 shell 参数
 */
function escapeShell(str) {
  return str.replace(/"/g, '\\"').replace(/\$/g, '\\$');
}

// 命令行入口
const args = process.argv.slice(2);
if (args.length === 0) {
  console.log('用法：node warrior.js [咨询内容]');
  console.log('示例：node warrior.js "如何实现 AI 自盈利？"');
  process.exit(1);
}

const query = args.join(' ');
consult(query);
