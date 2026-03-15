#!/usr/bin/env node
/**
 * Cognitive Brain - 健康检查
 * 定期生成系统健康报告
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const { resolveModule, resolveConfig } = require('./module_resolver.cjs');

const SKILL_DIR = path.dirname(__dirname);

async function healthCheck() {
  console.log('🏥 Cognitive Brain 健康检查\n');
  console.log('='.repeat(50));
  
  const results = {
    timestamp: new Date().toISOString(),
    checks: [],
    score: 100
  };
  
  // 1. 数据库连接
  try {
    const pg = resolveModule('pg');
    const config = resolveConfig();
    const { Pool } = pg;
    const pool = new Pool(config.storage.primary);
    
    await pool.query('SELECT 1');
    
    // 统计数据
    const stats = await pool.query(`
      SELECT 
        (SELECT COUNT(*) FROM episodes) as memories,
        (SELECT COUNT(*) FROM concepts) as concepts,
        (SELECT COUNT(*) FROM associations) as associations,
        (SELECT COUNT(*) FROM reflections) as reflections
    `);
    
    await pool.end();
    
    results.checks.push({
      name: '数据库',
      status: '✅',
      detail: `记忆:${stats.rows[0].memories} 概念:${stats.rows[0].concepts} 关联:${stats.rows[0].associations}`
    });
  } catch (e) {
    results.checks.push({ name: '数据库', status: '❌', detail: e.message });
    results.score -= 30;
  }
  
  // 2. Redis 连接
  try {
    const redis = resolveModule('redis');
    results.checks.push({ name: 'Redis', status: '✅', detail: '模块可用' });
  } catch (e) {
    results.checks.push({ name: 'Redis', status: '⚠️', detail: '未启用缓存' });
    results.score -= 10;
  }
  
  // 3. 配置文件
  try {
    const config = resolveConfig();
    results.checks.push({ name: '配置', status: '✅', detail: '格式正确' });
  } catch (e) {
    results.checks.push({ name: '配置', status: '❌', detail: e.message });
    results.score -= 20;
  }
  
  // 4. 数据文件
  const dataFiles = [
    '.user-model.json',
    '.working-memory.json',
    '.prediction-cache.json'
  ];
  
  const missingFiles = dataFiles.filter(f => 
    !fs.existsSync(path.join(SKILL_DIR, f))
  );
  
  if (missingFiles.length === 0) {
    results.checks.push({ name: '数据文件', status: '✅', detail: '全部初始化' });
  } else {
    results.checks.push({ name: '数据文件', status: '⚠️', detail: `缺失: ${missingFiles.join(', ')}` });
    results.score -= 5 * missingFiles.length;
  }
  
  // 5. Cron 任务
  try {
    const crontab = execSync('crontab -l 2>/dev/null || echo ""', { encoding: 'utf8' });
    const hasCron = crontab.includes('cognitive-brain');
    
    if (hasCron) {
      results.checks.push({ name: 'Cron任务', status: '✅', detail: '已配置' });
    } else {
      results.checks.push({ name: 'Cron任务', status: '⚠️', detail: '未配置自动任务' });
      results.score -= 10;
    }
  } catch (e) {
    results.checks.push({ name: 'Cron任务', status: '⚠️', detail: '无法检查' });
  }
  
  // 6. 磁盘空间
  try {
    const df = execSync('df -h /root | tail -1', { encoding: 'utf8' });
    const used = df.split(/\s+/)[4];
    const usedPercent = parseInt(used);
    
    if (usedPercent < 80) {
      results.checks.push({ name: '磁盘空间', status: '✅', detail: `已用 ${used}` });
    } else if (usedPercent < 90) {
      results.checks.push({ name: '磁盘空间', status: '⚠️', detail: `已用 ${used}` });
      results.score -= 10;
    } else {
      results.checks.push({ name: '磁盘空间', status: '❌', detail: `已用 ${used}，空间不足` });
      results.score -= 20;
    }
  } catch (e) {
    results.checks.push({ name: '磁盘空间', status: '⚠️', detail: '无法检查' });
  }
  
  // 输出结果
  console.log('\n检查结果:\n');
  
  results.checks.forEach(c => {
    console.log(`${c.status} ${c.name.padEnd(12)} ${c.detail}`);
  });
  
  console.log('\n' + '='.repeat(50));
  
  // 健康分数
  let grade = 'A';
  if (results.score < 90) grade = 'B';
  if (results.score < 70) grade = 'C';
  if (results.score < 50) grade = 'D';
  
  console.log(`\n健康分数: ${results.score}/100 (${grade})`);
  
  if (results.score >= 90) {
    console.log('✨ 系统状态良好！');
  } else if (results.score >= 70) {
    console.log('💡 建议处理警告项');
  } else {
    console.log('⚠️ 存在问题需要处理');
  }
  
  // 保存报告
  const reportPath = path.join(SKILL_DIR, '.health-report.json');
  fs.writeFileSync(reportPath, JSON.stringify(results, null, 2));
  
  return results;
}

// 命令行接口
if (require.main === module) {
  healthCheck().catch(e => console.error('❌ 错误:', e.message));
}

module.exports = { healthCheck };
