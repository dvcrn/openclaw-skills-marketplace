#!/usr/bin/env node
/**
 * Cognitive Brain - 意图识别快捷接口
 */

const intent = require('./intent.cjs');

function recognizeIntent(text) {
  return intent.recognize(text);
}

module.exports = { recognizeIntent };

if (require.main === module) {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.log('用法: node intent_helper.cjs "文本"');
    process.exit(1);
  }
  const result = recognizeIntent(args.join(' '));
  console.log(JSON.stringify(result, null, 2));
}
