#!/usr/bin/env node

/**
 * 智能路由器技能安装脚本
 */

const fs = require('fs').promises;
const path = require('path');
const { exec } = require('child_process');
const { promisify } = require('util');

const execAsync = promisify(exec);

// 技能配置
const SKILL_CONFIG = {
  name: '智能路由器',
  version: '1.0.0',
  id: 'smart-router'
};

// OpenClaw路径
const OPENCLAW_SKILLS_DIR = '/opt/homebrew/lib/node_modules/openclaw/skills';
const OPENCLAW_CONFIG_PATH = path.join(process.env.HOME || '/Users/nora', '.openclaw/openclaw.json');

class SkillInstaller {
  constructor() {
    this.skillSourceDir = __dirname;
    this.skillTargetDir = path.join(OPENCLAW_SKILLS_DIR, SKILL_CONFIG.id);
    this.workspaceDir = path.join(process.env.HOME || '/Users/nora', '.openclaw/users/main/workspace');
  }

  async install() {
    console.log(`🚀 开始安装 ${SKILL_CONFIG.name} v${SKILL_CONFIG.version}`);
    
    try {
      // 1. 检查前提条件
      await this.checkPrerequisites();
      
      // 2. 复制技能文件
      await this.copySkillFiles();
      
      // 3. 更新OpenClaw配置
      await this.updateOpenClawConfig();
      
      // 4. 创建必要的目录和文件
      await this.createRequiredDirectories();
      
      // 5. 初始化技能
      await this.initializeSkill();
      
      // 6. 创建定时任务
      await this.createCronJobs();
      
      console.log(`🎉 ${SKILL_CONFIG.name} 技能安装完成!`);
      console.log('\n📋 安装摘要:');
      console.log(`   技能目录: ${this.skillTargetDir}`);
      console.log(`   配置文件: ${OPENCLAW_CONFIG_PATH}`);
      console.log(`   工作空间: ${this.workspaceDir}`);
      console.log('\n🚀 下一步: 重启OpenClaw以应用更改');
      console.log('   命令: openclaw gateway restart');
      
      return { success: true, skill: SKILL_CONFIG };
    } catch (error) {
      console.error(`❌ 安装失败: ${error.message}`);
      return { success: false, error: error.message };
    }
  }

  async checkPrerequisites() {
    console.log('🔍 检查前提条件...');
    
    const checks = [
      this.checkOpenClawInstalled.bind(this),
      this.checkNodeVersion.bind(this),
      this.checkRequiredEnvVars.bind(this),
      this.checkDiskSpace.bind(this)
    ];
    
    for (const check of checks) {
      try {
        await check();
      } catch (error) {
        throw new Error(`前提条件检查失败: ${error.message}`);
      }
    }
    
    console.log('✅ 所有前提条件满足');
  }

  async checkOpenClawInstalled() {
    try {
      const { stdout } = await execAsync('which openclaw');
      if (!stdout.trim()) {
        throw new Error('OpenClaw未安装');
      }
      
      const { stdout: version } = await execAsync('openclaw --version');
      console.log(`✅ OpenClaw已安装: ${version.trim()}`);
    } catch (error) {
      throw new Error('OpenClaw未安装或不可用');
    }
  }

  async checkNodeVersion() {
    const version = process.version;
    const majorVersion = parseInt(version.replace('v', '').split('.')[0]);
    
    if (majorVersion < 18) {
      throw new Error(`Node.js版本过低 (${version})，需要18+`);
    }
    
    console.log(`✅ Node.js版本: ${version}`);
  }

  async checkRequiredEnvVars() {
    const requiredVars = ['OPENROUTER_API_KEY'];
    const missingVars = [];
    
    for (const varName of requiredVars) {
      if (!process.env[varName]) {
        missingVars.push(varName);
      }
    }
    
    if (missingVars.length > 0) {
      console.warn(`⚠️ 缺少环境变量: ${missingVars.join(', ')}`);
      console.warn('   技能功能可能受限，但安装可以继续');
    } else {
      console.log('✅ 所有必需环境变量已设置');
    }
  }

  async checkDiskSpace() {
    try {
      const { stdout } = await execAsync('df -h . | tail -1');
      const [, size, used, avail, percent] = stdout.trim().split(/\s+/);
      
      console.log(`✅ 磁盘空间: ${avail} 可用 (${percent} 已使用)`);
      
      // 检查是否有足够空间（至少100MB）
      const availMB = parseInt(avail);
      if (availMB < 100) {
        console.warn('⚠️ 磁盘空间可能不足');
      }
    } catch (error) {
      console.warn('⚠️ 磁盘空间检查失败，继续安装');
    }
  }

  async copySkillFiles() {
    console.log('📁 复制技能文件...');
    
    try {
      // 检查目标目录是否存在
      try {
        await fs.access(this.skillTargetDir);
        console.log(`📁 技能目录已存在: ${this.skillTargetDir}`);
        console.log('🔄 将更新现有文件...');
      } catch {
        // 目录不存在，创建它
        await fs.mkdir(this.skillTargetDir, { recursive: true });
        console.log(`📁 创建技能目录: ${this.skillTargetDir}`);
      }
      
      // 复制所有文件
      const files = await fs.readdir(this.skillSourceDir);
      
      for (const file of files) {
        // 跳过node_modules和隐藏文件
        if (file === 'node_modules' || file.startsWith('.')) {
          continue;
        }
        
        const sourcePath = path.join(this.skillSourceDir, file);
        const targetPath = path.join(this.skillTargetDir, file);
        const stats = await fs.stat(sourcePath);
        
        if (stats.isDirectory()) {
          // 复制目录
          await this.copyDirectory(sourcePath, targetPath);
        } else {
          // 复制文件
          await fs.copyFile(sourcePath, targetPath);
        }
        
        console.log(`   ✅ ${file}`);
      }
      
      console.log('✅ 技能文件复制完成');
    } catch (error) {
      throw new Error(`文件复制失败: ${error.message}`);
    }
  }

  async copyDirectory(source, target) {
    await fs.mkdir(target, { recursive: true });
    const files = await fs.readdir(source);
    
    for (const file of files) {
      if (file === 'node_modules' || file.startsWith('.')) {
        continue;
      }
      
      const sourcePath = path.join(source, file);
      const targetPath = path.join(target, file);
      const stats = await fs.stat(sourcePath);
      
      if (stats.isDirectory()) {
        await this.copyDirectory(sourcePath, targetPath);
      } else {
        await fs.copyFile(sourcePath, targetPath);
      }
    }
  }

  async updateOpenClawConfig() {
    console.log('⚙️ 更新OpenClaw配置...');
    
    try {
      // 读取当前配置
      const configData = await fs.readFile(OPENCLAW_CONFIG_PATH, 'utf8');
      const config = JSON.parse(configData);
      
      // 确保skills配置存在
      if (!config.skills) {
        config.skills = {
          install: {
            nodeManager: 'pnpm'
          },
          entries: {}
        };
      }
      
      if (!config.skills.entries) {
        config.skills.entries = {};
      }
      
      // 添加智能路由器技能
      config.skills.entries[SKILL_CONFIG.id] = {
        enabled: true,
        name: SKILL_CONFIG.name,
        version: SKILL_CONFIG.version,
        autoUpdate: true
      };
      
      // 添加技能特定的配置
      if (!config.smartRouter) {
        config.smartRouter = {
          enabled: true,
          autoRouting: true,
          costOptimization: {
            enabled: true,
            dailyLimit: 1.0,
            monthlyLimit: 10.0
          },
          scanning: {
            enabled: true,
            schedule: "0 6 * * *",
            autoUpdate: true
          }
        };
      }
      
      // 保存更新后的配置
      await fs.writeFile(OPENCLAW_CONFIG_PATH, JSON.stringify(config, null, 2));
      
      console.log('✅ OpenClaw配置更新完成');
    } catch (error) {
      throw new Error(`配置更新失败: ${error.message}`);
    }
  }

  async createRequiredDirectories() {
    console.log('📁 创建必要目录...');
    
    const directories = [
      path.join(this.workspaceDir, 'smart-router'),
      path.join(this.workspaceDir, 'smart-router/logs'),
      path.join(this.workspaceDir, 'smart-router/backups'),
      path.join(this.workspaceDir, 'smart-router/config')
    ];
    
    for (const dir of directories) {
      try {
        await fs.mkdir(dir, { recursive: true });
        console.log(`   ✅ ${path.relative(this.workspaceDir, dir)}`);
      } catch (error) {
        if (error.code !== 'EEXIST') {
          console.warn(`⚠️ 创建目录失败 ${dir}: ${error.message}`);
        }
      }
    }
    
    console.log('✅ 目录创建完成');
  }

  async initializeSkill() {
    console.log('🚀 初始化技能...');
    
    try {
      // 复制核心文件到工作空间
      const coreFiles = [
        'enhanced-intent-router.js',
        'smart-router-config.json',
        'openrouter-scanner.js',
        'smart-router-maintenance.js'
      ];
      
      for (const file of coreFiles) {
        const sourcePath = path.join(this.skillSourceDir, 'lib', file);
        const targetPath = path.join(this.workspaceDir, 'smart-router', file);
        
        try {
          await fs.copyFile(sourcePath, targetPath);
          console.log(`   ✅ 复制 ${file}`);
        } catch (error) {
          console.warn(`⚠️ 复制 ${file} 失败: ${error.message}`);
        }
      }
      
      // 运行技能初始化
      const skillInitPath = path.join(this.skillTargetDir, 'index.js');
      const { stdout } = await execAsync(`node "${skillInitPath}" init`);
      console.log(stdout);
      
      console.log('✅ 技能初始化完成');
    } catch (error) {
      console.warn(`⚠️ 技能初始化失败: ${error.message}`);
      console.warn('   可以手动运行: node index.js init');
    }
  }

  async createCronJobs() {
    console.log('⏰ 创建定时任务...');
    
    const cronJobs = [
      {
        name: '智能路由器每日扫描',
        schedule: '0 6 * * *',
        command: `cd "${this.workspaceDir}/smart-router" && node openrouter-scanner.js`
      },
      {
        name: '智能路由器每日报告',
        schedule: '0 0 * * *',
        command: `cd "${this.workspaceDir}/smart-router" && node enhanced-intent-router.js report`
      },
      {
        name: '智能路由器每日维护',
        schedule: '30 23 * * *',
        command: `cd "${this.workspaceDir}/smart-router" && node smart-router-maintenance.js daily`
      }
    ];
    
    for (const job of cronJobs) {
      try {
        // 使用OpenClaw的cron系统
        const cronCmd = `openclaw cron add --name "${job.name}" --cron "${job.schedule}" --session isolated --message "${job.command}" --announce --channel feishu`;
        
        const { stdout } = await execAsync(cronCmd);
        console.log(`   ✅ ${job.name}`);
      } catch (error) {
        console.warn(`⚠️ 创建定时任务失败 ${job.name}: ${error.message}`);
      }
    }
    
    console.log('✅ 定时任务创建完成');
  }

  async uninstall() {
    console.log(`🗑️ 开始卸载 ${SKILL_CONFIG.name}...`);
    
    try {
      // 1. 从配置中移除技能
      await this.removeFromConfig();
      
      // 2. 删除技能目录
      await this.removeSkillDirectory();
      
      // 3. 清理工作空间文件
      await this.cleanWorkspace();
      
      console.log(`✅ ${SKILL_CONFIG.name} 卸载完成`);
      return { success: true };
    } catch (error) {
      console.error(`❌ 卸载失败: ${error.message}`);
      return { success: false, error: error.message };
    }
  }

  async removeFromConfig() {
    try {
      const configData = await fs.readFile(OPENCLAW_CONFIG_PATH, 'utf8');
      const config = JSON.parse(configData);
      
      // 从skills.entries中移除
      if (config.skills && config.skills.entries && config.skills.entries[SKILL_CONFIG.id]) {
        delete config.skills.entries[SKILL_CONFIG.id];
      }
      
      // 移除smartRouter配置
      if (config.smartRouter) {
        delete config.smartRouter;
      }
      
      await fs.writeFile(OPENCLAW_CONFIG_PATH, JSON.stringify(config, null, 2));
      console.log('✅ 从配置中移除技能');
    } catch (error) {
      console.warn(`⚠️ 配置清理失败: ${error.message}`);
    }
  }

  async removeSkillDirectory() {
    try {
      await fs.rm(this.skillTargetDir, { recursive: true, force: true });
      console.log(`✅ 删除技能目录: ${this.skillTargetDir}`);
    } catch (error) {
      console.warn(`⚠️ 技能目录删除失败: ${error.message}`);
    }
  }

  async cleanWorkspace() {
    const workspaceSkillDir = path.join(this.workspaceDir, 'smart-router');
    
    try {
      await fs.rm(workspaceSkillDir, { recursive: true, force: true });
      console.log(`✅ 清理工作空间: ${workspaceSkillDir}`);
    } catch (error) {
      console.warn(`⚠️ 工作空间清理失败: ${error.message}`);
    }
  }
}

// 命令行接口
async function main() {
  const args = process.argv.slice(2);
  const command = args[0] || 'install';
  
  const installer = new SkillInstaller();
  
  if (command === 'install') {
    await installer.install();
  } else if (command === 'uninstall') {
    await installer.uninstall();
  } else if (command === 'help') {
    console.log(`
📖 智能路由器技能安装脚本

用法:
  node install.js [命令]

命令:
  install    - 安装技能 (默认)
  uninstall  - 卸载技能
  help       - 显示帮助

示例:
  node install.js install
  node install.js uninstall
    `);
  } else {
    console.log(`未知命令: ${command}`);
    console.log('使用 "node install.js help" 查看帮助');
  }
}

// 执行主函数
if (require.main === module) {
  main().catch(error => {
    console.error('❌ 未处理的错误:', error);
    process.exit(1);
  });
}

module.exports = SkillInstaller;