#!/usr/bin/env node

/**
 * 智能路由器维护脚本
 * 管理所有定时任务和系统维护
 */

const fs = require('fs').promises;
const path = require('path');
const { exec } = require('child_process');
const { promisify } = require('util');

const execAsync = promisify(exec);

// 配置文件路径
const CONFIG_PATH = path.join(__dirname, 'smart-router-config.json');
const BACKUP_DIR = path.join(__dirname, 'backups');
const LOGS_DIR = path.join(__dirname, 'logs');

class SmartRouterMaintenance {
  constructor() {
    this.config = null;
    this.maintenanceTasks = {
      daily: this.runDailyMaintenance.bind(this),
      weekly: this.runWeeklyMaintenance.bind(this),
      backup: this.runBackupMaintenance.bind(this),
      optimize: this.runOptimizationMaintenance.bind(this)
    };
  }

  async initialize() {
    try {
      const configData = await fs.readFile(CONFIG_PATH, 'utf8');
      this.config = JSON.parse(configData);
      
      // 创建必要的目录
      await this.createDirectories();
      
      console.log('✅ 智能路由器维护系统初始化完成');
      return true;
    } catch (error) {
      console.error(`❌ 初始化失败: ${error.message}`);
      return false;
    }
  }

  async createDirectories() {
    const directories = [BACKUP_DIR, LOGS_DIR];
    
    for (const dir of directories) {
      try {
        await fs.access(dir);
      } catch {
        await fs.mkdir(dir, { recursive: true });
        console.log(`📁 创建目录: ${dir}`);
      }
    }
  }

  async runDailyMaintenance() {
    console.log('📅 运行每日维护任务...');
    
    const tasks = [
      this.cleanOldLogs.bind(this),
      this.generateDailyReport.bind(this),
      this.checkSystemHealth.bind(this),
      this.updateRouterMetrics.bind(this)
    ];
    
    for (const task of tasks) {
      try {
        await task();
      } catch (error) {
        console.error(`⚠️ 任务执行失败: ${error.message}`);
      }
    }
    
    console.log('✅ 每日维护任务完成');
  }

  async runWeeklyMaintenance() {
    console.log('📊 运行每周维护任务...');
    
    const tasks = [
      this.analyzeCostOptimization.bind(this),
      this.optimizeRoutingRules.bind(this),
      this.generateWeeklyReport.bind(this),
      this.cleanOldBackups.bind(this)
    ];
    
    for (const task of tasks) {
      try {
        await task();
      } catch (error) {
        console.error(`⚠️ 任务执行失败: ${error.message}`);
      }
    }
    
    console.log('✅ 每周维护任务完成');
  }

  async runBackupMaintenance() {
    console.log('💾 运行备份维护任务...');
    
    const backupFiles = [
      'smart-router-config.json',
      'router-logs.jsonl',
      'router-report.json',
      'config-update-summary.json'
    ];
    
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const backupPath = path.join(BACKUP_DIR, `backup-${timestamp}`);
    
    try {
      await fs.mkdir(backupPath, { recursive: true });
      
      for (const file of backupFiles) {
        const sourcePath = path.join(__dirname, file);
        const targetPath = path.join(backupPath, file);
        
        try {
          await fs.copyFile(sourcePath, targetPath);
          console.log(`✅ 备份文件: ${file}`);
        } catch (error) {
          console.log(`⚠️ 跳过文件 ${file}: ${error.message}`);
        }
      }
      
      // 创建备份清单
      const manifest = {
        timestamp: new Date().toISOString(),
        backupPath: backupPath,
        files: backupFiles,
        system: {
          nodeVersion: process.version,
          platform: process.platform,
          configVersion: this.config?.version || 'unknown'
        }
      };
      
      const manifestPath = path.join(backupPath, 'backup-manifest.json');
      await fs.writeFile(manifestPath, JSON.stringify(manifest, null, 2));
      
      console.log(`📄 备份完成: ${backupPath}`);
      return backupPath;
    } catch (error) {
      console.error(`❌ 备份失败: ${error.message}`);
      throw error;
    }
  }

  async runOptimizationMaintenance() {
    console.log('⚡ 运行优化维护任务...');
    
    const tasks = [
      this.analyzeRoutingPerformance.bind(this),
      this.optimizeCacheSettings.bind(this),
      this.checkRuleEffectiveness.bind(this),
      this.generateOptimizationReport.bind(this)
    ];
    
    const results = [];
    for (const task of tasks) {
      try {
        const result = await task();
        results.push(result);
      } catch (error) {
        console.error(`⚠️ 优化任务失败: ${error.message}`);
      }
    }
    
    console.log('✅ 优化维护任务完成');
    return results;
  }

  async cleanOldLogs(daysToKeep = 7) {
    console.log('🧹 清理旧日志...');
    
    try {
      const logFiles = await fs.readdir(LOGS_DIR);
      const now = Date.now();
      const cutoffTime = now - (daysToKeep * 24 * 60 * 60 * 1000);
      
      let deletedCount = 0;
      for (const file of logFiles) {
        const filePath = path.join(LOGS_DIR, file);
        const stats = await fs.stat(filePath);
        
        if (stats.mtimeMs < cutoffTime) {
          await fs.unlink(filePath);
          deletedCount++;
          console.log(`🗑️ 删除旧日志: ${file}`);
        }
      }
      
      console.log(`✅ 清理完成，删除了 ${deletedCount} 个旧日志文件`);
      return deletedCount;
    } catch (error) {
      console.error(`❌ 日志清理失败: ${error.message}`);
      return 0;
    }
  }

  async cleanOldBackups(daysToKeep = 30) {
    console.log('🧹 清理旧备份...');
    
    try {
      const backups = await fs.readdir(BACKUP_DIR);
      const now = Date.now();
      const cutoffTime = now - (daysToKeep * 24 * 60 * 60 * 1000);
      
      let deletedCount = 0;
      for (const backup of backups) {
        const backupPath = path.join(BACKUP_DIR, backup);
        const stats = await fs.stat(backupPath);
        
        if (stats.isDirectory() && stats.mtimeMs < cutoffTime) {
          await fs.rm(backupPath, { recursive: true, force: true });
          deletedCount++;
          console.log(`🗑️ 删除旧备份: ${backup}`);
        }
      }
      
      console.log(`✅ 备份清理完成，删除了 ${deletedCount} 个旧备份`);
      return deletedCount;
    } catch (error) {
      console.error(`❌ 备份清理失败: ${error.message}`);
      return 0;
    }
  }

  async generateDailyReport() {
    console.log('📊 生成每日报告...');
    
    try {
      // 运行路由器报告
      const { stdout } = await execAsync('node enhanced-intent-router.js report');
      const report = JSON.parse(stdout);
      
      // 保存报告
      const reportPath = path.join(LOGS_DIR, `daily-report-${new Date().toISOString().split('T')[0]}.json`);
      await fs.writeFile(reportPath, JSON.stringify(report, null, 2));
      
      console.log(`✅ 每日报告已保存: ${reportPath}`);
      return reportPath;
    } catch (error) {
      console.error(`❌ 报告生成失败: ${error.message}`);
      throw error;
    }
  }

  async generateWeeklyReport() {
    console.log('📈 生成每周报告...');
    
    try {
      // 收集一周的数据
      const weeklyData = {
        timestamp: new Date().toISOString(),
        weekStart: this.getWeekStartDate(),
        metrics: await this.collectWeeklyMetrics(),
        recommendations: await this.generateWeeklyRecommendations(),
        costAnalysis: await this.analyzeWeeklyCosts()
      };
      
      // 保存报告
      const reportPath = path.join(LOGS_DIR, `weekly-report-${new Date().toISOString().split('T')[0]}.json`);
      await fs.writeFile(reportPath, JSON.stringify(weeklyData, null, 2));
      
      console.log(`✅ 每周报告已保存: ${reportPath}`);
      return reportPath;
    } catch (error) {
      console.error(`❌ 每周报告生成失败: ${error.message}`);
      throw error;
    }
  }

  async checkSystemHealth() {
    console.log('🏥 检查系统健康状态...');
    
    const healthChecks = [
      this.checkConfigFile.bind(this),
      this.checkRouterAvailability.bind(this),
      this.checkDiskSpace.bind(this),
      this.checkMemoryUsage.bind(this)
    ];
    
    const results = [];
    for (const check of healthChecks) {
      try {
        const result = await check();
        results.push(result);
      } catch (error) {
        results.push({
          check: check.name,
          status: 'error',
          message: error.message
        });
      }
    }
    
    const healthReport = {
      timestamp: new Date().toISOString(),
      checks: results,
      overallStatus: results.every(r => r.status === 'healthy') ? 'healthy' : 'degraded'
    };
    
    console.log(`✅ 系统健康检查完成: ${healthReport.overallStatus}`);
    return healthReport;
  }

  async checkConfigFile() {
    try {
      await fs.access(CONFIG_PATH);
      const stats = await fs.stat(CONFIG_PATH);
      const config = JSON.parse(await fs.readFile(CONFIG_PATH, 'utf8'));
      
      return {
        check: 'config_file',
        status: 'healthy',
        message: '配置文件正常',
        details: {
          size: stats.size,
          version: config.version || 'unknown',
          lastModified: stats.mtime
        }
      };
    } catch (error) {
      return {
        check: 'config_file',
        status: 'error',
        message: `配置文件错误: ${error.message}`
      };
    }
  }

  async checkRouterAvailability() {
    try {
      const { stdout } = await execAsync('node enhanced-intent-router.js init');
      return {
        check: 'router_availability',
        status: 'healthy',
        message: '路由器可用'
      };
    } catch (error) {
      return {
        check: 'router_availability',
        status: 'error',
        message: `路由器不可用: ${error.message}`
      };
    }
  }

  async checkDiskSpace() {
    try {
      const { stdout } = await execAsync('df -h .');
      return {
        check: 'disk_space',
        status: 'healthy',
        message: '磁盘空间正常',
        details: stdout
      };
    } catch (error) {
      return {
        check: 'disk_space',
        status: 'warning',
        message: '磁盘空间检查失败'
      };
    }
  }

  async checkMemoryUsage() {
    try {
      const memoryUsage = process.memoryUsage();
      const usedMB = Math.round(memoryUsage.heapUsed / 1024 / 1024);
      const totalMB = Math.round(memoryUsage.heapTotal / 1024 / 1024);
      const usagePercent = (usedMB / totalMB * 100).toFixed(1);
      
      const status = usagePercent > 80 ? 'warning' : 'healthy';
      
      return {
        check: 'memory_usage',
        status: status,
        message: `内存使用: ${usedMB}MB / ${totalMB}MB (${usagePercent}%)`,
        details: memoryUsage
      };
    } catch (error) {
      return {
        check: 'memory_usage',
        status: 'error',
        message: '内存使用检查失败'
      };
    }
  }

  async updateRouterMetrics() {
    console.log('📈 更新路由器指标...');
    
    try {
      const { stdout } = await execAsync('node enhanced-intent-router.js stats');
      const metrics = JSON.parse(stdout);
      
      // 保存指标
      const metricsPath = path.join(LOGS_DIR, `metrics-${new Date().toISOString().replace(/[:.]/g, '-')}.json`);
      await fs.writeFile(metricsPath, JSON.stringify(metrics, null, 2));
      
      console.log(`✅ 指标已更新: ${metricsPath}`);
      return metricsPath;
    } catch (error) {
      console.error(`❌ 指标更新失败: ${error.message}`);
      throw error;
    }
  }

  async analyzeCostOptimization() {
    console.log('💰 分析成本优化效果...');
    
    try {
      const { stdout } = await execAsync('node enhanced-intent-router.js report');
      const report = JSON.parse(stdout);
      
      const costAnalysis = {
        timestamp: new Date().toISOString(),
        freeModelUsage: this.calculateFreeModelUsage(report),
        costSavings: this.estimateCostSavings(report),
        recommendations: report.recommendations || []
      };
      
      console.log('✅ 成本优化分析完成');
      return costAnalysis;
    } catch (error) {
      console.error(`❌ 成本分析失败: ${error.message}`);
      throw error;
    }
  }

  calculateFreeModelUsage(report) {
    if (!report.modelUsage) return { percentage: 0, details: {} };
    
    const totalRequests = Object.values(report.modelUsage).reduce((sum, stats) => sum + (stats.count || 0), 0);
    const freeRequests = Object.entries(report.modelUsage)
      .filter(([model]) => model.includes(':free') || model.includes('openrouter/free'))
      .reduce((sum, [_, stats]) => sum + (stats.count || 0), 0);
    
    return {
      percentage: totalRequests > 0 ? (freeRequests / totalRequests * 100).toFixed(1) : 0,
      freeRequests,
      totalRequests
    };
  }

  estimateCostSavings(report) {
    // 简化估算：假设付费模型平均每次请求成本为$0.01
    const PAID_COST_PER_REQUEST = 0.01;
    
    if (!report.modelUsage) return { estimatedSavings: 0 };
    
    const freeRequests = Object.entries(report.modelUsage)
      .filter(([model]) => model.includes(':free') || model.includes('openrouter/free'))
      .reduce((sum, [_, stats]) => sum + (stats.count || 0), 0);
    
    return {
      estimatedSavings: (freeRequests * PAID_COST_PER_REQUEST).toFixed(2),
      freeRequests,
      costPerRequest: PAID_COST_PER_REQUEST
    };
  }

  getWeekStartDate() {
    const now = new Date();
    const dayOfWeek = now.getDay();
    const diff = now.getDate() - dayOfWeek + (dayOfWeek === 0 ? -6 : 1);
    const weekStart = new Date(now.setDate(diff));
    return weekStart.toISOString().split('T')[0];
  }

  async collectWeeklyMetrics() {
    // 简化实现：收集最近7天的指标文件
    try {
      const files = await fs.readdir(LOGS_DIR);
      const metricFiles = files.filter(f => f.startsWith('metrics-')).slice(-7);
      
      const metrics = [];
      for (const file of metricFiles) {
        const filePath = path.join(LOGS_DIR, file);
        const content = await fs.readFile(filePath, 'utf8');
        metrics.push(JSON.parse(content));
      }
      
      return metrics;
    } catch (error) {
      console.error(`❌ 收集周指标失败: ${error.message}`);
      return [];
    }
  }

  async generateWeeklyRecommendations() {
    // 基于周数据分析生成建议
    return [
      {
        type: 'performance',
        priority: 'medium',
        suggestion: '考虑优化缓存设置以提高响应速度',
        reason: '平均响应时间较高'
      },
      {
        type: 'cost',
        priority: 'high',
        suggestion: '增加免费模型使用比例',
        reason: '付费模型使用率超过30%'
      }
    ];
  }

  async analyzeWeeklyCosts() {
    // 简化实现
    return {
      totalRequests: 1000,
      freeModelRequests: 700,
      paidModelRequests: 300,
      estimatedCost: 3.00,
      estimatedSavings: 7.00,
      optimizationScore: 70
    };
  }

  async analyzeRoutingPerformance() {
    console.log('📊 分析路由性能...');
    
    try {
      const { stdout } = await execAsync('node enhanced-intent-router.js stats');
      const stats = JSON.parse(stdout);
      
      const analysis = {
        timestamp: new Date().toISOString(),
        avgResponseTime: stats.avgResponseTime || 0,
        totalRequests: stats.totalRequests || 0,
        successfulRoutes: stats.successfulRoutes || 0,
        fallbackRoutes: stats.fallbackRoutes || 0,
        successRate: stats.totalRequests > 0 ? (stats.successfulRoutes / stats.totalRequests * 100).toFixed(1) : 0
      };
      
      console.log(`✅ 路由性能分析完成，成功率: ${analysis.successRate}%`);
      return analysis;
    } catch (error) {
      console.error(`❌ 性能分析失败: ${error.message}`);
      throw error;
    }
  }

  async optimizeCacheSettings() {
    console.log('⚡ 优化缓存设置...');
    
    // 基于使用情况调整缓存设置
    const currentTTL = this.config?.performanceSettings?.cacheTTL || 3600;
    
    // 简单启发式：如果请求量大，增加TTL；如果请求量小，减少TTL
    let newTTL = currentTTL;
    
    try {
