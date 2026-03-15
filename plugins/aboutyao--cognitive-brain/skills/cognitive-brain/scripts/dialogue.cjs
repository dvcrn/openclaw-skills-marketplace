#!/usr/bin/env node
/**
 * Cognitive Brain - 对话管理模块
 * 管理对话流程和上下文
 */

const fs = require('fs');
const path = require('path');

const HOME = process.env.HOME || '/root';
const SKILL_DIR = path.join(HOME, '.openclaw/workspace/skills/cognitive-brain');
const DIALOGUE_STATE_PATH = path.join(SKILL_DIR, '.dialogue-state.json');

// 对话状态
let dialogueState = {
  // 当前对话
  current: {
    id: null,
    startedAt: null,
    turnCount: 0,
    topic: null,
    subTopic: null,
    intent: null,
    slots: {}
  },

  // 对话历史（最近的）
  history: [],

  // 待确认项
  pendingConfirmations: [],

  // 多轮对话追踪
  multiTurn: {
    isActive: false,
    type: null,       // 'qa', 'task', 'clarification'
    originalIntent: null,
    gatheredInfo: {},
    remainingQuestions: []
  },

  // 配置
  config: {
    maxHistorySize: 100,
    confirmationTimeout: 5 * 60 * 1000  // 5 分钟
  }
};

/**
 * 加载对话状态
 */
function load() {
  try {
    if (fs.existsSync(DIALOGUE_STATE_PATH)) {
      const data = JSON.parse(fs.readFileSync(DIALOGUE_STATE_PATH, 'utf8'));
      dialogueState = { ...dialogueState, ...data };
    }
  } catch (e) {
    // ignore
  }
}

/**
 * 保存对话状态
 */
function save() {
  try {
    fs.writeFileSync(DIALOGUE_STATE_PATH, JSON.stringify(dialogueState, null, 2));
  } catch (e) {
    // ignore
  }
}

/**
 * 开始新对话
 */
function startDialogue(initialIntent = null) {
  dialogueState.current = {
    id: `dlg_${Date.now()}`,
    startedAt: Date.now(),
    turnCount: 0,
    topic: null,
    subTopic: null,
    intent: initialIntent,
    slots: {}
  };

  dialogueState.multiTurn = {
    isActive: false,
    type: null,
    originalIntent: null,
    gatheredInfo: {},
    remainingQuestions: []
  };

  save();
  return dialogueState.current;
}

/**
 * 添加对话轮次
 */
function addTurn(role, content, metadata = {}) {
  const turn = {
    role,        // 'user' | 'agent'
    content,
    timestamp: Date.now(),
    dialogueId: dialogueState.current.id,
    ...metadata
  };

  // 添加到历史
  dialogueState.history.push(turn);
  if (dialogueState.history.length > dialogueState.config.maxHistorySize) {
    dialogueState.history.shift();
  }

  // 更新轮次计数
  if (role === 'user') {
    dialogueState.current.turnCount++;
  }

  save();
  return turn;
}

/**
 * 设置话题
 */
function setTopic(topic, subTopic = null) {
  dialogueState.current.topic = topic;
  dialogueState.current.subTopic = subTopic;
  save();
}

/**
 * 设置意图
 */
function setIntent(intent) {
  dialogueState.current.intent = intent;
  save();
}

/**
 * 设置槽位
 */
function setSlot(name, value) {
  dialogueState.current.slots[name] = value;
  save();
}

/**
 * 获取槽位
 */
function getSlot(name) {
  return dialogueState.current.slots[name];
}

/**
 * 获取所有槽位
 */
function getAllSlots() {
  return { ...dialogueState.current.slots };
}

/**
 * 开始多轮对话
 */
function startMultiTurn(type, originalIntent, questions) {
  dialogueState.multiTurn = {
    isActive: true,
    type,
    originalIntent,
    gatheredInfo: {},
    remainingQuestions: questions
  };
  save();
}

/**
 * 添加收集的信息
 */
function addGatheredInfo(info) {
  Object.assign(dialogueState.multiTurn.gatheredInfo, info);

  // 移除已回答的问题
  const answeredKeys = Object.keys(info);
  dialogueState.multiTurn.remainingQuestions =
    dialogueState.multiTurn.remainingQuestions.filter(q => !answeredKeys.includes(q.key));

  // 检查是否完成
  if (dialogueState.multiTurn.remainingQuestions.length === 0) {
    dialogueState.multiTurn.isActive = false;
  }

  save();
}

/**
 * 获取下一个问题
 */
function getNextQuestion() {
  if (!dialogueState.multiTurn.isActive) {
    return null;
  }

  return dialogueState.multiTurn.remainingQuestions[0] || null;
}

/**
 * 添加待确认项
 */
function addConfirmation(item) {
  const confirmation = {
    id: `conf_${Date.now()}`,
    item,
    createdAt: Date.now(),
    status: 'pending'
  };

  dialogueState.pendingConfirmations.push(confirmation);
  save();

  return confirmation;
}

/**
 * 确认/拒绝
 */
function resolveConfirmation(confirmationId, accepted) {
  const conf = dialogueState.pendingConfirmations.find(c => c.id === confirmationId);
  if (conf) {
    conf.status = accepted ? 'accepted' : 'rejected';
    conf.resolvedAt = Date.now();
    save();
  }
  return conf;
}

/**
 * 获取待确认项
 */
function getPendingConfirmations() {
  // 过滤过期的
  const now = Date.now();
  dialogueState.pendingConfirmations = dialogueState.pendingConfirmations.filter(
    c => c.status === 'pending' && now - c.createdAt < dialogueState.config.confirmationTimeout
  );
  save();

  return dialogueState.pendingConfirmations;
}

/**
 * 获取对话摘要
 */
function getDialogueSummary() {
  const recentTurns = dialogueState.history.slice(-10);

  return {
    dialogueId: dialogueState.current.id,
    duration: Date.now() - dialogueState.current.startedAt,
    turnCount: dialogueState.current.turnCount,
    topic: dialogueState.current.topic,
    intent: dialogueState.current.intent,
    slots: dialogueState.current.slots,
    recentTopics: extractRecentTopics(recentTurns),
    isMultiTurn: dialogueState.multiTurn.isActive,
    pendingConfirmations: dialogueState.pendingConfirmations.filter(c => c.status === 'pending').length
  };
}

/**
 * 提取最近话题
 */
function extractRecentTopics(turns) {
  const topics = [];
  const keywords = {};

  for (const turn of turns) {
    if (turn.role !== 'user') continue;

    // 简单提取关键词
    const words = turn.content.split(/\s+/);
    for (const word of words) {
      if (word.length >= 2) {
        keywords[word] = (keywords[word] || 0) + 1;
      }
    }
  }

  // 返回高频词
  return Object.entries(keywords)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([word]) => word);
}

/**
 * 检测话题转换
 */
function detectTopicShift(newContent) {
  if (!dialogueState.current.topic) {
    return { shifted: false };
  }

  // 简单检测：新内容是否与当前话题相关
  const topicKeywords = dialogueState.current.topic.split(/\s+/);
  const related = topicKeywords.some(kw => newContent.includes(kw));

  if (!related) {
    return {
      shifted: true,
      previousTopic: dialogueState.current.topic,
      suggestion: '话题可能已转换，建议确认'
    };
  }

  return { shifted: false };
}

/**
 * 结束对话
 */
function endDialogue() {
  const summary = getDialogueSummary();

  dialogueState.current = {
    id: null,
    startedAt: null,
    turnCount: 0,
    topic: null,
    subTopic: null,
    intent: null,
    slots: {}
  };

  dialogueState.multiTurn = {
    isActive: false,
    type: null,
    originalIntent: null,
    gatheredInfo: {},
    remainingQuestions: []
  };

  save();

  return summary;
}

// ===== 主函数 =====
async function main() {
  const action = process.argv[2];
  const args = process.argv.slice(3);

  load();

  switch (action) {
    case 'summary':
      console.log(JSON.stringify(getDialogueSummary(), null, 2));
      break;

    case 'start':
      const newDlg = startDialogue(args[0]);
      console.log('✅ 新对话开始:', newDlg.id);
      break;

    case 'turn':
      if (args[0] && args[1]) {
        addTurn(args[0], args.slice(1).join(' '));
        console.log('✅ 轮次已添加');
      }
      break;

    case 'topic':
      if (args[0]) {
        setTopic(args[0], args[1]);
        console.log('✅ 话题已设置:', args[0]);
      } else {
        console.log('当前话题:', dialogueState.current.topic);
      }
      break;

    case 'slots':
      console.log('槽位:', getAllSlots());
      break;

    case 'history':
      const recent = dialogueState.history.slice(-10);
      console.log('最近对话:');
      recent.forEach((t, i) => {
        console.log(`   ${i + 1}. [${t.role}] ${t.content.slice(0, 50)}...`);
      });
      break;

    case 'end':
      const summary = endDialogue();
      console.log('📊 对话结束:');
      console.log(JSON.stringify(summary, null, 2));
      break;

    default:
      console.log(`
对话管理模块

用法:
  node dialogue.cjs summary           # 获取对话摘要
  node dialogue.cjs start [intent]    # 开始新对话
  node dialogue.cjs turn <role> <content>  # 添加轮次
  node dialogue.cjs topic [topic] [subTopic]  # 设置/查看话题
  node dialogue.cjs slots             # 查看槽位
  node dialogue.cjs history           # 查看对话历史
  node dialogue.cjs end               # 结束对话
      `);
  }
}

main();
