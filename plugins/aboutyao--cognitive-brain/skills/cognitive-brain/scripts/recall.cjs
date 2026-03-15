#!/usr/bin/env node
const { resolveModule } = require('./module_resolver.cjs');
/**
 * Cognitive Brain - 记忆检索脚本
 * 从记忆系统中检索相关信息
 */

const fs = require('fs');
const path = require('path');

// 加载配置
const configPath = path.join(__dirname, '..', 'config.json');
const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));

// 解析参数
function parseArgs() {
  const args = process.argv.slice(2);
  const params = {};
  for (let i = 0; i < args.length; i += 2) {
    const key = args[i].replace('--', '');
    params[key] = args[i + 1];
  }
  return params;
}

// Redis 缓存层
let redis = null;
let redisClient = null;

// Embedding 支持 - 使用服务客户端
const { getEmbeddingService } = require('./embedding_service.cjs');
let embeddingService = null;

async function getEmbedding(text) {
  if (config.embedding?.provider !== 'local') return null;
  
  try {
    // 延迟初始化服务
    if (!embeddingService) {
      embeddingService = getEmbeddingService();
    }
    
    // 使用非阻塞模式 - 如果服务未就绪立即返回 null
    return await embeddingService.embed(text, false);
  } catch (e) {
    return null;
  }
}

async function vectorSearch(pool, query, limit = 10) {
  const embedding = await getEmbedding(query);
  if (!embedding) return [];
  
  try {
    // 使用 pgvector 进行向量搜索
    const result = await pool.query(`
      SELECT id, summary, content, timestamp, importance, type,
        1 - (embedding <=> $1::vector) as similarity
      FROM episodes
      WHERE embedding IS NOT NULL
      ORDER BY embedding <=> $1::vector
      LIMIT $2
    `, [JSON.stringify(embedding), limit]);
    
    return result.rows;
  } catch (e) {
    return [];
  }
}

async function initRedis() {
  if (redis) return true;
  
  try {
    redis = require('redis');
    const { createClient } = redis;
    
    redisClient = createClient({
      socket: {
        host: config.storage.cache?.host || 'localhost',
        port: config.storage.cache?.port || 6379
      },
      database: config.storage.cache?.db || 0
    });
    
    await redisClient.connect();
    return true;
  } catch (e) {
    console.log('[recall] Redis 不可用，跳过缓存');
    return false;
  }
}

// 获取缓存
async function getCache(key) {
  if (!redisClient) return null;
  
  try {
    const cached = await redisClient.get(`brain:${key}`);
    if (cached) {
      return JSON.parse(cached);
    }
  } catch (e) {
    // ignore
  }
  return null;
}

// 设置缓存
async function setCache(key, value, ttlSeconds = 60) {
  if (!redisClient) return;
  
  try {
    await redisClient.setEx(`brain:${key}`, ttlSeconds, JSON.stringify(value));
  } catch (e) {
    // ignore
  }
}

// 关键词检索（支持多关键词）
async function keywordSearch(pool, query, limit = 10) {
  try {
    // 分割查询词，支持空格分隔的多个关键词
    const keywords = query.split(/\s+/).filter(k => k.length > 0);
    
    // 构建条件：每个关键词匹配 summary 或 content
    const conditions = keywords.map((_, i) => 
      `(summary ILIKE $${i + 1} OR content ILIKE $${i + 1})`
    ).join(' OR ');
    
    const params = keywords.map(k => `%${k}%`);
    params.push(limit);
    
    const result = await pool.query(`
      SELECT id, summary, content, timestamp, importance, type
      FROM episodes
      WHERE ${conditions}
      ORDER BY importance DESC, timestamp DESC
      LIMIT $${params.length}
    `, params);
    
    return result.rows;
  } catch (e) {
    console.error('keywordSearch error:', e.message);
    return [];
  }
}

// 联想激活检索
async function associationSearch(pool, query, limit = 10) {
  try {
    // 1. 找到查询相关的概念
    const concepts = await pool.query(`
      SELECT id, name FROM concepts 
      WHERE name ILIKE $1
      LIMIT 5
    `, [`%${query}%`]);
    
    if (concepts.rows.length === 0) return [];
    
    // 2. 激活传播
    const activated = new Map();
    const frontier = new Map();
    
    concepts.rows.forEach(c => frontier.set(c.id, { name: c.name, level: 1.0 }));
    
    const threshold = 0.3;
    const decay = 0.9;
    
    for (let depth = 0; depth < 3; depth++) {
      const newFrontier = new Map();
      
      for (const [conceptId, data] of frontier) {
        if (data.level < threshold) continue;
        
        activated.set(conceptId, data);
        
        // 沿边传播
        const edges = await pool.query(`
          SELECT c.id, c.name, a.weight 
          FROM associations a
          JOIN concepts c ON c.id = a.to_id
          WHERE a.from_id = $1
        `, [conceptId]);
        
        for (const edge of edges.rows) {
          const newLevel = data.level * decay * edge.weight;
          if (!newFrontier.has(edge.id) || newFrontier.get(edge.id).level < newLevel) {
            newFrontier.set(edge.id, { name: edge.name, level: newLevel });
          }
        }
      }
      
      frontier.clear();
      newFrontier.forEach((v, k) => frontier.set(k, v));
    }
    
    // 3. 用激活的概念检索记忆
    const conceptNames = [...activated.values()].map(a => a.name);
    
    if (conceptNames.length === 0) return [];
    
    const placeholders = conceptNames.map((_, i) => `$${i + 1}`).join(',');
    
    const result = await pool.query(`
      SELECT DISTINCT e.id, e.summary, e.content, e.timestamp, e.importance, e.type
      FROM episodes e
      WHERE EXISTS (
        SELECT 1 FROM json_array_elements_text(e.entities) entity
        WHERE entity IN (${placeholders})
      )
      ORDER BY e.importance DESC
      LIMIT $${conceptNames.length + 1}
    `, [...conceptNames, limit]);
    
    return result.rows;
  } catch (e) {
    return [];
  }
}

// 混合检索 - 增强版（集成工作记忆）
async function hybridSearch(pool, query, options = {}) {
  const limit = options.limit || 10;
  
  // 加载工作记忆
  const workingMemoryPath = path.join(__dirname, '..', '.working-memory.json');
  let workingMemory = null;
  try {
    if (fs.existsSync(workingMemoryPath)) {
      workingMemory = JSON.parse(fs.readFileSync(workingMemoryPath, 'utf8'));
    }
  } catch (e) {
    // ignore
  }
  
  const keywordResults = await keywordSearch(pool, query, limit);
  const assocResults = await associationSearch(pool, query, limit);
  const vectorResults = await vectorSearch(pool, query, limit);
  
  // 合并去重
  const merged = new Map();
  
  keywordResults.forEach((r, i) => {
    merged.set(r.id, { 
      ...r, 
      score: (limit - i) / limit * 0.3,
      source: 'keyword'
    });
  });
  
  assocResults.forEach((r, i) => {
    if (merged.has(r.id)) {
      merged.get(r.id).score += (limit - i) / limit * 0.3;
      merged.get(r.id).source = 'hybrid';
    } else {
      merged.set(r.id, { 
        ...r, 
        score: (limit - i) / limit * 0.3,
        source: 'association'
      });
    }
  });
  
  // 向量搜索结果权重更高
  vectorResults.forEach((r, i) => {
    const vectorScore = r.similarity ? r.similarity * 0.4 : (limit - i) / limit * 0.4;
    if (merged.has(r.id)) {
      merged.get(r.id).score += vectorScore;
      merged.get(r.id).source = 'hybrid+vector';
    } else {
      merged.set(r.id, { 
        ...r, 
        score: vectorScore,
        source: 'vector'
      });
    }
  });
  
  // 工作记忆增强：提升当前活跃话题相关记忆的分数
  if (workingMemory?.activeContext) {
    const activeEntities = workingMemory.activeContext.entities || [];
    const activeTopic = workingMemory.activeContext.topic;
    
    merged.forEach((memory, id) => {
      let boost = 0;
      
      // 匹配活跃实体
      if (memory.entities && Array.isArray(memory.entities)) {
        const entityMatch = memory.entities.filter(e => activeEntities.includes(e));
        if (entityMatch.length > 0) {
          boost += 0.1 * entityMatch.length;
        }
      }
      
      // 匹配活跃话题
      if (activeTopic && (memory.summary?.includes(activeTopic) || memory.content?.includes(activeTopic))) {
        boost += 0.15;
      }
      
      if (boost > 0) {
        memory.score += boost;
        memory.source = memory.source === 'hybrid' ? 'hybrid+working' : 'working_boost';
      }
    });
  }
  
  // 排序返回
  return [...merged.values()]
    .sort((a, b) => b.score - a.score)
    .slice(0, limit);
}

// 从文件检索（后备方案）
function searchFromFile(query, limit = 10) {
  const memoryFile = path.join(__dirname, '..', 'data', 'memories.jsonl');
  
  if (!fs.existsSync(memoryFile)) {
    return [];
  }
  
  const lines = fs.readFileSync(memoryFile, 'utf8').split('\n').filter(Boolean);
  const memories = lines.map(line => JSON.parse(line));
  
  const results = memories
    .filter(m => 
      m.summary?.includes(query) || 
      m.content?.includes(query) ||
      m.entities?.some(e => e.includes(query))
    )
    .sort((a, b) => b.importance - a.importance)
    .slice(0, limit);
  
  return results;
}

// 主函数
async function recall(query, options = {}) {
  let results = [];
  let source = 'file';
  const limit = options.limit || 10;
  
  // 0. 意图识别（新增）
  let intent = null;
  try {
    const intentPath = path.join(__dirname, 'intent.cjs');
    if (fs.existsSync(intentPath)) {
      const intentModule = require(intentPath);
      intent = intentModule.recognizeIntent(query);
      
      // 根据意图调整检索策略
      if (intent) {
        options.intentBoost = {
          question: intent.name === 'question' ? 0.2 : 0,
          search: intent.name === 'search' ? 0.3 : 0,
          request: intent.name === 'request' ? 0.15 : 0
        };
      }
    }
  } catch (e) {
    // 意图识别失败不影响主流程
  }
  
  // 1. 生成缓存 key
  const cacheKey = `recall:${query}:${limit}`;
  
  // 2. 尝试从 Redis 获取
  const redisOk = await initRedis();
  if (redisOk) {
    const cached = await getCache(cacheKey);
    if (cached) {
      console.log('[recall] ✅ Redis 缓存命中');
      return {
        query,
        results: cached,
        total: cached.length,
        source: 'redis',
        cached: true,
        timestamp: new Date().toISOString()
      };
    }
  }
  
  // 3. 从 PostgreSQL 检索
  try {
    const pg = resolveModule('pg');
    const { Pool } = pg;
    const pool = new Pool(config.storage.primary);
    
    results = await hybridSearch(pool, query, options);
    source = 'postgresql';
    
    // 更新访问计数
    for (const r of results) {
      await pool.query(`
        UPDATE episodes 
        SET access_count = access_count + 1, last_accessed = NOW()
        WHERE id = $1
      `, [r.id]);
    }
    
    await pool.end();
    
    // 4. 写入 Redis 缓存
    if (redisOk && results.length > 0) {
      // 根据重要性决定 TTL
      const maxImportance = Math.max(...results.map(r => r.importance || 0.5));
      let ttl = 60; // 默认 1 分钟
      if (maxImportance >= 0.8) ttl = 600;      // 高重要性 10 分钟
      else if (maxImportance >= 0.5) ttl = 180; // 中等 3 分钟
      
      await setCache(cacheKey, results, ttl);
      console.log(`[recall] 📦 已缓存 ${results.length} 条结果 (${ttl}s)`);
    }
    
  } catch (e) {
    results = searchFromFile(query, limit);
  }
  
  return {
    query,
    results,
    total: results.length,
    source,
    cached: false,
    timestamp: new Date().toISOString()
  };
}

// 执行
async function main() {
  const params = parseArgs();
  
  if (!params.query) {
    console.log('用法: node recall.cjs --query "关键词" [--options \'{"limit":5}\' ]');
    console.log('\n示例:');
    console.log('  node recall.cjs --query "项目"');
    console.log('  node recall.cjs --query "Alpha" --options \'{"limit":3}\'');
    process.exit(1);
  }
  
  const options = params.options ? JSON.parse(params.options) : {};
  
  console.log(`🔍 检索: "${params.query}"\n`);
  
  const result = await recall(params.query, options);
  
  console.log(`✅ 找到 ${result.total} 条记忆 (来源: ${result.source})\n`);
  
  result.results.forEach((r, i) => {
    console.log(`[${i + 1}] ${r.summary.slice(0, 50)}...`);
    console.log(`    类型: ${r.type} | 重要性: ${r.importance?.toFixed(2) || 'N/A'}`);
    console.log(`    时间: ${r.timestamp || r.created_at}`);
    if (r.score) console.log(`    相关度: ${(r.score * 100).toFixed(1)}%`);
    console.log();
  });
}

main();
