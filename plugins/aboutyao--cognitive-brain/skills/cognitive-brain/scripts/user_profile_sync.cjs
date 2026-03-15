#!/usr/bin/env node
const { resolveModule } = require('./module_resolver.cjs');
/**
 * Cognitive Brain - 用户画像同步
 * 同步 .user-model.json 到数据库
 */

const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

const HOME = process.env.HOME || '/root';
const SKILL_DIR = path.join(HOME, '.openclaw/workspace/skills/cognitive-brain');
const CONFIG_PATH = path.join(SKILL_DIR, 'config.json');
const USER_MODEL_PATH = path.join(SKILL_DIR, '.user-model.json');

/**
 * 同步用户画像到数据库
 */
async function syncToDatabase(userId = 'default') {
  try {
    // 读取本地用户建模
    if (!fs.existsSync(USER_MODEL_PATH)) {
      console.log('用户建模文件不存在');
      return false;
    }
    
    const userModel = JSON.parse(fs.readFileSync(USER_MODEL_PATH, 'utf8'));
    
    // 连接数据库
    const pg = resolveModule('pg');
    const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
    const { Pool } = pg;
    const pool = new Pool(config.storage.primary);
    
    // 检查是否已存在
    const existing = await pool.query(
      'SELECT id FROM user_profiles WHERE user_id = $1',
      [userId]
    );
    
    const profileData = {
      preferences: userModel.preferences || {},
      patterns: userModel.patterns || {},
      known_facts: {
        concepts: userModel.knowledge?.knownConcepts || [],
        expertise: userModel.knowledge?.expertiseAreas || []
      },
      interaction_stats: {
        total: userModel.stats?.totalInteractions || 0,
        lastInteraction: userModel.stats?.lastInteraction,
        sessions: userModel.stats?.sessions?.length || 0,
        emotionPatterns: userModel.emotionPatterns?.dominantEmotions || {},
        taskPreferences: userModel.taskPreferences?.taskPatterns || {}
      }
    };
    
    if (existing.rows.length > 0) {
      // 更新
      await pool.query(`
        UPDATE user_profiles 
        SET preferences = $2, patterns = $3, known_facts = $4, 
            interaction_stats = $5, last_updated = NOW()
        WHERE user_id = $1
      `, [userId, JSON.stringify(profileData.preferences), JSON.stringify(profileData.patterns),
          JSON.stringify(profileData.known_facts), JSON.stringify(profileData.interaction_stats)]);
      console.log('✅ 用户画像已更新');
    } else {
      // 插入
      await pool.query(`
        INSERT INTO user_profiles (id, user_id, preferences, patterns, known_facts, interaction_stats)
        VALUES ($1, $2, $3, $4, $5, $6)
      `, [uuidv4(), userId, JSON.stringify(profileData.preferences), JSON.stringify(profileData.patterns),
          JSON.stringify(profileData.known_facts), JSON.stringify(profileData.interaction_stats)]);
      console.log('✅ 用户画像已创建');
    }
    
    await pool.end();
    return true;
  } catch (e) {
    console.error('❌ 同步失败:', e.message);
    return false;
  }
}

/**
 * 从数据库加载用户画像
 */
async function loadFromDatabase(userId = 'default') {
  try {
    const pg = resolveModule('pg');
    const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
    const { Pool } = pg;
    const pool = new Pool(config.storage.primary);
    
    const result = await pool.query(
      'SELECT * FROM user_profiles WHERE user_id = $1',
      [userId]
    );
    
    await pool.end();
    
    if (result.rows.length > 0) {
      return result.rows[0];
    }
    return null;
  } catch (e) {
    console.error('加载失败:', e.message);
    return null;
  }
}

module.exports = { syncToDatabase, loadFromDatabase };

// 命令行接口
if (require.main === module) {
  const args = process.argv.slice(2);
  const action = args[0] || 'sync';
  const userId = args[1] || 'default';
  
  if (action === 'sync') {
    syncToDatabase(userId);
  } else if (action === 'load') {
    loadFromDatabase(userId).then(profile => {
      console.log(JSON.stringify(profile, null, 2));
    });
  } else {
    console.log('用法: node user_profile_sync.cjs [sync|load] [userId]');
  }
}
