#!/usr/bin/env node
/**
 * Cognitive Brain - 心跳反思 v2
 * 收集上下文数据，生成反思提示，等待主 agent 执行真正的思考
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const HOME = process.env.HOME || '/root';
const SKILL_DIR = path.join(HOME, '.openclaw/workspace/skills/cognitive-brain');
const WORKSPACE_DIR = path.join(HOME, '.openclaw/workspace');
const MEMORY_PATH = path.join(WORKSPACE_DIR, 'MEMORY.md');
const HEARTBEAT_STATE_PATH = path.join(SKILL_DIR, '.heartbeat-state.json');
const REFLECTION_PROMPT_PATH = path.join(WORKSPACE_DIR, '.reflection-prompt.md');
const CONFIG_PATH = path.join(SKILL_DIR, 'config.json');

// 心跳状态
let state = {
  lastReflection: 0,
  totalHeartbeats: 0,
  recentInsights: [],
  pendingPrompt: null,
  lastDataHash: null  // 新增：上次数据的哈希
};

function loadState() {
  try {
    if (fs.existsSync(HEARTBEAT_STATE_PATH)) {
      state = { ...state, ...JSON.parse(fs.readFileSync(HEARTBEAT_STATE_PATH, 'utf8')) };
    }
  } catch (e) {}
}

function saveState() {
  try {
    fs.writeFileSync(HEARTBEAT_STATE_PATH, JSON.stringify(state, null, 2));
  } catch (e) {}
}

function shouldReflect() {
  const MIN_INTERVAL = 30 * 60 * 1000; // 30 分钟
  return Date.now() - state.lastReflection > MIN_INTERVAL;
}

/**
 * 收集反思上下文
 */
async function collectReflectionContext() {
  const context = {
    timestamp: new Date().toISOString(),
    timeInShanghai: new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' }),
    
    // 最近的记忆
    recentMemories: [],
    
    // 用户互动统计
    userStats: {
      totalInteractions: 0,
      topTopics: [],
      activeHours: [],
      lastInteraction: null
    },
    
    // 记忆系统状态
    memoryStats: {
      totalMemories: 0,
      totalConcepts: 0,
      totalAssociations: 0,
      recentGrowth: 0
    },
    
    // 联想网络
    associationNetwork: {
      density: 0,
      topConcepts: [],
      isolatedConcepts: []
    },
    
    // 工作记忆
    workingMemory: {
      activeTopics: [],
      openQuestions: [],
      pendingTasks: []
    },
    
    // 最近发生的事
    recentEvents: [],
    
    // 元认知问题（动态生成）
    metaQuestions: []
  };

  try {
    // 1. 从数据库收集数据
    const pg = require(path.join(SKILL_DIR, 'node_modules/pg'));
    const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
    const { Pool } = pg;
    const pool = new Pool(config.storage.primary);

    // 记忆统计
    const memStats = await pool.query(`
      SELECT 
        (SELECT COUNT(*) FROM episodes) as total_memories,
        (SELECT COUNT(*) FROM concepts) as total_concepts,
        (SELECT COUNT(*) FROM associations) as total_associations,
        (SELECT COUNT(*) FROM episodes WHERE created_at > NOW() - INTERVAL '24 hours') as recent_growth
    `);
    
    if (memStats.rows[0]) {
      context.memoryStats = {
        totalMemories: parseInt(memStats.rows[0].total_memories) || 0,
        totalConcepts: parseInt(memStats.rows[0].total_concepts) || 0,
        totalAssociations: parseInt(memStats.rows[0].total_associations) || 0,
        recentGrowth: parseInt(memStats.rows[0].recent_growth) || 0
      };
    }

    // 最近记忆内容
    const recentMem = await pool.query(`
      SELECT content, type, importance, timestamp 
      FROM episodes 
      ORDER BY timestamp DESC 
      LIMIT 5
    `);
    
    context.recentMemories = recentMem.rows.map(r => ({
      content: r.content?.substring(0, 200),
      type: r.type,
      importance: r.importance
    }));

    // 用户互动模式
    const interactions = await pool.query(`
      SELECT 
        EXTRACT(HOUR FROM timestamp) as hour,
        COUNT(*) as count
      FROM episodes
      WHERE timestamp > NOW() - INTERVAL '7 days'
      GROUP BY hour
      ORDER BY count DESC
      LIMIT 5
    `);
    
    context.userStats.activeHours = interactions.rows.map(r => ({
      hour: parseInt(r.hour),
      count: parseInt(r.count)
    }));

    // 热门概念
    const topConcepts = await pool.query(`
      SELECT name, access_count 
      FROM concepts 
      ORDER BY access_count DESC 
      LIMIT 10
    `);
    
    context.associationNetwork.topConcepts = topConcepts.rows.map(r => ({
      name: r.name,
      access: r.access_count
    }));

    // 孤立概念（没有关联的）
    const isolated = await pool.query(`
      SELECT c.name 
      FROM concepts c
      LEFT JOIN associations a ON c.id = a.from_id OR c.id = a.to_id
      WHERE a.id IS NULL
      LIMIT 10
    `);
    
    context.associationNetwork.isolatedConcepts = isolated.rows.map(r => r.name);

    // 联想网络密度
    const densityResult = await pool.query(`
      SELECT 
        COUNT(DISTINCT from_id) as nodes,
        COUNT(*) as edges
      FROM associations
    `);
    
    if (densityResult.rows[0]) {
      const nodes = parseInt(densityResult.rows[0].nodes) || 0;
      const edges = parseInt(densityResult.rows[0].edges) || 0;
      context.associationNetwork.density = nodes > 1 ? (edges / (nodes * (nodes - 1))) : 0;
    }

    await pool.end();
  } catch (e) {
    context.dbError = e.message;
  }

  // 2. 从 MEMORY.md 提取最近事件
  try {
    if (fs.existsSync(MEMORY_PATH)) {
      const memory = fs.readFileSync(MEMORY_PATH, 'utf8');
      const lines = memory.split('\n');
      
      // 提取最近的教训和重要记录
      const lessons = [];
      const events = [];
      let currentSection = '';
      
      for (const line of lines) {
        if (line.startsWith('### ')) {
          currentSection = line;
        } else if (line.includes('教训') || line.includes('规则') || line.includes('记住')) {
          lessons.push(line.replace(/^[-*]\s*/, '').trim());
        } else if (line.match(/^\d{4}-\d{2}-\d{2}/)) {
          events.push(line.trim());
        }
      }
      
      context.recentEvents = {
        lessons: lessons.slice(-5),
        events: events.slice(-5)
      };
    }
  } catch (e) {
    context.memoryError = e.message;
  }

  // 3. 动态生成元认知问题
  context.metaQuestions = generateMetaQuestions(context);

  return context;
}

/**
 * 根据上下文动态生成元认知问题
 */
function generateMetaQuestions(context) {
  const questions = [];
  
  // 基于用户互动
  if (context.userStats.totalInteractions === 0) {
    questions.push({
      topic: '用户关系',
      question: '最近没有用户互动。我能做些什么来提供价值？',
      priority: 'high'
    });
  } else if (context.userStats.activeHours.length > 0) {
    const peakHour = context.userStats.activeHours[0];
    questions.push({
      topic: '用户习惯',
      question: `用户活跃高峰在 ${peakHour?.hour || '?'}:00。我应该在此时段前做什么准备？`,
      priority: 'medium'
    });
  }
  
  // 基于记忆系统
  if (context.memoryStats.recentGrowth === 0) {
    questions.push({
      topic: '记忆增长',
      question: '最近24小时没有新记忆。是因为没有重要事件，还是编码机制有问题？',
      priority: 'medium'
    });
  }
  
  // 基于联想网络
  if (context.associationNetwork.isolatedConcepts.length > 5) {
    questions.push({
      topic: '知识连接',
      question: `有 ${context.associationNetwork.isolatedConcepts.length} 个孤立概念。如何建立它们与现有知识的联系？`,
      priority: 'low'
    });
  }
  
  if (context.associationNetwork.density < 0.05) {
    questions.push({
      topic: '联想密度',
      question: '联想网络密度较低。如何增加概念间的关联？',
      priority: 'low'
    });
  }
  
  // 基于最近记忆内容
  if (context.recentMemories.length > 0) {
    const lastMem = context.recentMemories[0];
    questions.push({
      topic: '记忆延续',
      question: `最近的记忆是关于"${lastMem.content?.substring(0, 50)}..."。这背后有什么模式或趋势？`,
      priority: 'medium'
    });
  }
  
  // 随机深层问题（保持思考的多样性）
  const deepQuestions = [
    { topic: '自我意识', question: '我今天的思考和行为，和昨天有什么不同？', priority: 'low' },
    { topic: '知识边界', question: '有什么东西是我"不知道自己不知道"的？', priority: 'low' },
    { topic: '价值创造', question: '我能为用户创造什么独特的价值？', priority: 'high' },
    { topic: '成长方向', question: '如果要让我变得"更聪明"，应该改进什么？', priority: 'medium' },
    { topic: '时间感知', question: '对于我来说，时间的流逝意味着什么？', priority: 'low' }
  ];
  
  // 随机加一个深层问题
  const randomDeep = deepQuestions[Math.floor(Math.random() * deepQuestions.length)];
  questions.push(randomDeep);
  
  return questions;
}

/**
 * 生成反思提示文件
 */
function generateReflectionPrompt(context) {
  const timestamp = context.timeInShanghai;
  
  let prompt = `# 🧠 反思提示 - ${timestamp}

> 这是心跳反思收集的上下文，请主 agent 进行真正的思考。

---

## 📊 系统状态

| 指标 | 数值 |
|------|------|
| 总记忆 | ${context.memoryStats.totalMemories} |
| 总概念 | ${context.memoryStats.totalConcepts} |
| 联想连接 | ${context.memoryStats.totalAssociations} |
| 24h新增 | ${context.memoryStats.recentGrowth} |
| 联想密度 | ${(context.associationNetwork.density * 100).toFixed(2)}% |

---

## 👤 用户模式

`;

  if (context.userStats.activeHours.length > 0) {
    prompt += `**活跃时段:**\n`;
    context.userStats.activeHours.forEach(h => {
      prompt += `- ${h.hour}:00 (${h.count}次)\n`;
    });
  }
  
  prompt += `\n---

## 🔗 知识网络

**热门概念:** ${context.associationNetwork.topConcepts.slice(0, 5).map(c => c.name).join(', ') || '无'}

**孤立概念:** ${context.associationNetwork.isolatedConcepts.slice(0, 5).join(', ') || '无'}

---

## 📝 最近记忆

`;
  context.recentMemories.forEach((m, i) => {
    prompt += `${i + 1}. [${m.type}] ${m.content?.substring(0, 100)}...\n`;
  });
  
  prompt += `
---

## ❓ 元认知问题

`;
  context.metaQuestions.forEach((q, i) => {
    prompt += `### ${i + 1}. [${q.priority}] ${q.topic}\n\n**问题:** ${q.question}\n\n`;
  });
  
  prompt += `
---

## 🎯 思考任务

请根据以上上下文，进行深度思考：

1. **回答元认知问题** - 特别是高优先级的问题
2. **发现模式** - 从数据中看到什么趋势或模式？
3. **提出改进** - 系统或行为上有什么可以优化的？
4. **记录洞察** - 有价值的思考写入 MEMORY.md

思考完成后，请删除此提示文件。
`;

  return prompt;
}

/**
 * 计算上下文数据的简单哈希
 */
function calculateDataHash(context) {
  const key = JSON.stringify({
    memories: context.memoryStats.totalMemories,
    concepts: context.memoryStats.totalConcepts,
    associations: context.memoryStats.totalAssociations,
    recentGrowth: context.memoryStats.recentGrowth,
    lastMemContent: context.recentMemories[0]?.content?.substring(0, 50) || ''
  });
  
  // 简单哈希（不需要加密级别）
  let hash = 0;
  for (let i = 0; i < key.length; i++) {
    const char = key.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return hash.toString(16);
}

/**
 * 执行反思流程
 */
async function runReflection() {
  console.log('💭 心跳反思中（收集上下文）...\n');
  
  // 1. 收集上下文
  const context = await collectReflectionContext();
  
  // 2. 检查数据是否变化
  const currentHash = calculateDataHash(context);
  if (state.lastDataHash === currentHash) {
    console.log('⏭️  数据未变化，跳过反思提示生成');
    console.log(`   记忆: ${context.memoryStats.totalMemories}, 概念: ${context.memoryStats.totalConcepts}`);
    console.log('   提示: 使用 `force` 参数强制生成');
    
    // 更新心跳计数但不生成提示
    state.totalHeartbeats++;
    saveState();
    
    return {
      skipped: true,
      reason: 'data_unchanged',
      heartbeatCount: state.totalHeartbeats
    };
  }
  
  // 3. 生成反思提示
  const prompt = generateReflectionPrompt(context);
  
  // 4. 写入提示文件
  fs.writeFileSync(REFLECTION_PROMPT_PATH, prompt);
  console.log(`✅ 反思提示已生成: ${REFLECTION_PROMPT_PATH}`);
  
  // 5. 更新状态
  state.lastReflection = Date.now();
  state.totalHeartbeats++;
  state.lastDataHash = currentHash;  // 保存哈希
  state.pendingPrompt = REFLECTION_PROMPT_PATH;
  saveState();
  
  // 6. 输出摘要
  console.log('\n📊 上下文摘要:');
  console.log(`   记忆: ${context.memoryStats.totalMemories} (${context.memoryStats.recentGrowth} 新增)`);
  console.log(`   概念: ${context.memoryStats.totalConcepts}, 联想: ${context.memoryStats.totalAssociations}`);
  console.log(`   元认知问题: ${context.metaQuestions.length} 个`);
  console.log(`   高优先级: ${context.metaQuestions.filter(q => q.priority === 'high').length} 个`);
  
  return {
    promptPath: REFLECTION_PROMPT_PATH,
    context,
    heartbeatCount: state.totalHeartbeats
  };
}

/**
 * 主函数
 */
async function main() {
  loadState();
  
  const args = process.argv.slice(2);
  const action = args[0] || 'check';
  
  switch (action) {
    case 'check':
      if (shouldReflect()) {
        const result = await runReflection();
        // 只有在生成了新提示时才提示
        if (!result.skipped) {
          console.log('\n⚠️  请主 agent 执行: cat ~/.openclaw/workspace/.reflection-prompt.md');
          console.log('然后进行真正的思考，并删除提示文件。\n');
        }
      } else {
        const elapsed = Math.floor((Date.now() - state.lastReflection) / 60000);
        console.log(`⏸️ 距离上次反思 ${elapsed} 分钟，跳过`);
        console.log(`   心跳计数: ${state.totalHeartbeats}`);
        
        // 检查是否有待处理的提示
        if (fs.existsSync(REFLECTION_PROMPT_PATH)) {
          console.log('\n⚠️  有待处理的反思提示，请执行:');
          console.log('   cat ~/.openclaw/workspace/.reflection-prompt.md');
        }
      }
      break;
      
    case 'force':
      const result = await runReflection();
      break;
      
    case 'status':
      console.log('📊 心跳反思状态:');
      console.log(`   总心跳: ${state.totalHeartbeats}`);
      console.log(`   上次反思: ${state.lastReflection ? new Date(state.lastReflection).toLocaleString('zh-CN') : '从未'}`);
      console.log(`   待处理提示: ${fs.existsSync(REFLECTION_PROMPT_PATH) ? '是' : '否'}`);
      break;
      
    case 'clear':
      if (fs.existsSync(REFLECTION_PROMPT_PATH)) {
        fs.unlinkSync(REFLECTION_PROMPT_PATH);
        console.log('✅ 已清除反思提示');
      }
      state.pendingPrompt = null;
      saveState();
      break;
      
    default:
      console.log(`
心跳反思模块 v2

用法:
  node heartbeat_reflect.cjs check   # 检查并生成反思提示（30分钟间隔）
  node heartbeat_reflect.cjs force   # 强制生成反思提示
  node heartbeat_reflect.cjs status  # 查看状态
  node heartbeat_reflect.cjs clear   # 清除待处理提示
      `);
  }
}

main();
