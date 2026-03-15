import { db } from '../src/db/index.js';
import { crawlResults } from '../src/db/schema.js';
import { eq } from 'drizzle-orm';

const taskId = '9252b605-f115-464c-a2bc-3014e84a6016';

// 查询所有待审核的内容
const pendingResults = await db.select()
  .from(crawlResults)
  .where(eq(crawlResults.taskId, taskId));

console.log(`📋 找到 ${pendingResults.length} 条待审核内容\n`);

// 全部确认通过
let approvedCount = 0;
for (const result of pendingResults) {
  await db.update(crawlResults)
    .set({
      curationStatus: 'approved',
      curationNotes: '用户全部确认通过',
      curatedAt: new Date(),
      isAvailable: true
    })
    .where(eq(crawlResults.id, result.id));
  
  approvedCount++;
  console.log(`✅ 已通过: ${result.title?.slice(0, 40) || '无标题'}`);
}

console.log(`\n───────────────────────────────────────`);
console.log(`审核完成: ${approvedCount} 条内容已通过`);
console.log(`状态: 已进入可用语料库`);
console.log(`───────────────────────────────────────`);

// 显示审核后的统计
const approvedResults = await db.select()
  .from(crawlResults)
  .where(eq(crawlResults.taskId, taskId));

const availableCount = approvedResults.filter(r => r.isAvailable).length;
const highQuality = approvedResults.filter(r => r.qualityScore >= 8).length;

console.log(`\n📊 语料库统计:`);
console.log(`   总内容: ${approvedResults.length} 条`);
console.log(`   可用: ${availableCount} 条`);
console.log(`   高质量(8+分): ${highQuality} 条`);
