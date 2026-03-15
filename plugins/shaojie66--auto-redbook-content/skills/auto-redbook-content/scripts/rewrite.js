#!/usr/bin/env node

/**
 * AI 改写模块
 * 支持两种模式：
 * - direct: 直接调用 AI API（需要在 OpenClaw agent 环境中运行）
 * - agent: 通过 sessions_spawn 调用其他 agent
 */

const path = require('path');

// 加载环境变量
require('dotenv').config({ path: path.join(__dirname, '../.env') });

const REWRITE_MODE = process.env.REWRITE_MODE || 'direct';

/**
 * 模式 A：通过 OpenClaw agent 调用 AI
 * 注意：此模式需要在 OpenClaw agent 环境中运行
 */
async function rewriteWithDirectAI(note) {
  // 构建提示词
  const imageInfo = note.image_analysis && note.image_analysis.length > 0
    ? `\n\n图片分析结果：\n${note.image_analysis.map((desc, i) => 
        `图片 ${i + 1}: ${desc}`
      ).join('\n')}`
    : '';

  const ocrInfo = note.ocr_text && note.ocr_text.length > 0
    ? `\n\n图片文字内容：\n${note.ocr_text.join('\n')}`
    : '';

  const prompt = `请帮我改写以下小红书笔记，要求：
1. 保持原意，但用不同的表达方式
2. 风格轻松活泼，适合年轻人阅读
3. 标题控制在 30 字以内，正文控制在 500 字以内
4. 使用 emoji 增加趣味性
5. 参考图片分析结果（如有），确保内容与图片一致
6. 提取 3-5 个相关标签

原标题：${note.original_title}
原内容：${note.original_content}${imageInfo}${ocrInfo}

请以 JSON 格式返回，包含以下字段：
{
  "title": "改写后的标题",
  "content": "改写后的正文",
  "tags": ["标签1", "标签2", "标签3"]
}`;

  console.log('[改写] Direct 模式需要在 OpenClaw agent 环境中运行');
  console.log('[改写] 提示词:', prompt.substring(0, 200) + '...');
  
  // 在实际使用中，这里应该通过 OpenClaw 的工具调用 AI
  // 例如使用 oracle 或其他 AI 工具
  throw new Error('Direct 模式需要在 OpenClaw agent 环境中通过 AI 工具调用');
}

/**
 * 模式 B：通过 sessions_spawn 调用其他 agent
 * 注意：此函数需要在 OpenClaw agent 环境中运行
 */
async function rewriteWithAgent(note) {
  const AGENT_ID = process.env.AGENT_ID || 'libu';

  const imageInfo = note.image_analysis && note.image_analysis.length > 0
    ? `\n\n图片分析结果：\n${note.image_analysis.map((desc, i) => 
        `图片 ${i + 1}: ${desc}`
      ).join('\n')}`
    : '';

  const ocrInfo = note.ocr_text && note.ocr_text.length > 0
    ? `\n\n图片文字内容：\n${note.ocr_text.join('\n')}`
    : '';

  const task = `请帮我改写以下小红书笔记，要求：
1. 保持原意，但用不同的表达方式
2. 风格轻松活泼，适合年轻人阅读
3. 标题控制在 30 字以内，正文控制在 500 字以内
4. 使用 emoji 增加趣味性
5. 参考图片分析结果（如有），确保内容与图片一致
6. 提取 3-5 个相关标签

原标题：${note.original_title}
原内容：${note.original_content}${imageInfo}${ocrInfo}

请以 JSON 格式返回，包含以下字段：
{
  "title": "改写后的标题",
  "content": "改写后的正文",
  "tags": ["标签1", "标签2", "标签3"]
}`;

  console.log(`[改写] Agent 模式: 调用 ${AGENT_ID}`);
  console.log(`[改写] 任务: ${task.substring(0, 100)}...`);
  
  // 注意：这里只是示例，实际需要通过 OpenClaw 的 sessions_spawn 工具调用
  // 在 SKILL.md 中会有完整的调用示例
  throw new Error('Agent 模式需要在 OpenClaw agent 环境中通过 sessions_spawn 调用');
}

/**
 * 统一改写接口
 */
async function rewriteNote(note) {
  console.log(`[改写] 模式: ${REWRITE_MODE}`);
  
  if (REWRITE_MODE === 'direct') {
    return await rewriteWithDirectAI(note);
  } else if (REWRITE_MODE === 'agent') {
    return await rewriteWithAgent(note);
  } else {
    throw new Error(`不支持的 REWRITE_MODE: ${REWRITE_MODE}`);
  }
}

module.exports = { 
  rewriteNote, 
  rewriteWithDirectAI, 
  rewriteWithAgent,
  rewriteByLibu: rewriteNote  // 别名，兼容 run.js
};

// 如果直接运行此脚本（用于测试）
if (require.main === module) {
  const testNote = {
    original_title: 'AI绘画新手入门指南｜零基础也能画出大片',
    original_content: '最近迷上了AI绘画，从完全不会到现在能画出自己满意的作品...',
    image_analysis: [],
    ocr_text: [],
  };

  rewriteNote(testNote)
    .then(result => {
      console.log('\n[改写结果]');
      console.log(JSON.stringify(result, null, 2));
    })
    .catch(error => {
      console.error('[改写失败]', error.message);
      process.exit(1);
    });
}
