#!/usr/bin/env node
/**
 * Cognitive Brain - 冲突解决模块
 * 检测和解决信息冲突
 */

const fs = require('fs');
const path = require('path');

const HOME = process.env.HOME || '/root';
const SKILL_DIR = path.join(HOME, '.openclaw/workspace/skills/cognitive-brain');
const CONFLICT_LOG_PATH = path.join(SKILL_DIR, '.conflict-log.json');

// 冲突日志
let conflictLog = [];

/**
 * 加载日志
 */
function load() {
  try {
    if (fs.existsSync(CONFLICT_LOG_PATH)) {
      conflictLog = JSON.parse(fs.readFileSync(CONFLICT_LOG_PATH, 'utf8'));
    }
  } catch (e) {
    conflictLog = [];
  }
}

/**
 * 保存日志
 */
function save() {
  try {
    fs.writeFileSync(CONFLICT_LOG_PATH, JSON.stringify(conflictLog.slice(-200), null, 2));
  } catch (e) {
    // ignore
  }
}

/**
 * 冲突类型
 */
const CONFLICT_TYPES = {
  CONTRADICTION: {
    name: 'contradiction',
    description: '直接矛盾',
    severity: 'high'
  },
  OUTDATED: {
    name: 'outdated',
    description: '信息过时',
    severity: 'medium'
  },
  AMBIGUITY: {
    name: 'ambiguity',
    description: '模糊冲突',
    severity: 'low'
  },
  CONTEXT: {
    name: 'context',
    description: '上下文冲突',
    severity: 'medium'
  }
};

/**
 * 检测冲突
 */
function detectConflict(newInfo, existingMemories) {
  const conflicts = [];

  for (const memory of existingMemories) {
    // 检查实体冲突
    if (newInfo.entity && memory.entity === newInfo.entity) {
      if (newInfo.value !== memory.value) {
        conflicts.push({
          type: CONFLICT_TYPES.CONTRADICTION.name,
          severity: CONFLICT_TYPES.CONTRADICTION.severity,
          entity: newInfo.entity,
          oldValue: memory.value,
          newValue: newInfo.value,
          memoryId: memory.id,
          timestamp: Date.now()
        });
      }
    }

    // 检查时间冲突
    if (newInfo.timestamp && memory.timestamp) {
      if (newInfo.timestamp < memory.timestamp && newInfo.value !== memory.value) {
        conflicts.push({
          type: CONFLICT_TYPES.OUTDATED.name,
          severity: CONFLICT_TYPES.OUTDATED.severity,
          message: '新信息可能已过时',
          oldTimestamp: memory.timestamp,
          newTimestamp: newInfo.timestamp
        });
      }
    }
  }

  return conflicts;
}

/**
 * 解决冲突
 */
function resolveConflict(conflict, strategy = 'ask') {
  const resolution = {
    conflictId: `conf_${Date.now()}`,
    timestamp: Date.now(),
    conflict,
    strategy,
    outcome: null,
    reasoning: []
  };

  switch (strategy) {
    case 'newer_wins':
      // 新信息覆盖旧信息
      resolution.outcome = 'accept_new';
      resolution.reasoning.push('新信息优先');
      break;

    case 'confidence_wins':
      // 根据置信度决定
      if (conflict.newConfidence > conflict.oldConfidence) {
        resolution.outcome = 'accept_new';
        resolution.reasoning.push('新信息置信度更高');
      } else {
        resolution.outcome = 'keep_old';
        resolution.reasoning.push('旧信息置信度更高');
      }
      break;

    case 'merge':
      // 合并信息
      resolution.outcome = 'merged';
      resolution.reasoning.push('合并冲突信息');
      resolution.mergedValue = `${conflict.oldValue} 或 ${conflict.newValue}`;
      break;

    case 'ask':
      // 需要用户确认
      resolution.outcome = 'pending';
      resolution.reasoning.push('需要用户确认');
      resolution.question = `信息冲突：旧值是"${conflict.oldValue}"，新值是"${conflict.newValue}"，哪个是对的？`;
      break;

    default:
      resolution.outcome = 'keep_old';
      resolution.reasoning.push('默认保留旧信息');
  }

  load();
  conflictLog.push(resolution);
  save();

  return resolution;
}

/**
 * 批量检测和解决
 */
function processConflicts(newInfo, existingMemories) {
  const conflicts = detectConflict(newInfo, existingMemories);

  const results = {
    total: conflicts.length,
    high: conflicts.filter(c => c.severity === 'high').length,
    medium: conflicts.filter(c => c.severity === 'medium').length,
    low: conflicts.filter(c => c.severity === 'low').length,
    resolutions: []
  };

  for (const conflict of conflicts) {
    // 根据严重程度选择策略
    let strategy = 'ask';
    if (conflict.severity === 'low') {
      strategy = 'newer_wins';
    } else if (conflict.severity === 'medium') {
      strategy = 'confidence_wins';
    }

    const resolution = resolveConflict(conflict, strategy);
    results.resolutions.push(resolution);
  }

  return results;
}

/**
 * 获取冲突统计
 */
function getStats() {
  load();

  const stats = {
    total: conflictLog.length,
    byType: {},
    byOutcome: {},
    pending: 0
  };

  for (const conf of conflictLog) {
    const type = conf.conflict?.type || 'unknown';
    stats.byType[type] = (stats.byType[type] || 0) + 1;

    const outcome = conf.outcome || 'unknown';
    stats.byOutcome[outcome] = (stats.byOutcome[outcome] || 0) + 1;

    if (conf.outcome === 'pending') {
      stats.pending++;
    }
  }

  return stats;
}

/**
 * 获取待处理冲突
 */
function getPendingConflicts() {
  load();

  return conflictLog.filter(c => c.outcome === 'pending');
}

/**
 * 确认冲突解决方案
 */
function confirmResolution(conflictId, userChoice) {
  load();

  const conf = conflictLog.find(c => c.conflictId === conflictId);
  if (conf) {
    conf.outcome = userChoice; // 'accept_new' | 'keep_old' | 'merged'
    conf.confirmedAt = Date.now();
    conf.confirmedBy = 'user';
    save();
  }

  return conf;
}

// ===== 主函数 =====
async function main() {
  const action = process.argv[2];
  const args = process.argv.slice(3);

  load();

  switch (action) {
    case 'test': {
      const newInfo = { entity: '项目', value: 'Alpha', timestamp: Date.now() };
      const existing = [
        { id: 'mem_1', entity: '项目', value: 'Beta', timestamp: Date.now() - 86400000 }
      ];

      const result = processConflicts(newInfo, existing);
      console.log('🔍 冲突检测结果:');
      console.log(JSON.stringify(result, null, 2));
      break;
    }

    case 'stats':
      console.log('📊 冲突统计:');
      console.log(JSON.stringify(getStats(), null, 2));
      break;

    case 'pending':
      console.log('📋 待处理冲突:');
      console.log(JSON.stringify(getPendingConflicts(), null, 2));
      break;

    default:
      console.log(`
冲突解决模块

用法:
  node conflict_resolution.cjs test     # 测试冲突检测
  node conflict_resolution.cjs stats    # 查看统计
  node conflict_resolution.cjs pending  # 查看待处理
      `);
  }
}

main();
