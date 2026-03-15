#!/usr/bin/env node
/**
 * Cognitive Brain - 上下文切换模块
 * 管理多任务上下文切换
 */

const fs = require('fs');
const path = require('path');

const HOME = process.env.HOME || '/root';
const SKILL_DIR = path.join(HOME, '.openclaw/workspace/skills/cognitive-brain');
const CONTEXT_STACK_PATH = path.join(SKILL_DIR, '.context-stack.json');

// 上下文栈
let contextStack = {
  stack: [],          // 上下文栈
  current: null,      // 当前上下文
  history: [],        // 切换历史
  config: {
    maxStackSize: 10,
    autoSaveInterval: 30000
  }
};

/**
 * 加载上下文栈
 */
function load() {
  try {
    if (fs.existsSync(CONTEXT_STACK_PATH)) {
      contextStack = JSON.parse(fs.readFileSync(CONTEXT_STACK_PATH, 'utf8'));
    }
  } catch (e) {
    contextStack = { stack: [], current: null, history: [], config: { maxStackSize: 10, autoSaveInterval: 30000 } };
  }
}

/**
 * 保存上下文栈
 */
function save() {
  try {
    fs.writeFileSync(CONTEXT_STACK_PATH, JSON.stringify(contextStack, null, 2));
  } catch (e) {
    // ignore
  }
}

/**
 * 创建上下文
 */
function createContext(name, data = {}) {
  return {
    id: `ctx_${Date.now()}`,
    name,
    data,
    createdAt: Date.now(),
    lastAccessed: Date.now(),
    accessCount: 0,
    state: {
      topic: null,
      entities: [],
      openQuestions: [],
      pendingActions: []
    }
  };
}

/**
 * 推入新上下文（暂停当前，开始新任务）
 */
function pushContext(name, data = {}) {
  load();

  // 保存当前上下文
  if (contextStack.current) {
    contextStack.current.lastAccessed = Date.now();
    contextStack.stack.unshift(contextStack.current);

    // 限制栈大小
    if (contextStack.stack.length > contextStack.config.maxStackSize) {
      const removed = contextStack.stack.pop();
      console.log(`[context-switch] 上下文栈已满，移除: ${removed.name}`);
    }
  }

  // 创建新上下文
  const newContext = createContext(name, data);
  contextStack.current = newContext;

  // 记录历史
  contextStack.history.push({
    action: 'push',
    contextName: name,
    timestamp: Date.now()
  });

  save();

  console.log(`[context-switch] 推入上下文: ${name}`);
  return newContext;
}

/**
 * 弹出上下文（恢复上一个任务）
 */
function popContext() {
  load();

  if (contextStack.stack.length === 0) {
    console.log('[context-switch] 上下文栈为空，无法弹出');
    return null;
  }

  // 保存当前上下文到历史
  const currentName = contextStack.current?.name;

  // 恢复上一个上下文
  contextStack.current = contextStack.stack.shift();
  contextStack.current.lastAccessed = Date.now();
  contextStack.current.accessCount++;

  // 记录历史
  contextStack.history.push({
    action: 'pop',
    from: currentName,
    to: contextStack.current.name,
    timestamp: Date.now()
  });

  save();

  console.log(`[context-switch] 弹出上下文，恢复: ${contextStack.current.name}`);
  return contextStack.current;
}

/**
 * 切换到指定上下文
 */
function switchToContext(contextId) {
  load();

  // 在栈中查找
  const index = contextStack.stack.findIndex(c => c.id === contextId);
  if (index === -1) {
    console.log(`[context-switch] 未找到上下文: ${contextId}`);
    return null;
  }

  // 保存当前
  if (contextStack.current) {
    contextStack.current.lastAccessed = Date.now();
    contextStack.stack.unshift(contextStack.current);
  }

  // 切换到目标
  contextStack.current = contextStack.stack.splice(index, 1)[0];
  contextStack.current.lastAccessed = Date.now();
  contextStack.current.accessCount++;

  // 记录历史
  contextStack.history.push({
    action: 'switch',
    to: contextStack.current.name,
    timestamp: Date.now()
  });

  save();

  console.log(`[context-switch] 切换到上下文: ${contextStack.current.name}`);
  return contextStack.current;
}

/**
 * 更新当前上下文状态
 */
function updateCurrentState(state) {
  load();

  if (!contextStack.current) {
    return null;
  }

  Object.assign(contextStack.current.state, state);
  contextStack.current.lastAccessed = Date.now();
  save();

  return contextStack.current;
}

/**
 * 获取当前上下文
 */
function getCurrentContext() {
  load();
  return contextStack.current;
}

/**
 * 获取上下文栈
 */
function getStack() {
  load();
  return contextStack.stack.map(c => ({
    id: c.id,
    name: c.name,
    lastAccessed: c.lastAccessed,
    accessCount: c.accessCount
  }));
}

/**
 * 获取栈深度
 */
function getStackDepth() {
  load();
  return contextStack.stack.length;
}

/**
 * 清空栈
 */
function clearStack() {
  load();

  const cleared = contextStack.stack.length;
  contextStack.stack = [];
  save();

  console.log(`[context-switch] 清空上下文栈，移除 ${cleared} 个`);
  return cleared;
}

/**
 * 生成上下文摘要
 */
function getContextSummary() {
  load();

  if (!contextStack.current) {
    return { current: null, stackSize: 0 };
  }

  return {
    current: {
      name: contextStack.current.name,
      accessCount: contextStack.current.accessCount,
      state: contextStack.current.state
    },
    stackSize: contextStack.stack.length,
    stack: contextStack.stack.slice(0, 3).map(c => c.name)
  };
}

/**
 * 检测上下文切换需求
 */
function detectSwitchNeed(newInput, currentContext) {
  const signals = [];

  // 检测话题转换
  if (currentContext?.state?.topic) {
    const topicKeywords = currentContext.state.topic.split(/\s+/);
    const related = topicKeywords.some(kw => newInput.includes(kw));

    if (!related) {
      signals.push({
        type: 'topic_shift',
        confidence: 0.6,
        suggestion: '可能需要切换上下文'
      });
    }
  }

  // 检测明确切换信号
  const switchPatterns = [
    /(先不说这个|换个话题|另一个事)/,
    /(对了|顺便|对了还有)/,
    /(回到|继续|刚才)/
  ];

  for (const pattern of switchPatterns) {
    if (pattern.test(newInput)) {
      signals.push({
        type: 'explicit_switch',
        confidence: 0.9,
        matchedPattern: pattern.toString()
      });
    }
  }

  return signals;
}

/**
 * 获取切换历史
 */
function getSwitchHistory(limit = 20) {
  load();

  return contextStack.history.slice(-limit);
}

// ===== 主函数 =====
async function main() {
  const action = process.argv[2];
  const args = process.argv.slice(3);

  load();

  switch (action) {
    case 'push':
      if (args[0]) {
        const ctx = pushContext(args[0]);
        console.log('✅ 推入上下文:', ctx.name);
      }
      break;

    case 'pop':
      const restored = popContext();
      if (restored) {
        console.log('✅ 恢复上下文:', restored.name);
      }
      break;

    case 'current':
      const current = getCurrentContext();
      if (current) {
        console.log('📍 当前上下文:');
        console.log(JSON.stringify(current, null, 2));
      } else {
        console.log('❌ 无当前上下文');
      }
      break;

    case 'stack':
      const stack = getStack();
      console.log('📚 上下文栈:');
      stack.forEach((c, i) => {
        console.log(`   ${i + 1}. ${c.name} (访问 ${c.accessCount} 次)`);
      });
      break;

    case 'summary':
      console.log(JSON.stringify(getContextSummary(), null, 2));
      break;

    case 'clear':
      const cleared = clearStack();
      console.log(`✅ 清空栈，移除 ${cleared} 个上下文`);
      break;

    default:
      console.log(`
上下文切换模块

用法:
  node context_switching.cjs push <name>  # 推入新上下文
  node context_switching.cjs pop          # 弹出上下文
  node context_switching.cjs current      # 查看当前上下文
  node context_switching.cjs stack        # 查看栈
  node context_switching.cjs summary      # 上下文摘要
  node context_switching.cjs clear        # 清空栈
      `);
  }
}

main();
