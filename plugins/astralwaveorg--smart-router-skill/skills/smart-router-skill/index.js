#!/usr/bin/env node

/**
 * 智能路由器技能 - 主入口文件
 */

const fs = require('fs').promises;
const path = require('path');

// 技能配置
const SKILL_CONFIG = {
  name: '智能路由器',
  version: '1.0.0',
  description: '多维度智能模型调度和成本优化系统',
  author: 'OpenClaw AI',
  license: 'MIT'
};

// 核心模块
const modules = {
  router: require('./lib/enhanced-intent-router'),
  scanner: require('./lib/openrouter-scanner'),
  maintenance: require('./lib/smart-router-maintenance'),
  config: require('./lib/config-manager')
};

class SmartRouterSkill {
  constructor(options = {}) {
    this.options = options;
    this.initialized = false;
    this.modules = {};
  }

  async initialize() {
    if (this.initialized) return true;

    console.log(`🚀 初始化 ${SKILL_CONFIG.name} v${SKILL_CONFIG.version}`);
    
    try {
      // 初始化各模块
      for (const [name, module] of Object.entries(modules)) {
        if (module.initialize) {
          await module.initialize();
          this.modules[name] = module;
          console.log(`✅ ${name} 模块初始化完成`);
        }
      }

      this.initialized = true;
      console.log(`🎉 ${SKILL_CONFIG.name} 技能初始化完成`);
      return true;
    } catch (error) {
      console.error(`❌ 技能初始化失败: ${error.message}`);
      return false;
    }
  }

  async routeMessage(message, context = {}) {
    await this.initialize();
    
    try {
      const decision = await this.modules.router.analyzeMessage(message, context);
      
      // 记录路由决策
      await this.logRouting(decision, message, context);
      
      return {
        success: true,
        skill: SKILL_CONFIG.name,
        version: SKILL_CONFIG.version,
        decision: decision,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error(`❌ 路由失败: ${error.message}`);
      
      return {
        success: false,
        skill: SKILL_CONFIG.name,
        error: error.message,
        fallback: {
          agentId: 'free-agent',
          model: 'openrouter/google/gemma-3-27b-it:free'
        },
        timestamp: new Date().toISOString()
      };
    }
  }

  async scanOpenRouterModels(options = {}) {
    await this.initialize();
    
    try {
      const result = await this.modules.scanner.scan(options);
      return {
        success: true,
        skill: SKILL_CONFIG.name,
        result: result,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error(`❌ OpenRouter扫描失败: ${error.message}`);
      return {
        success: false,
        skill: SKILL_CONFIG.name,
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }

  async runMaintenance(task, options = {}) {
    await this.initialize();
    
    try {
      let result;
      switch (task) {
        case 'daily':
          result = await this.modules.maintenance.runDailyMaintenance();
          break;
        case 'weekly':
          result = await this.modules.maintenance.runWeeklyMaintenance();
          break;
        case 'backup':
          result = await this.modules.maintenance.runBackupMaintenance();
          break;
        case 'health':
          result = await this.modules.maintenance.checkSystemHealth();
          break;
        default:
          throw new Error(`未知的维护任务: ${task}`);
      }

      return {
        success: true,
        skill: SKILL_CONFIG.name,
        task: task,
        result: result,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error(`❌ 维护任务失败: ${error.message}`);
      return {
        success: false,
        skill: SKILL_CONFIG.name,
        task: task,
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }

  async getMetrics() {
    await this.initialize();
    
    try {
      const metrics = await this.modules.router.getMetrics();
      return {
        success: true,
        skill: SKILL_CONFIG.name,
        metrics: metrics,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error(`❌ 获取指标失败: ${error.message}`);
      return {
        success: false,
        skill: SKILL_CONFIG.name,
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }

  async generateReport() {
    await this.initialize();
    
    try {
      const report = await this.modules.router.generateReport();
      return {
        success: true,
        skill: SKILL_CONFIG.name,
        report: report,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error(`❌ 生成报告失败: ${error.message}`);
      return {
        success: false,
        skill: SKILL_CONFIG.name,
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }

  async updateConfig(newConfig) {
    await this.initialize();
    
    try {
      const result = await this.modules.config.update(newConfig);
      return {
        success: true,
        skill: SKILL_CONFIG.name,
        result: result,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error(`❌ 配置更新失败: ${error.message}`);
      return {
        success: false,
        skill: SKILL_CONFIG.name,
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }

  async logRouting(decision, message, context) {
    const logEntry = {
      timestamp: new Date().toISOString(),
      skill: SKILL_CONFIG.name,
      version: SKILL_CONFIG.version,
      decision: {
        agentId: decision.agentId,
        model: decision.model,
        ruleName: decision.ruleName,
        confidence: decision.confidence
      },
      message: {
        preview: message.length > 100 ? message.substring(0, 100) + '...' : message,
        length: message.length
      },
      context: context
    };

    try {
      const logPath = path.join(__dirname, 'logs', 'routing.log');
      await fs.appendFile(logPath, JSON.stringify(logEntry) + '\n');
    } catch (error) {
      // 日志写入失败不影响主要功能
      console.warn(`⚠️ 路由日志写入失败: ${error.message}`);
    }
  }

  getInfo() {
    return {
      ...SKILL_CONFIG,
      initialized: this.initialized,
      modules: Object.keys(this.modules),
      capabilities: [
        'message_routing',
        'cost_optimization',
        'model_scanning',
        'maintenance',
        'monitoring',
        'reporting'
      ]
    };
  }
}

// 命令行接口
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  const skill = new SmartRouterSkill();

  if (!command) {
    console.log(`
🤖 ${SKILL_CONFIG.name} v${SKILL_CONFIG.version}

用法:
  node index.js <命令> [参数]

命令:
  init                    - 初始化技能
  route <消息>           - 路由消息
  scan                   - 扫描OpenRouter模型
  metrics                - 获取性能指标
  report                 - 生成详细报告
  maintenance <任务>     - 运行维护任务
  info                   - 显示技能信息
  help                   - 显示帮助

维护任务:
  daily    - 每日维护
  weekly   - 每周维护
  backup   - 备份维护
  health   - 健康检查

示例:
  node index.js init
  node index.js route "帮我写代码"
  node index.js scan
  node index.js maintenance daily
  node index.js info
    `);
    return;
  }

  try {
    switch (command) {
      case 'init':
        console.log('🚀 初始化智能路由器技能...');
        const initialized = await skill.initialize();
        if (initialized) {
          console.log('✅ 技能初始化完成');
        } else {
          console.log('❌ 技能初始化失败');
          process.exit(1);
        }
        break;

      case 'route':
        if (args.length < 2) {
          console.log('❌ 请提供要路由的消息');
          break;
        }
        const message = args.slice(1).join(' ');
        console.log(`📨 路由消息: "${message.substring(0, 50)}${message.length > 50 ? '...' : ''}"`);
        const result = await skill.routeMessage(message);
        console.log(JSON.stringify(result, null, 2));
        break;

      case 'scan':
        console.log('🔍 扫描OpenRouter模型...');
        const scanResult = await skill.scanOpenRouterModels();
        console.log(JSON.stringify(scanResult, null, 2));
        break;

      case 'metrics':
        console.log('📊 获取性能指标...');
        const metrics = await skill.getMetrics();
        console.log(JSON.stringify(metrics, null, 2));
        break;

      case 'report':
        console.log('📈 生成详细报告...');
        const report = await skill.generateReport();
        console.log(JSON.stringify(report, null, 2));
        break;

      case 'maintenance':
        if (args.length < 2) {
          console.log('❌ 请指定维护任务');
          console.log('可用任务: daily, weekly, backup, health');
          break;
        }
        const task = args[1];
        console.log(`🔧 运行维护任务: ${task}`);
        const maintenanceResult = await skill.runMaintenance(task);
        console.log(JSON.stringify(maintenanceResult, null, 2));
        break;

      case 'info':
        const info = skill.getInfo();
        console.log(JSON.stringify(info, null, 2));
        break;

      case 'help':
      default:
        console.log('使用 "node index.js" 查看帮助');
        break;
    }
  } catch (error) {
    console.error(`❌ 错误: ${error.message}`);
    process.exit(1);
  }
}

// 导出技能
module.exports = {
  SmartRouterSkill,
  SKILL_CONFIG,
  modules
};

// 执行主函数
if (require.main === module) {
  main().catch(error => {
    console.error('❌ 未处理的错误:', error);
    process.exit(1);
  });
}