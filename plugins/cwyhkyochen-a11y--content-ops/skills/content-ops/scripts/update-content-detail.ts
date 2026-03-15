import { db } from '../src/db/index.js';
import { crawlResults } from '../src/db/schema.js';
import { eq } from 'drizzle-orm';
import fs from 'fs';

// 读取带详情的抓取结果
const detailedData = JSON.parse(fs.readFileSync('/tmp/xhs_ai_detailed.json', 'utf8'));

console.log('📝 更新数据库中的内容正文...\n');

let updatedCount = 0;
for (const note of detailedData.notes) {
  // 通过 sourceId 查找对应记录
  const records = await db.select()
    .from(crawlResults)
    .where(eq(crawlResults.sourceId, note.id));
  
  if (records.length > 0) {
    const record = records[0];
    
    // 构建正文内容
    let fullContent = '';
    if (note.description) {
      fullContent = note.description;
    } else {
      // 如果没有正文，使用组合信息
      fullContent = `标题: ${note.title || note.full_title || '无标题'}\n`;
      fullContent += `作者: ${note.user}\n`;
      fullContent += `点赞: ${note.liked_count} | 收藏: ${note.collected_count} | 评论: ${note.comment_count}`;
    }
    
    // 更新记录
    await db.update(crawlResults)
      .set({
        content: fullContent,
        title: note.full_title || note.title || record.title,
        mediaUrls: note.images || [],
        metadata: {
          ...record.metadata,
          tags: note.tags || [],
          fetchDetailSuccess: note.fetch_success,
          hasFullDescription: !!note.description
        }
      })
      .where(eq(crawlResults.id, record.id));
    
    updatedCount++;
    console.log(`✅ 已更新: ${(note.full_title || note.title || '无标题').slice(0, 40)}...`);
  }
}

console.log(`\n📊 更新完成: ${updatedCount}/${detailedData.notes.length} 条记录`);
console.log('\n⚠️ 小红书网页端对详情页有访问限制');
console.log('   建议基于标题 + 互动数据 + AI 生成发布内容');
