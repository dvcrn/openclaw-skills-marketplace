#!/usr/bin/env node
/**
 * Cognitive Brain - 安全检查快捷接口
 * 用于在关键操作前进行安全检查
 */

const safety = require('./safety.cjs');

/**
 * 检查操作是否安全
 */
function isOperationSafe(operation, context = {}) {
  // 加载安全模块
  const result = safety.checkSafety(operation, context);
  
  if (result.safe === false) {
    console.log('⚠️ 安全检查未通过:', result.reason);
    return { safe: false, reason: result.reason, severity: result.severity };
  }
  
  return { safe: true };
}

/**
 * 导出
 */
module.exports = { isOperationSafe };

// 命令行接口
if (require.main === module) {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.log('用法: node safety_check.cjs "操作内容"');
    process.exit(1);
  }
  
  const result = isOperationSafe(args.join(' '));
  console.log(JSON.stringify(result, null, 2));
}
