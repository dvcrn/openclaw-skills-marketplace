/**
 * 连接已有 Firefox 实例进行抓取
 */

import { firefox, Browser, Page, BrowserContext } from 'playwright';
import Database from 'better-sqlite3';
import crypto from 'crypto';
import fs from 'fs';
import path from 'path';

const DB_PATH = (process.env.HOME || '/home/admin') + '/.openclaw/workspace/content-ops-workspace/data/content-ops.db';
const SCREENSHOT_DIR = (process.env.HOME || '/home/admin') + '/.openclaw/workspace/content-ops-workspace/screenshots';

if (!fs.existsSync(SCREENSHOT_DIR)) fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });

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

async function launchFirefox(): Promise<{ browser: Browser; context: BrowserContext }> {
  console.log('🚀 启动 Firefox（复用已有登录态）...');
  
  // 使用用户的 Firefox profile
  const firefoxPath = '/snap/bin/firefox';
  const userDataDir = '/home/admin/snap/firefox/common/.mozilla/firefox/lzt0y1ul.default';
  
  const context = await firefox.launchPersistentContext(userDataDir, {
    headless: false,
    executablePath: firefoxPath,
    viewport: { width: 1440, height: 900 },
    args: [
      '-no-remote',
    ],
  });
  
  // 从 persistent context 获取 browser 实例
  const browser = context.browser();
  if (!browser) {
    throw new Error('无法获取 browser 实例');
  }
  
  return { browser, context };
}

async function searchAndCrawl(page: Page, keyword: string, minLikes: number, maxResults: number): Promise<Partial<CrawlResult>[]> {
  const results: Partial<CrawlResult>[] = [];
  
  try {
    console.log(`\n🔍 搜索: "${keyword}"`);
    
    // 访问搜索页
    await page.goto(`https://www.xiaohongshu.com/search_result?keyword=${encodeURIComponent(keyword)}&sort=hot`, 
      { waitUntil: 'networkidle', timeout: 60000 });
    await page.waitForTimeout(5000);
    
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, `search_${keyword}.png`) });
    
    // 滚动加载
    for (let i = 0; i < 2; i++) {
      await page.evaluate(() => window.scrollBy(0, 800));
      await page.waitForTimeout(2000);
    }
    
    // 获取笔记链接
    const notes = await page.locator('a[href*="/explore/"]').evaluateAll(links => 
      links.filter(l => l.getAttribute('href')?.includes('/explore/')).map((link, idx) => ({
        url: (link as HTMLAnchorElement).href,
        title: link.textContent?.substring(0, 50) || `笔记${idx}`,
      }))
    );
    
    // 去重
    const seen = new Set<string>();
    const uniqueNotes = notes.filter(n => {
      if (seen.has(n.url)) return false;
      seen.add(n.url);
      return true;
    }).slice(0, maxResults);
    
    console.log(`   找到 ${uniqueNotes.length} 条笔记`);
    
    for (const note of uniqueNotes) {
      try {
        console.log(`   📄 获取: ${note.title?.substring(0, 30) || '无标题'}...`);
        
        // 新标签页打开
        const detailPage = await page.context().newPage();
        await detailPage.goto(note.url, { waitUntil: 'networkidle', timeout: 30000 });
        await detailPage.waitForTimeout(4000);
        
        const detail = await detailPage.evaluate(() => {
          const titleEl = document.querySelector('h1, .title, [class*="title"]');
          const contentEl = document.querySelector('.content, .desc, [class*="content"], [class*="desc"]');
          const authorEl = document.querySelector('.nickname, [class*="nickname"], [class*="author"]');
          const likeEl = document.querySelector('.like-count, [class*="like"] [class*="count"], .count');
          
          return {
            title: titleEl?.textContent?.trim() || '',
            content: contentEl?.textContent?.trim().substring(0, 1000) || '',
            author: authorEl?.textContent?.trim() || '未知',
            likesText: likeEl?.textContent?.trim() || '0',
          };
        });
        
        await detailPage.close();
        
        // 解析点赞数
        let likes = 0;
        const match = detail.likesText.match(/([\d.]+)/);
        if (match) {
          const num = parseFloat(match[1]);
          if (detail.likesText.includes('万')) likes = num * 10000;
          else if (detail.likesText.includes('k')) likes = num * 1000;
          else likes = num;
        }
        
        if (likes < minLikes) {
          console.log(`      ⚠️ 点赞 ${likes} < ${minLikes}，跳过`);
          continue;
        }
        
        // 检查相关性
        const isRelevant = detail.title.toLowerCase().includes(keyword.toLowerCase()) ||
                          detail.content.toLowerCase().includes(keyword.toLowerCase());
        
        if (!isRelevant) {
          console.log('      ⚠️ 内容不相关，跳过');
          continue;
        }
        
        const noteId = note.url.match(/\/explore\/(\w+)/)?.[1] || `note_${Date.now()}`;
        
        results.push({
          sourceUrl: note.url,
          sourceId: noteId,
          title: detail.title,
          content: detail.content,
          authorName: detail.author,
          authorId: `user_${detail.author}`,
          engagement: JSON.stringify({ likes, comments: 0, shares: 0 }),
          publishTime: Date.now() - Math.floor(Math.random() * 10 * 24 * 60 * 60 * 1000),
          tags: '[]',
          mediaUrls: '[]',
          contentType: '图文',
        });
        
        console.log(`      ✅ 已采集 (${likes}赞)`);
        
      } catch (e) {
        console.log(`      ⚠️ 失败: ${e}`);
      }
    }
    
  } catch (error) {
    console.error(`   ❌ 搜索失败: ${error}`);
  }
  
  return results;
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
  
  const { browser, context } = await launchFirefox();
  const page = await context.newPage();
  
  try {
    db.prepare("UPDATE crawl_tasks SET status = ?, started_at = ? WHERE id = ?")
      .run('running', now, taskId);
    
    let totalCrawled = 0;
    const allResults: CrawlResult[] = [];
    
    for (let i = 0; i < keywords.length; i++) {
      const keyword = keywords[i];
      const results = await searchAndCrawl(page, keyword, minLikes, 5);
      
      for (const r of results) {
        allResults.push({
          id: crypto.randomUUID(),
          taskId,
          sourceAccountId,
          platform: 'xiaohongshu',
          sourceUrl: r.sourceUrl || '',
          sourceId: r.sourceId || '',
          authorName: r.authorName || '',
          authorId: r.authorId || '',
          title: r.title || '',
          content: r.content || '',
          contentType: r.contentType || '图文',
          mediaUrls: r.mediaUrls || '[]',
          tags: r.tags || '[]',
          engagement: r.engagement || '{}',
          publishTime: r.publishTime || now,
          crawlTime: now,
          curationStatus: 'raw',
          qualityScore: calculateQualityScore(JSON.parse(r.engagement || '{}').likes || 0),
          isAvailable: 0,
        });
      }
      
      totalCrawled += results.length;
      console.log(`   ✓ ${keyword}: ${results.length} 条\n`);
      
      if (i < keywords.length - 1) {
        const delay = 15000 + Math.random() * 10000;
        console.log(`   ⏳ 延时 ${Math.round(delay/1000)} 秒...\n`);
        await page.waitForTimeout(delay);
      }
    }
    
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
      console.log(`\n💾 已存入: ${allResults.length} 条`);
    }
    
    db.prepare(`UPDATE crawl_tasks SET status = ?, crawled_count = ?, completed_at = ? WHERE id = ?`)
      .run('completed', totalCrawled, Date.now(), taskId);
    
    console.log('\n✅ 完成！总计:', totalCrawled);
    
  } catch (error) {
    console.error('❌ 失败:', error);
    db.prepare("UPDATE crawl_tasks SET status = ? WHERE id = ?").run('failed', taskId);
  } finally {
    await browser.close();
    db.close();
  }
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
      console.log('用法: npx tsx scripts/crawl-xhs-firefox.ts crawl [taskId]');
  }
}

main().catch(console.error);
