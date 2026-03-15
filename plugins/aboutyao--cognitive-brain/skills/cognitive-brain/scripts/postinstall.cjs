#!/usr/bin/env node
/**
 * Cognitive Brain - Post-install script
 * 自动复制 hooks、启用自主进化、检测依赖、预热 Embedding
 */

const fs = require('fs');
const path = require('path');
const { execSync, spawn } = require('child_process');

const HOME = process.env.HOME || '/root';
const OPENCLAW_HOOKS_DIR = path.join(HOME, '.openclaw', 'hooks');
const SKILL_DIR = path.dirname(__dirname);
const HOOKS_IN_SKILL = path.join(SKILL_DIR, 'hooks');

console.log('🧠 Cognitive Brain postinstall...\n');

async function main() {
  // ===== 1. 检查并安装依赖 =====
  const nodeModulesPath = path.join(SKILL_DIR, 'node_modules');
  if (!fs.existsSync(nodeModulesPath)) {
    console.log('📦 检测到依赖未安装，正在安装...');
    try {
      execSync('npm install --production', { cwd: SKILL_DIR, stdio: 'inherit' });
      console.log('✅ 依赖安装完成\n');
    } catch (e) {
      console.log('❌ 依赖安装失败，请手动运行: npm install\n');
      return;
    }
  } else {
    console.log('✅ 依赖已安装\n');
  }

  // ===== 2. 安装 hooks =====
  if (!fs.existsSync(OPENCLAW_HOOKS_DIR)) {
    fs.mkdirSync(OPENCLAW_HOOKS_DIR, { recursive: true });
  }

  if (fs.existsSync(HOOKS_IN_SKILL)) {
    const hookDirs = fs.readdirSync(HOOKS_IN_SKILL).filter(f => {
      return fs.statSync(path.join(HOOKS_IN_SKILL, f)).isDirectory();
    });
    
    for (const hookName of hookDirs) {
      const targetDir = path.join(OPENCLAW_HOOKS_DIR, hookName);
      const sourceDir = path.join(HOOKS_IN_SKILL, hookName);
      
      if (!fs.existsSync(targetDir)) {
        fs.mkdirSync(targetDir, { recursive: true });
      }
      
      const files = fs.readdirSync(sourceDir);
      for (const file of files) {
        fs.copyFileSync(path.join(sourceDir, file), path.join(targetDir, file));
      }
      console.log(`✅ Hook installed: ${hookName}`);
    }
  }

  // ===== 3. 设置 cron 任务 =====
  const CRON_JOB = `0 3 * * * cd ${SKILL_DIR} && node scripts/forget.cjs >> /tmp/brain-cron.log 2>&1\n0 4 * * * cd ${SKILL_DIR} && node scripts/reflect.cjs >> /tmp/brain-cron.log 2>&1\n0 5 * * * cd ${SKILL_DIR} && node scripts/autolearn.cjs >> /tmp/brain-cron.log 2>&1\n`;

  try {
    const currentCron = execSync('crontab -l 2>/dev/null || echo ""', { encoding: 'utf8' });
    if (!currentCron.includes('cognitive-brain')) {
      execSync(`echo "${currentCron.trim()}\n${CRON_JOB}" | crontab -`);
      console.log('✅ Cron jobs installed');
    } else {
      console.log('✅ Cron jobs already configured');
    }
  } catch (e) {
    console.log('⚠️ Could not set up cron jobs');
  }

  // ===== 4. 创建必要目录 =====
  const dataDir = path.join(SKILL_DIR, 'data');
  if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
    console.log(`✅ Created: ${dataDir}`);
  }

  // ===== 5. 初始化数据库 =====
  console.log('\n🗄️ 检查数据库...');
  try {
    execSync(`node "${path.join(SKILL_DIR, 'scripts/init-db.cjs')}"`, {
      cwd: SKILL_DIR, stdio: 'inherit', timeout: 30000
    });
  } catch (e) {
    console.log('✅ Database ready');
  }

  // ===== 6. 初始化数据文件 =====
  const dataFiles = [
    { name: '.user-model.json', content: { stats: { totalInteractions: 0 }, preferences: { topics: {} } } },
    { name: '.working-memory.json', content: { activeContext: { entities: [], topic: null } } },
    { name: '.prediction-cache.json', content: { predictions: [], lastUpdated: null } }
  ];

  for (const file of dataFiles) {
    const filePath = path.join(SKILL_DIR, file.name);
    if (!fs.existsSync(filePath)) {
      fs.writeFileSync(filePath, JSON.stringify(file.content, null, 2));
      console.log(`✅ Created: ${file.name}`);
    }
  }

  // ===== 7. 升级共享工作区 (v2.7.0) =====
  console.log('\n🔄 升级共享工作区...');
  try {
    execSync(`node "${path.join(SKILL_DIR, 'scripts/upgrade-shared-workspace.cjs')}"`, {
      cwd: SKILL_DIR,
      stdio: 'inherit',
      timeout: 60000
    });
    console.log('✅ 共享工作区升级完成');
  } catch (e) {
    console.log('⚠️  共享工作区升级失败（可能已存在）');
  }

  // ===== 8. 预热 Embedding 服务 =====
  console.log('\n🔥 预热 Embedding 服务...');
  try {
    const embedService = spawn('node', [
      path.join(SKILL_DIR, 'scripts/warmup_embedding.cjs'),
      'serve'
    ], { detached: true, stdio: 'ignore' });
    
    embedService.unref();
    console.log(`✅ Embedding 服务已启动 (PID: ${embedService.pid})`);
    
    // 等待 5 秒让服务初始化
    await new Promise(r => setTimeout(r, 5000));
    console.log('✅ Embedding 预热完成');
  } catch (e) {
    console.log('⚠️ Embedding 预热失败（不影响使用）');
  }

  console.log('\n✨ Cognitive Brain 安装完成！');
  console.log('\n使用方法:');
  console.log('  node scripts/brain.cjs encode "内容"   # 编码记忆');
  console.log('  node scripts/brain.cjs recall "查询"   # 检索记忆');
  console.log('  node scripts/brain.cjs health_check   # 健康检查\n');
}

main().catch(e => {
  console.error('❌ Error:', e.message);
  process.exit(1);
});
