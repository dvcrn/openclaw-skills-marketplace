#!/usr/bin/env node
/**
 * Cognitive Brain - 记忆时间线
 * 按时间轴查看和管理记忆
 */

const fs = require('fs');
const path = require('path');
const { resolveModule } = require('./module_resolver.cjs');

const HOME = process.env.HOME || '/root';
const SKILL_DIR = path.join(HOME, '.openclaw/workspace/skills/cognitive-brain');
const CONFIG_PATH = path.join(SKILL_DIR, 'config.json');
const OUTPUT_DIR = path.join(HOME, '.openclaw/workspace/brain-visuals');

const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));

if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

/**
 * 生成记忆时间线
 */
async function generateTimeline(days = 7) {
  const { Pool } = resolveModule('pg');
  const pool = new Pool(config.storage.primary);
  
  try {
    console.log(`📅 生成最近 ${days} 天的记忆时间线...\n`);
    
    const result = await pool.query(`
      SELECT 
        id, 
        type, 
        summary, 
        content,
        importance,
        created_at,
        entities
      FROM episodes
      WHERE created_at > NOW() - INTERVAL '${days} days'
      ORDER BY created_at DESC
    `);
    
    if (result.rows.length === 0) {
      console.log('该时间段内没有记忆。');
      return;
    }
    
    // 按日期分组
    const grouped = {};
    for (const row of result.rows) {
      const date = new Date(row.created_at).toISOString().split('T')[0];
      if (!grouped[date]) {
        grouped[date] = [];
      }
      grouped[date].push(row);
    }
    
    // 生成 Markdown 时间线
    let md = '# 📅 记忆时间线\n\n';
    md += `生成时间: ${new Date().toLocaleString('zh-CN')}\n`;
    md += `时间范围: 最近 ${days} 天\n`;
    md += `总记忆数: ${result.rows.length} 条\n\n`;
    md += '---\n\n';
    
    const typeEmoji = {
      'conversation': '💬',
      'task': '✅',
      'error': '❌',
      'correction': '🔧',
      'reflection': '🤔',
      'thought': '💭',
      'test': '🧪',
      'success': '🎉',
      'episode': '📝'
    };
    
    for (const [date, memories] of Object.entries(grouped).sort().reverse()) {
      const dateObj = new Date(date);
      const weekday = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][dateObj.getDay()];
      
      md += `## ${date} ${weekday}\n\n`;
      
      for (const m of memories) {
        const time = new Date(m.created_at).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
        const emoji = typeEmoji[m.type] || '📝';
        const stars = '★'.repeat(Math.floor(m.importance * 5));
        
        md += `<details>\n`;
        md += `<summary>${emoji} <b>${time}</b> ${m.summary || m.content.substring(0, 50)}${m.content.length > 50 ? '...' : ''} ${stars}</summary>\n\n`;
        md += `- **类型**: ${m.type}\n`;
        md += `- **重要性**: ${(m.importance * 100).toFixed(0)}%\n`;
        
        if (m.entities && m.entities.length > 2) {
          try {
            const entities = JSON.parse(m.entities);
            if (Array.isArray(entities) && entities.length > 0) {
              md += `- **实体**: ${entities.slice(0, 5).join(', ')}\n`;
            }
          } catch (e) {
            // ignore
          }
        }
        
        md += `\n**内容**:\n> ${m.content.replace(/\n/g, '\n> ')}\n`;
        md += `</details>\n\n`;
      }
    }
    
    // 添加统计
    md += '---\n\n';
    md += '## 📊 统计\n\n';
    
    const typeStats = await pool.query(`
      SELECT type, COUNT(*) as count
      FROM episodes
      WHERE created_at > NOW() - INTERVAL '${days} days'
      GROUP BY type
      ORDER BY count DESC
    `);
    
    md += '| 类型 | 数量 | 占比 |\n';
    md += '|------|------|------|\n';
    for (const row of typeStats.rows) {
      const pct = ((row.count / result.rows.length) * 100).toFixed(1);
      const emoji = typeEmoji[row.type] || '📝';
      md += `| ${emoji} ${row.type} | ${row.count} | ${pct}% |\n`;
    }
    
    // 保存
    const mdPath = path.join(OUTPUT_DIR, `timeline-${days}d.md`);
    fs.writeFileSync(mdPath, md);
    
    console.log(`✅ 时间线已保存: ${mdPath}`);
    console.log(`   总记忆: ${result.rows.length} 条`);
    console.log(`   日期跨度: ${Object.keys(grouped).length} 天`);
    
    return { md, path: mdPath, count: result.rows.length };
    
  } finally {
    await pool.end();
  }
}

/**
 * 生成简洁的时间线（文本格式）
 */
async function generateSimpleTimeline(days = 7) {
  const { Pool } = resolveModule('pg');
  const pool = new Pool(config.storage.primary);
  
  try {
    console.log(`\n📅 生成简洁时间线...\n`);
    
    const result = await pool.query(`
      SELECT 
        DATE(created_at) as date,
        COUNT(*) as count,
        STRING_AGG(DISTINCT type, ', ') as types
      FROM episodes
      WHERE created_at > NOW() - INTERVAL '${days} days'
      GROUP BY DATE(created_at)
      ORDER BY date DESC
    `);
    
    let text = '📅 记忆时间线（简洁版）\n';
    text += '=' .repeat(50) + '\n\n';
    
    for (const row of result.rows) {
      const date = new Date(row.date);
      const weekday = ['日', '一', '二', '三', '四', '五', '六'][date.getDay()];
      text += `${row.date} (周${weekday}) `;
      text += '█'.repeat(Math.min(row.count, 20));
      text += ` ${row.count}条 [${row.types}]\n`;
    }
    
    text += '\n' + '='.repeat(50) + '\n';
    text += `总计: ${result.rows.reduce((a, b) => a + parseInt(b.count), 0)} 条记忆\n`;
    
    console.log(text);
    
    return text;
    
  } finally {
    await pool.end();
  }
}

/**
 * 搜索特定日期的记忆
 */
async function searchByDate(dateStr) {
  const { Pool } = resolveModule('pg');
  const pool = new Pool(config.storage.primary);
  
  try {
    console.log(`\n🔍 搜索 ${dateStr} 的记忆...\n`);
    
    const result = await pool.query(`
      SELECT type, summary, content, importance, created_at
      FROM episodes
      WHERE DATE(created_at) = $1
      ORDER BY created_at ASC
    `, [dateStr]);
    
    if (result.rows.length === 0) {
      console.log('该日期没有记忆。');
      return;
    }
    
    console.log(`${dateStr} 共有 ${result.rows.length} 条记忆:\n`);
    
    for (const m of result.rows) {
      const time = new Date(m.created_at).toLocaleTimeString('zh-CN');
      console.log(`[${time}] ${m.type}`);
      console.log(`  ${m.summary || m.content.substring(0, 80)}`);
      console.log(`  重要性: ${'★'.repeat(Math.floor(m.importance * 5))}`);
      console.log();
    }
    
  } finally {
    await pool.end();
  }
}

/**
 * 生成思绪流时间线（合并 thoughts/ 和 episodes）
 */
async function generateThoughtTimeline() {
  const thoughtsDir = path.join(HOME, '.openclaw/workspace/thoughts');
  
  console.log('\n💭 思绪流时间线\n');
  console.log('='.repeat(50));
  
  if (!fs.existsSync(thoughtsDir)) {
    console.log('还没有思绪记录。');
    return;
  }
  
  const files = fs.readdirSync(thoughtsDir)
    .filter(f => f.endsWith('.md'))
    .sort()
    .reverse();
  
  let totalThoughts = 0;
  
  for (const file of files.slice(0, 7)) { // 最近7天
    const content = fs.readFileSync(path.join(thoughtsDir, file), 'utf8');
    const thoughts = content.split('\n---\n').filter(t => t.includes('## ['));
    
    const date = file.replace('.md', '');
    console.log(`\n${date}: ${thoughts.length} 条思绪`);
    
    for (const t of thoughts.slice(0, 3)) { // 只显示前3条
      const lines = t.split('\n').filter(l => l.trim());
      const title = lines.find(l => l.startsWith('##')) || '';
      const preview = title.replace(/## \[.*?\] /, '').substring(0, 40);
      console.log(`  • ${preview}${preview.length >= 40 ? '...' : ''}`);
    }
    
    if (thoughts.length > 3) {
      console.log(`  ... 还有 ${thoughts.length - 3} 条`);
    }
    
    totalThoughts += thoughts.length;
  }
  
  console.log('\n' + '='.repeat(50));
  console.log(`总计: ${totalThoughts} 条思绪`);
}

// 主函数
async function main() {
  const args = process.argv.slice(2);
  const action = args[0] || 'recent';
  
  console.log('📅 Cognitive Brain 记忆时间线\n');
  
  try {
    switch (action) {
      case 'recent':
        const days = parseInt(args[1]) || 7;
        await generateTimeline(days);
        break;
        
      case 'simple':
        await generateSimpleTimeline(parseInt(args[1]) || 7);
        break;
        
      case 'date':
        if (!args[1]) {
          console.log('用法: node timeline.cjs date YYYY-MM-DD');
          return;
        }
        await searchByDate(args[1]);
        break;
        
      case 'thoughts':
        await generateThoughtTimeline();
        break;
        
      case 'all':
        await generateTimeline(30);
        await generateThoughtTimeline();
        break;
        
      default:
        console.log(`
用法:
  node timeline.cjs [action] [参数]

操作:
  recent [天数]     生成详细时间线（默认7天）
  simple [天数]     生成简洁时间线
  date YYYY-MM-DD   搜索特定日期
  thoughts          思绪流时间线
  all               生成完整报告

示例:
  node timeline.cjs recent 3      # 最近3天
  node timeline.cjs date 2026-03-13  # 特定日期
  node timeline.cjs thoughts      # 思绪流
        `);
    }
    
  } catch (err) {
    console.error('❌ 错误:', err.message);
    process.exit(1);
  }
}

module.exports = {
  generateTimeline,
  generateSimpleTimeline,
  searchByDate,
  generateThoughtTimeline
};

if (require.main === module) {
  main();
}
