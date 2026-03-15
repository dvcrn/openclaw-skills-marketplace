#!/usr/bin/env node

/**
 * 写入飞书多维表格
 * 使用 OpenClaw feishu_bitable_create_record
 */

const { spawnSync } = require('child_process');
const path = require('path');

// 使用 dotenv 加载环境变量
require('dotenv').config({ path: path.join(__dirname, '..', '.env') });

/**
 * 构建飞书表格字段
 */
function buildFields(note, rewritten) {
  const fields = {
    '原标题': note.original_title,
    '原文链接': {
      text: note.original_title,
      link: note.url || '',
    },
    '作者': note.author || '',
    '点赞数': note.likes || 0,
    '抓取时间': Date.now(),
    '状态': '待审核',
  };
  
  if (rewritten) {
    fields['改写后标题'] = rewritten.title;
    fields['改写后正文'] = rewritten.content;
    fields['提取标签'] = rewritten.tags.join(', ');
  }
  
  return fields;
}

/**
 * 写入飞书表格
 * @param {Object} note - 原始笔记
 * @param {Object} rewritten - 改写结果
 * @returns {Promise<string>} record_id
 */
async function writeToFeishu(note, rewritten) {
  console.log(`[飞书] 写入表格: ${note.original_title}`);
  
  try {
    const appToken = process.env.FEISHU_APP_TOKEN;
    const tableId = process.env.FEISHU_TABLE_ID;
    
    if (!appToken || !tableId) {
      throw new Error('飞书配置缺失: FEISHU_APP_TOKEN 或 FEISHU_TABLE_ID');
    }
    
    // 验证 token 和 table_id 格式
    if (!/^(bascn|cli)_[a-zA-Z0-9_-]+$/.test(appToken)) {
      throw new Error('FEISHU_APP_TOKEN 格式无效');
    }
    
    if (!/^tbl[a-zA-Z0-9]+$/.test(tableId)) {
      throw new Error('FEISHU_TABLE_ID 格式无效');
    }
    
    const fields = buildFields(note, rewritten);
    const fieldsJson = JSON.stringify(fields);
    
    const result = spawnSync('openclaw', [
      'feishu-bitable',
      'create-record',
      '--app-token',
      appToken,
      '--table-id',
      tableId,
      '--fields',
      fieldsJson
    ], {
      encoding: 'utf-8',
      stdio: ['pipe', 'pipe', 'pipe'],
      timeout: 30000
    });
    
    if (result.error) {
      throw result.error;
    }
    
    if (result.status !== 0) {
      throw new Error(result.stderr || '飞书写入失败');
    }
    
    const response = result.stdout;
    
    // 提取 record_id
    const match = response.match(/record_id["\s:]+([a-zA-Z0-9_-]+)/);
    if (!match) {
      throw new Error('未能从响应中提取 record_id');
    }
    
    const recordId = match[1];
    console.log(`[飞书] 成功写入，record_id: ${recordId}`);
    return recordId;
    
  } catch (error) {
    console.error(`[飞书] 写入失败:`, error.message);
    throw error;
  }
}

module.exports = { writeToFeishu };

// 如果直接运行此脚本
if (require.main === module) {
  const testNote = {
    original_title: '测试标题',
    url: 'https://www.xiaohongshu.com/explore/test',
    author: '测试作者',
    likes: 100,
  };
  
  const testRewritten = {
    title: '改写后的标题',
    content: '改写后的正文',
    tags: ['标签1', '标签2'],
  };
  
  writeToFeishu(testNote, testRewritten)
    .then(recordId => {
      console.log(`Record ID: ${recordId}`);
    })
    .catch(error => {
      console.error(error);
      process.exit(1);
    });
}
