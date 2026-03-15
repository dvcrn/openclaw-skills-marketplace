#!/usr/bin/env node

/**
 * 抓取小红书笔记
 * 使用 mcporter 调用 xiaohongshu MCP
 * 集成图片识别：moltshell-vision + image-ocr
 * 输出到本地 JSON 文件
 */

const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

/**
 * 下载图片到临时目录
 */
async function downloadImage(url) {
  return new Promise((resolve, reject) => {
    const tmpDir = '/tmp/xhs-images';
    if (!fs.existsSync(tmpDir)) {
      fs.mkdirSync(tmpDir, { recursive: true });
    }
    
    const filename = path.join(tmpDir, `${Date.now()}-${Math.random().toString(36).substr(2, 9)}.jpg`);
    const file = fs.createWriteStream(filename);
    
    const client = url.startsWith('https') ? https : http;
    client.get(url, (response) => {
      response.pipe(file);
      file.on('finish', () => {
        file.close();
        resolve(filename);
      });
    }).on('error', (err) => {
      fs.unlink(filename, () => {});
      reject(err);
    });
  });
}

/**
 * 使用 moltshell-vision 分析图片
 */
async function analyzeImageWithVision(imageUrl) {
  try {
    if (!imageUrl || typeof imageUrl !== 'string') {
      throw new Error('Invalid image URL');
    }
    
    const result = spawnSync('moltshell-vision', [
      imageUrl,
      '请详细描述这张图片的内容、风格、主要元素和视觉特点'
    ], {
      encoding: 'utf-8',
      stdio: ['pipe', 'pipe', 'ignore'],
      timeout: 30000
    });
    
    if (result.error) {
      throw result.error;
    }
    
    return result.stdout ? result.stdout.trim() : '';
  } catch (error) {
    console.warn(`[图片分析] Vision 失败: ${error.message}`);
    return '';
  }
}

/**
 * 使用 image-ocr 提取图片文字
 */
async function extractTextFromImage(imagePath) {
  try {
    if (!imagePath || typeof imagePath !== 'string') {
      throw new Error('Invalid image path');
    }
    
    if (!fs.existsSync(imagePath)) {
      throw new Error('Image file not found');
    }
    
    const result = spawnSync('image-ocr', [
      imagePath,
      '--lang',
      'chi_sim+eng'
    ], {
      encoding: 'utf-8',
      stdio: ['pipe', 'pipe', 'ignore'],
      timeout: 30000
    });
    
    if (result.error) {
      throw result.error;
    }
    
    return result.stdout ? result.stdout.trim() : '';
  } catch (error) {
    console.warn(`[OCR] 提取失败: ${error.message}`);
    return '';
  }
}

/**
 * 处理单张图片：Vision 分析 + OCR 提取
 */
async function processImage(imageUrl) {
  const result = { vision: '', ocr: '' };
  
  try {
    result.vision = await analyzeImageWithVision(imageUrl);
    const localPath = await downloadImage(imageUrl);
    
    try {
      result.ocr = await extractTextFromImage(localPath);
    } finally {
      if (fs.existsSync(localPath)) {
        fs.unlinkSync(localPath);
      }
    }
  } catch (error) {
    console.warn(`[图片处理] 失败: ${error.message}`);
  }
  
  return result;
}

/**
 * 抓取小红书笔记并处理
 */
async function fetchNotes(maxResults = 3) {
  console.log(`[开始] 抓取 ${maxResults} 条小红书笔记...`);
  
  let notes = [];
  
  try {
    const result = spawnSync('mcporter', [
      'call',
      'xiaohongshu',
      'search_notes',
      '--query',
      'AI创作',
      '--count',
      maxResults.toString()
    ], {
      encoding: 'utf-8',
      stdio: ['pipe', 'pipe', 'pipe'],
      timeout: 30000
    });
    
    if (result.error) {
      throw result.error;
    }
    
    if (result.status === 0 && result.stdout) {
      const parsed = JSON.parse(result.stdout);
      if (parsed && parsed.notes && Array.isArray(parsed.notes)) {
        notes = parsed.notes;
        console.log(`[MCP] 成功抓取 ${notes.length} 条笔记`);
      }
    } else {
      throw new Error('MCP 调用失败');
    }
  } catch (error) {
    console.warn('[MCP] 调用失败，使用模拟数据');
    notes = getMockNotes(maxResults);
  }
  
  const processedNotes = [];
  const timestamp = new Date().toISOString();
  
  for (let i = 0; i < notes.length; i++) {
    const note = notes[i];
    console.log(`\n[${i + 1}/${notes.length}] 处理笔记: ${note.title}`);
    
    try {
      const imageAnalysis = [];
      if (note.images && note.images.length > 0) {
        console.log(`  处理 ${note.images.length} 张图片...`);
        for (const imageUrl of note.images) {
          const analysis = await processImage(imageUrl);
          imageAnalysis.push(analysis);
        }
      }
      
      const processedNote = {
        original_title: note.title,
        original_content: note.content,
        author: note.author || '',
        likes: note.likes || 0,
        image_analysis: imageAnalysis.map(img => img.vision).filter(Boolean),
        ocr_text: imageAnalysis.map(img => img.ocr).filter(Boolean),
        rewritten_title: '',
        rewritten_content: '',
        tags: note.tags || [],
        url: note.url || '',
        fetch_time: timestamp
      };
      
      processedNotes.push(processedNote);
      console.log(`  ✓ 完成`);
      
    } catch (error) {
      console.error(`  ✗ 处理失败: ${error.message}`);
    }
  }
  
  const outputDir = path.join(__dirname, '..', 'output');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  
  const now = new Date();
  const dateStr = now.toISOString().replace(/[-:]/g, '').replace('T', '_').split('.')[0];
  const outputFile = path.join(outputDir, `xiaohongshu_${dateStr}.json`);
  
  fs.writeFileSync(outputFile, JSON.stringify(processedNotes, null, 2), 'utf-8');
  console.log(`\n[完成] 已保存到: ${outputFile}`);
  
  return processedNotes;
}

/**
 * 获取模拟数据
 */
function getMockNotes(count) {
  const mockNotes = [
    {
      title: '分享一个超实用的AI工具，让你的工作效率翻倍！',
      content: '最近发现了一个宝藏AI工具，真的太好用了！可以帮你自动生成文案、做图、剪视频，简直是打工人的福音。而且操作超简单，小白也能轻松上手。强烈推荐给大家！',
      author: '科技小达人',
      likes: 1234,
      url: 'https://www.xiaohongshu.com/explore/mock001',
      images: [],
      tags: ['AI工具', '效率提升', '职场技能'],
    },
    {
      title: '副业月入过万？这些AI赚钱方法你一定要知道',
      content: '今天给大家分享几个用AI做副业的方法，亲测有效！1. AI绘画接单 2. AI写作变现 3. AI视频剪辑...每个月轻松多赚几千块，有的甚至能月入过万。感兴趣的姐妹们可以试试！',
      author: '副业达人小美',
      likes: 2345,
      url: 'https://www.xiaohongshu.com/explore/mock002',
      images: [],
      tags: ['副业', 'AI赚钱', '自由职业'],
    },
    {
      title: '用AI做自媒体，3个月涨粉10万的秘诀',
      content: '分享我用AI做自媒体的经验：选题用AI分析热点，文案用AI生成框架，配图用AI绘制，剪辑用AI自动化...3个月从0到10万粉丝，收益也很可观。关键是要找对方法！',
      author: '自媒体老王',
      likes: 3456,
      url: 'https://www.xiaohongshu.com/explore/mock003',
      images: [],
      tags: ['副业', 'AI创作', '自媒体'],
    },
  ];
  
  return mockNotes.slice(0, count);
}

module.exports = { fetchNotes };

if (require.main === module) {
  const arg = process.argv[2] || '3';
  
  if (!/^\d+$/.test(arg)) {
    console.error('错误：参数必须是纯数字');
    process.exit(1);
  }
  
  const maxResults = parseInt(arg);
  
  if (isNaN(maxResults) || maxResults < 1 || maxResults > 100) {
    console.error('错误：maxResults 必须是 1-100 之间的数字');
    process.exit(1);
  }
  
  fetchNotes(maxResults)
    .then(notes => {
      console.log(JSON.stringify(notes, null, 2));
    })
    .catch(error => {
      console.error(error);
      process.exit(1);
    });
}
