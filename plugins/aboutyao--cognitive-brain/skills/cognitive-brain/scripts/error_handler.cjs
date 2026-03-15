#!/usr/bin/env node
/**
 * Cognitive Brain - 错误恢复快捷接口
 * 用于在发生错误时自动处理
 */

const errorRecovery = require('./error_recovery.cjs');

/**
 * 处理错误并返回恢复策略
 */
async function handleError(error, context = {}) {
  // 分类错误
  const classification = errorRecovery.classifyError(error);
  
  console.log(`🔧 错误分类: ${classification.type} (严重性: ${classification.severity})`);
  
  // 获取恢复策略
  const strategies = errorRecovery.getRecoveryStrategies(classification.type);
  
  if (strategies.length === 0) {
    return {
      handled: false,
      reason: '无法自动恢复',
      suggestion: '请手动处理此错误'
    };
  }
  
  // 尝试第一个恢复策略
  const strategy = strategies[0];
  console.log(`📋 尝试恢复策略: ${strategy.description}`);
  
  try {
    if (strategy.action) {
      await strategy.action(context);
    }
    
    return {
      handled: true,
      strategy: strategy.description,
      type: classification.type
    };
  } catch (recoveryError) {
    console.log(`❌ 恢复失败: ${recoveryError.message}`);
    return {
      handled: false,
      reason: recoveryError.message,
      fallbackSuggestion: strategies[1]?.description || '无备用策略'
    };
  }
}

/**
 * 包装函数 - 自动处理错误
 */
async function withRecovery(fn, context = {}) {
  try {
    return await fn();
  } catch (error) {
    const result = await handleError(error, context);
    if (!result.handled) {
      throw error;
    }
    // 重试
    return await fn();
  }
}

/**
 * 导出
 */
module.exports = { handleError, withRecovery };

// 命令行接口
if (require.main === module) {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.log('用法: node error_handler.cjs "错误信息"');
    process.exit(1);
  }
  
  handleError(new Error(args.join(' '))).then(result => {
    console.log(JSON.stringify(result, null, 2));
  });
}
