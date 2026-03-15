#!/usr/bin/env node
/**
 * Cognitive Brain - 错误恢复模块
 * 处理错误并提供恢复策略
 */

const fs = require('fs');
const path = require('path');

const HOME = process.env.HOME || '/root';
const SKILL_DIR = path.join(HOME, '.openclaw/workspace/skills/cognitive-brain');
const ERROR_LOG_PATH = path.join(SKILL_DIR, '.error-log.json');

// 错误类型分类
const ERROR_TYPES = {
  NETWORK: {
    name: 'network',
    patterns: [
      /ECONNREFUSED/,
      /ETIMEDOUT/,
      /ENOTFOUND/,
      /network/i,
      /网络/
    ],
    severity: 'medium',
    recoverable: true
  },

  DATABASE: {
    name: 'database',
    patterns: [
      /ECONNREFUSED.*5432/,
      /relation.*does not exist/,
      /数据库/,
      /connection refused/
    ],
    severity: 'high',
    recoverable: true
  },

  PERMISSION: {
    name: 'permission',
    patterns: [
      /EACCES/,
      /EPERM/,
      /permission denied/i,
      /权限/
    ],
    severity: 'high',
    recoverable: false
  },

  RESOURCE: {
    name: 'resource',
    patterns: [
      /ENOENT/,
      /not found/i,
      /不存在/,
      /找不到/
    ],
    severity: 'medium',
    recoverable: true
  },

  VALIDATION: {
    name: 'validation',
    patterns: [
      /invalid/i,
      /validation/i,
      /无效/,
      /格式错误/
    ],
    severity: 'low',
    recoverable: true
  },

  TIMEOUT: {
    name: 'timeout',
    patterns: [
      /ETIMEDOUT/,
      /timeout/i,
      /超时/
    ],
    severity: 'medium',
    recoverable: true
  },

  RATE_LIMIT: {
    name: 'rate_limit',
    patterns: [
      /429/,
      /rate limit/i,
      /too many/i,
      /频率/
    ],
    severity: 'medium',
    recoverable: true
  },

  UNKNOWN: {
    name: 'unknown',
    patterns: [],
    severity: 'high',
    recoverable: false
  }
};

// 恢复策略
const RECOVERY_STRATEGIES = {
  network: [
    { name: 'retry', description: '重试操作', delay: 1000, maxRetries: 3 },
    { name: 'fallback_cache', description: '使用缓存数据', requires: 'cache' },
    { name: 'offline_mode', description: '切换离线模式', requires: 'offline_support' }
  ],

  database: [
    { name: 'reconnect', description: '重新连接数据库', delay: 2000, maxRetries: 3 },
    { name: 'fallback_file', description: '降级到文件存储', requires: 'file_storage' },
    { name: 'queue_operation', description: '排队等待恢复', requires: 'queue' }
  ],

  permission: [
    { name: 'request_permission', description: '请求用户授权' },
    { name: 'alternative_path', description: '尝试替代路径', requires: 'alternative' }
  ],

  resource: [
    { name: 'create_missing', description: '创建缺失资源', requires: 'create_capability' },
    { name: 'suggest_alternative', description: '建议替代资源' }
  ],

  validation: [
    { name: 'correct_input', description: '修正输入并重试' },
    { name: 'request_clarification', description: '请求用户澄清' }
  ],

  timeout: [
    { name: 'increase_timeout', description: '增加超时时间' },
    { name: 'retry', description: '重试操作', delay: 2000, maxRetries: 2 }
  ],

  rate_limit: [
    { name: 'wait_and_retry', description: '等待后重试', delay: 60000 },
    { name: 'reduce_frequency', description: '降低请求频率' }
  ],

  unknown: [
    { name: 'report_to_user', description: '报告给用户' },
    { name: 'log_for_analysis', description: '记录用于分析' }
  ]
};

// 错误日志
let errorLog = [];

/**
 * 加载错误日志
 */
function loadErrorLog() {
  try {
    if (fs.existsSync(ERROR_LOG_PATH)) {
      errorLog = JSON.parse(fs.readFileSync(ERROR_LOG_PATH, 'utf8'));
    }
  } catch (e) {
    errorLog = [];
  }
}

/**
 * 保存错误日志
 */
function saveErrorLog() {
  try {
    // 只保留最近 500 条
    errorLog = errorLog.slice(-500);
    fs.writeFileSync(ERROR_LOG_PATH, JSON.stringify(errorLog, null, 2));
  } catch (e) {
    // ignore
  }
}

/**
 * 分类错误
 */
function classifyError(error) {
  const message = error.message || String(error);

  for (const [key, type] of Object.entries(ERROR_TYPES)) {
    if (key === 'UNKNOWN') continue;

    for (const pattern of type.patterns) {
      if (pattern.test(message)) {
        return {
          type: type.name,
          severity: type.severity,
          recoverable: type.recoverable,
          matchedPattern: pattern.toString()
        };
      }
    }
  }

  return {
    type: 'unknown',
    severity: 'high',
    recoverable: false
  };
}

/**
 * 获取恢复策略
 */
function getRecoveryStrategies(errorType) {
  return RECOVERY_STRATEGIES[errorType] || RECOVERY_STRATEGIES.unknown;
}

/**
 * 记录错误
 */
function logError(error, context = {}) {
  loadErrorLog();

  const classified = classifyError(error);

  const record = {
    id: `err_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    timestamp: Date.now(),
    message: error.message || String(error),
    stack: error.stack,
    ...classified,
    context,
    resolved: false,
    recoveryAttempts: []
  };

  errorLog.push(record);
  saveErrorLog();

  return record;
}

/**
 * 记录恢复尝试
 */
function logRecoveryAttempt(errorId, strategy, result) {
  loadErrorLog();

  const record = errorLog.find(e => e.id === errorId);
  if (record) {
    record.recoveryAttempts.push({
      strategy: strategy.name,
      timestamp: Date.now(),
      result // 'success', 'failed', 'skipped'
    });

    if (result === 'success') {
      record.resolved = true;
      record.resolvedAt = Date.now();
    }

    saveErrorLog();
  }
}

/**
 * 执行恢复
 */
async function executeRecovery(error, context = {}) {
  const classified = classifyError(error);
  const strategies = getRecoveryStrategies(classified.type);

  console.log(`\n🔧 错误类型: ${classified.type}`);
  console.log(`⚠️  严重程度: ${classified.severity}`);
  console.log(`🔄 可恢复: ${classified.recoverable ? '是' : '否'}`);

  if (!classified.recoverable) {
    console.log('\n❌ 此错误不可自动恢复');
    return { success: false, reason: 'non_recoverable' };
  }

  console.log('\n📋 可用恢复策略:');
  strategies.forEach((s, i) => {
    console.log(`   ${i + 1}. ${s.name}: ${s.description}`);
  });

  // 按顺序尝试恢复策略
  for (const strategy of strategies) {
    console.log(`\n⏳ 尝试策略: ${strategy.name}`);

    try {
      const result = await executeStrategy(strategy, error, context);

      if (result.success) {
        console.log(`✅ 恢复成功: ${strategy.name}`);
        return { success: true, strategy: strategy.name, result };
      } else {
        console.log(`❌ 策略失败: ${strategy.name} - ${result.reason}`);
      }
    } catch (e) {
      console.log(`❌ 策略异常: ${strategy.name} - ${e.message}`);
    }

    // 延迟后尝试下一个策略
    if (strategy.delay) {
      await new Promise(resolve => setTimeout(resolve, strategy.delay));
    }
  }

  return { success: false, reason: 'all_strategies_failed' };
}

/**
 * 执行单个策略
 */
async function executeStrategy(strategy, error, context) {
  switch (strategy.name) {
    case 'retry':
      if (context.retryCount >= (strategy.maxRetries || 3)) {
        return { success: false, reason: 'max_retries_exceeded' };
      }
      return { success: true, action: 'retry', delay: strategy.delay || 1000 };

    case 'reconnect':
      console.log('   尝试重新连接...');
      // 实际重连逻辑需要外部提供
      return { success: true, action: 'reconnect' };

    case 'fallback_file':
      console.log('   降级到文件存储...');
      return { success: true, action: 'use_file_storage' };

    case 'wait_and_retry':
      console.log(`   等待 ${strategy.delay / 1000} 秒后重试...`);
      return { success: true, action: 'wait_and_retry', delay: strategy.delay };

    case 'request_clarification':
      return { success: true, action: 'ask_user', message: '需要更多信息来处理此问题' };

    case 'report_to_user':
      return { success: true, action: 'report', message: error.message };

    default:
      return { success: false, reason: 'strategy_not_implemented' };
  }
}

/**
 * 获取错误统计
 */
function getErrorStats() {
  loadErrorLog();

  const stats = {
    total: errorLog.length,
    byType: {},
    bySeverity: {},
    recentUnresolved: 0
  };

  const oneHourAgo = Date.now() - 60 * 60 * 1000;

  for (const error of errorLog) {
    // 按类型统计
    stats.byType[error.type] = (stats.byType[error.type] || 0) + 1;

    // 按严重程度统计
    stats.bySeverity[error.severity] = (stats.bySeverity[error.severity] || 0) + 1;

    // 最近未解决
    if (!error.resolved && error.timestamp > oneHourAgo) {
      stats.recentUnresolved++;
    }
  }

  return stats;
}

// ===== 主函数 =====
async function main() {
  const action = process.argv[2];
  const args = process.argv.slice(3);

  switch (action) {
    case 'stats':
      console.log('📊 错误统计:');
      console.log(JSON.stringify(getErrorStats(), null, 2));
      break;

    case 'recent':
      loadErrorLog();
      const recent = errorLog.slice(-10);
      console.log('📋 最近错误:');
      recent.forEach((e, i) => {
        console.log(`   ${i + 1}. [${e.type}] ${e.message.slice(0, 50)}...`);
        console.log(`      状态: ${e.resolved ? '已解决' : '未解决'}`);
      });
      break;

    case 'test':
      const testError = new Error(args.join(' ') || 'ECONNREFUSED connection failed');
      const classified = classifyError(testError);
      console.log('🧪 测试错误分类:');
      console.log(JSON.stringify(classified, null, 2));
      console.log('\n📋 恢复策略:');
      console.log(JSON.stringify(getRecoveryStrategies(classified.type), null, 2));
      break;

    default:
      console.log(`
错误恢复模块

用法:
  node error_recovery.cjs stats       # 查看错误统计
  node error_recovery.cjs recent      # 查看最近错误
  node error_recovery.cjs test [msg]  # 测试错误分类

示例:
  node error_recovery.cjs test "ECONNREFUSED"
  node error_recovery.cjs test "数据库连接失败"
      `);
  }
}

main();
