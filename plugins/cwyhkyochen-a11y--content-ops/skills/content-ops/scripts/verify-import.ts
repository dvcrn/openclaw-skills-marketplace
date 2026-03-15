import { db } from '../src/db/index.js';
import { crawlResults } from '../src/db/schema.js';
import { eq, desc } from 'drizzle-orm';

const results = await db.select()
  .from(crawlResults)
  .orderBy(desc(crawlResults.qualityScore))
  .limit(5);

console.log('📋 导入后的内容数据\n');
console.log('='.repeat(80));

for (const r of results) {
  const meta = r.metadata || {};
  console.log(`\n标题: ${r.title}`);
  console.log(`正文长度: ${(r.content || '').length} 字符`);
  console.log(`人工导入: ${meta.manualImported ? '✅ 是' : '❌ 否'}`);
  if (r.content && r.content.length > 50) {
    console.log(`预览: ${r.content.slice(0, 100)}...`);
  }
  console.log('-'.repeat(80));
}
