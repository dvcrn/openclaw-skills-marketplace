import { db } from '../src/db/index.js';
import { crawlResults } from '../src/db/schema.js';
import { eq, desc } from 'drizzle-orm';
import fs from 'fs';

// 读取原始抓取结果（包含类型信息）
const crawlData = JSON.parse(fs.readFileSync('/tmp/xhs_ai_crawled.json', 'utf8'));

console.log('📝 更新内容类型信息...\n');

// 更新类型（从之前的搜索结果中我们知道类型）
const typeMap = {
  '69a1686e0000000015021952': 'video',     // 当吃货遇上人工智能
  '699f0139000000000e00fd1e': 'video',     // 访谈谷歌AI科学家
  '699b183a000000002800b81a': 'normal',    // 盘点一周AI大事
  '69a102bf000000000e00fb3e': 'video',     // 不买Mac Mini
  '699c5069000000000a03f6e3': 'video',     // 无标题(未来奇点)
  '699d047a000000000a02ddf3': 'normal',    // AI像一场大雪
  '2d3ab0c9-ca12-4474-8b3b-5794c38e3514': 'video', // 无标题
  '699d1b41000000001a026150': 'normal',    // 用了三年AI
  '699d6b59000000000e00e9e3': 'video',     // 如何让AI翻车
  '699becf9000000002801d09f': 'video',     // AI大刘
};

let updatedCount = 0;
for (const note of crawlData.notes) {
  const contentType = typeMap[note.id] || 'unknown';
  
  // 更新数据库
  const records = await db.select()
    .from(crawlResults)
    .where(eq(crawlResults.sourceId, note.id));
  
  if (records.length > 0) {
    await db.update(crawlResults)
      .set({
        contentType: contentType,
        metadata: {
          ...records[0].metadata,
          noteType: contentType,
          coverUrl: note.cover_url
        }
      })
      .where(eq(crawlResults.id, records[0].id));
    
    const typeEmoji = contentType === 'video' ? '🎬' : '📷';
    console.log(`${typeEmoji} ${contentType.padEnd(6)} | ${(note.title || '无标题').slice(0, 40)}`);
    updatedCount++;
  }
}

console.log(`\n✅ 已更新 ${updatedCount} 条记录的内容类型`);

// 显示统计
const results = await db.select()
  .from(crawlResults)
  .where(eq(crawlResults.taskId, '9252b605-f115-464c-a2bc-3014e84a6016'));

const videoCount = results.filter(r => r.contentType === 'video').length;
const imageCount = results.filter(r => r.contentType === 'normal').length;

console.log(`\n📊 内容类型分布:`);
console.log(`   🎬 视频: ${videoCount} 条`);
console.log(`   📷 图文: ${imageCount} 条`);
console.log(`   ❓ 未知: ${results.length - videoCount - imageCount} 条`);
