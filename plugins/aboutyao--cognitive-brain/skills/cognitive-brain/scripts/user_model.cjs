#!/usr/bin/env node
const { resolveModule } = require('./module_resolver.cjs');
/**
 * Cognitive Brain - 用户建模模块
 * 构建和维护用户画像
 */

const fs = require('fs');
const path = require('path');

const HOME = process.env.HOME || '/root';
const SKILL_DIR = path.join(HOME, '.openclaw/workspace/skills/cognitive-brain');
const CONFIG_PATH = path.join(SKILL_DIR, 'config.json');
const USER_MODEL_PATH = path.join(SKILL_DIR, '.user-model.json');

// 用户模型
const userModel = {
  // 基本信息
  basic: {
    name: null,
    preferredName: null,
    timezone: null,
    language: 'zh-CN',
    communicationStyle: 'casual' // casual, formal, technical
  },

  // 偏好
  preferences: {
    topics: {},           // { topic: interest_score }
    communicationTone: 'friendly',
    responseLength: 'medium', // short, medium, long
    levelOfDetail: 'balanced', // brief, balanced, detailed
    proactivity: 'moderate'    // passive, moderate, proactive
  },

  // 行为模式
  patterns: {
    activeHours: [],      // 活跃时段
    commonTasks: {},      // 常见任务
    interactionFrequency: 0,
    avgSessionLength: 0
  },

  // 知识水平
  knowledge: {
    knownConcepts: [],
    expertiseAreas: [],
    learningInterests: []
  },

  // 统计
  stats: {
    totalInteractions: 0,
    lastInteraction: null,
    sessions: []
  },

  // 新增：任务偏好
  taskPreferences: {
    completedTasks: [],      // 完成的任务历史
    taskPatterns: {},        // 任务模式 { taskType: { count, avgDuration, successRate } }
    preferredTools: {},      // 偏好工具
    taskSequencePatterns: [] // 任务序列模式
  },

  // 新增：情绪模式
  emotionPatterns: {
    history: [],             // 情绪历史 [{ timestamp, emotion, context }]
    dominantEmotions: {},    // 主导情绪统计
    emotionTriggers: {},     // 情绪触发因素
    emotionalTrend: 'stable' // 情绪趋势
  },

  // 新增：常用表达
  commonExpressions: {
    phrases: {},             // 常用短语 { phrase: count }
    greetings: [],           // 常用问候语
    questions: [],           // 常问问题
    commands: []             // 常用命令
  },

  // 新增：交互历史
  interactionHistory: {
    recentInteractions: [],  // 最近交互
    lastTopics: [],          // 最近话题
    contextSwitches: 0       // 上下文切换次数
  }
};

/**
 * 加载用户模型
 */
function load() {
  try {
    if (fs.existsSync(USER_MODEL_PATH)) {
      const data = JSON.parse(fs.readFileSync(USER_MODEL_PATH, 'utf8'));
      Object.assign(userModel, data);
    }
  } catch (e) {
    console.warn('[user-model] Load failed:', e.message);
  }
}

/**
 * 保存用户模型
 */
function save() {
  try {
    fs.writeFileSync(USER_MODEL_PATH, JSON.stringify(userModel, null, 2));
  } catch (e) {
    console.warn('[user-model] Save failed:', e.message);
  }
}

/**
 * 更新基本信息
 */
function updateBasic(info) {
  Object.assign(userModel.basic, info);
  save();
}

/**
 * 记录兴趣
 */
function recordInterest(topic, delta = 0.1) {
  if (!userModel.preferences.topics[topic]) {
    userModel.preferences.topics[topic] = 0;
  }
  userModel.preferences.topics[topic] = Math.min(1,
    Math.max(0, userModel.preferences.topics[topic] + delta)
  );
  save();
}

/**
 * 获取用户偏好
 */
function getPreferences() {
  return {
    ...userModel.preferences,
    topInterests: Object.entries(userModel.preferences.topics)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([topic, score]) => ({ topic, score }))
  };
}

/**
 * 记录交互
 */
function recordInteraction(metadata = {}) {
  userModel.stats.totalInteractions++;
  userModel.stats.lastInteraction = Date.now();

  // 记录活跃时段
  const hour = new Date().getHours();
  const activeHours = userModel.patterns.activeHours;
  if (!activeHours.includes(hour)) {
    activeHours.push(hour);
    activeHours.sort();
  }

  // 记录常见任务
  if (metadata.task) {
    userModel.patterns.commonTasks[metadata.task] =
      (userModel.patterns.commonTasks[metadata.task] || 0) + 1;
  }

  // 记录话题兴趣
  if (metadata.topic) {
    recordInterest(metadata.topic, 0.1);
  }

  save();
}

/**
 * 记录会话
 */
function recordSession(duration, interactions) {
  userModel.stats.sessions.push({
    startedAt: Date.now() - duration,
    endedAt: Date.now(),
    duration,
    interactions
  });

  // 保留最近 30 天的会话
  const cutoff = Date.now() - 30 * 24 * 60 * 60 * 1000;
  userModel.stats.sessions = userModel.stats.sessions
    .filter(s => s.startedAt > cutoff);

  // 更新平均会话长度
  const avgLength = userModel.stats.sessions
    .reduce((sum, s) => sum + s.duration, 0) / userModel.stats.sessions.length;
  userModel.patterns.avgSessionLength = avgLength;
  userModel.patterns.interactionFrequency = userModel.stats.sessions.length;

  save();
}

/**
 * 新增：记录任务偏好
 */
function recordTaskPreference(taskType, duration, success, tools = []) {
  // 更新任务模式
  if (!userModel.taskPreferences.taskPatterns[taskType]) {
    userModel.taskPreferences.taskPatterns[taskType] = {
      count: 0,
      avgDuration: 0,
      successCount: 0
    };
  }
  
  const pattern = userModel.taskPreferences.taskPatterns[taskType];
  pattern.count++;
  pattern.avgDuration = (pattern.avgDuration * (pattern.count - 1) + duration) / pattern.count;
  if (success) pattern.successCount++;
  
  // 记录偏好工具
  tools.forEach(tool => {
    userModel.taskPreferences.preferredTools[tool] = 
      (userModel.taskPreferences.preferredTools[tool] || 0) + 1;
  });
  
  // 记录到完成历史
  userModel.taskPreferences.completedTasks.push({
    taskType,
    duration,
    success,
    timestamp: Date.now()
  });
  
  // 保留最近100条
  userModel.taskPreferences.completedTasks = 
    userModel.taskPreferences.completedTasks.slice(-100);
  
  save();
}

/**
 * 新增：记录情绪模式
 */
function recordEmotion(emotion, context = {}) {
  const entry = {
    timestamp: Date.now(),
    emotion,
    context: context.description || ''
  };
  
  // 添加到历史
  userModel.emotionPatterns.history.push(entry);
  userModel.emotionPatterns.history = userModel.emotionPatterns.history.slice(-50);
  
  // 更新主导情绪统计
  userModel.emotionPatterns.dominantEmotions[emotion] = 
    (userModel.emotionPatterns.dominantEmotions[emotion] || 0) + 1;
  
  // 记录触发因素
  if (context.trigger) {
    userModel.emotionPatterns.emotionTriggers[context.trigger] = 
      (userModel.emotionPatterns.emotionTriggers[context.trigger] || 0) + 1;
  }
  
  // 分析情绪趋势
  analyzeEmotionTrend();
  
  save();
}

/**
 * 新增：分析情绪趋势
 */
function analyzeEmotionTrend() {
  const recent = userModel.emotionPatterns.history.slice(-10);
  if (recent.length < 3) return;
  
  // 简单趋势分析
  const positiveEmotions = ['positive', 'excited', 'curious'];
  const negativeEmotions = ['negative', 'frustrated', 'anxious'];
  
  let positiveCount = 0;
  let negativeCount = 0;
  
  recent.forEach(e => {
    if (positiveEmotions.includes(e.emotion)) positiveCount++;
    if (negativeEmotions.includes(e.emotion)) negativeCount++;
  });
  
  if (positiveCount > negativeCount * 2) {
    userModel.emotionPatterns.emotionalTrend = 'positive';
  } else if (negativeCount > positiveCount * 2) {
    userModel.emotionPatterns.emotionalTrend = 'negative';
  } else {
    userModel.emotionPatterns.emotionalTrend = 'stable';
  }
}

/**
 * 新增：记录常用表达
 */
function recordExpression(text) {
  // 提取关键短语（简化版）
  const phrases = text.match(/[\u4e00-\u9fa5]{2,8}/g) || [];
  
  phrases.forEach(phrase => {
    userModel.commonExpressions.phrases[phrase] = 
      (userModel.commonExpressions.phrases[phrase] || 0) + 1;
  });
  
  // 识别问候语
  const greetings = ['你好', '在吗', 'hi', 'hello', '早', '晚上好'];
  greetings.forEach(g => {
    if (text.toLowerCase().includes(g) && !userModel.commonExpressions.greetings.includes(g)) {
      userModel.commonExpressions.greetings.push(g);
    }
  });
  
  // 识别问题
  if (text.includes('？') || text.includes('?')) {
    userModel.commonExpressions.questions.push(text.slice(0, 50));
    userModel.commonExpressions.questions = 
      [...new Set(userModel.commonExpressions.questions)].slice(-20);
  }
  
  save();
}

/**
 * 新增：记录交互历史
 */
function recordInteractionHistory(topic, action, result) {
  userModel.interactionHistory.recentInteractions.push({
    timestamp: Date.now(),
    topic,
    action,
    result: result ? 'success' : 'failure'
  });
  
  // 保留最近50条
  userModel.interactionHistory.recentInteractions = 
    userModel.interactionHistory.recentInteractions.slice(-50);
  
  // 记录最近话题
  if (topic && !userModel.interactionHistory.lastTopics.includes(topic)) {
    userModel.interactionHistory.lastTopics.push(topic);
    userModel.interactionHistory.lastTopics = 
      userModel.interactionHistory.lastTopics.slice(-10);
  }
  
  save();
}

/**
 * 新增：检测上下文切换
 */
function detectContextSwitch(currentTopic) {
  const lastTopic = userModel.interactionHistory.lastTopics[
    userModel.interactionHistory.lastTopics.length - 1
  ];
  
  if (lastTopic && lastTopic !== currentTopic) {
    userModel.interactionHistory.contextSwitches++;
    save();
    return true;
  }
  return false;
}

/**
 * 新增：获取完整用户画像
 */
function getFullProfile() {
  return {
    // 基本信息
    basic: userModel.basic,
    
    // 兴趣偏好
    preferences: {
      topInterests: Object.entries(userModel.preferences.topics)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10)
        .map(([topic, score]) => ({ topic, score })),
      communicationTone: userModel.preferences.communicationTone,
      proactivity: userModel.preferences.proactivity
    },
    
    // 任务偏好
    taskPreferences: {
      frequentTasks: Object.entries(userModel.taskPreferences.taskPatterns)
        .sort((a, b) => b[1].count - a[1].count)
        .slice(0, 5)
        .map(([task, data]) => ({
          task,
          count: data.count,
          successRate: (data.successCount / data.count * 100).toFixed(1) + '%'
        })),
      preferredTools: Object.entries(userModel.taskPreferences.preferredTools)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5)
        .map(([tool, count]) => ({ tool, count }))
    },
    
    // 情绪模式
    emotionPatterns: {
      dominantEmotions: Object.entries(userModel.emotionPatterns.dominantEmotions)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5),
      emotionalTrend: userModel.emotionPatterns.emotionalTrend
    },
    
    // 常用表达
    commonExpressions: {
      topPhrases: Object.entries(userModel.commonExpressions.phrases)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10)
        .map(([phrase, count]) => ({ phrase, count })),
      greetings: userModel.commonExpressions.greetings,
      recentQuestions: userModel.commonExpressions.questions.slice(-5)
    },
    
    // 统计
    stats: {
      totalInteractions: userModel.stats.totalInteractions,
      contextSwitches: userModel.interactionHistory.contextSwitches,
      activeHours: userModel.patterns.activeHours
    }
  };
}

/**
 * 添加已知概念
 */
function addKnownConcept(concept) {
  if (!userModel.knowledge.knownConcepts.includes(concept)) {
    userModel.knowledge.knownConcepts.push(concept);
    save();
  }
}

/**
 * 添加专业领域
 */
function addExpertiseArea(area) {
  if (!userModel.knowledge.expertiseAreas.includes(area)) {
    userModel.knowledge.expertiseAreas.push(area);
    save();
  }
}

/**
 * 添加学习兴趣
 */
function addLearningInterest(interest) {
  if (!userModel.knowledge.learningInterests.includes(interest)) {
    userModel.knowledge.learningInterests.push(interest);
    save();
  }
}

/**
 * 推断沟通风格
 */
function inferCommunicationStyle(messages) {
  // 简单的启发式规则
  const formalIndicators = ['请', '麻烦', '能否', '是否', '您好'];
  const casualIndicators = ['哈', '哈哈', '嗯', '啊', '呢', '吧'];
  const technicalIndicators = ['代码', '实现', '配置', '参数', '模块'];

  let formalCount = 0;
  let casualCount = 0;
  let technicalCount = 0;

  for (const msg of messages) {
    for (const indicator of formalIndicators) {
      if (msg.includes(indicator)) formalCount++;
    }
    for (const indicator of casualIndicators) {
      if (msg.includes(indicator)) casualCount++;
    }
    for (const indicator of technicalIndicators) {
      if (msg.includes(indicator)) technicalCount++;
    }
  }

  if (technicalCount > formalCount && technicalCount > casualCount) {
    userModel.basic.communicationStyle = 'technical';
  } else if (formalCount > casualCount) {
    userModel.basic.communicationStyle = 'formal';
  } else {
    userModel.basic.communicationStyle = 'casual';
  }

  save();
}

/**
 * 获取用户画像摘要
 */
function getProfileSummary() {
  return {
    name: userModel.basic.name || userModel.basic.preferredName || 'Unknown',
    communicationStyle: userModel.basic.communicationStyle,
    topInterests: Object.entries(userModel.preferences.topics)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([topic]) => topic),
    expertiseAreas: userModel.knowledge.expertiseAreas,
    activeHours: userModel.patterns.activeHours,
    totalInteractions: userModel.stats.totalInteractions,
    avgSessionLength: Math.round(userModel.patterns.avgSessionLength / 60000) + ' min'
  };
}

/**
 * 预测用户需求
 */
function predictNeeds() {
  const predictions = [];

  // 基于时间预测
  const hour = new Date().getHours();
  if (userModel.patterns.activeHours.includes(hour)) {
    predictions.push({
      type: 'timing',
      confidence: 0.7,
      message: '用户通常在这个时段活跃'
    });
  }

  // 基于常见任务预测
  const commonTasks = Object.entries(userModel.patterns.commonTasks)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3);

  if (commonTasks.length > 0) {
    predictions.push({
      type: 'task',
      confidence: 0.6,
      message: `用户经常做: ${commonTasks.map(([t]) => t).join(', ')}`
    });
  }

  // 基于兴趣预测
  const topInterests = Object.entries(userModel.preferences.topics)
    .filter(([_, score]) => score > 0.5)
    .slice(0, 3);

  if (topInterests.length > 0) {
    predictions.push({
      type: 'interest',
      confidence: 0.5,
      message: `用户感兴趣: ${topInterests.map(([t]) => t).join(', ')}`
    });
  }

  return predictions;
}

// ===== 主函数 =====
async function main() {
  const action = process.argv[2];
  const args = process.argv.slice(3);

  load();

  switch (action) {
    case 'summary':
      console.log(JSON.stringify(getProfileSummary(), null, 2));
      break;

    case 'preferences':
      console.log(JSON.stringify(getPreferences(), null, 2));
      break;

    case 'predict':
      console.log(JSON.stringify(predictNeeds(), null, 2));
      break;

    case 'name':
      if (args[0]) {
        updateBasic({ name: args[0] });
        console.log('✅ Name set:', args[0]);
      } else {
        console.log('Name:', userModel.basic.name);
      }
      break;

    case 'interest':
      if (args[0]) {
        recordInterest(args[0], parseFloat(args[1]) || 0.1);
        console.log('✅ Interest recorded:', args[0]);
      }
      break;

    case 'interact':
      recordInteraction(args[0] ? { task: args[0] } : {});
      console.log('✅ Interaction recorded');
      break;

    case 'concept':
      if (args[0]) {
        addKnownConcept(args[0]);
        console.log('✅ Concept added:', args[0]);
      } else {
        console.log('Known concepts:', userModel.knowledge.knownConcepts);
      }
      break;

    case 'expertise':
      if (args[0]) {
        addExpertiseArea(args[0]);
        console.log('✅ Expertise added:', args[0]);
      } else {
        console.log('Expertise areas:', userModel.knowledge.expertiseAreas);
      }
      break;

    case 'full':
      console.log(JSON.stringify(userModel, null, 2));
      break;

    default:
      console.log(`
用户建模模块

用法:
  node user_model.cjs summary              # 获取画像摘要
  node user_model.cjs preferences          # 获取偏好
  node user_model.cjs predict              # 预测用户需求
  node user_model.cjs name [name]          # 设置/查看名字
  node user_model.cjs interest [topic] [score]  # 记录兴趣
  node user_model.cjs interact [task]      # 记录交互
  node user_model.cjs concept [concept]    # 添加/查看已知概念
  node user_model.cjs expertise [area]     # 添加/查看专业领域
  node user_model.cjs full                 # 完整用户模型
      `);
  }
}

main();
