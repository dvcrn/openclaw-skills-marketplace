#!/usr/bin/env node
/**
 * Cognitive Brain - 性能监控
 * 记录和分析操作性能
 */

const fs = require('fs');
const path = require('path');

const SKILL_DIR = path.dirname(__dirname);
const PERF_LOG = path.join(SKILL_DIR, '.perf.json');

/**
 * 性能计时器
 */
class PerfTimer {
  constructor(operation) {
    this.operation = operation;
    this.startTime = Date.now();
    this.metrics = {};
  }
  
  checkpoint(name) {
    this.metrics[name] = Date.now() - this.startTime;
  }
  
  end(additional = {}) {
    const totalTime = Date.now() - this.startTime;
    const record = {
      operation: this.operation,
      totalTime,
      metrics: this.metrics,
      ...additional,
      timestamp: new Date().toISOString()
    };
    
    this.save(record);
    return record;
  }
  
  save(record) {
    let logs = [];
    if (fs.existsSync(PERF_LOG)) {
      logs = JSON.parse(fs.readFileSync(PERF_LOG, 'utf8'));
    }
    logs.push(record);
    
    // 只保留最近1000条
    if (logs.length > 1000) {
      logs = logs.slice(-1000);
    }
    
    fs.writeFileSync(PERF_LOG, JSON.stringify(logs, null, 2));
  }
}

/**
 * 性能统计
 */
function getStats() {
  if (!fs.existsSync(PERF_LOG)) {
    return { message: '无性能数据' };
  }
  
  const logs = JSON.parse(fs.readFileSync(PERF_LOG, 'utf8'));
  
  // 按操作类型分组统计
  const stats = {};
  
  logs.forEach(log => {
    const op = log.operation;
    if (!stats[op]) {
      stats[op] = {
        count: 0,
        totalTime: 0,
        minTime: Infinity,
        maxTime: 0,
        avgTime: 0
      };
    }
    
    stats[op].count++;
    stats[op].totalTime += log.totalTime;
    stats[op].minTime = Math.min(stats[op].minTime, log.totalTime);
    stats[op].maxTime = Math.max(stats[op].maxTime, log.totalTime);
  });
  
  // 计算平均值
  Object.keys(stats).forEach(op => {
    stats[op].avgTime = (stats[op].totalTime / stats[op].count).toFixed(2);
  });
  
  return {
    totalRecords: logs.length,
    operations: stats
  };
}

/**
 * 生成报告
 */
function generateReport() {
  const stats = getStats();
  
  console.log('📊 性能监控报告\n');
  console.log(`总记录数: ${stats.totalRecords || 0}\n`);
  
  if (!stats.operations) {
    console.log('暂无操作记录');
    return;
  }
  
  console.log('操作统计:');
  console.log('-'.repeat(60));
  
  Object.entries(stats.operations)
    .sort((a, b) => b[1].count - a[1].count)
    .forEach(([op, s]) => {
      console.log(`\n${op}:`);
      console.log(`  调用次数: ${s.count}`);
      console.log(`  平均耗时: ${s.avgTime}ms`);
      console.log(`  最小耗时: ${s.minTime}ms`);
      console.log(`  最大耗时: ${s.maxTime}ms`);
    });
}

// 命令行接口
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args[0] === 'report') {
    generateReport();
  } else if (args[0] === 'clear') {
    fs.writeFileSync(PERF_LOG, '[]');
    console.log('✅ 性能日志已清空');
  } else {
    console.log(`
性能监控工具

用法:
  node perf_monitor.cjs report    # 查看性能报告
  node perf_monitor.cjs clear     # 清空性能日志

代码中使用:
  const { PerfTimer } = require('./perf_monitor.cjs');
  const timer = new PerfTimer('encode');
  // ... 操作 ...
  timer.checkpoint('embedding');
  timer.end({ memories: 5 });
`);
  }
}

module.exports = { PerfTimer, getStats, generateReport };
