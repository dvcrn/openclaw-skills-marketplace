#!/usr/bin/env node

/**
 * 小红书自动化工具
 * 使用 Playwright 进行浏览器操作
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

// 配置
const CONFIG = {
  baseURL: 'https://www.xiaohongshu.com',
  sessionPath: process.env.XHS_SESSION_PATH || path.join(process.env.HOME, '.openclaw', 'xiaohongshu', 'session.json'),
  headless: process.env.XHS_BROWSER_HEADLESS === 'true',
  slowMo: 100, // 操作间隔（毫秒），降低风控风险
};

// 确保会话目录存在
const sessionDir = path.dirname(CONFIG.sessionPath);
if (!fs.existsSync(sessionDir)) {
  fs.mkdirSync(sessionDir, { recursive: true });
}

class XiaohongshuBot {
  constructor() {
    this.browser = null;
    this.page = null;
    this.context = null;
  }

  async init() {
    this.browser = await chromium.launch({
      headless: CONFIG.headless,
      slowMo: CONFIG.slowMo,
    });
    
    // 加载会话
    const userDataDir = path.join(sessionDir, 'user-data');
    this.context = await this.browser.newContext({
      storageState: this.loadSession(),
      viewport: { width: 1280, height: 800 },
    });
    
    this.page = await this.context.newPage();
    await this.page.goto(CONFIG.baseURL);
  }

  loadSession() {
    if (fs.existsSync(CONFIG.sessionPath)) {
      try {
        return JSON.parse(fs.readFileSync(CONFIG.sessionPath, 'utf-8'));
      } catch (e) {
        console.log('会话文件损坏，将重新登录');
      }
    }
    return null;
  }

  saveSession() {
    const storage = this.context.storageState();
    fs.writeFileSync(CONFIG.sessionPath, JSON.stringify(storage, null, 2));
    console.log('会话已保存');
  }

  async checkLogin() {
    await this.page.goto(CONFIG.baseURL);
    await this.page.waitForTimeout(2000);
    
    // 检查是否登录（查找用户头像）
    const userAvatar = await this.page.$('.user-avatar');
    return !!userAvatar;
  }

  async login() {
    console.log('请在打开的浏览器中完成登录...');
    await this.page.goto(CONFIG.baseURL + '/login');
    
    // 等待用户手动登录
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    });

    return new Promise((resolve) => {
      rl.question('登录完成后按回车继续...', async () => {
        rl.close();
        this.saveSession();
        const isLoggedIn = await this.checkLogin();
        resolve(isLoggedIn);
      });
    });
  }

  async publishNote({ title, content, images, tags }) {
    console.log('开始发布笔记...');
    
    // 进入发布页面
    await this.page.goto(CONFIG.baseURL + '/create');
    await this.page.waitForTimeout(2000);

    // 上传图片
    if (images && images.length > 0) {
      const fileInput = await this.page.$('input[type="file"]');
      if (fileInput) {
        await fileInput.setInputFiles(images);
        await this.page.waitForTimeout(3000); // 等待上传完成
      }
    }

    // 填写标题
    const titleInput = await this.page.$('input[placeholder*="标题"]');
    if (titleInput) {
      await titleInput.fill(title);
    }

    // 填写内容
    const contentInput = await this.page.$('textarea[placeholder*="正文"]');
    if (contentInput) {
      await contentInput.fill(content);
    }

    // 添加标签
    if (tags && tags.length > 0) {
      const tagInput = await this.page.$('input[placeholder*="标签"]');
      if (tagInput) {
        for (const tag of tags) {
          await tagInput.fill('#' + tag);
          await this.page.keyboard.press('Enter');
          await this.page.waitForTimeout(500);
        }
      }
    }

    // 发布
    const publishBtn = await this.page.$('button:has-text("发布")');
    if (publishBtn) {
      await publishBtn.click();
      await this.page.waitForTimeout(3000);
      console.log('笔记发布成功！');
      return true;
    }

    console.log('发布失败，未找到发布按钮');
    return false;
  }

  async getStats(noteId) {
    console.log('获取笔记数据...');
    
    const url = noteId 
      ? `${CONFIG.baseURL}/explore/${noteId}`
      : `${CONFIG.baseURL}/me`;
    
    await this.page.goto(url);
    await this.page.waitForTimeout(2000);

    // 获取点赞、收藏、评论数
    const stats = await this.page.evaluate(() => {
      const likeEl = document.querySelector('.like-count');
      const collectEl = document.querySelector('.collect-count');
      const commentEl = document.querySelector('.comment-count');
      
      return {
        likes: likeEl ? parseInt(likeEl.textContent) : 0,
        collects: collectEl ? parseInt(collectEl.textContent) : 0,
        comments: commentEl ? parseInt(commentEl.textContent) : 0,
      };
    });

    console.log('数据统计:', stats);
    return stats;
  }

  async getComments(noteId) {
    console.log('获取评论列表...');
    
    await this.page.goto(`${CONFIG.baseURL}/explore/${noteId}`);
    await this.page.waitForTimeout(2000);

    const comments = await this.page.evaluate(() => {
      const commentEls = document.querySelectorAll('.comment-item');
      return Array.from(commentEls).map(el => ({
        id: el.dataset.id,
        user: el.querySelector('.user-name')?.textContent,
        content: el.querySelector('.comment-content')?.textContent,
        time: el.querySelector('.comment-time')?.textContent,
      }));
    });

    console.log(`找到 ${comments.length} 条评论`);
    return comments;
  }

  async replyComment(commentId, text) {
    console.log('回复评论...');
    
    const commentEl = await this.page.$(`[data-comment-id="${commentId}"]`);
    if (commentEl) {
      const replyBtn = await commentEl.$('.reply-btn');
      if (replyBtn) {
        await replyBtn.click();
        await this.page.waitForTimeout(500);
        
        const input = await this.page.$('textarea[placeholder*="回复"]');
        if (input) {
          await input.fill(text);
          await this.page.keyboard.press('Enter');
          console.log('回复成功！');
          return true;
        }
      }
    }
    
    console.log('回复失败');
    return false;
  }

  async scrapeNote(noteUrl) {
    console.log('爬取笔记内容...');
    
    await this.page.goto(noteUrl);
    await this.page.waitForTimeout(2000);

    const noteData = await this.page.evaluate(() => {
      return {
        title: document.querySelector('h1')?.textContent,
        content: document.querySelector('.note-content')?.textContent,
        images: Array.from(document.querySelectorAll('.note-image')).map(img => img.src),
        author: document.querySelector('.author-name')?.textContent,
        likes: document.querySelector('.like-count')?.textContent,
        collects: document.querySelector('.collect-count')?.textContent,
        comments: document.querySelector('.comment-count')?.textContent,
        time: document.querySelector('.publish-time')?.textContent,
      };
    });

    console.log('笔记数据:', JSON.stringify(noteData, null, 2));
    return noteData;
  }

  async scrapeTopic(topic, limit = 10) {
    console.log(`爬取话题 "${topic}" 的笔记...`);
    
    await this.page.goto(`${CONFIG.baseURL}/search?keyword=${encodeURIComponent(topic)}`);
    await this.page.waitForTimeout(3000);

    const notes = await this.page.evaluate((limit) => {
      const noteEls = document.querySelectorAll('.note-item');
      return Array.from(noteEls).slice(0, limit).map(el => ({
        id: el.dataset.id,
        title: el.querySelector('.note-title')?.textContent,
        author: el.querySelector('.author-name')?.textContent,
        likes: el.querySelector('.like-count')?.textContent,
        url: el.querySelector('a')?.href,
      }));
    }, limit);

    console.log(`找到 ${notes.length} 篇笔记`);
    return notes;
  }

  async logout() {
    console.log('退出登录...');
    
    // 清除会话文件
    if (fs.existsSync(CONFIG.sessionPath)) {
      fs.unlinkSync(CONFIG.sessionPath);
    }
    
    // 清除浏览器数据
    const userDataDir = path.join(sessionDir, 'user-data');
    if (fs.existsSync(userDataDir)) {
      fs.rmSync(userDataDir, { recursive: true, force: true });
    }
    
    console.log('已退出登录');
  }

  async close() {
    if (this.browser) {
      await this.browser.close();
    }
  }
}

// CLI 命令处理
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  const bot = new XiaohongshuBot();
  
  try {
    await bot.init();
    
    switch (command) {
      case 'login':
        if (args.includes('--check')) {
          const isLoggedIn = await bot.checkLogin();
          console.log(isLoggedIn ? '已登录' : '未登录');
        } else if (args.includes('--logout')) {
          await bot.logout();
        } else {
          await bot.login();
        }
        break;
        
      case 'publish': {
        const title = args.find((_, i) => args[i-1] === '--title');
        const content = args.find((_, i) => args[i-1] === '--content');
        const imagesStr = args.find((_, i) => args[i-1] === '--images');
        const tagsStr = args.find((_, i) => args[i-1] === '--tags');
        
        const images = imagesStr ? imagesStr.split(',') : [];
        const tags = tagsStr ? tagsStr.split(',') : [];
        
        await bot.publishNote({ title, content, images, tags });
        break;
      }
        
      case 'stats':
        const noteId = args.find((_, i) => args[i-1] === '--note-id');
        await bot.getStats(noteId);
        break;
        
      case 'comments':
        if (args.includes('--list')) {
          const noteId = args.find((_, i) => args[i-1] === '--note-id');
          await bot.getComments(noteId);
        } else if (args.includes('--reply')) {
          const commentId = args.find((_, i) => args[i-1] === '--comment-id');
          const text = args.find((_, i) => args[i-1] === '--text');
          await bot.replyComment(commentId, text);
        }
        break;
        
      case 'scrape':
        if (args.includes('--note')) {
          const url = args.find((_, i) => args[i-1] === '--note');
          await bot.scrapeNote(url);
        } else if (args.includes('--topic')) {
          const topic = args.find((_, i) => args[i-1] === '--topic');
          const limit = parseInt(args.find((_, i) => args[i-1] === '--limit') || '10');
          await bot.scrapeTopic(topic, limit);
        }
        break;
        
      default:
        console.log('用法：xhs <command> [options]');
        console.log('命令：login, publish, stats, comments, scrape');
    }
  } catch (error) {
    console.error('错误:', error.message);
  } finally {
    await bot.close();
  }
}

// 导出给 Skill 调用
if (require.main === module) {
  main();
}

module.exports = { XiaohongshuBot };
