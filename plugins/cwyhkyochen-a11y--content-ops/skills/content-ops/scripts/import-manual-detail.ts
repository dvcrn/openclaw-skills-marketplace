import { db } from '../src/db/index.js';
import { crawlResults } from '../src/db/schema.js';
import { eq } from 'drizzle-orm';
import fs from 'fs';
import path from 'path';
import { randomUUID } from 'crypto';

/**
 * 导入用户提供的详情内容
 * 
 * 使用方式:
 * npx tsx scripts/import-manual-detail.ts --input /tmp/manual_details.txt
 * 
 * 文件格式:
 * 详情 1
 * [正文内容]
 * ---
 * 详情 2
 * [正文内容]
 * ---
 */

interface ManualDetail {
  index: number;
  content: string;
}

function parseManualInput(inputPath: string): ManualDetail[] {
  const content = fs.readFileSync(inputPath, 'utf8');
  const lines = content.split('\n');
  
  const details: ManualDetail[] = [];
  let currentIndex: number | null = null;
  let currentContent: string[] = [];
  
  for (const line of lines) {
    const trimmed = line.trim();
    
    // 检测新条目标记: "详情 1" 或 "详情 2"
    const match = trimmed.match(/^详情\s*(\d+)$/);
    if (match) {
      // 保存之前的
      if (currentIndex !== null && currentContent.length > 0) {
        details.push({
          index: currentIndex,
          content: currentContent.join('\n').trim()
        });
      }
      currentIndex = parseInt(match[1]);
      currentContent = [];
    }
    // 检测分隔符
    else if (trimmed === '---') {
      if (currentIndex !== null && currentContent.length > 0) {
        details.push({
          index: currentIndex,
          content: currentContent.join('\n').trim()
        });
        currentIndex = null;
        currentContent = [];
      }
    }
    // 普通内容行
    else if (currentIndex !== null) {
      currentContent.push(line);
    }
  }
  
  // 处理最后一个
  if (currentIndex !== null && currentContent.length > 0) {
    details.push({
      index: currentIndex,
      content: currentContent.join('\n').trim()
    });
  }
  
  return details;
}

async function importManualDetails(inputPath: string) {
  console.log('📝 导入人工提供的详情内容\n');
  console.log('='.repeat(80));
  
  // 1. 读取待补充列表
  const pendingPath = '/tmp/pending_details.json';
  if (!fs.existsSync(pendingPath)) {
    console.log('❌ 未找到待补充列表，请先运行: npx tsx scripts/show-pending-details.ts');
    process.exit(1);
  }
  
  const pending = JSON.parse(fs.readFileSync(pendingPath, 'utf8'));
  const pendingItems = pending.items;
  
  // 2. 解析用户输入
  const details = parseManualInput(inputPath);
  
  console.log(`📥 解析到 ${details.length} 条人工详情\n`);
  
  // 3. 创建本地存储目录
  const corpusDir = path.join(
    process.env.HOME || '',
    '.openclaw/workspace/content-ops-workspace/corpus/manual'
  );
  fs.mkdirSync(corpusDir, { recursive: true });
  
  const imported = [];
  
  // 4. 导入每条详情
  for (const detail of details) {
    // 找到对应的笔记
    const pendingItem = pendingItems.find((p: any) => p.index === detail.index);
    
    if (!pendingItem) {
      console.log(`⚠️ 序号 ${detail.index} 不在待补充列表中，跳过`);
      continue;
    }
    
    console.log(`\n【${detail.index}】${pendingItem.title}`);
    console.log(`   原文长度: ${detail.content.length} 字符`);
    
    // 更新数据库
    const records = await db.select()
      .from(crawlResults)
      .where(eq(crawlResults.id, pendingItem.id));
    
    if (records.length === 0) {
      console.log(`   ❌ 数据库中未找到记录`);
      continue;
    }
    
    const record = records[0];
    
    // 更新 content 字段
    await db.update(crawlResults)
      .set({
        content: detail.content,
        metadata: {
          ...record.metadata,
          manualImported: true,
          importedAt: new Date().toISOString(),
          originalLength: detail.content.length
        }
      })
      .where(eq(crawlResults.id, record.id));
    
    // 保存到本地文件
    const filename = `manual_${record.id}_${Date.now()}.json`;
    const filepath = path.join(corpusDir, filename);
    
    fs.writeFileSync(filepath, JSON.stringify({
      noteId: record.id,
      title: record.title,
      author: record.authorName,
      sourceUrl: record.sourceUrl,
      content: detail.content,
      importedAt: new Date().toISOString()
    }, null, 2));
    
    console.log(`   ✅ 已导入数据库`);
    console.log(`   💾 已保存: ${filename}`);
    
    imported.push({
      index: detail.index,
      title: pendingItem.title,
      contentLength: detail.content.length
    });
  }
  
  // 5. 生成汇总
  console.log('\n' + '='.repeat(80));
  console.log(`✅ 导入完成: ${imported.length}/${details.length} 条成功`);
  console.log('='.repeat(80));
  
  // 保存汇总
  const summaryPath = path.join(corpusDir, `import_summary_${Date.now()}.json`);
  fs.writeFileSync(summaryPath, JSON.stringify({
    importedAt: new Date().toISOString(),
    total: imported.length,
    items: imported
  }, null, 2));
  
  console.log(`\n📁 汇总文件: ${summaryPath}`);
  console.log(`📁 语料目录: ${corpusDir}`);
  
  return imported;
}

// 主函数
async function main() {
  // 解析命令行参数
  const args = process.argv.slice(2);
  const inputIndex = args.indexOf('--input');
  
  if (inputIndex === -1 || !args[inputIndex + 1]) {
    console.log('用法: npx tsx scripts/import-manual-detail.ts --input <文件路径>');
    console.log('');
    console.log('文件格式:');
    console.log('  详情 1');
    console.log('  [正文内容]');
    console.log('  ---');
    console.log('  详情 2');
    console.log('  [正文内容]');
    console.log('  ---');
    process.exit(1);
  }
  
  const inputPath = args[inputIndex + 1];
  
  if (!fs.existsSync(inputPath)) {
    console.log(`❌ 文件不存在: ${inputPath}`);
    process.exit(1);
  }
  
  await importManualDetails(inputPath);
}

main().catch(console.error);
