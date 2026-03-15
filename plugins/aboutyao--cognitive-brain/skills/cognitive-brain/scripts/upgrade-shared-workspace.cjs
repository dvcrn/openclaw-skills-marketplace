#!/usr/bin/env node
/**
 * Cognitive Brain - 共享工作区升级脚本 v2.7.0
 */

const { resolveModule } = require('./module_resolver.cjs');
const fs = require('fs');
const path = require('path');

const HOME = process.env.HOME || '/root';
const SKILL_DIR = path.join(HOME, '.openclaw/workspace/skills/cognitive-brain');
const CONFIG_PATH = path.join(SKILL_DIR, 'config.json');

const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));

const SHARED_WORKSPACE_SCHEMA = `
-- ============================================
-- 共享工作区 - 系统记忆表 (替代 MEMORY.md)
-- ============================================
CREATE TABLE IF NOT EXISTS system_memory (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  key TEXT NOT NULL UNIQUE,
  category TEXT NOT NULL DEFAULT 'general',
  content TEXT NOT NULL,
  importance REAL DEFAULT 0.5,
  version INTEGER DEFAULT 1,
  updated_by TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_system_memory_key ON system_memory (key);
CREATE INDEX IF NOT EXISTS idx_system_memory_category ON system_memory (category);

-- ============================================
-- 共享工作区 - 会话间共享上下文
-- ============================================
CREATE TABLE IF NOT EXISTS shared_context (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id TEXT NOT NULL,
  context_type TEXT NOT NULL,
  content JSONB NOT NULL,
  ttl INTEGER DEFAULT 3600,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_shared_context_session ON shared_context (session_id);
CREATE INDEX IF NOT EXISTS idx_shared_context_type ON shared_context (context_type);
CREATE INDEX IF NOT EXISTS idx_shared_context_expires ON shared_context (expires_at);

-- ============================================
-- 共享工作区 - 变更日志
-- ============================================
CREATE TABLE IF NOT EXISTS memory_changes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  table_name TEXT NOT NULL,
  record_id UUID NOT NULL,
  change_type TEXT NOT NULL,
  old_data JSONB,
  new_data JSONB,
  changed_by TEXT,
  changed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_memory_changes_time ON memory_changes (changed_at DESC);
CREATE INDEX IF NOT EXISTS idx_memory_changes_table ON memory_changes (table_name);
`;

const NOTIFY_FUNCTION = `
CREATE OR REPLACE FUNCTION notify_memory_change()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    PERFORM pg_notify('memory_change', json_build_object(
      'table', TG_TABLE_NAME,
      'id', NEW.id,
      'type', 'INSERT'
    )::text);
    RETURN NEW;
  ELSIF TG_OP = 'UPDATE' THEN
    PERFORM pg_notify('memory_change', json_build_object(
      'table', TG_TABLE_NAME,
      'id', NEW.id,
      'type', 'UPDATE'
    )::text);
    RETURN NEW;
  ELSIF TG_OP = 'DELETE' THEN
    PERFORM pg_notify('memory_change', json_build_object(
      'table', TG_TABLE_NAME,
      'id', OLD.id,
      'type', 'DELETE'
    )::text);
    RETURN OLD;
  END IF;
END;
$$ LANGUAGE plpgsql;
`;

async function upgrade() {
  console.log('🔄 Cognitive Brain - 共享工作区升级 v2.7.0');
  console.log('==============================================\n');
  
  try {
    const pg = resolveModule('pg');
    const { Pool } = pg;
    const pool = new Pool(config.storage.primary);
    
    console.log('📦 连接 PostgreSQL...');
    await pool.query('SELECT NOW()');
    console.log('✅ PostgreSQL 连接成功\n');
    
    console.log('📋 创建共享工作区表...');
    await pool.query(SHARED_WORKSPACE_SCHEMA);
    console.log('✅ 表创建完成\n');
    
    console.log('🔔 创建变更通知函数...');
    await pool.query(NOTIFY_FUNCTION);
    console.log('✅ 函数创建完成\n');
    
    console.log('⚡ 添加触发器...');
    await pool.query(`
      DROP TRIGGER IF EXISTS system_memory_change ON system_memory;
      CREATE TRIGGER system_memory_change
        AFTER INSERT OR UPDATE OR DELETE ON system_memory
        FOR EACH ROW EXECUTE FUNCTION notify_memory_change();
    `);
    console.log('✅ 触发器添加完成\n');
    
    // 统计
    const stats = await pool.query(`
      SELECT 
        (SELECT count(*) FROM system_memory) as system_memory,
        (SELECT count(*) FROM shared_context) as shared_context,
        (SELECT count(*) FROM memory_changes) as memory_changes
    `);
    
    console.log('📊 共享工作区状态:');
    console.log(`   系统记忆: ${stats.rows[0].system_memory}`);
    console.log(`   共享上下文: ${stats.rows[0].shared_context}`);
    console.log(`   变更日志: ${stats.rows[0].memory_changes}\n`);
    
    await pool.end();
    
    console.log('🎉 共享工作区升级完成！');
    console.log('\n新功能:');
    console.log('  - 跨会话共享记忆');
    console.log('  - 实时变更通知');
    console.log('  - Redis 缓存加速');
    
  } catch (error) {
    console.error('❌ 升级失败:', error.message);
    process.exit(1);
  }
}

upgrade();
