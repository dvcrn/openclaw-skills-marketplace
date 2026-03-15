#!/usr/bin/env node
/**
 * Cognitive Brain - 对话管理快捷接口
 */

const dialogue = require('./dialogue.cjs');

/**
 * 开始新对话
 */
function startDialogue(context = {}) {
  return dialogue.startDialogue(context);
}

/**
 * 处理对话轮次
 */
function processTurn(userInput, response) {
  return dialogue.processTurn(userInput, response);
}

/**
 * 获取对话上下文
 */
function getContext() {
  return dialogue.getDialogueContext();
}

/**
 * 检测话题切换
 */
function detectTopicChange(currentInput) {
  const context = getContext();
  if (!context || !context.current?.topic) return false;
  
  // 简单检测：关键词变化
  const prevTopic = context.current.topic;
  const keywords = currentInput.toLowerCase().split(/\s+/);
  
  // 如果新输入与之前话题无关
  const related = keywords.some(k => prevTopic.toLowerCase().includes(k));
  return !related && keywords.length > 2;
}

module.exports = { startDialogue, processTurn, getContext, detectTopicChange };

// 命令行接口
if (require.main === module) {
  const args = process.argv.slice(2);
  const action = args[0] || 'context';
  
  if (action === 'start') {
    const result = startDialogue({ topic: args[1] || 'general' });
    console.log(JSON.stringify(result, null, 2));
  } else if (action === 'context') {
    const result = getContext();
    console.log(JSON.stringify(result, null, 2));
  } else {
    console.log('用法: node dialogue_helper.cjs [start|context] [topic]');
  }
}
