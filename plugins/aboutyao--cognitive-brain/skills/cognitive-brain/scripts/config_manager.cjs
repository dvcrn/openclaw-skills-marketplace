#!/usr/bin/env node
/**
 * Cognitive Brain - 配置管理器
 * 支持热重载和配置验证
 */

const fs = require('fs');
const path = require('path');

const SKILL_DIR = path.dirname(__dirname);
const CONFIG_PATH = path.join(SKILL_DIR, 'config.json');

// 配置缓存
let configCache = null;
let lastModified = 0;

/**
 * 获取配置（自动检测变更）
 */
function getConfig() {
  const stat = fs.statSync(CONFIG_PATH);
  const modified = stat.mtimeMs;
  
  if (modified > lastModified || !configCache) {
    configCache = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
    lastModified = modified;
    console.log('🔄 配置已重新加载');
  }
  
  return configCache;
}

/**
 * 更新配置
 */
function updateConfig(updates) {
  const config = getConfig();
  const newConfig = deepMerge(config, updates);
  
  // 验证
  validateConfig(newConfig);
  
  // 保存
  fs.writeFileSync(CONFIG_PATH, JSON.stringify(newConfig, null, 2));
  
  // 清除缓存
  configCache = null;
  
  console.log('✅ 配置已更新');
  return newConfig;
}

/**
 * 深度合并
 */
function deepMerge(target, source) {
  const result = { ...target };
  
  for (const key in source) {
    if (source[key] instanceof Object && !Array.isArray(source[key])) {
      result[key] = deepMerge(result[key] || {}, source[key]);
    } else {
      result[key] = source[key];
    }
  }
  
  return result;
}

/**
 * 验证配置
 */
function validateConfig(config) {
  const errors = [];
  
  // 检查必要字段
  if (!config.storage?.primary?.host) {
    errors.push('缺少数据库主机配置');
  }
  
  if (!config.storage?.primary?.database) {
    errors.push('缺少数据库名称配置');
  }
  
  if (errors.length > 0) {
    throw new Error('配置验证失败:\n' + errors.join('\n'));
  }
  
  return true;
}

/**
 * 显示当前配置
 */
function showConfig() {
  const config = getConfig();
  
  console.log('📋 当前配置\n');
  
  // 数据库配置（脱敏）
  console.log('数据库:');
  console.log(`  主机: ${config.storage.primary.host}`);
  console.log(`  端口: ${config.storage.primary.port}`);
  console.log(`  数据库: ${config.storage.primary.database}`);
  console.log(`  用户: ${config.storage.primary.user}`);
  
  // Redis 配置
  if (config.cache?.redis) {
    console.log('\nRedis:');
    console.log(`  主机: ${config.cache.redis.host}`);
    console.log(`  前缀: ${config.cache.redis.prefix}`);
  }
  
  // 功能开关
  if (config.features) {
    console.log('\n功能:');
    Object.entries(config.features).forEach(([k, v]) => {
      console.log(`  ${k}: ${v ? '✅' : '❌'}`);
    });
  }
}

/**
 * 重置为默认配置
 */
function resetConfig() {
  const defaultConfig = {
    storage: {
      primary: {
        host: 'localhost',
        port: 5432,
        database: 'cognitive_brain',
        user: 'postgres',
        password: 'postgres'
      }
    },
    cache: {
      redis: {
        host: 'localhost',
        port: 6379,
        prefix: 'brain:'
      }
    },
    features: {
      enableEmbedding: true,
      enableReflection: true,
      enablePrediction: true
    }
  };
  
  fs.writeFileSync(CONFIG_PATH, JSON.stringify(defaultConfig, null, 2));
  configCache = null;
  
  console.log('✅ 配置已重置为默认值');
}

// 命令行接口
if (require.main === module) {
  const args = process.argv.slice(2);
  const action = args[0];
  
  switch (action) {
    case 'show':
      showConfig();
      break;
    case 'set':
      const key = args[1];
      const value = args[2];
      if (!key || !value) {
        console.log('用法: node config_manager.cjs set <key> <value>');
        break;
      }
      try {
        const parsed = JSON.parse(value);
        updateConfig({ [key]: parsed });
      } catch {
        updateConfig({ [key]: value });
      }
      break;
    case 'reset':
      resetConfig();
      break;
    default:
      console.log(`
配置管理器

用法:
  node config_manager.cjs show          显示当前配置
  node config_manager.cjs set <k> <v>   设置配置项
  node config_manager.cjs reset         重置为默认值
`);
  }
}

module.exports = { getConfig, updateConfig, validateConfig };
