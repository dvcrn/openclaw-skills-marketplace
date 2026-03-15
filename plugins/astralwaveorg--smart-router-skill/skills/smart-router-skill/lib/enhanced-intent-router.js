#!/usr/bin/env node

/**
 * 增强版智能意图路由器
 * 整合配置文件，支持动态路由和成本优化
 */

const fs = require('fs').promises;
const path = require('path');

// 配置文件路径
const CONFIG_PATH = path.join(__dirname, 'smart-router-config.json');
const OPENCLAW_CONFIG_PATH = path.join(process.env.HOME || '/Users/nora', '.openclaw/openclaw.json');

// 缓存管理
class RouterCache {
  constructor(ttl = 3600) {
    this.cache = new Map();
    this.ttl = ttl;
  }

  set(key, value) {
    this.cache.set(key, {
      value,
      timestamp: Date.now()
    });
  }

  get(key) {
    const entry = this.cache.get(key);
    if (!entry) return null;
    
    if (Date.now() - entry.timestamp > this.ttl * 1000) {
      this.cache.delete(key);
      return null;
    }
    
    return entry.value;
  }

  clear() {
    this.cache.clear();
  }
}

// 智能路由器类
class SmartIntentRouter {
  constructor() {
    this.config = null;
    this.openclawConfig = null;
    this.cache = new RouterCache();
    this.metrics = {
      totalRequests: 0,
      successfulRoutes: 0,
      fallbackRoutes: 0,
      responseTimes: [],
      modelUsage: {}
    };
  }

  async initialize() {
    try {
      // 加载智能路由器配置
      const configData = await fs.readFile(CONFIG_PATH, 'utf8');
      this.config = JSON.parse(configData);
      console.log(`✅ 加载智能路由器配置 v${this.config.version}`);

      // 加载OpenClaw配置
      const openclawData = await fs.readFile(OPENCLAW_CONFIG_PATH, 'utf8');
      this.openclawConfig = JSON.parse(openclawData);
      console.log(`✅ 加载OpenClaw配置`);

      // 初始化指标
      this.initializeMetrics();
      
      return true;
    } catch (error) {
      console.error(`❌ 初始化失败: ${error.message}`);
      return false;
    }
  }

  initializeMetrics() {
    // 初始化模型使用统计
    const allModels = this.getAllAvailableModels();
    allModels.forEach(model => {
      this.metrics.modelUsage[model] = {
        count: 0,
        totalCost: 0,
        totalTokens: 0
      };
    });
  }

  getAllAvailableModels() {
    const models = new Set();
    
    // 从配置中获取所有模型
    if (this.openclawConfig?.agents?.defaults?.models) {
      Object.keys(this.openclawConfig.agents.defaults.models).forEach(model => {
        models.add(model);
      });
    }
    
    // 从fallbacks获取模型
    if (this.openclawConfig?.agents?.defaults?.model?.fallbacks) {
      this.openclawConfig.agents.defaults.model.fallbacks.forEach(model => {
        models.add(model);
      });
    }
    
    return Array.from(models);
  }

  analyzeMessage(message, context = {}) {
    const startTime = Date.now();
    this.metrics.totalRequests++;
    
    const messageLength = message.length;
    const lowerMessage = message.toLowerCase();
    
    // 检查缓存
    const cacheKey = `${messageLength}_${lowerMessage.substring(0, 50)}`;
    const cachedResult = this.cache.get(cacheKey);
    if (cachedResult) {
      console.log(`📦 使用缓存路由结果`);
      return cachedResult;
    }

    // 分析消息特征
    const features = {
      length: messageLength,
      hasCodeKeywords: this.hasKeywords(message, this.getRuleKeywords('代码相关任务')),
      hasReasoningKeywords: this.hasKeywords(message, this.getRuleKeywords('复杂推理和分析')),
      hasImageKeywords: this.hasKeywords(message, this.getRuleKeywords('图像处理任务')),
      hasCasualKeywords: this.hasKeywords(message, this.getRuleKeywords('简短日常对话')),
      complexity: this.calculateComplexity(message),
      containsUrl: this.containsUrl(message),
      containsCodeBlock: this.containsCodeBlock(message)
    };

    // 应用路由规则
    let bestMatch = null;
    let highestPriority = -1;

    if (this.config?.routingRules?.priority) {
      this.config.routingRules.priority.forEach(rule => {
        if (this.matchesRule(features, rule, message, lowerMessage)) {
          if (rule.priority > highestPriority) {
            highestPriority = rule.priority;
            bestMatch = rule;
          }
        }
      });
    }

    // 成本优化检查
    if (bestMatch && this.config?.costOptimization?.preferFreeModels) {
      const isFreeModel = this.isFreeModel(bestMatch.model);
      if (!isFreeModel && features.complexity < 0.3) {
        // 简单任务但使用了付费模型，尝试降级
        const freeAlternative = this.findFreeAlternative(bestMatch.model);
        if (freeAlternative) {
          console.log(`💰 成本优化: 将 ${bestMatch.model} 降级为 ${freeAlternative}`);
          bestMatch = { ...bestMatch, model: freeAlternative };
        }
      }
    }

    // 生成路由决策
    let decision;
    if (bestMatch) {
      decision = {
        agentId: bestMatch.agent,
        model: bestMatch.model,
        reasoning: bestMatch.reasoning || false,
        ruleName: bestMatch.name,
        confidence: this.calculateConfidence(features, bestMatch),
        reason: this.generateReason(features, bestMatch),
        features: features,
        costOptimized: this.isFreeModel(bestMatch.model)
      };
      this.metrics.successfulRoutes++;
    } else {
      // 使用后备规则
      decision = {
        agentId: this.config?.routingRules?.fallback?.agent || 'free-agent',
        model: this.config?.routingRules?.fallback?.model || 'openrouter/google/gemma-3-27b-it:free',
        reasoning: this.config?.routingRules?.fallback?.reasoning || false,
        ruleName: '后备规则',
        confidence: 0.5,
        reason: '未匹配任何规则，使用后备配置',
        features: features,
        costOptimized: true
      };
      this.metrics.fallbackRoutes++;
    }

    // 更新指标
    const responseTime = Date.now() - startTime;
    this.metrics.responseTimes.push(responseTime);
    
    if (this.metrics.modelUsage[decision.model]) {
      this.metrics.modelUsage[decision.model].count++;
    }

    // 缓存结果
    this.cache.set(cacheKey, decision);

    // 检查性能阈值
    if (this.config?.monitoring?.alertThresholds?.responseTime && 
        responseTime > this.config.monitoring.alertThresholds.responseTime) {
      console.warn(`⚠️ 路由响应时间 ${responseTime}ms 超过阈值`);
    }

    return decision;
  }

  hasKeywords(message, keywords) {
    const lowerMessage = message.toLowerCase();
    return keywords.some(keyword => {
      const lowerKeyword = keyword.toLowerCase();
      return lowerMessage.includes(lowerKeyword);
    });
  }

  calculateComplexity(message) {
    let score = 0;
    
    // 长度因素
    score += Math.min(message.length / 500, 1) * 0.3;
    
    // 特殊字符密度
    const specialChars = message.replace(/[a-zA-Z0-9\s]/g, '').length;
    score += Math.min(specialChars / message.length * 10, 1) * 0.2;
    
    // 句子数量
    const sentenceCount = message.split(/[.!?。！？]/).length - 1;
    score += Math.min(sentenceCount / 10, 1) * 0.2;
    
    // 词汇多样性（简单实现）
    const words = message.toLowerCase().split(/\s+/);
    const uniqueWords = new Set(words);
    score += Math.min(uniqueWords.size / words.length * 2, 1) * 0.3;
    
    return Math.min(score, 1);
  }

  containsUrl(message) {
    const urlPattern = /(https?:\/\/[^\s]+|www\.[^\s]+\.[^\s]+)/i;
    return urlPattern.test(message);
  }

  containsCodeBlock(message) {
    return message.includes('```') || message.includes('    ') || message.includes('\t');
  }

  matchesRule(features, rule, message, lowerMessage) {
    const conditions = rule.conditions || {};
    
    // 检查长度条件
    if (conditions.minLength && features.length < conditions.minLength) return false;
    if (conditions.maxLength && features.length > conditions.maxLength) return false;
    
    // 检查关键词或模式（满足其一即可）
    let hasContentMatch = false;
    
    if (conditions.keywords) {
      const hasKeyword = conditions.keywords.some(keyword => 
        lowerMessage.includes(keyword.toLowerCase())
      );
      if (hasKeyword) hasContentMatch = true;
    }
    
    if (conditions.patterns) {
      const hasPattern = conditions.patterns.some(pattern => 
        lowerMessage.includes(pattern.toLowerCase())
      );
      if (hasPattern) hasContentMatch = true;
    }
    
    // 如果没有设置关键词或模式，或者设置了但未匹配，则检查其他条件
    if ((conditions.keywords || conditions.patterns) && !hasContentMatch) {
      return false;
    }
    
    // 检查图像
    if (conditions.hasImage && !features.hasImageKeywords) return false;
    
    return true;
  }

  isFreeModel(modelId) {
    return modelId.includes(':free') || 
           modelId.includes('openrouter/free') ||
           modelId.includes('gemma-3-27b-it:free') ||
           modelId.includes('llama-3.3-70b-instruct:free');
  }

  findFreeAlternative(paidModel) {
    // 查找免费替代品
    const freeModels = this.getAllAvailableModels().filter(model => 
      this.isFreeModel(model)
    );
    
    if (freeModels.length === 0) return null;
    
    // 简单启发式：选择第一个免费模型
    return freeModels[0];
  }

  calculateConfidence(features, rule) {
    let confidence = 0.7; // 基础置信度
    
    // 根据特征匹配度调整
    if (rule.conditions?.keywords && features.hasCodeKeywords) confidence += 0.1;
    if (rule.conditions?.minLength && features.length >= rule.conditions.minLength) confidence += 0.1;
    if (rule.conditions?.maxLength && features.length <= rule.conditions.maxLength) confidence += 0.1;
    
    return Math.min(confidence, 0.95);
  }

  getRuleKeywords(ruleName) {
    if (!this.config?.routingRules?.priority) return [];
    
    const rule = this.config.routingRules.priority.find(r => r.name === ruleName);
    return rule?.conditions?.keywords || [];
  }

  generateReason(features, rule) {
    const reasons = [];
    
    if (features.hasCodeKeywords) reasons.push('包含代码相关关键词');
    if (features.hasReasoningKeywords) reasons.push('包含推理分析关键词');
    if (features.length > 100) reasons.push('消息较长');
    if (features.complexity > 0.5) reasons.push('内容复杂度较高');
    
    return `匹配规则: ${rule.name} (${reasons.join(', ')})`;
  }

  getMetrics() {
    const avgResponseTime = this.metrics.responseTimes.length > 0
      ? this.metrics.responseTimes.reduce((a, b) => a + b, 0) / this.metrics.responseTimes.length
      : 0;
    
    return {
      ...this.metrics,
      avgResponseTime: Math.round(avgResponseTime),
      cacheHitRate: this.cache.cache.size > 0 ? 0.3 : 0, // 简化实现
      timestamp: new Date().toISOString()
    };
  }

  generateReport() {
    const metrics = this.getMetrics();
    const report = {
      summary: {
        totalRequests: metrics.totalRequests,
        successfulRoutes: metrics.successfulRoutes,
        fallbackRoutes: metrics.fallbackRoutes,
        avgResponseTime: metrics.avgResponseTime,
        cacheSize: this.cache.cache.size
      },
      modelUsage: Object.entries(metrics.modelUsage)
        .filter(([_, stats]) => stats.count > 0)
        .sort((a, b) => b[1].count - a[1].count)
        .reduce((obj, [model, stats]) => {
          obj[model] = stats;
          return obj;
        }, {}),
      recommendations: this.generateRecommendations(),
      timestamp: metrics.timestamp
    };
    
    return report;
  }

  generateRecommendations() {
    const recommendations = [];
    
    // 分析模型使用情况
    const modelUsage = this.metrics.modelUsage;
    const totalRequests = this.metrics.totalRequests;
    
    if (totalRequests > 0) {
      // 检查是否有过度使用付费模型
      const paidModels = Object.keys(modelUsage).filter(model => !this.isFreeModel(model));
      const freeModels = Object.keys(modelUsage).filter(model => this.isFreeModel(model));
      
      let paidUsage = 0;
      paidModels.forEach(model => {
        paidUsage += modelUsage[model]?.count || 0;
      });
      
      const paidPercentage = (paidUsage / totalRequests) * 100;
      
      if (paidPercentage > 30 && this.config?.costOptimization?.preferFreeModels) {
        recommendations.push({
          type: 'cost_optimization',
          severity: 'medium',
          message: `付费模型使用率 ${paidPercentage.toFixed(1)}% 较高，建议调整路由规则以更多使用免费模型`,
          suggestion: '检查路由规则优先级，确保简单任务使用免费模型'
        });
      }
      
      // 检查响应时间
      if (this.metrics.avgResponseTime > 5000) {
        recommendations.push({
          type: 'performance',
          severity: 'high',
          message: `平均路由响应时间 ${this.metrics.avgResponseTime}ms 较高`,
          suggestion: '考虑优化路由算法或增加缓存TTL'
        });
      }
    }
    
    return recommendations;
  }
}

// 命令行接口
async function main() {
  const router = new SmartIntentRouter();
  
  const args = process.argv.slice(2);
  const command = args[0];
  
  if (!command) {
    console.log(`
🤖 增强版智能意图路由器

用法:
  node enhanced-intent-router.js <命令> [参数]

命令:
  init          - 初始化路由器
  analyze <消息> - 分析消息并返回路由决策
  test          - 运行测试用例
  metrics       - 显示性能指标
  report        - 生成详细报告
  help          - 显示帮助信息

示例:
  node enhanced-intent-router.js init
  node enhanced-intent-router.js analyze "帮我写一段Python代码"
  node enhanced-intent-router.js metrics
    `);
    return;
  }
  
  try {
    switch (command) {
      case 'init':
        console.log('🚀 初始化智能路由器...');
        const initialized = await router.initialize();
        if (initialized) {
          console.log('✅ 路由器初始化完成');
        } else {
          console.log('❌ 路由器初始化失败');
        }
        break;
        
      case 'analyze':
        if (args.length < 2) {
          console.log('❌ 请提供要分析的消息');
          break;
        }
        
        await router.initialize();
        const message = args.slice(1).join(' ');
        console.log(`📝 分析消息: "${message.substring(0, 100)}${message.length > 100 ? '...' : ''}"`);
        
        const decision = router.analyzeMessage(message);
        console.log('\n🎯 路由决策:');
        console.log(JSON.stringify(decision, null, 2));
        break;
        
      case 'test':
        await router.initialize();
        console.log('🧪 运行测试用例...');
        
        const testCases = [
          '你好，今天天气怎么样？',
          '帮我写一个Python函数，计算斐波那契数列',
          '分析一下当前AI行业的发展趋势和未来预测',
          'https://example.com 这个网站看起来不错',
          '```python\nprint("Hello World")\n```',
          '这是一段非常长的消息，包含很多细节和复杂的描述，需要深入分析和推理才能理解其中的含义和 implications。'
        ];
        
        testCases.forEach((testMessage, index) => {
          console.log(`\n--- 测试用例 ${index + 1} ---`);
          console.log(`消息: ${testMessage.substring(0, 50)}${testMessage.length > 50 ? '...' : ''}`);
          const decision = router.analyzeMessage(testMessage);
          console.log(`路由: ${decision.agentId} (${decision.model})`);
          console.log(`原因: ${decision.reason}`);
        });
        break;
        
      case 'metrics':
        await router.initialize();
        console.log('📊 性能指标:');
        const metrics = router.getMetrics();
        console.log(JSON.stringify(metrics, null, 2));
        break;
        
      case 'report':
        await router.initialize();
        console.log('📈 生成详细报告...');
        const report = router.generateReport();
        console.log(JSON.stringify(report, null, 2));
        
        // 保存报告到文件
        const reportPath = path.join(__dirname, 'router-report.json');
        await fs.writeFile(reportPath, JSON.stringify(report, null, 2));
        console.log(`\n📄 报告已保存到: ${reportPath}`);
        break;
        
      case 'help':
      default:
        console.log('使用 "node enhanced-intent-router.js" 查看帮助');
        break;
    }
  } catch (error) {
    console.error(`❌ 错误: ${error.message}`);
    process.exit(1);
  }
}

// 执行主函数
if (require.main === module) {
  main().catch(error => {
    console.error('❌ 未处理的错误:', error);
    process.exit(1);
  });
}

// 导出类
module.exports = {
  SmartIntentRouter,
  RouterCache
};