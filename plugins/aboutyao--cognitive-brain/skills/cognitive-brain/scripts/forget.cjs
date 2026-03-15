#!/usr/bin/env node
const { resolveModule } = require('./module_resolver.cjs');
/**
 * Cognitive Brain - 遗忘模块
 * 实现记忆衰减和清理机制
 */

const fs = require('fs');
const path = require('path');

const HOME = process.env.HOME || '/root';
const SKILL_DIR = path.join(HOME, '.openclaw/workspace/skills/cognitive-brain');
const CONFIG_PATH = path.join(SKILL_DIR, 'config.json');
const FORGET_LOG_PATH = path.join(SKILL_DIR, '.forget-log.json');

// 遗忘配置
const DEFAULT_CONFIG = {
  enabled: true,
  schedule: '0 3 * * *',  // 每天凌晨 3 点
  retentionDays: {
    high: 365,     // 高重要性
    medium: 30,    // 中等重要性
    low: 7         // 低重要性
  },
  minImportance: 0.1,
  batchSize: 100
};

// 遗忘日志
let forgetLog = [];

/**
 * 加载配置
 */
function loadConfig() {
  try {
    if (fs.existsSync(CONFIG_PATH)) {
      const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
      return { ...DEFAULT_CONFIG, ...config.forgetting };
    }
  } catch (e) {
    // ignore
  }
  return DEFAULT_CONFIG;
}

/**
 * 加载日志
 */
function loadLog() {
  try {
    if (fs.existsSync(FORGET_LOG_PATH)) {
      forgetLog = JSON.parse(fs.readFileSync(FORGET_LOG_PATH, 'utf8'));
    }
  } catch (e) {
    forgetLog = [];
  }
}

/**
 * 保存日志
 */
function saveLog() {
  try {
    forgetLog = forgetLog.slice(-100);
    fs.writeFileSync(FORGET_LOG_PATH, JSON.stringify(forgetLog, null, 2));
  } catch (e) {
    // ignore
  }
}

/**
 * 计算遗忘曲线
 * 艾宾浩斯遗忘曲线: R = e^(-t/S)
 * R = 保留率, t = 时间, S = 记忆强度
 */
function calculateRetention(importance, ageMs) {
  // 根据重要性确定记忆强度（天数转毫秒）
  const config = loadConfig();
  let strengthDays;

  if (importance >= 0.8) {
    strengthDays = config.retentionDays.high;
  } else if (importance >= 0.5) {
    strengthDays = config.retentionDays.medium;
  } else {
    strengthDays = config.retentionDays.low;
  }

  const strengthMs = strengthDays * 24 * 60 * 60 * 1000;
  const retention = Math.exp(-ageMs / strengthMs);

  return retention;
}

/**
 * 判断是否应该遗忘
 */
function shouldForget(memory, config) {
  const ageMs = Date.now() - new Date(memory.timestamp || memory.created_at).getTime();
  
  // 特殊处理 test 类型记忆：快速遗忘（1天）
  if (memory.type === 'test') {
    const testRetentionDays = 1; // 1天后遗忘
    const testStrengthMs = testRetentionDays * 24 * 60 * 60 * 1000;
    const retention = Math.exp(-ageMs / testStrengthMs);
    return retention < 0.3; // 保留率低于30%就遗忘
  }
  
  // 普通记忆的遗忘逻辑
  const importance = memory.importance || 0.5;
  
  // 如果重要性低于阈值，直接遗忘
  if (importance < config.minImportance) {
    return true;
  }
  
  // 计算保留率
  const retention = calculateRetention(importance, ageMs);
  
  // 保留率低于30%时遗忘
  return retention < 0.3;
}

/**
 * 执行遗忘
 */
async function forget(config = null) {
  config = config || loadConfig();

  if (!config.enabled) {
    console.log('[forget] 遗忘功能已禁用');
    return { enabled: false };
  }

  loadLog();

  const result = {
    timestamp: Date.now(),
    forgotten: 0,
    retained: 0,
    errors: 0,
    details: []
  };

  try {
    const pg = require(path.join(SKILL_DIR, 'node_modules/pg'));
    const dbConfig = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));

    const { Pool } = pg;
    const pool = new Pool(dbConfig.storage.primary);

    // 获取所有记忆
    const memories = await pool.query(`
      SELECT id, summary, importance, timestamp, created_at, access_count
      FROM episodes
      ORDER BY importance ASC, timestamp ASC
      LIMIT $1
    `, [config.batchSize * 10]);

    const toDelete = [];
    const toRetain = [];

    // 评估每条记忆
    for (const memory of memories.rows) {
      const evaluation = shouldForget(memory, config);

      if (evaluation.shouldForget) {
        toDelete.push(memory.id);
        result.details.push({
          id: memory.id,
          summary: memory.summary?.slice(0, 50),
          retention: evaluation.retention,
          importance: memory.importance
        });
      } else {
        toRetain.push(memory.id);
      }
    }

    // 执行删除
    if (toDelete.length > 0) {
      await pool.query(`
        DELETE FROM episodes
        WHERE id = ANY($1)
      `, [toDelete]);

      result.forgotten = toDelete.length;
    }

    result.retained = toRetain.length;

    await pool.end();

  } catch (e) {
    console.error('[forget] 数据库错误:', e.message);
    result.errors++;
    result.error = e.message;
  }

  // 记录日志
  forgetLog.push(result);
  saveLog();

  console.log(`[forget] 完成: 遗忘 ${result.forgotten} 条，保留 ${result.retained} 条`);

  return result;
}

/**
 * 软遗忘（降低重要性而不是删除）
 */
async function softForget(config = null) {
  config = config || loadConfig();

  const result = {
    timestamp: Date.now(),
    decayed: 0,
    errors: 0
  };

  try {
    const pg = require(path.join(SKILL_DIR, 'node_modules/pg'));
    const dbConfig = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));

    const { Pool } = pg;
    const pool = new Pool(dbConfig.storage.primary);

    // 衰减所有记忆的重要性
    const decayFactor = 0.95;

    await pool.query(`
      UPDATE episodes
      SET importance = importance * $1
      WHERE importance > $2
    `, [decayFactor, config.minImportance]);

    const updated = await pool.query(`
      SELECT COUNT(*) as count
      FROM episodes
      WHERE importance > $1
    `, [config.minImportance]);

    result.decayed = parseInt(updated.rows[0].count);
    await pool.end();

  } catch (e) {
    console.error('[forget] 软遗忘错误:', e.message);
    result.errors++;
  }

  return result;
}

/**
 * 强化记忆
 */
async function strengthenMemory(memoryId, factor = 1.2) {
  try {
    const pg = require(path.join(SKILL_DIR, 'node_modules/pg'));
    const dbConfig = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));

    const { Pool } = pg;
    const pool = new Pool(dbConfig.storage.primary);

    await pool.query(`
      UPDATE episodes
      SET 
        importance = LEAST(1.0, importance * $1),
        access_count = access_count + 1,
        last_accessed = NOW()
      WHERE id = $2
    `, [factor, memoryId]);

    await pool.end();

    return { success: true, memoryId, factor };

  } catch (e) {
    return { success: false, error: e.message };
  }
}

/**
 * 获取遗忘统计
 */
function getStats() {
  loadLog();

  const stats = {
    totalRuns: forgetLog.length,
    totalForgotten: forgetLog.reduce((sum, l) => sum + (l.forgotten || 0), 0),
    totalRetained: forgetLog.reduce((sum, l) => sum + (l.retained || 0), 0),
    lastRun: forgetLog.length > 0 ? forgetLog[forgetLog.length - 1] : null
  };

  return stats;
}

/**
 * 预览将被遗忘的记忆
 */
async function preview(config = null) {
  config = config || loadConfig();

  const preview = {
    willForget: [],
    willRetain: [],
    stats: { total: 0, toForget: 0, toRetain: 0 }
  };

  try {
    const pg = require(path.join(SKILL_DIR, 'node_modules/pg'));
    const dbConfig = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));

    const { Pool } = pg;
    const pool = new Pool(dbConfig.storage.primary);

    const memories = await pool.query(`
      SELECT id, summary, importance, timestamp, created_at, access_count
      FROM episodes
      ORDER BY importance ASC
      LIMIT 100
    `);

    preview.stats.total = memories.rows.length;

    for (const memory of memories.rows) {
      const evaluation = shouldForget(memory, config);

      if (evaluation.shouldForget) {
        preview.willForget.push({
          id: memory.id,
          summary: memory.summary?.slice(0, 50),
          importance: memory.importance,
          retention: evaluation.retention
        });
      } else {
        preview.willRetain.push({
          id: memory.id,
          summary: memory.summary?.slice(0, 50),
          importance: memory.importance,
          retention: evaluation.retention
        });
      }
    }

    preview.stats.toForget = preview.willForget.length;
    preview.stats.toRetain = preview.willRetain.length;

    await pool.end();

  } catch (e) {
    preview.error = e.message;
  }

  return preview;
}

// ===== 主函数 =====
async function main() {
  const action = process.argv[2];
  const args = process.argv.slice(3);

  switch (action) {
    case 'run':
      const result = await forget();
      console.log('🗑️ 遗忘完成:');
      console.log(`   遗忘: ${result.forgotten} 条`);
      console.log(`   保留: ${result.retained} 条`);
      break;

    case 'soft':
      const softResult = await softForget();
      console.log('📉 软遗忘完成:');
      console.log(JSON.stringify(softResult, null, 2));
      break;

    case 'preview':
      const previewResult = await preview();
      console.log('👀 预览结果:');
      console.log(`   总计: ${previewResult.stats.total}`);
      console.log(`   将遗忘: ${previewResult.stats.toForget}`);
      console.log(`   将保留: ${previewResult.stats.toRetain}`);
      if (previewResult.willForget.length > 0) {
        console.log('\n   将被遗忘的记忆:');
        previewResult.willForget.slice(0, 5).forEach(m => {
          console.log(`     - ${m.summary} (重要性: ${m.importance?.toFixed(2)})`);
        });
      }
      break;

    case 'stats':
      console.log('📊 遗忘统计:');
      console.log(JSON.stringify(getStats(), null, 2));
      break;

    case 'strengthen':
      if (args[0]) {
        const result = await strengthenMemory(args[0], parseFloat(args[1]) || 1.2);
        console.log('💪 强化结果:', result);
      }
      break;

    default:
      console.log(`
遗忘模块

用法:
  node forget.cjs run              # 执行遗忘
  node forget.cjs soft             # 软遗忘（降低重要性）
  node forget.cjs preview          # 预览将被遗忘的记忆
  node forget.cjs stats            # 查看统计
  node forget.cjs strengthen <id> [factor]  # 强化记忆

遗忘条件:
  - 重要性 < 0.1 且超过 7 天未访问
  - 保留率 < 10% 且从未被访问

保留率计算:
  高重要性 (≥0.8): 365 天
  中重要性 (0.5-0.8): 30 天
  低重要性 (<0.5): 7 天
      `);
  }
}

main();
