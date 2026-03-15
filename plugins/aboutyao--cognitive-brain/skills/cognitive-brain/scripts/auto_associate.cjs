#!/usr/bin/env node
/**
 * Cognitive Brain - 自动联想构建
 * 基于共现关系自动构建概念关联
 */

const fs = require('fs');
const path = require('path');
const { resolveModule, resolveConfig } = require('./module_resolver.cjs');

const SKILL_DIR = path.dirname(__dirname);
const CONFIG_PATH = path.join(SKILL_DIR, 'config.json');

/**
 * 分析记忆并构建共现关联
 */
async function buildCooccurrenceAssociations() {
  const pg = resolveModule('pg');
  const config = resolveConfig();
  const { Pool } = pg;
  const pool = new Pool(config.storage.primary);
  
  console.log('🔗 开始构建共现关联...\n');
  
  // 1. 获取所有记忆的实体
  const memories = await pool.query(`
    SELECT id, entities, tags, importance
    FROM episodes
    WHERE entities IS NOT NULL
  `);
  
  console.log(`📊 分析 ${memories.rows.length} 条记忆`);
  
  // 2. 构建共现矩阵
  const cooccurrence = new Map();
  
  memories.rows.forEach(memory => {
    const entities = memory.entities || [];
    const tags = memory.tags || [];
    const allTerms = [...entities, ...tags];
    
    // 统计共现
    for (let i = 0; i < allTerms.length; i++) {
      for (let j = i + 1; j < allTerms.length; j++) {
        const term1 = allTerms[i];
        const term2 = allTerms[j];
        
        if (term1 === term2) continue;
        
        const key = [term1, term2].sort().join('|||');
        cooccurrence.set(key, (cooccurrence.get(key) || 0) + 1);
      }
    }
  });
  
  console.log(`📈 发现 ${cooccurrence.size} 对共现关系`);
  
  // 3. 插入关联到数据库
  let inserted = 0;
  
  for (const [key, count] of cooccurrence.entries()) {
    const [concept1, concept2] = key.split('|||');
    
    // 计算权重（基于共现次数）
    const weight = Math.min(1, count / 5);
    
    // 获取概念ID
    const c1 = await pool.query('SELECT id FROM concepts WHERE name = $1', [concept1]);
    const c2 = await pool.query('SELECT id FROM concepts WHERE name = $1', [concept2]);
    
    if (c1.rows.length > 0 && c2.rows.length > 0) {
      const id1 = c1.rows[0].id;
      const id2 = c2.rows[0].id;
      
      // 插入或更新关联
      await pool.query(`
        INSERT INTO associations (id, from_id, to_id, weight, type)
        VALUES (gen_random_uuid(), $1, $2, $3, 'cooccurrence')
        ON CONFLICT (from_id, to_id, type) 
        DO UPDATE SET weight = GREATEST(associations.weight, $3)
      `, [id1, id2, weight]);
      
      inserted++;
    }
  }
  
  console.log(`✅ 插入/更新 ${inserted} 条关联`);
  
  // 4. 统计新密度
  const stats = await pool.query(`
    SELECT 
      (SELECT COUNT(*) FROM concepts) as nodes,
      (SELECT COUNT(*) FROM associations) as edges
  `);
  
  const nodes = parseInt(stats.rows[0].nodes);
  const edges = parseInt(stats.rows[0].edges);
  const density = nodes > 1 ? (edges / (nodes * (nodes - 1))).toFixed(4) : 0;
  
  console.log(`\n📊 联想网络状态:`);
  console.log(`   节点: ${nodes}`);
  console.log(`   边: ${edges}`);
  console.log(`   密度: ${density}`);
  
  await pool.end();
}

/**
 * 基于相似度构建关联
 */
async function buildSimilarityAssociations() {
  const pg = resolveModule('pg');
  const config = resolveConfig();
  const { Pool } = pg;
  const pool = new Pool(config.storage.primary);
  
  console.log('🔗 开始构建相似度关联...\n');
  
  // 获取所有概念
  const concepts = await pool.query('SELECT id, name FROM concepts LIMIT 100');
  
  console.log(`📊 分析 ${concepts.rows.length} 个概念`);
  
  // 简单的文本相似度（可以后续替换为 embedding 相似度）
  const { execSync } = require('child_process');
  let inserted = 0;
  
  for (let i = 0; i < concepts.rows.length; i++) {
    for (let j = i + 1; j < concepts.rows.length; j++) {
      const c1 = concepts.rows[i];
      const c2 = concepts.rows[j];
      
      // 计算简单的字符串相似度
      const similarity = calculateStringSimilarity(c1.name, c2.name);
      
      if (similarity > 0.6) {
        await pool.query(`
          INSERT INTO associations (id, from_id, to_id, weight, type)
          VALUES (gen_random_uuid(), $1, $2, $3, 'similarity')
          ON CONFLICT (from_id, to_id, type) 
          DO UPDATE SET weight = GREATEST(associations.weight, $3)
        `, [c1.id, c2.id, similarity]);
        
        inserted++;
      }
    }
  }
  
  console.log(`✅ 插入 ${inserted} 条相似度关联`);
  await pool.end();
}

/**
 * 计算字符串相似度（Jaccard）
 */
function calculateStringSimilarity(str1, str2) {
  const set1 = new Set(str1.split(''));
  const set2 = new Set(str2.split(''));
  
  const intersection = new Set([...set1].filter(x => set2.has(x)));
  const union = new Set([...set1, ...set2]);
  
  return intersection.size / union.size;
}

/**
 * 主函数
 */
async function main() {
  const args = process.argv.slice(2);
  const mode = args[0] || 'all';
  
  if (mode === 'cooccurrence' || mode === 'all') {
    await buildCooccurrenceAssociations();
  }
  
  if (mode === 'similarity' || mode === 'all') {
    await buildSimilarityAssociations();
  }
}

main().catch(e => console.error('❌ 错误:', e.message));
