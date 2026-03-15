const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

// Cognitive Brain config
const HOME = process.env.HOME || '/root';
const SKILL_DIR = path.join(HOME, '.openclaw/workspace/skills/cognitive-brain');
const CONFIG_PATH = path.join(SKILL_DIR, 'config.json');
const MEMORY_PATH = path.join(HOME, '.openclaw/workspace/MEMORY.md');
const KEYWORDS_PATH = path.join(SKILL_DIR, '.dynamic-keywords.json');
const USER_MODEL_PATH = path.join(SKILL_DIR, '.user-model.json');

let sharedMemory = null;
let sharedMemoryReady = false;

async function initSharedMemory() {
  if (sharedMemoryReady) return true;
  
  try {
    const { getSharedMemory } = require(path.join(SKILL_DIR, 'scripts/shared_memory.cjs'));
    sharedMemory = await getSharedMemory();
    sharedMemoryReady = true;
    console.log('[cognitive-recall] Shared memory initialized');
    return true;
  } catch (e) {
    console.log('[cognitive-recall] Shared memory not available, using fallback');
    return false;
  }
}

async function getLessonsFromSharedMemory() {
  if (!sharedMemoryReady) {
    await initSharedMemory();
  }
  
  if (sharedMemory) {
    try {
      const lessons = await sharedMemory.getLessons();
      return lessons.map(l => ({
        summary: l.content.substring(0, 100),
        content: l.content,
        importance: l.importance,
        source: 'shared_memory'
      }));
    } catch (e) {
      console.log('[cognitive-recall] Shared memory query failed, using file fallback');
    }
  }
  
  // Fallback to MEMORY.md
  return getLessonsFromMemory();
}

async function getUserProfileFromSharedMemory() {
  if (!sharedMemoryReady) {
    await initSharedMemory();
  }
  
  if (sharedMemory) {
    try {
      const profile = await sharedMemory.getUserProfile();
      if (profile && profile.length > 0) {
        return JSON.parse(profile[0].content);
      }
    } catch (e) {
      console.log('[cognitive-recall] Shared memory profile failed, using file fallback');
    }
  }
  
  // Fallback to file-based user model
  return getUserModelFromFile();
}

// ============================================================================
// 1. 性能监控
// ============================================================================

const perfLog = {
  queries: [],
  maxEntries: 100,
  warnThreshold: 100, // ms

  record(operation, durationMs, success = true) {
    this.queries.push({
      operation,
      duration: durationMs,
      success,
      timestamp: Date.now()
    });

    // Keep only recent entries
    if (this.queries.length > this.maxEntries) {
      this.queries.shift();
    }

    // Warn if slow
    if (durationMs > this.warnThreshold) {
      console.warn(`[cognitive-recall] ⚠️ Slow query: ${operation} took ${durationMs}ms`);
    }
  },

  getStats() {
    if (this.queries.length === 0) return null;
    const durations = this.queries.map(q => q.duration);
    return {
      count: this.queries.length,
      avg: Math.round(durations.reduce((a, b) => a + b, 0) / durations.length),
      max: Math.max(...durations),
      min: Math.min(...durations)
    };
  }
};

// ============================================================================
// 2. 缓存优化 - 按重要性分级
// ============================================================================

const recallCache = new Map();

const CACHE_CONFIG = {
  high: { ttl: 10 * 60 * 1000 },    // 10 minutes (importance >= 0.8)
  medium: { ttl: 3 * 60 * 1000 },   // 3 minutes (importance 0.5-0.8)
  low: { ttl: 60 * 1000 },          // 1 minute (importance < 0.5)
  default: { ttl: 60 * 1000 }       // 1 minute (unknown)
};

function getCacheTTL(importance) {
  if (importance >= 0.8) return CACHE_CONFIG.high.ttl;
  if (importance >= 0.5) return CACHE_CONFIG.medium.ttl;
  return CACHE_CONFIG.low.ttl;
}

function getCacheEntry(key) {
  const entry = recallCache.get(key);
  if (!entry) return null;

  const now = Date.now();
  const maxTTL = Math.max(...Object.values(CACHE_CONFIG).map(c => c.ttl));

  // Use the stored TTL for this entry
  if (now - entry.timestamp > entry.ttl) {
    recallCache.delete(key);
    return null;
  }

  return entry.result;
}

function setCacheEntry(key, result, importance = 0.5) {
  const ttl = getCacheTTL(importance);
  recallCache.set(key, {
    result,
    timestamp: Date.now(),
    ttl
  });
}

// ============================================================================
// 3. 健康检查 + 降级
// ============================================================================

const healthState = {
  pgHealthy: null,
  lastCheck: 0,
  checkInterval: 30 * 1000, // 30 seconds
  fallbackMode: false,

  async check(pg, dbConfig) {
    const now = Date.now();

    // Skip if recently checked
    if (this.pgHealthy !== null && now - this.lastCheck < this.checkInterval) {
      return this.pgHealthy;
    }

    this.lastCheck = now;

    // Try a simple query
    let pool = null;
    try {
      const { Pool } = pg;
      pool = new Pool({
        host: dbConfig.host,
        port: dbConfig.port,
        database: dbConfig.database,
        user: dbConfig.user,
        password: dbConfig.password,
        connectionTimeoutMillis: 2000,
        query_timeout: 3000
      });

      await pool.query('SELECT 1');
      this.pgHealthy = true;
      this.fallbackMode = false;
      console.log('[cognitive-recall] ✅ PostgreSQL healthy');
      return true;
    } catch (err) {
      this.pgHealthy = false;
      this.fallbackMode = true;
      console.warn('[cognitive-recall] ⚠️ PostgreSQL unavailable, falling back to MEMORY.md');
      return false;
    } finally {
      if (pool) await pool.end().catch(() => {});
    }
  },

  async fallback(keywords, limit) {
    // Read from MEMORY.md
    try {
      if (!fs.existsSync(MEMORY_PATH)) {
        return [];
      }

      const content = fs.readFileSync(MEMORY_PATH, 'utf8');
      const lines = content.split('\n').filter(l => l.trim());

      // Simple keyword matching
      const matches = [];
      for (const line of lines) {
        if (line.startsWith('#') || line.startsWith('---')) continue;

        const matchCount = keywords.filter(kw =>
          line.toLowerCase().includes(kw.toLowerCase())
        ).length;

        if (matchCount > 0) {
          matches.push({
            summary: line.replace(/^[-*]\s*/, '').substring(0, 100),
            content: line,
            type: 'fallback',
            importance: matchCount / keywords.length,
            source: 'MEMORY.md'
          });
        }
      }

      return matches
        .sort((a, b) => b.importance - a.importance)
        .slice(0, limit);
    } catch (err) {
      console.error('[cognitive-recall] Fallback read error:', err.message);
      return [];
    }
  }
};

// ============================================================================
// 4. 动态关键词
// ============================================================================

const keywordState = {
  keywords: ['用户', 'master', '偏好', '重要', '项目'],
  lastUpdate: 0,
  updateInterval: 60 * 60 * 1000, // 1 hour

  load() {
    try {
      if (fs.existsSync(KEYWORDS_PATH)) {
        const data = JSON.parse(fs.readFileSync(KEYWORDS_PATH, 'utf8'));
        if (data.keywords && data.keywords.length > 0) {
          this.keywords = data.keywords;
          this.lastUpdate = data.lastUpdate || 0;
        }
      }
    } catch (err) {
      console.warn('[cognitive-recall] Failed to load keywords:', err.message);
    }
  },

  async update(pg, dbConfig) {
    const now = Date.now();
    if (now - this.lastUpdate < this.updateInterval) {
      return this.keywords;
    }

    let pool = null;
    try {
      const { Pool } = pg;
      pool = new Pool({
        host: dbConfig.host,
        port: dbConfig.port,
        database: dbConfig.database,
        user: dbConfig.user,
        password: dbConfig.password,
        connectionTimeoutMillis: 5000
      });

      // Extract high-frequency words from recent episodes
      const result = await pool.query(`
        SELECT summary, content
        FROM episodes
        WHERE timestamp > NOW() - INTERVAL '7 days'
        ORDER BY importance DESC
        LIMIT 100
      `);

      const wordFreq = new Map();

      for (const row of result.rows) {
        const text = `${row.summary} ${row.content || ''}`;
        // Extract Chinese words (2-4 chars) and English words
        const chineseWords = text.match(/[\u4e00-\u9fa5]{2,4}/g) || [];
        const englishWords = text.match(/[a-zA-Z]{3,}/gi) || [];

        for (const word of [...chineseWords, ...englishWords]) {
          wordFreq.set(word, (wordFreq.get(word) || 0) + 1);
        }
      }

      // Get top keywords (excluding common words)
      const stopWords = new Set(['的', '是', '在', '了', '和', '有', '不', '这', '我', '你', 'the', 'and', 'for', 'was', 'are', 'but', 'not']);

      const topKeywords = [...wordFreq.entries()]
        .filter(([word]) => !stopWords.has(word.toLowerCase()))
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10)
        .map(([word]) => word);

      if (topKeywords.length > 0) {
        // Merge with base keywords
        const baseKeywords = ['用户', 'master', '偏好', '重要', '项目'];
        this.keywords = [...new Set([...baseKeywords, ...topKeywords])].slice(0, 15);
        this.lastUpdate = now;

        // Save to file
        fs.writeFileSync(KEYWORDS_PATH, JSON.stringify({
          keywords: this.keywords,
          lastUpdate: this.lastUpdate
        }, null, 2));

        console.log('[cognitive-recall] 📝 Updated keywords:', this.keywords.join(', '));
      }

      return this.keywords;
    } catch (err) {
      console.warn('[cognitive-recall] Failed to update keywords:', err.message);
      return this.keywords;
    } finally {
      if (pool) await pool.end().catch(() => {});
    }
  },

  getKeywords() {
    return this.keywords;
  }
};

// Initialize keywords on load
keywordState.load();

// ============================================================================
// 5. 错误重试机制
// ============================================================================

const retryState = {
  installAttempts: 0,
  maxAttempts: 3,
  cooldownMs: 5 * 60 * 1000, // 5 minutes
  lastAttempt: 0,

  shouldRetry() {
    const now = Date.now();

    // Reset attempts after cooldown
    if (now - this.lastAttempt > this.cooldownMs) {
      this.installAttempts = 0;
    }

    return this.installAttempts < this.maxAttempts;
  },

  recordAttempt() {
    this.installAttempts++;
    this.lastAttempt = Date.now();
  }
};

// ============================================================================
// 依赖自动安装（带重试）
// ============================================================================

let isInstalling = false;
let pgLoaded = false;
let pgModule = null;

function ensurePgDependency() {
  if (pgLoaded && pgModule) {
    return pgModule;
  }

  // Try to load pg
  try {
    pgModule = require(path.join(SKILL_DIR, 'node_modules/pg'));
    pgLoaded = true;
    return pgModule;
  } catch (e) {
    if (isInstalling) {
      console.log('[cognitive-recall] npm install already in progress');
      return null;
    }

    // Check retry limit
    if (!retryState.shouldRetry()) {
      console.warn('[cognitive-recall] ⚠️ Max install attempts reached, waiting for cooldown');
      return null;
    }

    console.log('[cognitive-recall] pg not found, auto-installing...');
    isInstalling = true;
    retryState.recordAttempt();

    try {
      const startTime = Date.now();

      execSync('npm install --production', {
        cwd: SKILL_DIR,
        timeout: 30000,
        stdio: ['pipe', 'pipe', 'pipe']
      });

      const duration = Date.now() - startTime;
      perfLog.record('npm-install', duration);
      console.log(`[cognitive-recall] ✅ npm install completed in ${duration}ms`);

      // Reset retry state on success
      retryState.installAttempts = 0;

      // Try loading again
      pgModule = require(path.join(SKILL_DIR, 'node_modules/pg'));
      pgLoaded = true;
      return pgModule;
    } catch (installErr) {
      console.error('[cognitive-recall] ❌ Auto-install failed:', installErr.message);
      perfLog.record('npm-install', 0, false);
      return null;
    } finally {
      isInstalling = false;
    }
  }
}

// ============================================================================
// 主查询逻辑
// ============================================================================

async function recallFromDB(queries, limit = 3) {
  const startTime = Date.now();

  // Check cache
  const cacheKey = queries.join('|');
  const cached = getCacheEntry(cacheKey);
  if (cached) {
    perfLog.record('cache-hit', Date.now() - startTime);
    return cached;
  }

  // Load pg (with auto-install)
  const pg = ensurePgDependency();
  if (!pg) {
    console.error('[cognitive-recall] pg module unavailable');
    return healthState.fallback(queries, limit);
  }

  // Check config
  if (!fs.existsSync(CONFIG_PATH)) {
    console.log('[cognitive-recall] Config not found');
    return [];
  }

  const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
  const dbConfig = config.storage.primary;

  // Health check
  const isHealthy = await healthState.check(pg, dbConfig);

  if (!isHealthy) {
    // Fallback to MEMORY.md
    const result = await healthState.fallback(queries, limit);
    perfLog.record('fallback-query', Date.now() - startTime);
    return result;
  }

  // Update dynamic keywords (async, don't wait)
  keywordState.update(pg, dbConfig).catch(() => {});

  let pool = null;
  try {
    const { Pool } = pg;
    pool = new Pool({
      host: dbConfig.host,
      port: dbConfig.port,
      database: dbConfig.database,
      user: dbConfig.user,
      password: dbConfig.password,
      connectionTimeoutMillis: 3000,
      query_timeout: 5000
    });

    // Build OR conditions for multiple keywords
    const conditions = queries.map((q, i) => `(summary ILIKE $${i + 1} OR content ILIKE $${i + 1})`).join(' OR ');
    const params = queries.map(q => `%${q}%`);
    params.push(limit.toString());

    const result = await pool.query(`
      SELECT id, summary, content, type, importance, timestamp
      FROM episodes
      WHERE ${conditions}
      ORDER BY importance DESC, timestamp DESC
      LIMIT $${params.length}
    `, params);

    const memories = result.rows;

    // Cache result with importance-based TTL
    if (memories.length > 0) {
      const maxImportance = Math.max(...memories.map(m => m.importance || 0.5));
      setCacheEntry(cacheKey, memories, maxImportance);
    }

    perfLog.record('db-query', Date.now() - startTime);
    return memories;
  } catch (err) {
    console.error('[cognitive-recall] DB error:', err.message || String(err));
    perfLog.record('db-query', Date.now() - startTime, false);

    // Fallback on error
    return healthState.fallback(queries, limit);
  } finally {
    if (pool) {
      await pool.end().catch(() => {});
    }
  }
}

// ============================================================================
// 自动编码 - 记录对话到 brain
// ============================================================================

const encodeMemory = async (content, metadata = {}) => {
  const startTime = Date.now();
  
  // Skip short messages
  if (!content || content.length < 10) return null;
  
  // Skip system messages
  if (content.includes('[🧠 Memory Context]')) return null;
  
  // Skip duplicate encoding (check recent cache)
  const cacheKey = `encode:${content.slice(0, 50)}`;
  if (recallCache.has(cacheKey)) return null;
  
  let pg;
  try {
    pg = require('pg');
  } catch (e) {
    return null;
  }
  
  if (!fs.existsSync(CONFIG_PATH)) return null;
  
  const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
  const dbConfig = config.storage.primary;
  
  let pool = null;
  try {
    const { Pool } = pg;
    pool = new Pool({
      host: dbConfig.host,
      port: dbConfig.port,
      database: dbConfig.database,
      user: dbConfig.user,
      password: dbConfig.password,
      connectionTimeoutMillis: 2000,
      query_timeout: 3000
    });
    
    // Extract entities (simple keyword extraction)
    const entities = extractEntities(content);
    
    // Calculate importance
    const importance = calculateImportance(content, metadata);
    
    // Insert into episodes
    const result = await pool.query(`
      INSERT INTO episodes (summary, content, type, importance, entities, metadata, timestamp)
      VALUES ($1, $2, $3, $4, $5, $6, NOW())
      RETURNING id
    `, [
      content.slice(0, 200),
      content,
      metadata.type || 'conversation',
      importance,
      JSON.stringify(entities),
      JSON.stringify(metadata)
    ]);
    
    // Mark as encoded
    recallCache.set(cacheKey, true);
    
    perfLog.record('encode', Date.now() - startTime);
    return result.rows[0].id;
  } catch (err) {
    console.error('[cognitive-recall] Encode error:', err.message || String(err));
    return null;
  } finally {
    if (pool) {
      await pool.end().catch(() => {});
    }
  }
};

// 简单实体提取（改进版 - 与 encode.cjs 保持一致）
const STOPWORDS = new Set([
  '的', '是', '在', '了', '和', '与', '或', '有', '为', '以', '及', '等', '中', '到', '从', '对', '就', '也', '都', '而',
  '且', '但', '如', '被', '把', '让', '给', '向', '这', '那', '之', '所', '者', '于', '其', '将', '已', '不', '没', '很',
  '通过', '使用', '进行', '实现', '可以', '需要', '应该', '一个', '这个', '那个'
]);

const CONCEPT_PATTERNS = {
  tech: /\b(Rust|Python|JavaScript|TypeScript|AI|API|SQL|Redis|PostgreSQL|LLM|GPT|Embedding|Vector|Docker|K8s|Kubernetes|Brain|ClawHub|GitHub|Git|Linux|Ubuntu)\b/gi,
  chineseKeywords: /(用户|记忆|系统|模块|功能|项目|任务|计划|目标|问题|方案|设计|架构|数据|配置|文件|脚本|服务|概念|实体|情感|意图|决策|对话|预测|反思|联想|遗忘|学习|优化|改进|更新|版本|日志|错误|警告|分析|洞察|建议|偏好|兴趣|画像|模式|趋势|关系|网络|节点|向量|嵌入|缓存|存储|数据库|查询|检索|编码|处理|参数|选项|设置|环境|依赖|框架|工具|平台|接口|文档|测试|验证|检查|监控|性能|质量|准确性|可靠性|安全性|权限|认证|授权|路径|目录|格式|函数|方法|类|属性|变量|异常|内存|磁盘|网络|并发|异步|队列|索引|排序|搜索|过滤|创建|读取|写入|删除|事务|启动|停止|重启|初始化|安装|加载|保存|导出|导入|升级|发布|部署|维护|重构|修复|清理|网关|代理|路由|控制器|客户端|服务器|请求|响应|会话|Token|密钥|签名|加密|解密)/g
};

const extractEntities = (text) => {
  const entities = [];
  const seen = new Set();
  
  // 1. 技术术语
  const techTerms = text.match(CONCEPT_PATTERNS.tech) || [];
  techTerms.forEach(term => {
    const normalized = term.toLowerCase();
    if (!seen.has(normalized)) {
      seen.add(normalized);
      entities.push(term);
    }
  });
  
  // 2. 中文关键词
  const chineseKeywords = text.match(CONCEPT_PATTERNS.chineseKeywords) || [];
  chineseKeywords.forEach(word => {
    const normalized = word.toLowerCase();
    if (!seen.has(normalized)) {
      seen.add(normalized);
      entities.push(word);
    }
  });
  
  // 3. 简单中文词组（2-4字，过滤停用词）
  if (entities.length < 5) {
    const simpleMatches = text.match(/[\u4e00-\u9fa5]{2,4}/g) || [];
    for (const word of simpleMatches) {
      // 过滤停用词开头或结尾的词
      if (STOPWORDS.has(word[0]) || STOPWORDS.has(word.slice(-1))) continue;
      // 过滤纯停用词组合
      if (word.split('').every(c => STOPWORDS.has(c))) continue;
      
      const normalized = word.toLowerCase();
      if (!seen.has(normalized) && entities.length < 10) {
        seen.add(normalized);
        entities.push(word);
      }
    }
  }
  
  return entities.slice(0, 10);
};

// 计算重要性
const calculateImportance = (content, metadata) => {
  let importance = 0.5;
  
  // 用户消息更重要
  if (metadata.role === 'user') importance += 0.2;
  
  // 包含关键词
  const importantKeywords = ['记住', '重要', '偏好', '设置', '不要', '喜欢', '讨厌'];
  for (const kw of importantKeywords) {
    if (content.includes(kw)) {
      importance += 0.1;
    }
  }
  
  // 长内容可能更重要
  if (content.length > 100) importance += 0.1;
  if (content.length > 500) importance += 0.1;
  
  return Math.min(1.0, importance);
};

// ============================================================================
// 用户建模自动学习
// ============================================================================


// 话题关键词
const TOPIC_KEYWORDS = {
  '编程': ['代码', '函数', '变量', 'bug', 'error', '编译', '运行', '调试'],
  'AI': ['AI', '模型', '训练', '神经网络', '机器学习', '深度学习', 'LLM', 'GPT'],
  '记忆': ['记忆', '回忆', '记住', '忘记', 'brain', 'cognitive'],
  '项目': ['项目', '工程', '开发', '版本', '发布', '部署'],
  '数据': ['数据', '数据库', 'SQL', 'PostgreSQL', 'Redis', '存储'],
  '系统': ['系统', '配置', '服务器', '部署', '监控', '日志'],
  '文档': ['文档', 'markdown', '笔记', '记录', '总结'],
  '聊天': ['聊天', '对话', '消息', 'QQ', '私聊', '群']
};

// 从消息中提取话题
const extractTopics = (text) => {
  const topics = [];
  for (const [topic, keywords] of Object.entries(TOPIC_KEYWORDS)) {
    for (const kw of keywords) {
      if (text.toLowerCase().includes(kw.toLowerCase())) {
        topics.push(topic);
        break;
      }
    }
  }
  return topics;
};

// 推断沟通风格
const inferCommunicationStyle = (text) => {
  const formal = ['请', '麻烦', '能否', '是否', '您好'].filter(k => text.includes(k)).length;
  const casual = ['哈', '哈哈', '嗯', '啊', '呢', '吧', '～', '...'].filter(k => text.includes(k)).length;
  
  if (formal > casual) return 'formal';
  if (casual > formal) return 'casual';
  return 'balanced';
};

// 更新用户模型
const updateUserModel = (message, metadata) => {
  try {
    // 加载现有模型
    let userModel = {
      basic: { name: null, communicationStyle: 'casual' },
      preferences: { topics: {} },
      patterns: { activeHours: [], commonTasks: {} },
      knowledge: { knownConcepts: [], expertiseAreas: [] },
      stats: { totalInteractions: 0, lastInteraction: null }
    };
    
    if (fs.existsSync(USER_MODEL_PATH)) {
      userModel = JSON.parse(fs.readFileSync(USER_MODEL_PATH, 'utf8'));
    }
    
    // 更新交互统计
    userModel.stats.totalInteractions++;
    userModel.stats.lastInteraction = Date.now();
    
    // 记录活跃时段
    const hour = new Date().getHours();
    if (!userModel.patterns.activeHours.includes(hour)) {
      userModel.patterns.activeHours.push(hour);
      userModel.patterns.activeHours.sort();
    }
    
    // 提取并更新话题兴趣
    const topics = extractTopics(message);
    for (const topic of topics) {
      if (!userModel.preferences.topics[topic]) {
        userModel.preferences.topics[topic] = 0;
      }
      userModel.preferences.topics[topic] = Math.min(1, userModel.preferences.topics[topic] + 0.1);
    }
    
    // 推断沟通风格
    const style = inferCommunicationStyle(message);
    if (style !== 'balanced') {
      userModel.basic.communicationStyle = style;
    }
    
    // 提取用户名（如果消息中包含自我介绍）
    const nameMatch = message.match(/我叫(\S+)|我是(\S+)|名字[是为](\S+)/);
    if (nameMatch) {
      userModel.basic.name = nameMatch[1] || nameMatch[2] || nameMatch[3];
    }
    
    // 提取偏好关键词
    const prefs = message.match(/(喜欢|偏好|想要|希望)(\S+)/g);
    if (prefs) {
      for (const p of prefs) {
        const pref = p.replace(/喜欢|偏好|想要|希望/g, '');
        if (pref && pref.length < 10 && !userModel.knowledge.knownConcepts.includes(pref)) {
          userModel.knowledge.knownConcepts.push(pref);
        }
      }
    }
    
    // 保存
    fs.writeFileSync(USER_MODEL_PATH, JSON.stringify(userModel, null, 2));
    return userModel;
  } catch (e) {
    console.error('[cognitive-recall] User model update error:', e.message);
    return null;
  }
};

// ============================================================================
// 预测和预加载模块
// ============================================================================

const { predictAndPreload } = require(path.join(SKILL_DIR, 'scripts/prediction_client.cjs'));

// ============================================================================
// Hook handler
// ============================================================================

const handler = async (event) => {
  // Only handle preprocessed messages
  if (event.type !== 'message' || event.action !== 'preprocessed') {
    return;
  }

  // Skip if no context
  if (!event.context) {
    return;
  }

  // Only recall for direct messages (not groups)
  if (event.context.isGroup || event.context.groupId) {
    return;
  }

  // Skip if bodyForAgent is empty
  if (!event.context.bodyForAgent) {
    return;
  }

  // Get dynamic keywords
  const keywords = keywordState.getKeywords();
  
  // 教训关键词 - 始终检索
  const lessonKeywords = ['教训', '规则', '记住', '必须', '不要'];
  
  const sender = event.context.senderId || event.sender_id || 'unknown';

  try {
    // 初始化共享工作区
    await initSharedMemory();
    
    // 并行执行：检索记忆 + 教训 + 预测
    const [memoriesResult, lessonsResult, predictionResult] = await Promise.all([
      recallFromDB(keywords, 5),
      getLessonsFromSharedMemory(),
      predictAndPreload(sender, [event.context.bodyForAgent])
    ]);
    
    const memories = memoriesResult;
    const lessons = lessonsResult;
    const { predictions, memories: predictedMemories } = predictionResult;

    const contextParts = [];
    
    // 注入预测信息
    if (predictions && predictions.length > 0) {
      const predLines = predictions.map(p => {
        const confidenceEmoji = p.confidence > 0.7 ? '🔴' : p.confidence > 0.5 ? '🟡' : '🔵';
        return `  ${confidenceEmoji} ${p.reason}`;
      });
      contextParts.push(`[🔮 预测]\n${predLines.join('\n')}\n[/预测]`);
    }
    
    // 注入预加载的记忆
    if (predictedMemories && predictedMemories.length > 0) {
      const preloadLines = predictedMemories.map(m => {
        return `  - ${m.summary || m.content.substring(0, 80)}${m.preloadReason ? ` (${m.preloadReason})` : ''}`;
      });
      contextParts.push(`[⚡ 预加载]\n${preloadLines.join('\n')}\n[/预加载]`);
    }
    
    // 注入普通记忆
    if (memories && memories.length > 0) {
      const memoryLines = memories.map(m => {
        const source = m.source ? ` (${m.source})` : '';
        return `  - ${m.summary}${source}`;
      });
      contextParts.push(`[🧠 Memory Context]\n${memoryLines.join('\n')}\n[/Memory Context]`);
    }
    
    // 注入教训
    if (lessons && lessons.length > 0) {
      const lessonLines = lessons.map(l => `  - ${l.summary}`);
      contextParts.push(`[⚠️ 教训提醒]\n${lessonLines.join('\n')}\n[/教训提醒]`);
    }

    if (contextParts.length > 0) {
      const fullContext = '\n\n' + contextParts.join('\n\n') + '\n\n';
      event.context.bodyForAgent = fullContext + event.context.bodyForAgent;
      console.log('[cognitive-recall] Injected', 
        memories?.length || 0, 'memories +', 
        lessons?.length || 0, 'lessons +',
        predictions?.length || 0, 'predictions +',
        predictedMemories?.length || 0, 'preloaded');
    }
    
    // 自动编码用户消息（异步，不阻塞）
    const userMessage = event.context.bodyForAgent;
    
    encodeMemory(userMessage, {
      role: 'user',
      sender,
      channel: event.context.channel || 'unknown',
      type: 'conversation'
    }).then(id => {
      if (id) {
        console.log('[cognitive-recall] Auto-encoded user message:', id);
      }
    }).catch(() => {});
    
    // 自动学习用户偏好（异步）
    const userModel = updateUserModel(userMessage, { sender });
    if (userModel && userModel.preferences.topics) {
      const topTopics = Object.entries(userModel.preferences.topics)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 3)
        .map(([t]) => t);
      if (topTopics.length > 0) {
        console.log('[cognitive-recall] 用户兴趣:', topTopics.join(', '));
      }
    }
    
  } catch (err) {
    console.error('[cognitive-recall] Error:', err.message || String(err));
  }
};

module.exports = handler;
