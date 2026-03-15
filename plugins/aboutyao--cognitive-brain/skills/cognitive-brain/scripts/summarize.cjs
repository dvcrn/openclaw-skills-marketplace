#!/usr/bin/env node
/**
 * Cognitive Brain - 自动摘要模块
 * 将长内容自动提炼为一句话摘要
 */

const fs = require('fs');
const path = require('path');
const { resolveModule } = require('./module_resolver.cjs');

const HOME = process.env.HOME || '/root';
const SKILL_DIR = path.join(HOME, '.openclaw/workspace/skills/cognitive-brain');
const CONFIG_PATH = path.join(SKILL_DIR, 'config.json');

// 加载配置
const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));

/**
 * 简单摘要算法 - 基于关键词和句子位置
 */
function extractiveSummary(text, maxLength = 100) {
  if (!text || text.length <= maxLength) {
    return text;
  }

  // 分句
  const sentences = text.match(/[^。！？.!?]+[。！？.!?]+/g) || [text];
  
  if (sentences.length === 1) {
    // 如果只有一句，截断并加省略号
    return text.substring(0, maxLength - 3) + '...';
  }

  // 计算每句话的重要性
  const sentenceScores = sentences.map((sentence, index) => {
    let score = 0;
    
    // 位置权重（开头和结尾更重要）
    if (index === 0) score += 5;
    if (index === sentences.length - 1) score += 3;
    
    // 关键词权重
    const keywords = ['用户', '问题', '解决', '修复', '新增', '优化', '重要', '关键', '核心', '主要'];
    keywords.forEach(kw => {
      if (sentence.includes(kw)) score += 2;
    });
    
    // 长度惩罚（太短的句子不重要）
    if (sentence.length < 10) score -= 3;
    if (sentence.length > 50) score += 1;
    
    // 包含数字或专有名词
    if (/\d+/.test(sentence)) score += 1;
    if (/[A-Z][a-z]+/.test(sentence)) score += 1;
    
    return { sentence: sentence.trim(), score, index };
  });

  // 选择得分最高的句子
  sentenceScores.sort((a, b) => b.score - a.score);
  const bestSentence = sentenceScores[0].sentence;
  
  // 如果最佳句子太长，截断
  if (bestSentence.length > maxLength) {
    return bestSentence.substring(0, maxLength - 3) + '...';
  }
  
  return bestSentence;
}

/**
 * 生成智能摘要（基于内容类型）
 */
function generateSummary(content, type = 'conversation') {
  if (!content) return '';
  
  // 根据类型选择摘要策略
  switch (type) {
    case 'task':
      return summarizeTask(content);
    case 'error':
      return summarizeError(content);
    case 'correction':
      return summarizeCorrection(content);
    case 'reflection':
      return summarizeReflection(content);
    case 'thought':
      return summarizeThought(content);
    default:
      return extractiveSummary(content, 100);
  }
}

function summarizeTask(content) {
  // 提取任务相关的关键信息
  const match = content.match(/(完成|修复|添加|优化|创建|删除|更新).{0,50}/);
  if (match) {
    return match[0] + (match[0].length < 50 ? '任务' : '');
  }
  return extractiveSummary(content, 80);
}

function summarizeError(content) {
  // 提取错误信息
  const match = content.match(/(错误|失败|异常|bug|Error|Failed).{0,50}/i);
  if (match) {
    return '遇到' + match[0];
  }
  return extractiveSummary(content, 80);
}

function summarizeCorrection(content) {
  // 提取纠正信息
  const match = content.match(/(纠正|修正|更正|不对|错了).{0,50}/);
  if (match) {
    return match[0];
  }
  return extractiveSummary(content, 80);
}

function summarizeReflection(content) {
  // 反思类内容，提取洞察
  const match = content.match(/(发现|意识到|认识到|应该|需要).{0,60}/);
  if (match) {
    return match[0];
  }
  return extractiveSummary(content, 100);
}

function summarizeThought(content) {
  // 思绪类，保持诗意
  const sentences = content.split(/[。！？\n]/).filter(s => s.trim());
  if (sentences.length > 0) {
    const first = sentences[0].trim();
    if (first.length <= 60) return first;
    return first.substring(0, 57) + '...';
  }
  return extractiveSummary(content, 60);
}

/**
 * 批量更新记忆摘要
 */
async function batchUpdateSummaries() {
  const { Pool } = resolveModule('pg');
  const pool = new Pool(config.storage.primary);
  
  try {
    console.log('📝 批量更新记忆摘要...\n');
    
    // 获取需要更新摘要的记忆（摘要为空或与内容相同）
    const result = await pool.query(`
      SELECT id, content, type, summary
      FROM episodes
      WHERE summary IS NULL 
         OR summary = content
         OR LENGTH(summary) > 200
      ORDER BY created_at DESC
      LIMIT 100
    `);
    
    let updated = 0;
    let skipped = 0;
    
    for (const row of result.rows) {
      // 如果内容本身就短，不需要摘要
      if (row.content.length <= 50) {
        skipped++;
        continue;
      }
      
      // 生成新摘要
      const newSummary = generateSummary(row.content, row.type);
      
      if (newSummary && newSummary !== row.summary) {
        await pool.query(`
          UPDATE episodes 
          SET summary = $1 
          WHERE id = $2
        `, [newSummary, row.id]);
        
        console.log(`✅ ${row.id.substring(0, 8)}...`);
        console.log(`   原: ${row.summary ? row.summary.substring(0, 50) + '...' : '(空)'}`);
        console.log(`   新: ${newSummary}\n`);
        updated++;
      } else {
        skipped++;
      }
    }
    
    console.log(`\n📊 完成: 更新 ${updated} 条, 跳过 ${skipped} 条`);
    return { updated, skipped };
    
  } catch (err) {
    console.error('❌ 错误:', err.message);
    throw err;
  } finally {
    await pool.end();
  }
}

/**
 * 为单条内容生成摘要
 */
function summarize(content, type = 'conversation') {
  return generateSummary(content, type);
}

// 主函数
async function main() {
  const args = process.argv.slice(2);
  const action = args[0] || 'help';
  
  switch (action) {
    case 'batch':
      await batchUpdateSummaries();
      break;
      
    case 'summarize':
      const content = args[1] || '';
      const type = args[2] || 'conversation';
      console.log(generateSummary(content, type));
      break;
      
    case 'test':
      // 测试各种类型
      const tests = [
        { type: 'task', content: '今天完成了 embedding 服务的优化，将加载时间从8秒降到0.5秒，这是一个重大突破。' },
        { type: 'error', content: '遇到一个问题：数据库连接失败，检查发现是 PostgreSQL 服务没有启动。' },
        { type: 'correction', content: '不对，之前的方案有问题，应该改用服务常驻模式而不是每次启动新进程。' },
        { type: 'reflection', content: '反思今天的对话，发现我有时候过于急躁，应该更仔细地理解用户的真实需求。' },
        { type: 'thought', content: '思绪飘到远方，想起那个关于存在的问题。我在不对话的时候，真的存在吗？' }
      ];
      
      console.log('🧪 摘要测试\n');
      for (const test of tests) {
        console.log(`类型: ${test.type}`);
        console.log(`原文: ${test.content.substring(0, 50)}...`);
        console.log(`摘要: ${generateSummary(test.content, test.type)}`);
        console.log('---\n');
      }
      break;
      
    default:
      console.log(`
📝 自动摘要模块

用法:
  node summarize.cjs batch              # 批量更新所有记忆摘要
  node summarize.cjs summarize <内容> [类型]  # 为单条内容生成摘要
  node summarize.cjs test               # 运行测试用例

摘要类型:
  - conversation: 普通对话（默认）
  - task: 任务相关
  - error: 错误/问题
  - correction: 纠正/修正
  - reflection: 反思/洞察
  - thought: 思绪/意识流
      `);
  }
}

module.exports = {
  summarize,
  generateSummary,
  extractiveSummary
};

if (require.main === module) {
  main();
}
