import { db } from '../src/db/index.js';
import { crawlResults } from '../src/db/schema.js';
import { eq } from 'drizzle-orm';

const allResults = await db.select()
  .from(crawlResults)
  .where(eq(crawlResults.taskId, '9252b605-f115-464c-a2bc-3014e84a6016'));

console.log('📋 已存储的内容数据:\n');
for (const r of allResults) {
  console.log('标题:', r.title || '无标题');
  console.log('正文(content字段):', r.content || '(空)');
  console.log('作者:', r.authorName);
  console.log('来源URL:', r.sourceUrl);
  console.log('metadata点赞数:', r.metadata?.likedCount);
  console.log('---');
}

console.log(`\n⚠️ 共 ${allResults.length} 条记录`);
console.log(`当前存储: 标题、作者、链接、互动数据（点赞/收藏/评论数）`);
console.log(`缺失: 正文内容（需要调用详情接口获取）`);
