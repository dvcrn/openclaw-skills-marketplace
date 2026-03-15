#!/usr/bin/env node

/**
 * 主执行脚本
 * 编排完整流程：抓取 → 改写 → 写入飞书
 */

const { fetchNotes } = require('./fetch');
const { rewriteByLibu } = require('./rewrite');
const { writeToFeishu } = require('./write-feishu');
const path = require('path');

// 使用 dotenv 加载环境变量
require('dotenv').config({ path: path.join(__dirname, '..', '.env') });

/**
 * 加载配置
 */
function loadConfig() {
  return {
    maxResults: parseInt(process.env.XHS_MAX_RESULTS || '3'),
    appToken: process.env.FEISHU_APP_TOKEN,
    tableId: process.env.FEISHU_TABLE_ID,
  };
}

/**
 * 主流程
 */
async function main() {
  const startTime = Date.now();
  console.log('========================================');
  console.log('开始执行 auto-redbook-content 流程');
  console.log('========================================\n');
  
  try {
    // 加载配置
    const config = loadConfig();
    console.log(`配置: 抓取数量 ${config.maxResults}\n`);
    
    // 1. 抓取笔记
    console.log('【步骤 1/3】抓取小红书笔记');
    const notes = await fetchNotes(config.maxResults);
    console.log(`✓ 抓取成功: ${notes.length} 条\n`);
    
    // 2. 逐条处理
    console.log('【步骤 2/3】改写并写入飞书');
    let successCount = 0;
    let failCount = 0;
    
    for (let i = 0; i < notes.length; i++) {
      const note = notes[i];
      console.log(`\n[${i + 1}/${notes.length}] ${note.original_title}`);
      
      let retries = 3;
      while (retries > 0) {
        try {
          // 2.1 调用礼部改写
          const rewritten = await rewriteByLibu(note);
          
          // 2.2 写入飞书
          const recordId = await writeToFeishu(note, rewritten);
          
          console.log(`✓ 完成 (record_id: ${recordId})`);
          successCount++;
          break;
          
        } catch (error) {
          retries--;
          if (retries === 0) {
            console.error(`✗ 失败: ${error.message}`);
            failCount++;
          } else {
            console.log(`⚠ 重试 (剩余 ${retries} 次)`);
            await new Promise(r => setTimeout(r, 2000));
          }
        }
      }
    }
    
    // 3. 汇总结果
    const duration = ((Date.now() - startTime) / 1000).toFixed(1);
    console.log('\n========================================');
    console.log('【步骤 3/3】执行完成');
    console.log('========================================');
    console.log(`总计: ${notes.length} 条`);
    console.log(`成功: ${successCount} 条`);
    console.log(`失败: ${failCount} 条`);
    console.log(`耗时: ${duration}s`);
    console.log('========================================\n');
    
    process.exit(failCount > 0 ? 1 : 0);
    
  } catch (error) {
    console.error('\n流程执行失败:', error.message);
    process.exit(1);
  }
}

// 执行主流程
main();
