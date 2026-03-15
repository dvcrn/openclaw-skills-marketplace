#!/usr/bin/env node
/**
 * Cognitive Brain - 调试工具
 * 详细日志输出和问题诊断
 */

const fs = require('fs');
const path = require('path');

const SKILL_DIR = path.dirname(__dirname);
const DEBUG_LOG = path.join(SKILL_DIR, '.debug.log');

// 调试级别
const LEVELS = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3
};

let currentLevel = LEVELS.INFO;

/**
 * 设置调试级别
 */
function setLevel(level) {
  currentLevel = LEVELS[level] ?? LEVELS.INFO;
}

/**
 * 日志输出
 */
function log(level, category, message, data = null) {
  if (LEVELS[level] < currentLevel) return;
  
  const timestamp = new Date().toISOString();
  const prefix = `[${timestamp}] [${level}] [${category}]`;
  
  let output = `${prefix} ${message}`;
  
  if (data) {
    if (typeof data === 'object') {
      output += '\n' + JSON.stringify(data, null, 2);
    } else {
      output += ' ' + data;
    }
  }
  
  console.log(output);
  
  // 写入日志文件
  fs.appendFileSync(DEBUG_LOG, output + '\n');
}

const debug = (cat, msg, data) => log('DEBUG', cat, msg, data);
const info = (cat, msg, data) => log('INFO', cat, msg, data);
const warn = (cat, msg, data) => log('WARN', cat, msg, data);
const error = (cat, msg, data) => log('ERROR', cat, msg, data);

/**
 * 性能追踪
 */
const traces = new Map();

function startTrace(name) {
  traces.set(name, {
    start: Date.now(),
    checkpoints: []
  });
}

function checkpoint(name, label) {
  const trace = traces.get(name);
  if (trace) {
    trace.checkpoints.push({
      label,
      time: Date.now() - trace.start
    });
  }
}

function endTrace(name) {
  const trace = traces.get(name);
  if (!trace) return null;
  
  const result = {
    name,
    totalTime: Date.now() - trace.start,
    checkpoints: trace.checkpoints
  };
  
  traces.delete(name);
  
  debug('PERF', `操作完成: ${name}`, result);
  
  return result;
}

/**
 * 诊断报告
 */
async function diagnose() {
  console.log('🔍 诊断报告\n');
  console.log('='.repeat(50));
  
  // 1. 环境检查
  console.log('\n📦 环境:');
  console.log(`  Node.js: ${process.version}`);
  console.log(`  平台: ${process.platform}`);
  console.log(`  架构: ${process.arch}`);
  
  // 2. 依赖检查
  console.log('\n📚 依赖:');
  const deps = ['pg', 'redis', 'sentence-transformers'];
  
  for (const dep of deps) {
    try {
      if (dep === 'sentence-transformers') {
        // Python 模块
        const { execSync } = require('child_process');
        execSync('python3 -c "import sentence_transformers"', { stdio: 'ignore' });
        console.log(`  ✅ ${dep}`);
      } else {
        require.resolve(dep);
        console.log(`  ✅ ${dep}`);
      }
    } catch (e) {
      console.log(`  ❌ ${dep} - 未安装`);
    }
  }
  
  // 3. 文件检查
  console.log('\n📁 文件:');
  const files = [
    'config.json',
    '.user-model.json',
    '.working-memory.json',
    '.prediction-cache.json'
  ];
  
  files.forEach(f => {
    const fullPath = path.join(SKILL_DIR, f);
    if (fs.existsSync(fullPath)) {
      const stat = fs.statSync(fullPath);
      console.log(`  ✅ ${f} (${(stat.size / 1024).toFixed(2)}KB)`);
    } else {
      console.log(`  ❌ ${f} - 不存在`);
    }
  });
  
  // 4. 数据库连接测试
  console.log('\n🗄️ 数据库:');
  try {
    const { Pool } = require('pg');
    const config = require('../config.json');
    const pool = new Pool(config.storage.primary);
    
    const start = Date.now();
    await pool.query('SELECT 1');
    const latency = Date.now() - start;
    
    console.log(`  ✅ 连接正常 (${latency}ms)`);
    
    // 表统计
    const stats = await pool.query(`
      SELECT 
        (SELECT COUNT(*) FROM episodes) as memories,
        (SELECT COUNT(*) FROM concepts) as concepts,
        (SELECT COUNT(*) FROM associations) as associations
    `);
    
    console.log(`     记忆: ${stats.rows[0].memories}`);
    console.log(`     概念: ${stats.rows[0].concepts}`);
    console.log(`     关联: ${stats.rows[0].associations}`);
    
    await pool.end();
  } catch (e) {
    console.log(`  ❌ 连接失败: ${e.message}`);
  }
  
  // 5. 日志统计
  console.log('\n📊 日志:');
  if (fs.existsSync(DEBUG_LOG)) {
    const logs = fs.readFileSync(DEBUG_LOG, 'utf8').split('\n');
    const errors = logs.filter(l => l.includes('[ERROR]')).length;
    const warns = logs.filter(l => l.includes('[WARN]')).length;
    
    console.log(`  总行数: ${logs.length}`);
    console.log(`  错误: ${errors}`);
    console.log(`  警告: ${warns}`);
  } else {
    console.log('  无日志文件');
  }
  
  console.log('\n' + '='.repeat(50));
}

// 命令行接口
if (require.main === module) {
  const args = process.argv.slice(2);
  
  switch (args[0]) {
    case 'diagnose':
      diagnose();
      break;
    case 'clear':
      fs.writeFileSync(DEBUG_LOG, '');
      console.log('✅ 日志已清空');
      break;
    case 'tail':
      if (fs.existsSync(DEBUG_LOG)) {
        const logs = fs.readFileSync(DEBUG_LOG, 'utf8').split('\n').slice(-50);
        console.log(logs.join('\n'));
      }
      break;
    default:
      console.log(`
调试工具

用法:
  node debug.cjs diagnose    运行诊断
  node debug.cjs clear       清空日志
  node debug.cjs tail        查看最近日志

代码中使用:
  const { debug, info, warn, error } = require('./debug.cjs');
  debug('CATEGORY', '消息', { data });
`);
  }
}

module.exports = { debug, info, warn, error, startTrace, checkpoint, endTrace, diagnose };
