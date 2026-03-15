#!/usr/bin/env node
/**
 * Cognitive Brain - 联想网络初始化
 * 从已有记忆中提取实体，构建概念网络
 */

const fs = require('fs');
const path = require('path');

const HOME = process.env.HOME || '/root';
const SKILL_DIR = path.join(HOME, '.openclaw/workspace/skills/cognitive-brain');
const CONFIG_PATH = path.join(SKILL_DIR, 'config.json');

/**
 * 初始化联想网络
 */
async function initNetwork() {
  let pg;
  try {
    pg = require('pg');
  } catch (e) {
    console.log('❌ pg 模块未安装');
    return;
  }
  
  const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
  const { Pool } = pg;
  const pool = new Pool(config.storage.primary);
  
  console.log('🔍 正在从记忆中提取概念...\n');
  
  // 1. 获取所有记忆
  const memories = await pool.query(`
    SELECT id, summary, content, entities, type
    FROM episodes
    ORDER BY importance DESC
    LIMIT 500
  `);
  
  console.log(`📚 找到 ${memories.rows.length} 条记忆\n`);
  
  // 2. 提取所有概念
  const conceptMap = new Map();
  const coOccurrences = new Map();
  
  for (const row of memories.rows) {
    let entities = [];
    try {
      entities = typeof row.entities === 'string' ? JSON.parse(row.entities) : (row.entities || []);
    } catch (e) {}
    
    // 也从 summary 中提取
    const summaryEntities = row.summary?.match(/[\u4e00-\u9fa5]{2,6}/g) || [];
    entities.push(...summaryEntities);
    
    // 去重
    entities = [...new Set(entities)].filter(e => e && e.length > 1);
    
    // 记录概念
    for (const e of entities) {
      conceptMap.set(e, (conceptMap.get(e) || 0) + 1);
    }
    
    // 记录共现
    for (let i = 0; i < entities.length; i++) {
      for (let j = i + 1; j < entities.length; j++) {
        const key = `${entities[i]}:${entities[j]}`;
        coOccurrences.set(key, (coOccurrences.get(key) || 0) + 1);
      }
    }
  }
  
  console.log(`🧠 提取到 ${conceptMap.size} 个概念`);
  console.log(`🔗 发现 ${coOccurrences.size} 对共现关系\n`);
  
  // 3. 插入概念到数据库
  let insertedConcepts = 0;
  const conceptIdMap = new Map();
  
  for (const [name, count] of conceptMap) {
    if (count < 1) continue; // 至少出现1次
    
    try {
      const result = await pool.query(`
        INSERT INTO concepts (name, metadata, created_at)
        VALUES ($1, $2, NOW())
        ON CONFLICT (name) DO UPDATE SET metadata = EXCLUDED.metadata
        RETURNING id
      `, [name, JSON.stringify({ count, source: 'auto_extract' })]);
      
      if (result.rows[0]) {
        conceptIdMap.set(name, result.rows[0].id);
        insertedConcepts++;
      }
    } catch (e) {
      // 忽略错误
    }
  }
  
  console.log(`✅ 插入 ${insertedConcepts} 个概念\n`);
  
  // 4. 插入联想关系
  let insertedAssociations = 0;
  const total = memories.rows.length;
  
  for (const [key, count] of coOccurrences) {
    if (count < 1) continue;
    
    const [from, to] = key.split(':');
    const fromId = conceptIdMap.get(from);
    const toId = conceptIdMap.get(to);
    
    if (!fromId || !toId) continue;
    
    // 计算关联强度
    const weight = Math.min(1.0, count / total + 0.1);
    
    try {
      await pool.query(`
        INSERT INTO associations (from_id, to_id, type, weight, created_at)
        VALUES ($1, $2, $3, $4, NOW())
        ON CONFLICT DO NOTHING
      `, [fromId, toId, 'co_occurs', weight]);
      
      insertedAssociations++;
    } catch (e) {
      // 忽略错误
    }
  }
  
  console.log(`✅ 插入 ${insertedAssociations} 条联想关系\n`);
  
  // 5. 显示统计
  const stats = await pool.query(`
    SELECT 
      (SELECT COUNT(*) FROM concepts) as concepts,
      (SELECT COUNT(*) FROM associations) as associations
  `);
  
  console.log('📊 联想网络统计:');
  console.log(`   概念节点: ${stats.rows[0].concepts}`);
  console.log(`   联想边: ${stats.rows[0].associations}`);
  
  await pool.end();
}

// 主函数
async function main() {
  const args = process.argv.slice(2);
  
  if (args[0] === 'run') {
    await initNetwork();
  } else {
    console.log(`
联想网络初始化

用法:
  node init_associations.cjs run    # 从记忆中提取概念并构建网络
    `);
  }
}

main().catch(console.error);
