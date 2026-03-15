#!/usr/bin/env node
/**
 * Cognitive Brain - 数据导出
 * 支持导出到 JSON / Markdown / CSV
 */

const fs = require('fs');
const path = require('path');
const { resolveModule, resolveConfig } = require('./module_resolver.cjs');

const SKILL_DIR = path.dirname(__dirname);

/**
 * 导出所有记忆
 */
async function exportAll(format = 'json', outputPath = null) {
  const pg = resolveModule('pg');
  const config = resolveConfig();
  const { Pool } = pg;
  const pool = new Pool(config.storage.primary);
  
  console.log('📤 导出记忆数据...\n');
  
  // 获取所有数据
  const memories = await pool.query(`
    SELECT id, type, summary, content, entities, tags, importance, timestamp
    FROM episodes
    ORDER BY timestamp DESC
  `);
  
  const concepts = await pool.query(`
    SELECT id, name, access_count
    FROM concepts
    ORDER BY access_count DESC
  `);
  
  const associations = await pool.query(`
    SELECT a.weight, a.type, c1.name as from_name, c2.name as to_name
    FROM associations a
    JOIN concepts c1 ON a.from_id = c1.id
    JOIN concepts c2 ON a.to_id = c2.id
    ORDER BY a.weight DESC
  `);
  
  await pool.end();
  
  const data = {
    memories: memories.rows,
    concepts: concepts.rows,
    associations: associations.rows,
    exportedAt: new Date().toISOString(),
    stats: {
      totalMemories: memories.rows.length,
      totalConcepts: concepts.rows.length,
      totalAssociations: associations.rows.length
    }
  };
  
  // 根据格式导出
  let output = '';
  let ext = 'json';
  
  switch (format) {
    case 'json':
      output = JSON.stringify(data, null, 2);
      ext = 'json';
      break;
      
    case 'markdown':
    case 'md':
      output = generateMarkdown(data);
      ext = 'md';
      break;
      
    case 'csv':
      output = generateCSV(data);
      ext = 'csv';
      break;
      
    default:
      console.log('❌ 不支持的格式:', format);
      console.log('   支持格式: json, markdown, csv');
      process.exit(1);
  }
  
  // 确定输出路径
  if (!outputPath) {
    outputPath = path.join(SKILL_DIR, `export_${Date.now()}.${ext}`);
  }
  
  fs.writeFileSync(outputPath, output);
  
  console.log(`✅ 导出完成!`);
  console.log(`   文件: ${outputPath}`);
  console.log(`   大小: ${(output.length / 1024).toFixed(2)} KB`);
  console.log(`   记忆: ${data.stats.totalMemories} 条`);
  console.log(`   概念: ${data.stats.totalConcepts} 个`);
  console.log(`   关联: ${data.stats.totalAssociations} 条`);
  
  return outputPath;
}

/**
 * 生成 Markdown 格式
 */
function generateMarkdown(data) {
  let md = `# Cognitive Brain 导出报告

导出时间: ${data.exportedAt}

## 统计

- 记忆数量: ${data.stats.totalMemories}
- 概念数量: ${data.stats.totalConcepts}
- 关联数量: ${data.stats.totalAssociations}

---

## 记忆列表

`;

  data.memories.forEach((m, i) => {
    md += `### ${i + 1}. ${m.summary || m.content?.slice(0, 50)}\n\n`;
    md += `- **类型**: ${m.type}\n`;
    md += `- **重要性**: ${(m.importance * 100).toFixed(0)}%\n`;
    md += `- **时间**: ${m.timestamp}\n`;
    if (m.entities?.length > 0) {
      md += `- **实体**: ${m.entities.slice(0, 5).join(', ')}\n`;
    }
    if (m.tags?.length > 0) {
      md += `- **标签**: ${m.tags.join(', ')}\n`;
    }
    md += '\n---\n\n';
  });
  
  md += `## 概念网络\n\n`;
  
  data.concepts.slice(0, 20).forEach((c, i) => {
    md += `${i + 1}. **${c.name}** (访问: ${c.access_count || 0})\n`;
  });
  
  md += `\n## 关联网络\n\n`;
  
  data.associations.slice(0, 20).forEach((a, i) => {
    md += `${i + 1}. ${a.from_name} --${(a.weight * 100).toFixed(0)}%--> ${a.to_name}\n`;
  });
  
  return md;
}

/**
 * 生成 CSV 格式
 */
function generateCSV(data) {
  let csv = 'id,type,summary,importance,timestamp,entities,tags\n';
  
  data.memories.forEach(m => {
    csv += [
      m.id,
      m.type,
      `"${(m.summary || m.content || '').replace(/"/g, '""')}"`,
      m.importance,
      m.timestamp,
      `"${(m.entities || []).join(';')}"`,
      `"${(m.tags || []).join(';')}"`
    ].join(',') + '\n';
  });
  
  return csv;
}

/**
 * 导出用户画像
 */
async function exportUserProfile() {
  const userModelPath = path.join(SKILL_DIR, '.user-model.json');
  
  if (!fs.existsSync(userModelPath)) {
    console.log('❌ 用户画像不存在');
    return;
  }
  
  const userModel = JSON.parse(fs.readFileSync(userModelPath, 'utf8'));
  
  let md = `# 用户画像

导出时间: ${new Date().toISOString()}

## 基本信息

- 总交互: ${userModel.stats?.totalInteractions || 0}
- 最后交互: ${userModel.stats?.lastInteraction ? new Date(userModel.stats.lastInteraction).toLocaleString() : '无'}

## 兴趣话题

`;

  const topics = userModel.preferences?.topics || {};
  const sortedTopics = Object.entries(topics)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10);
  
  sortedTopics.forEach(([topic, score]) => {
    md += `- ${topic}: ${(score * 100).toFixed(0)}%\n`;
  });
  
  md += `\n## 情绪模式\n\n`;
  
  const emotions = userModel.emotionPatterns?.dominantEmotions || {};
  Object.entries(emotions)
    .sort((a, b) => b[1] - a[1])
    .forEach(([emotion, count]) => {
      md += `- ${emotion}: ${count} 次\n`;
    });
  
  const outputPath = path.join(SKILL_DIR, `user_profile_${Date.now()}.md`);
  fs.writeFileSync(outputPath, md);
  
  console.log(`✅ 用户画像已导出: ${outputPath}`);
  return outputPath;
}

// 命令行接口
if (require.main === module) {
  const args = process.argv.slice(2);
  const format = args[0] || 'json';
  const output = args[1] || null;
  
  if (args[0] === '--profile') {
    exportUserProfile();
  } else {
    exportAll(format, output);
  }
}

module.exports = { exportAll, exportUserProfile };
