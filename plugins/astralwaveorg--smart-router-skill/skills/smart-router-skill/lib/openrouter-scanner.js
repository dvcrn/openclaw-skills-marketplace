#!/usr/bin/env node

/**
 * OpenRouter免费模型扫描器
 * 定期扫描OpenRouter的免费模型，并更新OpenClaw配置
 */

const fs = require('fs').promises;
const path = require('path');
const https = require('https');

// OpenRouter API配置
const OPENROUTER_API_URL = 'https://openrouter.ai/api/v1/models';
const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY;

// OpenClaw配置路径
const OPENCLAW_CONFIG_PATH = path.join(process.env.HOME || '/Users/nora', '.openclaw/openclaw.json');

// 免费模型筛选条件
const FREE_MODEL_CRITERIA = {
  pricing: {
    prompt: 0,
    completion: 0,
    request: 0
  },
  // 优先考虑的模型提供商
  preferredProviders: ['google', 'meta-llama', 'qwen', 'microsoft', 'mistralai'],
  // 最小上下文窗口
  minContextWindow: 4000,
  // 支持的输入类型
  supportedInputs: ['text', 'image']
};

async function fetchOpenRouterModels() {
  return new Promise((resolve, reject) => {
    const options = {
      headers: {
        'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
        'Content-Type': 'application/json'
      }
    };

    https.get(OPENROUTER_API_URL, options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const response = JSON.parse(data);
          resolve(response.data || []);
        } catch (error) {
          reject(new Error(`Failed to parse response: ${error.message}`));
        }
      });
    }).on('error', (error) => {
      reject(new Error(`HTTP request failed: ${error.message}`));
    });
  });
}

function isFreeModel(model) {
  if (!model.pricing) return false;
  
  const { prompt, completion, request } = model.pricing;
  return prompt === 0 && completion === 0 && request === 0;
}

function meetsCriteria(model) {
  // 检查是否免费
  if (!isFreeModel(model)) return false;
  
  // 检查上下文窗口
  if (model.context_length && model.context_length < FREE_MODEL_CRITERIA.minContextWindow) {
    return false;
  }
  
  // 检查输入类型支持
  if (model.architecture && model.architecture.input_modalities) {
    const hasTextSupport = model.architecture.input_modalities.includes('text');
    if (!hasTextSupport) return false;
  }
  
  return true;
}

function calculateModelScore(model) {
  let score = 100;
  
  // 提供商优先级
  const provider = model.id.split('/')[0];
  if (FREE_MODEL_CRITERIA.preferredProviders.includes(provider)) {
    score += 50;
  }
  
  // 上下文窗口越大越好
  if (model.context_length) {
    score += Math.min(model.context_length / 1000, 100);
  }
  
  // 支持图像输入加分
  if (model.architecture && model.architecture.input_modalities) {
    if (model.architecture.input_modalities.includes('image')) {
      score += 30;
    }
  }
  
  // 推理能力加分
  if (model.id.includes('thinking') || model.id.includes('reason')) {
    score += 40;
  }
  
  // 热门模型加分
  if (model.top_provider && model.top_provider.requests_per_day > 1000) {
    score += 20;
  }
  
  return score;
}

function convertToOpenClawModel(model) {
  const modelId = model.id;
  const provider = modelId.split('/')[0];
  const modelName = modelId.split('/')[1] || modelId;
  
  return {
    id: modelId,
    name: `${model.name || modelName} (免费)`,
    reasoning: modelId.includes('thinking') || modelId.includes('reason'),
    input: model.architecture?.input_modalities?.includes('image') 
      ? ['text', 'image'] 
      : ['text'],
    cost: {
      input: 0,
      output: 0,
      cacheRead: 0,
      cacheWrite: 0
    },
    contextWindow: model.context_length || 4000,
    maxTokens: 4096
  };
}

async function updateOpenClawConfig(freeModels) {
  try {
    const configData = await fs.readFile(OPENCLAW_CONFIG_PATH, 'utf8');
    const config = JSON.parse(configData);
    
    // 确保openrouter配置存在
    if (!config.models.providers.openrouter) {
      config.models.providers.openrouter = {
        baseUrl: 'https://openrouter.ai/api/v1',
        apiKey: '${OPENROUTER_API_KEY}',
        api: 'openai-completions',
        models: []
      };
    }
    
    // 更新模型列表
    const openrouterModels = freeModels.map(convertToOpenClawModel);
    config.models.providers.openrouter.models = openrouterModels;
    
    // 更新agents.defaults.fallbacks
    const topModels = freeModels
      .sort((a, b) => calculateModelScore(b) - calculateModelScore(a))
      .slice(0, 5)
      .map(model => `openrouter/${model.id}`);
    
    // 确保fallbacks包含免费模型
    const currentFallbacks = config.agents.defaults.model.fallbacks || [];
    const newFallbacks = [...new Set([...topModels, ...currentFallbacks])];
    config.agents.defaults.model.fallbacks = newFallbacks;
    
    // 更新models配置
    if (!config.agents.defaults.models) {
      config.agents.defaults.models = {};
    }
    
    // 为每个免费模型添加配置
    freeModels.forEach(model => {
      const modelKey = `openrouter/${model.id}`;
      if (!config.agents.defaults.models[modelKey]) {
        config.agents.defaults.models[modelKey] = {};
      }
    });
    
    // 保存配置
    await fs.writeFile(OPENCLAW_CONFIG_PATH, JSON.stringify(config, null, 2));
    
    return {
      success: true,
      modelsAdded: openrouterModels.length,
      topModels: topModels
    };
  } catch (error) {
    throw new Error(`Failed to update OpenClaw config: ${error.message}`);
  }
}

async function main() {
  console.log('🚀 开始扫描OpenRouter免费模型...');
  
  if (!OPENROUTER_API_KEY) {
    console.error('❌ 错误: OPENROUTER_API_KEY环境变量未设置');
    process.exit(1);
  }
  
  try {
    // 1. 获取所有模型
    console.log('📡 从OpenRouter获取模型列表...');
    const allModels = await fetchOpenRouterModels();
    console.log(`✅ 获取到 ${allModels.length} 个模型`);
    
    // 2. 筛选免费模型
    console.log('🔍 筛选免费模型...');
    const freeModels = allModels.filter(meetsCriteria);
    console.log(`✅ 找到 ${freeModels.length} 个免费模型`);
    
    // 3. 计算模型评分
    const scoredModels = freeModels.map(model => ({
      model,
      score: calculateModelScore(model)
    }));
    
    // 4. 按评分排序
    scoredModels.sort((a, b) => b.score - a.score);
    
    // 5. 显示结果
    console.log('\n🏆 推荐的免费模型:');
    scoredModels.slice(0, 10).forEach((item, index) => {
      const model = item.model;
      console.log(`${index + 1}. ${model.id} (评分: ${Math.round(item.score)})`);
      console.log(`   名称: ${model.name}`);
      console.log(`   上下文: ${model.context_length || '未知'} tokens`);
      console.log(`   提供商: ${model.id.split('/')[0]}`);
      console.log(`   输入: ${model.architecture?.input_modalities?.join(', ') || 'text'}`);
      console.log('');
    });
    
    // 6. 更新OpenClaw配置
    console.log('⚙️ 更新OpenClaw配置...');
    const updateResult = await updateOpenClawConfig(freeModels);
    
    console.log(`✅ 配置更新完成!`);
    console.log(`   添加了 ${updateResult.modelsAdded} 个模型`);
    console.log(`   推荐的模型: ${updateResult.topModels.join(', ')}`);
    
    // 7. 生成报告
    const report = {
      timestamp: new Date().toISOString(),
      totalModels: allModels.length,
      freeModels: freeModels.length,
      topModels: scoredModels.slice(0, 5).map(item => ({
        id: item.model.id,
        name: item.model.name,
        score: Math.round(item.score),
        contextLength: item.model.context_length
      })),
      configUpdated: updateResult.success
    };
    
    const reportPath = path.join(path.dirname(OPENCLAW_CONFIG_PATH), 'openrouter-scan-report.json');
    await fs.writeFile(reportPath, JSON.stringify(report, null, 2));
    console.log(`📊 报告已保存到: ${reportPath}`);
    
  } catch (error) {
    console.error(`❌ 扫描失败: ${error.message}`);
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

module.exports = {
  fetchOpenRouterModels,
  isFreeModel,
  meetsCriteria,
  calculateModelScore,
  convertToOpenClawModel,
  updateOpenClawConfig
};