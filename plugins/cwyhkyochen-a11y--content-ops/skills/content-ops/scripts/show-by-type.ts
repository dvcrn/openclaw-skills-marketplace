import { db } from '../src/db/index.js';
import { crawlResults } from '../src/db/schema.js';
import { eq, desc } from 'drizzle-orm';

const results = await db.select()
  .from(crawlResults)
  .where(eq(crawlResults.taskId, '9252b605-f115-464c-a2bc-3014e84a6016'))
  .orderBy(desc(crawlResults.qualityScore));

console.log('📋 小红书 AI 内容 - 按类型分类\n');
console.log('='.repeat(70));

// 按类型分组
const videos = results.filter(r => r.contentType === 'video');
const images = results.filter(r => r.contentType === 'normal' || r.contentType === 'image');
const others = results.filter(r => !['video', 'normal', 'image'].includes(r.contentType || ''));

console.log(`\n🎬 视频内容 (${videos.length} 条):`);
console.log('-'.repeat(70));
for (let i = 0; i < videos.length; i++) {
  const r = videos[i];
  const meta = r.metadata || {};
  console.log(`${String(i + 1).padStart(2, '0')}. ${r.title || '无标题'}`);
  console.log(`     作者: ${r.authorName} | 👍${meta.likedCount || 0} 💾${meta.collectedCount || 0}`);
}

console.log(`\n📷 图文内容 (${images.length} 条):`);
console.log('-'.repeat(70));
for (let i = 0; i < images.length; i++) {
  const r = images[i];
  const meta = r.metadata || {};
  console.log(`${String(i + 1).padStart(2, '0')}. ${r.title || '无标题'}`);
  console.log(`     作者: ${r.authorName} | 👍${meta.likedCount || 0} 💾${meta.collectedCount || 0}`);
}

if (others.length > 0) {
  console.log(`\n❓ 其他 (${others.length} 条):`);
  console.log('-'.repeat(70));
  for (let i = 0; i < others.length; i++) {
    const r = others[i];
    console.log(`${String(i + 1).padStart(2, '0')}. ${r.title || '无标题'} (类型: ${r.contentType})`);
  }
}

console.log('\n' + '='.repeat(70));
console.log(`\n📊 总计: ${results.length} 条内容`);
console.log(`   🎬 视频: ${videos.length} 条 (${Math.round(videos.length/results.length*100)}%)`);
console.log(`   📷 图文: ${images.length} 条 (${Math.round(images.length/results.length*100)}%)`);
console.log(`\n💡 redesign 建议:`);
console.log(`   - 视频内容: 提取标题+观点，AI 重新组织文案`);
console.log(`   - 图文内容: 可参考文字结构+配图思路`);
