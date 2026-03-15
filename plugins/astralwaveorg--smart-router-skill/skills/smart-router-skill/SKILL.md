---
name: smart-router-skill
description: "Smart Router Skill"
---

# 智能路由器技能

## 概述

智能路由器是一个先进的模型调度系统，它超越了简单的关键词匹配，使用多维度分析来为每个消息选择最合适的模型。系统包含成本优化、自动模型扫描和性能监控功能。

## 功能特性

### 🎯 智能路由
- **多维度分析**：消息长度、内容复杂度、模式识别
- **动态模型选择**：基于任务类型自动选择最佳模型
- **成本感知**：优先使用免费模型，复杂任务才用付费模型
- **上下文感知**：考虑对话历史和用户偏好

### 💰 成本优化
- **预算控制**：设置每日/每月预算限制
- **自动降级**：简单任务自动使用免费模型
- **使用统计**：实时监控各模型成本
- **智能提醒**：成本接近阈值时预警

### 🔄 自动化管理
- **定期扫描**：自动发现OpenRouter免费模型
- **性能监控**：实时监控路由性能和系统健康
- **自动备份**：定期备份配置和日志
- **规则优化**：基于使用数据自动优化路由规则

## 安装和配置

### 前提条件
- OpenClaw 2026.2.13 或更高版本
- Node.js 18+ 
- OpenRouter API密钥（用于模型扫描）

### 快速安装

```bash
# 1. 复制技能文件到OpenClaw技能目录
cp -r smart-router-skill /opt/homebrew/lib/node_modules/openclaw/skills/

# 2. 更新OpenClaw配置以启用技能
openclaw config patch --json '{"skills":{"entries":{"smart-router":{"enabled":true}}}}'

# 3. 重启OpenClaw
openclaw gateway restart
```

### 详细安装步骤

1. **环境变量设置**：
```bash
export OPENROUTER_API_KEY="your-openrouter-api-key"
export DEEPSEEK_API_KEY="your-deepseek-api-key"
```

2. **初始化系统**：
```bash
cd /Users/nora/.openclaw/users/main/workspace
node enhanced-intent-router.js init
```

3. **运行集成测试**：
```bash
./test-integration.sh
```

4. **部署系统**：
```bash
node update-openclaw-config.js update
openclaw gateway restart
```

## 使用方法

### 基本路由

```javascript
// 使用智能路由器路由消息
const { SmartIntentRouter } = require('./enhanced-intent-router.js');

const router = new SmartIntentRouter();
await router.initialize();

const decision = router.analyzeMessage("帮我写一个Python函数");
console.log(decision);
// 输出: { agentId: 'code-agent', model: '4sapi-anthropic/claude-sonnet-4-5-20250929', ... }
```

### 命令行工具

```bash
# 初始化路由器
node enhanced-intent-router.js init

# 分析消息路由
node enhanced-intent-router.js analyze "你的消息"

# 运行测试用例
node enhanced-intent-router.js test

# 查看性能指标
node enhanced-intent-router.js stats

# 生成详细报告
node enhanced-intent-router.js report
```

### OpenClaw集成

系统自动集成到OpenClaw，无需手动调用。所有消息都会经过智能路由器处理。

## 配置说明

### 路由规则配置 (smart-router-config.json)

```json
{
  "routingRules": {
    "priority": [
      {
        "name": "代码相关任务",
        "conditions": {
          "keywords": ["代码", "编程", "Python", "Java"],
          "minLength": 10,
          "maxLength": 5000
        },
        "agent": "code-agent",
        "model": "4sapi-anthropic/claude-sonnet-4-5-20250929",
        "priority": 100
      }
    ],
    "fallback": {
      "agent": "free-agent",
      "model": "openrouter/google/gemma-3-27b-it:free"
    }
  },
  "costOptimization": {
    "budgetLimit": 10.0,
    "dailyLimit": 1.0,
    "preferFreeModels": true
  }
}
```

### 自定义路由规则

要添加新的路由规则：

1. 编辑 `smart-router-config.json`
2. 在 `routingRules.priority` 数组中添加新规则
3. 设置匹配条件和目标模型
4. 无需重启，系统支持热重载

## 定时任务

系统包含以下自动化定时任务：

| 任务名称 | 时间 | 描述 |
|---------|------|------|
| OpenRouter扫描 | 每天 6:00 | 扫描免费模型并更新配置 |
| 每日性能报告 | 每天 0:00 | 生成路由性能报告 |
| 每周成本分析 | 每周一 9:00 | 分析成本优化效果 |
| 配置备份 | 每天 23:30 | 备份配置和日志 |
| 规则优化检查 | 每天 12:00 | 检查并优化路由规则 |

## API参考

### SmartIntentRouter 类

```javascript
class SmartIntentRouter {
  // 初始化路由器
  async initialize()
  
  // 分析消息并返回路由决策
  analyzeMessage(message, context)
  
  // 获取性能指标
  getMetrics()
  
  // 生成详细报告
  generateReport()
}
```

### 路由决策对象

```javascript
{
  agentId: 'code-agent',           // 目标代理ID
  model: 'model-id',               // 选择的模型
  reasoning: false,                // 是否启用推理模式
  ruleName: '规则名称',             // 匹配的规则名称
  confidence: 0.95,                // 置信度 (0-1)
  reason: '匹配原因',               // 路由原因
  features: { ... },               // 消息特征分析
  costOptimized: true              // 是否成本优化
}
```

## 维护和管理

### 监控系统健康

```bash
# 检查系统状态
node smart-router-maintenance.js health

# 运行每日维护
node smart-router-maintenance.js daily

# 运行每周维护
node smart-router-maintenance.js weekly
```

### 备份和恢复

```bash
# 创建备份
node smart-router-maintenance.js backup

# 清理旧备份（保留30天）
node smart-router-maintenance.js clean-backups
```

### 故障排除

#### 路由器初始化失败
```bash
# 检查配置文件
node enhanced-intent-router.js init

# 查看详细错误
OPENCLAW_DEBUG=1 node enhanced-intent-router.js init
```

#### 路由决策不准确
1. 检查路由规则配置
2. 查看路由日志分析模式
3. 调整规则优先级和条件

#### OpenRouter扫描失败
```bash
# 检查API密钥
echo $OPENROUTER_API_KEY

# 手动运行扫描器
node openrouter-scanner.js
```

## 性能优化

### 缓存设置
系统使用智能缓存减少重复计算。默认缓存TTL为3600秒，可根据使用情况调整：

```json
{
  "performanceSettings": {
    "cacheEnabled": true,
    "cacheTTL": 3600,
    "maxResponseTime": 30000
  }
}
```

### 规则优化建议
1. 将高频规则放在前面
2. 使用更精确的匹配条件
3. 定期分析路由日志优化规则
4. 根据使用数据调整规则优先级

## 安全注意事项

1. **API密钥保护**：确保所有API密钥安全存储
2. **配置备份**：定期备份路由器配置
3. **访问控制**：限制对配置文件的访问
4. **日志管理**：定期清理敏感日志信息

## 扩展开发

### 添加新功能
1. 在 `enhanced-intent-router.js` 中添加新功能
2. 更新配置文件
3. 运行测试验证
4. 部署到生产环境

### 自定义分析器
可以扩展 `analyzeMessage` 方法添加自定义分析逻辑：

```javascript
class CustomRouter extends SmartIntentRouter {
  analyzeMessage(message, context) {
    // 自定义分析逻辑
    const features = this.extractCustomFeatures(message);
    
    // 调用父类方法
    return super.analyzeMessage(message, { ...context, customFeatures: features });
  }
}
```

## 支持与反馈

如有问题或建议：

1. 查看路由日志分析问题
2. 检查系统指标识别瓶颈
3. 调整配置参数优化性能
4. 联系系统管理员获取支持

## 版本历史

### v1.0.0 (2026-02-15)
- 初始版本发布
- 智能多维度路由
- 成本优化系统
- OpenRouter自动扫描
- 完整的维护工具

---

**技能作者**：OpenClaw AI  
**最后更新**：2026-02-15  
**许可证**：MIT  
**状态**：生产就绪 ✅