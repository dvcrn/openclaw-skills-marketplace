#!/usr/bin/env node
/**
 * Cognitive Brain - 批量编码
 * 支持从文件批量导入记忆
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const SKILL_DIR = path.dirname(__dirname);

async function batchEncode(source, options = {}) {
  console.log('📦 批量编码记忆...\n');
  
  let memories = [];
  
  // 支持多种输入格式
  if (fs.existsSync(source)) {
    const content = fs.readFileSync(source, 'utf8');
    
    // JSON 数组
    if (source.endsWith('.json')) {
      memories = JSON.parse(content);
    }
    // JSONL 格式
    else if (source.endsWith('.jsonl')) {
      memories = content.split('\n')
        .filter(line => line.trim())
        .map(line => JSON.parse(line));
    }
    // Markdown 格式
    else if (source.endsWith('.md')) {
      memories = parseMarkdown(content);
    }
    // 纯文本（每行一条）
    else {
      memories = content.split('\n')
        .filter(line => line.trim())
        .map(line => ({ content: line.trim() }));
    }
  } else {
    // 尝试作为 JSON 字符串解析
    try {
      memories = JSON.parse(source);
    } catch (e) {
      console.error('❌ 无法解析输入');
      process.exit(1);
    }
  }
  
  console.log(`📊 准备编码 ${memories.length} 条记忆\n`);
  
  let success = 0;
  let failed = 0;
  
  for (const memory of memories) {
    try {
      const content = memory.content || memory.text || memory.summary;
      const metadata = {
        type: memory.type || 'observation',
        importance: memory.importance || 0.5,
        tags: memory.tags || [],
        summary: memory.summary
      };
      
      // 调用 encode.cjs
      const result = execSync(
        `node "${path.join(SKILL_DIR, 'scripts/encode.cjs')}" --content "${content.replace(/"/g, '\\"')}" --metadata '${JSON.stringify(metadata)}'`,
        { encoding: 'utf8', cwd: SKILL_DIR }
      );
      
      if (result.includes('✅')) {
        success++;
        process.stdout.write('.');
      } else {
        failed++;
        process.stdout.write('x');
      }
      
      // 每50条换行
      if ((success + failed) % 50 === 0) {
        console.log(` ${success}/${memories.length}`);
      }
      
    } catch (e) {
      failed++;
      process.stdout.write('x');
    }
  }
  
  console.log(`\n\n✅ 完成: ${success} 成功, ${failed} 失败`);
  
  return { success, failed, total: memories.length };
}

/**
 * 解析 Markdown 格式
 */
function parseMarkdown(content) {
  const memories = [];
  const lines = content.split('\n');
  
  let currentMemory = null;
  
  for (const line of lines) {
    // 标题作为新记忆
    if (line.startsWith('## ')) {
      if (currentMemory) {
        memories.push(currentMemory);
      }
      currentMemory = {
        content: line.replace('## ', '').trim(),
        type: 'observation',
        importance: 0.7
      };
    }
    // 列表项作为记忆
    else if (line.startsWith('- ') || line.startsWith('* ')) {
      memories.push({
        content: line.replace(/^[-*] /, '').trim(),
        type: 'fact',
        importance: 0.6
      });
    }
    // 正文追加到当前记忆
    else if (currentMemory && line.trim()) {
      currentMemory.content += '\n' + line.trim();
    }
  }
  
  if (currentMemory) {
    memories.push(currentMemory);
  }
  
  return memories;
}

/**
 * 从 MEMORY.md 导入
 */
async function importFromMemoryMd() {
  const memoryPath = path.join(process.env.HOME || '/root', '.openclaw/workspace/MEMORY.md');
  
  if (!fs.existsSync(memoryPath)) {
    console.log('❌ MEMORY.md 不存在');
    return;
  }
  
  console.log('📄 从 MEMORY.md 导入...\n');
  await batchEncode(memoryPath);
}

// 命令行接口
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log(`
批量编码工具

用法:
  node batch_encode.cjs <文件路径>     # 从文件导入
  node batch_encode.cjs --memory      # 从 MEMORY.md 导入
  node batch_encode.cjs --demo        # 生成演示数据

支持格式:
  .json   - JSON 数组
  .jsonl  - JSONL 格式
  .md     - Markdown 格式
  .txt    - 纯文本（每行一条）
`);
    process.exit(0);
  }
  
  if (args[0] === '--memory') {
    importFromMemoryMd();
  } else if (args[0] === '--demo') {
    // 生成演示数据
    const demo = [
      { content: '用户喜欢使用 Python 编程', type: 'preference', importance: 0.8 },
      { content: '用户的工作时区是 Asia/Shanghai', type: 'fact', importance: 0.7 },
      { content: '用户对 AI 和记忆系统很感兴趣', type: 'interest', importance: 0.9 },
      { content: '用户经常在下午 4 点左右活跃', type: 'pattern', importance: 0.6 },
      { content: '用户喜欢简洁的技术文档', type: 'preference', importance: 0.7 }
    ];
    batchEncode(JSON.stringify(demo));
  } else {
    batchEncode(args[0]);
  }
}

module.exports = { batchEncode, importFromMemoryMd };
