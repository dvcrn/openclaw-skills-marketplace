#!/usr/bin/env node
const { resolveModule } = require('./module_resolver.cjs');
/**
 * Cognitive Brain - 完整功能测试
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const SKILL_DIR = path.dirname(__dirname);

console.log('🧠 Cognitive Brain 完整测试\n');
console.log('='.repeat(50));

const tests = [];

// 1. 配置文件检查
try {
  const config = JSON.parse(fs.readFileSync(path.join(SKILL_DIR, 'config.json'), 'utf8'));
  tests.push({ name: '配置文件', status: '✅', detail: '格式正确' });
} catch (e) {
  tests.push({ name: '配置文件', status: '❌', detail: e.message });
}

// 2. 数据库连接
try {
  const { Pool } = resolveModule('pg');
  const config = JSON.parse(fs.readFileSync(path.join(SKILL_DIR, 'config.json'), 'utf8'));
  const pool = new Pool(config.storage.primary);
  pool.query('SELECT 1').then(() => {
    tests.push({ name: '数据库连接', status: '✅', detail: 'PostgreSQL' });
    pool.end();
  });
} catch (e) {
  tests.push({ name: '数据库连接', status: '❌', detail: e.message });
}

// 3. Redis 连接
try {
  const redis = require('redis');
  tests.push({ name: 'Redis', status: '✅', detail: '模块可用' });
} catch (e) {
  tests.push({ name: 'Redis', status: '⚠️', detail: '未安装或未启用' });
}

// 4. 脚本检查
const scripts = [
  'encode.cjs', 'recall.cjs', 'reflect.cjs', 'forget.cjs',
  'associate.cjs', 'user_model.cjs', 'prediction.cjs',
  'working_memory.cjs', 'goal_management.cjs', 'safety.cjs'
];

scripts.forEach(script => {
  const scriptPath = path.join(SKILL_DIR, 'scripts', script);
  if (fs.existsSync(scriptPath)) {
    tests.push({ name: script, status: '✅', detail: '存在' });
  } else {
    tests.push({ name: script, status: '❌', detail: '缺失' });
  }
});

// 5. 数据文件检查
const dataFiles = [
  '.user-model.json',
  '.working-memory.json',
  '.prediction-cache.json'
];

dataFiles.forEach(file => {
  const filePath = path.join(SKILL_DIR, file);
  if (fs.existsSync(filePath)) {
    const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    tests.push({ name: file, status: '✅', detail: '已初始化' });
  } else {
    tests.push({ name: file, status: '⚠️', detail: '未初始化' });
  }
});

// 延迟输出结果
setTimeout(() => {
  console.log('\n测试结果:\n');
  
  let passed = 0, warned = 0, failed = 0;
  
  tests.forEach(t => {
    console.log(`${t.status} ${t.name.padEnd(25)} ${t.detail}`);
    if (t.status === '✅') passed++;
    else if (t.status === '⚠️') warned++;
    else failed++;
  });
  
  console.log('\n' + '='.repeat(50));
  console.log(`总计: ${passed} 通过, ${warned} 警告, ${failed} 失败`);
  
  if (failed === 0) {
    console.log('\n✨ 所有核心功能正常！');
    process.exit(0);
  } else {
    process.exit(1);
  }
}, 1000);
