/**
 * 视频下载模块 (v2.0 - 独立版)
 * 支持多种下载方式：yt-dlp、Playwright、直接下载
 */

const https = require('https');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const { promisify } = require('util');

const execAsync = promisify(exec);

const USER_AGENTS = [
  'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
  'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
];

/**
 * 获取随机 User-Agent
 */
function getRandomUserAgent() {
  return USER_AGENTS[Math.floor(Math.random() * USER_AGENTS.length)];
}

/**
 * 确保目录存在
 */
function ensureDir(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

/**
 * 检查 yt-dlp 是否安装
 */
async function checkYtDlp() {
  try {
    await execAsync('yt-dlp --version', { timeout: 5000 });
    return true;
  } catch (error) {
    return false;
  }
}

/**
 * 使用 yt-dlp 下载视频
 */
async function downloadWithYtDlp(videoUrl, outputDir, videoId, options = {}) {
  ensureDir(outputDir);
  const outputPath = path.join(outputDir, options.filename || `${videoId}.mp4`);
  
  // 如果文件已存在且足够大，直接返回
  if (fs.existsSync(outputPath)) {
    const stats = fs.statSync(outputPath);
    if (stats.size > 1000) { // 大于 1KB 认为是有效文件
      console.log(`  📁 视频已存在: ${outputPath}`);
      return { success: true, filePath: outputPath, size: stats.size };
    }
  }
  
  try {
    console.log(`  🔄 使用 yt-dlp 下载视频...`);
    
    // 构建 yt-dlp 命令
    let command = `yt-dlp -o "${outputPath}" --no-warnings --newline`;
    
    // 添加代理（如果配置）
    if (options.proxy) {
      command += ` --proxy ${options.proxy}`;
    }
    
    // 添加 cookies（如果配置）
    if (options.cookies) {
      command += ` --cookies ${options.cookies}`;
    }
    
    command += ` "${videoUrl}"`;
    
    const { stdout } = await execAsync(command, { 
      timeout: options.timeout || 120000,
      maxBuffer: 1024 * 1024 * 10 // 10MB buffer
    });
    
    if (fs.existsSync(outputPath)) {
      const stats = fs.statSync(outputPath);
      console.log(`  ✅ 下载完成: ${formatBytes(stats.size)}`);
      return { success: true, filePath: outputPath, size: stats.size };
    } else {
      return { success: false, error: '文件未生成' };
    }
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * 直接下载（备用方案）
 */
async function downloadDirect(videoUrl, outputDir, videoId) {
  ensureDir(outputDir);
  
  const fileName = `${videoId}.mp4`;
  const filePath = path.join(outputDir, fileName);
  
  // 如果文件已存在，直接返回
  if (fs.existsSync(filePath)) {
    const stats = fs.statSync(filePath);
    if (stats.size > 1000) {
      console.log(`  📁 视频已存在: ${filePath}`);
      return { success: true, filePath, size: stats.size };
    }
  }
  
  return new Promise((resolve, reject) => {
    const options = {
      headers: {
        'User-Agent': getRandomUserAgent(),
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://www.douyin.com/',
        'Connection': 'keep-alive'
      },
      timeout: 60000
    };
    
    const req = https.get(videoUrl, options, (res) => {
      // 处理重定向
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        console.log(`  🔄 跟随重定向...`);
        downloadDirect(res.headers.location, outputDir, videoId)
          .then(resolve)
          .catch(reject);
        return;
      }
      
      if (res.statusCode !== 200) {
        reject(new Error(`下载失败: HTTP ${res.statusCode}`));
        return;
      }
      
      const fileStream = fs.createWriteStream(filePath);
      let downloadedBytes = 0;
      let totalBytes = parseInt(res.headers['content-length'], 10) || 0;
      
      res.on('data', (chunk) => {
        downloadedBytes += chunk.length;
        if (totalBytes > 0) {
          const percent = Math.round((downloadedBytes / totalBytes) * 100);
          process.stdout.write(`  ⬇️  下载进度: ${percent}% (${formatBytes(downloadedBytes)})\r`);
        }
      });
      
      res.pipe(fileStream);
      
      fileStream.on('finish', () => {
        fileStream.close();
        console.log(`\n  ✅ 下载完成: ${filePath}`);
        resolve({ success: true, filePath, size: downloadedBytes });
      });
      
      fileStream.on('error', (err) => {
        fs.unlink(filePath, () => {});
        reject(new Error(`文件写入失败: ${err.message}`));
      });
    });
    
    req.on('error', (err) => {
      reject(new Error(`请求失败: ${err.message}`));
    });
    
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('下载超时'));
    });
  });
}

/**
 * 主下载函数
 */
async function downloadVideo(videoUrl, outputDir, videoId, options = {}) {
  // 优先使用 yt-dlp
  const hasYtDlp = await checkYtDlp();
  if (hasYtDlp) {
    const result = await downloadWithYtDlp(videoUrl, outputDir, videoId, options);
    if (result.success) {
      return result;
    }
    console.log(`  ⚠️ yt-dlp 下载失败，尝试直接下载...`);
  } else {
    console.log(`  ⚠️ 未安装 yt-dlp，使用直接下载（推荐安装 yt-dlp）`);
  }
  
  // 降级到直接下载
  return downloadDirect(videoUrl, outputDir, videoId);
}

/**
 * 格式化字节大小
 */
function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

module.exports = {
  downloadVideo,
  downloadWithYtDlp,
  downloadDirect,
  checkYtDlp,
  formatBytes,
  ensureDir
};
