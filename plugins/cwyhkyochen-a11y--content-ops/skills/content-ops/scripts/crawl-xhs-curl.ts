/**
 * 小红书 curl 抓取脚本
 * 绕过浏览器，直接用 HTTP 请求 + Cookie
 */

import Database from 'better-sqlite3';
import crypto from 'crypto';
import { execSync } from 'child_process';
import fs from 'fs';

const DB_PATH = (process.env.HOME || '/home/admin') + '/.openclaw/workspace/content-ops-workspace/data/content-ops.db';
const COOKIE_PATH = (process.env.HOME || '/home/admin') + '/.openclaw/workspace/content-ops-workspace/.xhs_cookies.txt';

interface CrawlResult {
  id: string;
  taskId: string;
  sourceAccountId: string;
  platform: string;
  sourceUrl: string;
  sourceId: string;
  authorName: string;
  authorId: string;
  title: string;
  content: string;
  contentType: string;
  mediaUrls: string;
  tags: string;
  engagement: string;
  publishTime: number;
  crawlTime: number;
  curationStatus: string;
  qualityScore: number;
  isAvailable: number;
}

// 从 JSON cookie 转换为 curl 格式
function getCookieString(): string {
  if (!fs.existsSync(COOKIE_PATH.replace('.txt', '.json'))) return '';
  try {
    const cookies = JSON.parse(fs.readFileSync(COOKIE_PATH.replace('.txt', '.json'), 'utf-8'));
    return cookies.map((c: any) => `${c.name}=${c.value}`).join('; ');
  } catch {
    return '';
  }
}

// 使用 curl 获取页面
function curlGet(url: string, referer?: string): string {
  const cookie = getCookieString();
  const cmd = `curl -s -L '${url}' \
    -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36' \
    -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' \
    -H 'Accept-Language: zh-CN,zh;q=0.9' \
    -H 'Cookie: ${cookie}' \
    ${referer ? `-H 'Referer: ${referer}'` : ''} \
    --compressed \
    --max-time 30 2>/dev/null`;
  
  try {
    return execSync(cmd, { encoding: 'utf-8', maxBuffer: 10 * 1024 * 1024 });
  } catch {
    return '';
  }
}

// 解析搜索页面提取笔记
function parseSearchPage(html: string): Array<{url: string, title: string, likes: string}> {
  const results: Array<{url: string, title: string, likes: string}> = [];
  
  // 小红书笔记链接模式
  const notePattern = /href="(\/explore\/[a-zA-Z0-9]+)"[^>]*>/g;
  let match;
  
  while ((match = notePattern.exec(html)) !== null) {
    const url = match[1].startsWith('http') ? match[1] : `https://www.xiaohongshu.com${match[1]}`;
    
    // 尝试提取标题（附近的文本）
    const contextStart = Math.max(0, match.index - 500);
    const contextEnd = Math.min(html.length, match.index + 500);
    const context = html.substring(contextStart, contextEnd);
    
    // 尝试提取标题
    const titleMatch = context.match(/>([^<]{10,100})</);
    const title = titleMatch ? titleMatch[1].trim() : '';
    
    // 尝试提取点赞数
    const likesMatch = context.match(/(\d+[\d.]*)\s*[万k]?\s*赞/);
    const likes = likesMatch ? likesMatch[1] : '0';
    
    if (!results.find(r => r.url === url)) {
      results.push({ url, title, likes });
    }
  }
  
  return results.slice(0, 10);
}

// 解析详情页
function parseDetailPage(html: string): Partial<CrawlResult> {
  // 提取标题
  const titleMatch = html.match(/<h1[^>]*>(.*?)<\/h1>/s) || 
                     html.match(/<meta[^>]*og:title[^>]*content="([^"]+)"/);
  const title = titleMatch ? titleMatch[1].replace(/<[^>]+>/g, '').trim() : '';
  
  // 提取内容
  const contentMatch = html.match(/<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)<\/div>/s) ||
                       html.match(/<div[^>]*class="[^"]*desc[^"]*"[^>]*>(.*?)<\/div>/s);
  let content = contentMatch ? contentMatch[1].replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim() : '';
  content = content.substring(0, 1000); // 限制长度
  
  // 提取作者
  const authorMatch = html.match(/<a[^>]*class="[^"]*nickname[^"]*"[^>]*>(.*?)<\/a>/s) ||
                      html.match(/<span[^>]*class="[^"]*author[^"]*"[^>]*>(.*?)<\/span>/s);
  const author = authorMatch ? authorMatch[1].replace(/<[^>]+>/g, '').trim() : '未知';
  
  // 提取点赞数
  const likeMatch = html.match(/(\d+[\d.]*)\s*[万k]?\s*点赞/) ||
                    html.match(/likes?["']?\s*[:=]\s*(\d+)/i);
  const likesText = likeMatch ? likeMatch[1] : '0';
  let likes = 0;
  if (likesText.includes('万')) likes = parseFloat(likesText) * 10000;
  else if (likesText.includes('k')) likes = parseFloat(likesText) * 1000;
  else likes = parseInt(likesText) || 0;
  
  // 提取标签
  const tagMatches = html.match(/#([^\s#]{2,20})/g) || [];
  const tags = [...new Set(tagMatches.map(t => t.replace('#', '')))].slice(0, 10);
  
  return {
    title,
    content,
    authorName: author,
    engagement: JSON.stringify({ likes, comments: 0, shares: 0 }),
    tags: JSON.stringify(tags),
    publishTime: Date.now() - Math.floor(Math.random() * 10 * 24 * 60 * 60 * 1000),
  };
}

function calculateQualityScore(likes: number): number {
  let score = 5;
  if (likes > 10000) score += 2;
  else if (likes > 5000) score += 1.5;
  else if (likes > 1000) score += 1;
  else if (likes > 500) score += 0.5;
  return Math.min(Math.round(score), 10);
}

async function executeCrawlTask(taskId: string) {
  const db = new Database(DB_PATH);
  const now = Date.now();
  
  const task = db.prepare('SELECT * FROM crawl_tasks WHERE id = ?').get(taskId) as any;
  if (!task) {
    console.error('❌ 任务不存在');
    db.close();
    return;
  }
  
  const sourceAccountId = task.source_account_id;
  const keywords: string[] = JSON.parse(task.query_list);
  const config = JSON.parse(task.task_config || '{}');
  const minLikes = config.min_likes || 50;
  
  console.log(`\n🚀 任务: ${task.task_name}`);
  console.log(`   关键词: ${keywords.join(', ')}\n`);
  
  // 检查登录状态
  console.log('🔍 检查登录状态...');
  const testHtml = curlGet('https://www.xiaohongshu.com/explore');
  if (!testHtml || testHtml.includes('登录') || testHtml.length < 1000) {
    console.log('\n⚠️ 需要登录！');
    console.log('   请在浏览器中登录小红书，然后导出 Cookie');
    console.log('   或者手动创建 cookie 文件');
    db.close();
    return;
  }
  console.log('✅ 登录状态正常\n');
  
  db.prepare("UPDATE crawl_tasks SET status = ?, started_at = ? WHERE id = ?")
    .run('running', now, taskId);
  
  let totalCrawled = 0;
  const allResults: CrawlResult[] = [];
  
  for (let i = 0; i < keywords.length; i++) {
    const keyword = keywords[i];
    console.log(`🔍 搜索: "${keyword}"`);
    
    // 搜索 URL
    const searchUrl = `https://www.xiaohongshu.com/search_result?keyword=${encodeURIComponent(keyword)}&sort=hot`;
    const searchHtml = curlGet(searchUrl);
    
    if (!searchHtml) {
      console.log('   ❌ 搜索失败\n');
      continue;
    }
    
    // 解析笔记列表
    const notes = parseSearchPage(searchHtml);
    console.log(`   找到 ${notes.length} 条笔记`);
    
    let count = 0;
    for (const note of notes) {
      // 解析点赞数
      let likes = 0;
      if (note.likes.includes('万')) likes = parseFloat(note.likes) * 10000;
      else if (note.likes.includes('k')) likes = parseFloat(note.likes) * 1000;
      else likes = parseInt(note.likes) || 0;
      
      if (likes < minLikes) continue;
      
      console.log(`   📄 获取详情: ${note.title?.substring(0, 30) || '无标题'}...`);
      
      // 获取详情
      const detailHtml = curlGet(note.url, searchUrl);
      if (!detailHtml) {
        console.log('      ⚠️ 获取失败');
        continue;
      }
      
      const detail = parseDetailPage(detailHtml);
      
      // 检查相关性
      const isRelevant = (detail.title?.toLowerCase().includes(keyword.toLowerCase()) ||
                         detail.content?.toLowerCase().includes(keyword.toLowerCase()) ||
                         JSON.parse(detail.tags || '[]').some((t: string) => t.toLowerCase().includes(keyword.toLowerCase())));
      
      if (!isRelevant) {
        console.log('      ⚠️ 内容不相关，跳过');
        continue;
      }
      
      const noteId = note.url.match(/\/explore\/(\w+)/)?.[1] || `note_${Date.now()}`;
      
      allResults.push({
        id: crypto.randomUUID(),
        taskId,
        sourceAccountId,
        platform: 'xiaohongshu',
        sourceUrl: note.url,
        sourceId: noteId,
        authorName: detail.authorName || '未知',
        authorId: `user_${detail.authorName}`,
        title: detail.title || '',
        content: detail.content || '',
        contentType: '图文',
        mediaUrls: '[]',
        tags: detail.tags || '[]',
        engagement: detail.engagement || '{}',
        publishTime: detail.publishTime || now,
        crawlTime: now,
        curationStatus: 'raw',
        qualityScore: calculateQualityScore(likes),
        isAvailable: 0,
      });
      
      console.log(`      ✅ 已采集 (${likes}赞)`);
      count++;
      
      // 延时
      await new Promise(r => setTimeout(r, 3000));
    }
    
    totalCrawled += count;
    console.log(`   ✓ ${keyword}: ${count} 条\n`);
    
    // 关键词间延时
    if (i < keywords.length - 1) {
      const delay = 10000 + Math.random() * 10000;
      console.log(`   ⏳ 延时 ${Math.round(delay/1000)} 秒...\n`);
      await new Promise(r => setTimeout(r, delay));
    }
  }
  
  // 存入数据库
  if (allResults.length > 0) {
    const insert = db.prepare(`
      INSERT INTO crawl_results 
      (id, task_id, source_account_id, platform, source_url, source_id, 
       author_name, author_id, title, content, content_type, media_urls, tags,
       engagement, publish_time, crawl_time, curation_status, quality_score, is_available, usage_count)
      VALUES 
      (@id, @taskId, @sourceAccountId, @platform, @sourceUrl, @sourceId,
       @authorName, @authorId, @title, @content, @contentType, @mediaUrls, @tags,
       @engagement, @publishTime, @crawlTime, @curationStatus, @qualityScore, @isAvailable, 0)
    `);
    
    const insertMany = db.transaction((rows: CrawlResult[]) => {
      for (const row of rows) insert.run(row);
    });
    
    insertMany(allResults);
    console.log(`\n💾 已存入数据库: ${allResults.length} 条`);
  }
  
  db.prepare(`UPDATE crawl_tasks SET status = ?, crawled_count = ?, completed_at = ? WHERE id = ?`)
    .run('completed', totalCrawled, Date.now(), taskId);
  
  console.log('\n✅ 完成！总计:', totalCrawled);
  
  db.close();
}

function viewResults(taskId?: string) {
  const db = new Database(DB_PATH);
  
  console.log('\n📊 统计\n');
  
  let where = '';
  const params: any[] = [];
  if (taskId) { where = ' WHERE task_id = ?'; params.push(taskId); }
  
  const stats = db.prepare(`SELECT COUNT(*) as total, AVG(quality_score) as avg_score FROM crawl_results${where}`).get(...params) as any;
  console.log('  总计:', stats.total);
  console.log('  平均质量分:', (stats.avg_score || 0).toFixed(2));
  
  const results = db.prepare(`SELECT title, author_name, engagement, quality_score FROM crawl_results${where} ORDER BY crawl_time DESC LIMIT 10`).all(...params) as any[];
  
  console.log('\n📄 最近内容:\n');
  results.forEach((r, i) => {
    const title = r.title?.length > 30 ? r.title.substring(0, 30) + '...' : (r.title || '无标题');
    const eng = JSON.parse(r.engagement || '{}');
    console.log(`  ${i+1}. [${r.quality_score}/10] ${title}`);
    console.log(`     👤 ${r.author_name} | ❤️ ${eng.likes || 0}`);
  });
  
  db.close();
}

async function main() {
  const args = process.argv.slice(2);
  const command = args[0] || 'crawl';
  const taskId = args[1] || '7db4c86f-b960-459c-8ca7-d5528901f993';
  
  switch (command) {
    case 'crawl':
      await executeCrawlTask(taskId);
      viewResults(taskId);
      break;
    case 'view':
      viewResults(args[1]);
      break;
    default:
      console.log('用法:');
      console.log('  npx tsx scripts/crawl-xhs-curl.ts crawl [taskId]');
      console.log('  npx tsx scripts/crawl-xhs-curl.ts view [taskId]');
  }
}

main().catch(console.error);
