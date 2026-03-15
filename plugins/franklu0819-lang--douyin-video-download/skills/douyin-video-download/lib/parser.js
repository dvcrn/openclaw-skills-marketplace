/**
 * 抖音链接解析模块
 * 使用 Playwright 绕过反爬，获取视频下载链接
 */

const { chromium } = require('playwright-chromium');
const { URL } = require('url');

/**
 * 解析短链接
 */
async function resolveShortUrl(shortUrl) {
  console.log(`  🔍 解析短链接: ${shortUrl}`);
  
  let browser;
  try {
    browser = await chromium.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
  } catch (error) {
    if (error.message.includes('executable doesn\'t exist')) {
      throw new Error('Playwright 浏览器未安装。请运行: npx playwright install chromium');
    }
    throw error;
  }
  
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'
  });
  
  const page = await context.newPage();
  
  try {
    await page.goto(shortUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
    
    const finalUrl = page.url();
    console.log(`  ✓ 解析完成: ${finalUrl}`);
    
    await browser.close();
    return finalUrl;
  } catch (error) {
    await browser.close();
    throw error;
  }
}

/**
 * 从完整 URL 中提取视频 ID
 */
function extractVideoId(url) {
  // 匹配 /video/123456 格式
  const match = url.match(/\/video\/(\d+)/);
  if (match) return match[1];
  
  // 匹配其他格式
  const paths = url.split('/');
  for (const path of paths) {
    if (/^\d{10,}$/.test(path)) {
      return path;
    }
  }
  
  // 如果没有找到，使用时间戳
  return Date.now().toString();
}

/**
 * 解析视频信息（播放器页面数据提取）
 */
async function fetchVideoInfo(url) {
  console.log(`  🌐 启动浏览器获取视频信息...`);
  
  let browser;
  try {
    browser = await chromium.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
  } catch (error) {
    if (error.message.includes('executable doesn\'t exist')) {
      return {
        success: false,
        error: 'Playwright 浏览器未安装。请运行: npx playwright install chromium'
      };
    }
    return {
      success: false,
      error: error.message
    };
  }
  
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  
  const page = await context.newPage();
  
  try {
    // 尝试拦截网络请求
    let interceptedUrl = null;
    
    page.on('response', async (response) => {
      const resUrl = response.url();
      // 检测视频文件
      if (resUrl.includes('.mp4') || resUrl.includes('video')) {
        interceptedUrl = resUrl;
      }
    });
    
    await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(3000);
    
    // 获取页面源码并尝试用正则提取 video_id (针对新版抖音页面)
    const content = await page.content();
    let videoId = null;
    
    // 方案 1: 从内容中正则表达式提取 video_id (playAddr 或 vid)
    const vidMatch = content.match(/video_id=([a-z0-9A-Z_]+)/i) || 
                     content.match(/\"vid\":\"([a-z0-9A-Z_]+)\"/i) ||
                     content.match(/vid=([a-z0-9A-Z_]+)/i);
    if (vidMatch) {
      videoId = vidMatch[1].replace(/\"/g, '');
    }
    
    // 方案 2: 如果正则没拿到，尝试从 URL 路径提取 (如果是完整视频页)
    if (!videoId) {
      const urlMatch = url.match(/\/video\/(\d+)/);
      if (urlMatch) videoId = urlMatch[1];
    }

    // 构建高清下载链接 (aweme/v1/play 接口通常不需要很复杂的签名即可获取 720p/1080p)
    let finalDownloadUrl = interceptedUrl;
    if (videoId) {
      finalDownloadUrl = `https://aweme.snssdk.com/aweme/v1/play/?video_id=${videoId}&ratio=1080p&line=0`;
    }
    
    // 提取页面信息
    const videoInfo = await page.evaluate(() => {
      return {
        title: document.title,
        description: document.querySelector('meta[name="description"]')?.content
      };
    });
    
    await browser.close();
    
    return {
      success: true,
      downloadUrl: finalDownloadUrl,
      videoId,
      info: videoInfo
    };
  } catch (error) {
    await browser.close();
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * 主解析函数
 */
async function parseDouyinUrl(inputUrl) {
  try {
    // 如果是短链接，先解析
    let targetUrl = inputUrl;
    if (inputUrl.includes('v.douyin.com')) {
      targetUrl = await resolveShortUrl(inputUrl);
    }
    
    // 提取视频 ID
    const videoId = extractVideoId(targetUrl);
    
    // 获取视频信息
    const result = await fetchVideoInfo(targetUrl);
    
    // 提取并重写目标 URL 以抓取 1080P
    if (result.downloadUrl) {
      result.downloadUrl = result.downloadUrl.replace('playwm', 'play');
    }

    return {
      videoId,
      originalUrl: inputUrl,
      targetUrl,
      ...result
    };
  } catch (error) {
    throw new Error(`解析失败: ${error.message}`);
  }
}

module.exports = {
  parseDouyinUrl,
  resolveShortUrl,
  extractVideoId,
  fetchVideoInfo
};
