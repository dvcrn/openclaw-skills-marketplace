#!/usr/bin/env node
const { resolveModule } = require('./module_resolver.cjs');
/**
 * Cognitive Brain - 元认知反思模块
 * 分析行为模式，生成洞察
 */

const fs = require('fs');
const path = require('path');

const HOME = process.env.HOME || '/root';
const SKILL_DIR = path.join(HOME, '.openclaw/workspace/skills/cognitive-brain');
const CONFIG_PATH = path.join(SKILL_DIR, 'config.json');
const REFLECTIONS_PATH = path.join(SKILL_DIR, '.reflections.json');

// 反思存储
let reflections = {
  records: [],
  insights: [],
  patterns: []
};

/**
 * 加载反思数据
 */
function load() {
  try {
    if (fs.existsSync(REFLECTIONS_PATH)) {
      reflections = JSON.parse(fs.readFileSync(REFLECTIONS_PATH, 'utf8'));
    }
  } catch (e) {
    reflections = { records: [], insights: [], patterns: [] };
  }
}

/**
 * 保存反思数据 - 增强版（同时保存到数据库）
 */
async function save() {
  try {
    // 保留最近 100 条
    reflections.records = reflections.records.slice(-100);
    fs.writeFileSync(REFLECTIONS_PATH, JSON.stringify(reflections, null, 2));
    
    // 同时保存到数据库
    const lastRecord = reflections.records[reflections.records.length - 1];
    if (lastRecord) {
      await saveToDatabase(lastRecord);
    }
  } catch (e) {
    // ignore
  }
}

/**
 * 保存反思到数据库
 */
async function saveToDatabase(reflection) {
  try {
    const pg = resolveModule('pg');
    const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
    const { Pool } = pg;
    const pool = new Pool(config.storage.primary);
    
    await pool.query(`
      INSERT INTO reflections (id, timestamp, trigger_type, trigger_event, context, analysis, insights, actions)
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
      ON CONFLICT (id) DO NOTHING
    `, [
      reflection.id,
      new Date(reflection.timestamp),
      reflection.trigger,
      reflection.trigger,
      JSON.stringify(reflection.context),
      JSON.stringify(reflection.analysis),
      JSON.stringify(reflection.insights),
      JSON.stringify(reflection.recommendations)
    ]);
    
    await pool.end();
  } catch (e) {
    // 数据库保存失败不影响主流程
    console.error('[reflect] 数据库保存失败:', e.message);
  }
}

/**
 * 反思触发类型
 */
const TRIGGER_TYPES = {
  TASK_FAILURE: {
    name: 'task_failure',
    description: '任务失败',
    priority: 'high'
  },
  TASK_SUCCESS: {
    name: 'task_success',
    description: '任务成功',
    priority: 'medium'
  },
  USER_CORRECTION: {
    name: 'user_correction',
    description: '用户纠正',
    priority: 'high'
  },
  PATTERN_FOUND: {
    name: 'pattern_found',
    description: '发现模式',
    priority: 'medium'
  },
  PERIODIC: {
    name: 'periodic',
    description: '定期反思',
    priority: 'low'
  }
};

/**
 * 执行反思
 */
async function reflect(triggerType, context = {}) {
  load();

  const { v4: uuidv4 } = require('uuid');
  
  const reflection = {
    id: uuidv4(),
    timestamp: Date.now(),
    trigger: triggerType,
    context,
    analysis: {},
    insights: [],
    recommendations: []
  };

  // 根据触发类型进行分析
  switch (triggerType) {
    case 'task_failure':
      reflection.analysis = analyzeFailure(context);
      break;

    case 'task_success':
      reflection.analysis = analyzeSuccess(context);
      break;

    case 'user_correction':
      reflection.analysis = analyzeCorrection(context);
      break;

    case 'pattern_found':
      reflection.analysis = analyzePattern(context);
      break;

    case 'periodic':
      reflection.analysis = await analyzePeriodic();
      break;
  }

  // 生成洞察
  reflection.insights = generateInsights(reflection.analysis);

  // 生成建议
  reflection.recommendations = generateRecommendations(reflection.insights);

  // 保存
  reflections.records.push(reflection);
  await save();

  return reflection;
}

/**
 * 分析失败
 */
function analyzeFailure(context) {
  const analysis = {
    errorType: context.error?.type || 'unknown',
    errorMessage: context.error?.message || '',
    attemptedAction: context.action || '',
    rootCause: null,
    contributingFactors: []
  };

  // 分析根本原因
  if (context.error?.message) {
    if (context.error.message.includes('ECONNREFUSED')) {
      analysis.rootCause = 'network';
      analysis.contributingFactors.push('网络连接问题');
    } else if (context.error.message.includes('ENOENT')) {
      analysis.rootCause = 'resource';
      analysis.contributingFactors.push('资源不存在');
    } else if (context.error.message.includes('permission')) {
      analysis.rootCause = 'permission';
      analysis.contributingFactors.push('权限不足');
    } else {
      analysis.rootCause = 'unknown';
      analysis.contributingFactors.push('未知错误');
    }
  }

  return analysis;
}

/**
 * 分析成功
 */
function analyzeSuccess(context) {
  return {
    action: context.action || '',
    duration: context.duration || 0,
    successFactors: context.factors || [],
    canReplicate: true
  };
}

/**
 * 分析用户纠正
 */
function analyzeCorrection(context) {
  return {
    originalAction: context.originalAction || '',
    correctedAction: context.correctedAction || '',
    whatWasWrong: context.whatWasWrong || '',
    lessonLearned: `用户偏好: ${context.correctedAction}`
  };
}

/**
 * 分析模式
 */
function analyzePattern(context) {
  return {
    pattern: context.pattern || '',
    occurrences: context.occurrences || 0,
    significance: context.significance || 'medium',
    relatedConcepts: context.concepts || []
  };
}

/**
 * 定期分析 - 增强版
 */
async function analyzePeriodic() {
  const analysis = {
    period: 'recent_24h',
    successRate: 0,
    failures: 0,
    successes: 0,
    commonErrors: [],
    // 新增深度分析
    userPatterns: {},
    memoryPatterns: {},
    knowledgeGaps: [],
    metaQuestions: []
  };

  try {
    const pg = require(path.join(SKILL_DIR, 'node_modules/pg'));
    const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
    const { Pool } = pg;
    const pool = new Pool(config.storage.primary);

    // 1. 分析用户交互模式
    const userResult = await pool.query(`
      SELECT 
        type,
        COUNT(*) as count,
        AVG(importance) as avg_importance,
        MAX(timestamp) as last_interaction
      FROM episodes
      WHERE timestamp > NOW() - INTERVAL '24 hours'
      GROUP BY type
      ORDER BY count DESC
    `);

    if (userResult.rows.length > 0) {
      analysis.userPatterns = {
        topTypes: userResult.rows.slice(0, 5).map(r => ({
          type: r.type,
          count: parseInt(r.count),
          avgImportance: parseFloat(r.avg_importance)
        })),
        totalInteractions: userResult.rows.reduce((sum, r) => sum + parseInt(r.count), 0)
      };
    }

    // 2. 分析记忆访问模式
    const accessResult = await pool.query(`
      SELECT 
        EXTRACT(HOUR FROM timestamp) as hour,
        COUNT(*) as count
      FROM episodes
      WHERE timestamp > NOW() - INTERVAL '7 days'
      GROUP BY hour
      ORDER BY count DESC
      LIMIT 5
    `);

    if (accessResult.rows.length > 0) {
      analysis.memoryPatterns = {
        peakHours: accessResult.rows.map(r => ({
          hour: parseInt(r.hour),
          count: parseInt(r.count)
        })),
        suggestion: `用户活跃时段集中在 ${accessResult.rows[0]?.hour || 0}:00 左右，可在此前预热记忆`
      };
    }

    // 3. 分析概念网络
    const conceptResult = await pool.query(`
      SELECT name, access_count 
      FROM concepts 
      ORDER BY access_count DESC 
      LIMIT 10
    `);

    const lowAccessConcepts = conceptResult.rows.filter(r => r.access_count < 2);
    if (lowAccessConcepts.length > 0) {
      analysis.knowledgeGaps = lowAccessConcepts.map(r => r.name);
    }

    // 4. 分析联想网络密度
    const assocResult = await pool.query(`
      SELECT 
        COUNT(DISTINCT from_id) as nodes,
        COUNT(*) as edges,
        AVG(weight) as avg_weight
      FROM associations
    `);

    const networkStats = assocResult.rows[0];
    if (networkStats) {
      const density = networkStats.nodes > 0 
        ? (networkStats.edges / (networkStats.nodes * (networkStats.nodes - 1)))
        : 0;
      
      if (density < 0.1) {
        analysis.metaQuestions.push({
          question: '联想网络密度较低，如何增加概念关联？',
          priority: 'medium',
          suggestion: '可以主动构建更多共现关系，或从知识图谱导入初始关联'
        });
      }
    }

    // 5. 分析用户兴趣变化
    const interestResult = await pool.query(`
      SELECT 
        tag,
        COUNT(*) as count,
        MAX(timestamp) as last_seen
      FROM episodes, jsonb_array_elements_text(tags) as tag
      WHERE timestamp > NOW() - INTERVAL '7 days'
        AND tags IS NOT NULL
        AND jsonb_array_length(tags) > 0
      GROUP BY tag
      ORDER BY count DESC
      LIMIT 10
    `);

    if (interestResult.rows.length > 0) {
      analysis.userPatterns.topInterests = interestResult.rows.map(r => ({
        topic: r.tag,
        count: parseInt(r.count),
        trending: 'stable' // 可以进一步分析趋势
      }));
    }

    // 6. 生成元认知问题
    if (analysis.userPatterns.totalInteractions < 10) {
      analysis.metaQuestions.push({
        question: '用户交互较少，如何提高主动性和价值？',
        priority: 'high',
        suggestion: '可以在心跳时主动提供有用的信息，或提醒用户关注事项'
      });
    }

    await pool.end();
  } catch (e) {
    analysis.error = e.message;
  }

  // 保留原有的成功率分析
  const recent = reflections.records.slice(-20);
  const failures = recent.filter(r => r.trigger === 'task_failure').length;
  const successes = recent.filter(r => r.trigger === 'task_success').length;
  const total = failures + successes;
  analysis.successRate = total > 0 ? successes / total : 0;
  analysis.failures = failures;
  analysis.successes = successes;

  return analysis;
}

/**
 * 生成洞察 - 增强版
 */
function generateInsights(analysis) {
  const insights = [];

  // 基于分析类型生成洞察
  if (analysis.rootCause) {
    insights.push({
      type: 'root_cause',
      content: `根本原因: ${analysis.rootCause}`,
      confidence: 0.8
    });
  }

  if (analysis.contributingFactors) {
    for (const factor of analysis.contributingFactors) {
      insights.push({
        type: 'contributing_factor',
        content: factor,
        confidence: 0.7
      });
    }
  }

  if (analysis.successRate !== undefined) {
    if (analysis.successRate < 0.5) {
      insights.push({
        type: 'performance_warning',
        content: `成功率较低: ${(analysis.successRate * 100).toFixed(1)}%`,
        confidence: 0.9
      });
    } else if (analysis.successRate > 0.8) {
      insights.push({
        type: 'performance_good',
        content: `表现良好，成功率: ${(analysis.successRate * 100).toFixed(1)}%`,
        confidence: 0.9
      });
    }
  }

  if (analysis.lessonLearned) {
    insights.push({
      type: 'lesson',
      content: analysis.lessonLearned,
      confidence: 0.9
    });
  }

  // 新增：基于深度分析的洞察
  
  // 用户交互模式洞察
  if (analysis.userPatterns?.topInterests) {
    const topInterest = analysis.userPatterns.topInterests[0];
    if (topInterest) {
      insights.push({
        type: 'user_interest',
        content: `用户最关注的话题: ${topInterest.topic} (${topInterest.count}次)`,
        confidence: 0.85
      });
    }
  }

  if (analysis.userPatterns?.totalInteractions !== undefined) {
    if (analysis.userPatterns.totalInteractions === 0) {
      insights.push({
        type: 'engagement_low',
        content: '近期无用户交互，考虑主动提供价值',
        confidence: 0.8
      });
    } else if (analysis.userPatterns.totalInteractions > 10) {
      insights.push({
        type: 'engagement_good',
        content: `用户互动活跃，近期${analysis.userPatterns.totalInteractions}次交互`,
        confidence: 0.8
      });
    }
  }

  // 记忆访问模式洞察
  if (analysis.memoryPatterns?.peakHours) {
    const peakHour = analysis.memoryPatterns.peakHours[0];
    if (peakHour) {
      insights.push({
        type: 'activity_pattern',
        content: `用户活跃高峰: ${peakHour.hour}:00 (${peakHour.count}次活动)`,
        confidence: 0.75
      });
    }
  }

  // 知识缺口洞察
  if (analysis.knowledgeGaps?.length > 0) {
    insights.push({
      type: 'knowledge_gap',
      content: `发现${analysis.knowledgeGaps.length}个概念未被充分使用，可能存在知识缺口`,
      confidence: 0.7
    });
  }

  // 元认知问题
  if (analysis.metaQuestions?.length > 0) {
    analysis.metaQuestions.forEach(mq => {
      insights.push({
        type: 'meta_question',
        content: mq.question,
        confidence: 0.6,
        suggestion: mq.suggestion
      });
    });
  }

  return insights;
}

/**
 * 生成建议
 */
function generateRecommendations(insights) {
  const recommendations = [];

  for (const insight of insights) {
    switch (insight.type) {
      case 'root_cause':
        if (insight.content.includes('network')) {
          recommendations.push('建议检查网络连接，或启用离线模式');
        } else if (insight.content.includes('resource')) {
          recommendations.push('建议先检查资源是否存在');
        } else if (insight.content.includes('permission')) {
          recommendations.push('建议请求用户授权或使用替代方案');
        }
        break;

      case 'performance_warning':
        recommendations.push('建议分析失败原因，优化策略');
        break;

      case 'lesson':
        recommendations.push(`记住这个偏好，以后避免类似错误`);
        break;
    }
  }

  return [...new Set(recommendations)];  // 去重
}

/**
 * 获取反思统计
 */
function getStats() {
  load();

  const byTrigger = {};
  for (const r of reflections.records) {
    byTrigger[r.trigger] = (byTrigger[r.trigger] || 0) + 1;
  }

  return {
    total: reflections.records.length,
    byTrigger,
    insights: reflections.insights.length,
    patterns: reflections.patterns.length
  };
}

/**
 * 获取最近洞察
 */
function getRecentInsights(limit = 20) {
  load();

  const insights = [];
  for (const r of reflections.records) {
    if (r.insights) {
      insights.push(...r.insights.map(i => ({
        ...i,
        timestamp: r.timestamp,
        trigger: r.trigger
      })));
    }
  }

  return insights.slice(-limit);
}

/**
 * 从数据库加载并反思
 */
async function reflectFromDB() {
  try {
    const pg = require(path.join(SKILL_DIR, 'node_modules/pg'));
    const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));

    const { Pool } = pg;
    const pool = new Pool(config.storage.primary);

    // 获取最近的 episodes
    const episodes = await pool.query(`
      SELECT * FROM episodes
      WHERE created_at > NOW() - INTERVAL '24 hours'
      ORDER BY created_at DESC
      LIMIT 100
    `);

    await pool.end();

    // 分析
    const failures = episodes.rows.filter(e => e.type === 'error').length;
    const successes = episodes.rows.filter(e => e.type === 'success').length;
    const corrections = episodes.rows.filter(e => e.type === 'correction').length;

    const context = {
      total: episodes.rows.length,
      failures,
      successes,
      corrections
    };

    return reflect('periodic', context);

  } catch (e) {
    console.log('[reflect] 数据库不可用');
    return reflect('periodic', {});
  }
}

// ===== 主函数 =====
async function main() {
  const action = process.argv[2];
  const args = process.argv.slice(3);

  load();

  switch (action) {
    case 'run':
      const trigger = args[0] || 'periodic';
      const result = await reflect(trigger, { note: args.slice(1).join(' ') });
      console.log('🤔 反思结果:');
      console.log(JSON.stringify(result, null, 2));
      break;

    case 'insights':
      const insights = getRecentInsights();
      console.log('💡 最近洞察:');
      insights.forEach((i, idx) => {
        console.log(`   ${idx + 1}. [${i.type}] ${i.content}`);
      });
      break;

    case 'stats':
      console.log(JSON.stringify(getStats(), null, 2));
      break;

    case 'history':
      const recent = reflections.records.slice(-10);
      console.log('📋 最近反思:');
      recent.forEach((r, i) => {
        console.log(`   ${i + 1}. [${r.trigger}] ${r.insights.length} 个洞察`);
      });
      break;

    default:
      console.log(`
元认知反思模块

用法:
  node reflect.cjs run [trigger] [note]   # 执行反思
  node reflect.cjs insights               # 查看洞察
  node reflect.cjs stats                  # 查看统计
  node reflect.cjs history                # 查看历史

触发类型:
  - task_failure: 任务失败
  - task_success: 任务成功
  - user_correction: 用户纠正
  - pattern_found: 发现模式
  - periodic: 定期反思
      `);
  }
}

main();
