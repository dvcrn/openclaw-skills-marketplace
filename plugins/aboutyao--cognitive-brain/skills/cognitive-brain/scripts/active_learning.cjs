#!/usr/bin/env node
/**
 * Cognitive Brain - 主动学习模块
 * 主动向用户学习新知识
 */

const fs = require('fs');
const path = require('path');

const HOME = process.env.HOME || '/root';
const SKILL_DIR = path.join(HOME, '.openclaw/workspace/skills/cognitive-brain');
const LEARNING_QUEUE_PATH = path.join(SKILL_DIR, '.learning-queue.json');

// 学习队列
let learningQueue = {
  pending: [],      // 待学习的问题
  learned: [],      // 已学习的知识
  skipped: []       // 跳过的
};

/**
 * 加载队列
 */
function load() {
  try {
    if (fs.existsSync(LEARNING_QUEUE_PATH)) {
      learningQueue = JSON.parse(fs.readFileSync(LEARNING_QUEUE_PATH, 'utf8'));
    }
  } catch (e) {
    learningQueue = { pending: [], learned: [], skipped: [] };
  }
}

/**
 * 保存队列
 */
function save() {
  try {
    fs.writeFileSync(LEARNING_QUEUE_PATH, JSON.stringify(learningQueue, null, 2));
  } catch (e) {
    // ignore
  }
}

/**
 * 学习触发条件
 */
const LEARNING_TRIGGERS = {
  UNKNOWN_ENTITY: {
    name: 'unknown_entity',
    description: '遇到未知实体',
    priority: 'high'
  },
  AMBIGUOUS_CONTEXT: {
    name: 'ambiguous_context',
    description: '上下文模糊',
    priority: 'medium'
  },
  USER_CORRECTION: {
    name: 'user_correction',
    description: '用户纠正',
    priority: 'high'
  },
  NEW_CONCEPT: {
    name: 'new_concept',
    description: '新概念',
    priority: 'medium'
  },
  GAP_IN_KNOWLEDGE: {
    name: 'knowledge_gap',
    description: '知识空白',
    priority: 'low'
  }
};

/**
 * 生成学习问题
 */
function generateLearningQuestion(trigger, context) {
  const questions = [];

  switch (trigger) {
    case 'unknown_entity':
      questions.push({
        id: `learn_${Date.now()}`,
        type: trigger,
        question: `"${context.entity}" 是什么？`,
        context,
        priority: 'high',
        createdAt: Date.now()
      });
      break;

    case 'ambiguous_context':
      questions.push({
        id: `learn_${Date.now()}`,
        type: trigger,
        question: `我不确定你指的是哪个 "${context.term}"，能具体说明吗？`,
        context,
        priority: 'medium',
        createdAt: Date.now()
      });
      break;

    case 'user_correction':
      questions.push({
        id: `learn_${Date.now()}`,
        type: trigger,
        question: `明白了，"${context.correctInfo}" 才是对的。我记住了。`,
        context,
        priority: 'high',
        createdAt: Date.now(),
        autoLearn: true
      });
      break;

    case 'new_concept':
      questions.push({
        id: `learn_${Date.now()}`,
        type: trigger,
        question: `"${context.concept}" 是新概念吗？能告诉我更多吗？`,
        context,
        priority: 'medium',
        createdAt: Date.now()
      });
      break;

    case 'knowledge_gap':
      questions.push({
        id: `learn_${Date.now()}`,
        type: trigger,
        question: `关于 "${context.topic}" 我想了解更多，能告诉我吗？`,
        context,
        priority: 'low',
        createdAt: Date.now()
      });
      break;
  }

  return questions;
}

/**
 * 添加学习问题到队列
 */
function enqueueLearning(trigger, context) {
  load();

  const questions = generateLearningQuestion(trigger, context);

  for (const q of questions) {
    // 检查是否已存在类似问题
    const exists = learningQueue.pending.some(
      p => p.question === q.question
    );

    if (!exists) {
      learningQueue.pending.push(q);
    }
  }

  save();

  return questions;
}

/**
 * 获取下一个学习问题
 */
function getNextLearningQuestion() {
  load();

  if (learningQueue.pending.length === 0) {
    return null;
  }

  // 按优先级排序
  const priorityOrder = { high: 0, medium: 1, low: 2 };
  learningQueue.pending.sort(
    (a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]
  );

  return learningQueue.pending[0];
}

/**
 * 记录学习结果
 */
function recordLearning(questionId, answer, source = 'user') {
  load();

  const question = learningQueue.pending.find(q => q.id === questionId);
  if (!question) {
    return null;
  }

  // 从待学习移到已学习
  learningQueue.pending = learningQueue.pending.filter(q => q.id !== questionId);

  const learned = {
    ...question,
    answer,
    source,
    learnedAt: Date.now()
  };

  learningQueue.learned.push(learned);
  save();

  return learned;
}

/**
 * 跳过学习问题
 */
function skipLearning(questionId, reason = null) {
  load();

  const question = learningQueue.pending.find(q => q.id === questionId);
  if (!question) {
    return null;
  }

  learningQueue.pending = learningQueue.pending.filter(q => q.id !== questionId);

  const skipped = {
    ...question,
    reason,
    skippedAt: Date.now()
  };

  learningQueue.skipped.push(skipped);
  save();

  return skipped;
}

/**
 * 检查是否需要学习
 */
function checkLearningNeeds(context) {
  const needs = [];

  // 检查未知实体
  if (context.unknownEntities && context.unknownEntities.length > 0) {
    needs.push(...context.unknownEntities.map(entity => ({
      trigger: 'unknown_entity',
      context: { entity },
      priority: 'high'
    })));
  }

  // 检查知识空白
  if (context.knowledgeGaps && context.knowledgeGaps.length > 0) {
    needs.push(...context.knowledgeGaps.map(topic => ({
      trigger: 'knowledge_gap',
      context: { topic },
      priority: 'low'
    })));
  }

  return needs;
}

/**
 * 获取学习统计
 */
function getStats() {
  load();

  return {
    pending: learningQueue.pending.length,
    learned: learningQueue.learned.length,
    skipped: learningQueue.skipped.length,
    byPriority: {
      high: learningQueue.pending.filter(q => q.priority === 'high').length,
      medium: learningQueue.pending.filter(q => q.priority === 'medium').length,
      low: learningQueue.pending.filter(q => q.priority === 'low').length
    },
    recentLearned: learningQueue.learned.slice(-10).map(l => ({
      question: l.question,
      answer: l.answer?.slice(0, 50)
    }))
  };
}

/**
 * 获取已学知识
 */
function getLearnedKnowledge(limit = 20) {
  load();

  return learningQueue.learned
    .slice(-limit)
    .map(l => ({
      question: l.question,
      answer: l.answer,
      learnedAt: l.learnedAt
    }));
}

// ===== 主函数 =====
async function main() {
  const action = process.argv[2];
  const args = process.argv.slice(3);

  load();

  switch (action) {
    case 'enqueue':
      if (args[0] && args[1]) {
        const questions = enqueueLearning(args[0], { entity: args[1] });
        console.log('✅ 学习问题已添加:');
        questions.forEach(q => console.log(`   - ${q.question}`));
      }
      break;

    case 'next':
      const next = getNextLearningQuestion();
      if (next) {
        console.log('❓ 下一个学习问题:');
        console.log(`   ${next.question}`);
        console.log(`   优先级: ${next.priority}`);
      } else {
        console.log('✅ 没有待学习的问题');
      }
      break;

    case 'stats':
      console.log('📊 学习统计:');
      console.log(JSON.stringify(getStats(), null, 2));
      break;

    case 'learned':
      console.log('📚 已学知识:');
      console.log(JSON.stringify(getLearnedKnowledge(), null, 2));
      break;

    default:
      console.log(`
主动学习模块

用法:
  node active_learning.cjs enqueue <trigger> <entity>  # 添加学习问题
  node active_learning.cjs next                        # 获取下一个问题
  node active_learning.cjs stats                       # 查看统计
  node active_learning.cjs learned                     # 查看已学知识
      `);
  }
}

main();
