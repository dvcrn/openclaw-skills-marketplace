#!/usr/bin/env node

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

// 配色方案
const COLORS = {
  primary: '#8B7355',      // 咖啡棕
  background: '#FFF8F0',   // 纸质米白
  accent: '#D4A574',       // 浅咖
  text: '#4A3F35',         // 深咖文字
  shadow: 'rgba(139, 115, 85, 0.15)'
};

/**
 * 智能分块：将长文本分成多个段落
 */
function splitContent(text) {
  // 按换行、数字列表分割
  const lines = text.split(/\n+/).filter(l => l.trim());
  
  // 如果已经有明确分段，直接使用
  if (lines.length > 1) {
    return lines;
  }
  
  // 否则按标点符号分割
  const sentences = text.split(/[。！？]/).filter(s => s.trim());
  
  // 如果句子太少，按长度分块
  if (sentences.length <= 2) {
    const chunks = [];
    const chunkSize = 80;
    for (let i = 0; i < text.length; i += chunkSize) {
      chunks.push(text.substring(i, i + chunkSize));
    }
    return chunks.filter(c => c.trim());
  }
  
  return sentences.map(s => s.trim() + (s.endsWith('。') ? '' : '。'));
}

/**
 * 生成卡片HTML
 */
function generateHTML(content, index, total, title = '') {
  const isFirstCard = index === 1 && title;
  
  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    body {
      width: 1080px;
      height: 1440px;
      background: ${COLORS.background};
      font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
      display: flex;
      flex-direction: column;
      position: relative;
      overflow: hidden;
    }
    
    /* 顶部装饰条 */
    .top-bar {
      width: 100%;
      height: 12px;
      background: linear-gradient(90deg, ${COLORS.accent}, ${COLORS.primary});
    }
    
    /* 主内容区 */
    .container {
      flex: 1;
      padding: 80px;
      position: relative;
    }
    
    /* 页码标签 */
    .page-label {
      position: absolute;
      top: 80px;
      right: 80px;
      width: 80px;
      height: 80px;
      border-radius: 50%;
      background: ${COLORS.primary};
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 32px;
      font-weight: bold;
      box-shadow: 0 4px 12px ${COLORS.shadow};
    }
    
    /* 标题 */
    .title {
      font-size: 58px;
      font-weight: bold;
      color: ${COLORS.primary};
      margin-bottom: 30px;
      padding-bottom: 20px;
      border-bottom: 5px solid ${COLORS.accent};
      max-width: 700px;
    }
    
    /* 内容 */
    .content {
      font-size: 42px;
      line-height: 1.8;
      color: ${COLORS.text};
      margin-top: ${isFirstCard ? '60px' : '100px'};
      max-width: 850px;
      text-align: justify;
      word-break: break-word;
    }
    
    /* 装饰元素 */
    .decoration {
      position: absolute;
      bottom: 80px;
      left: 80px;
      right: 80px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .dots {
      display: flex;
      gap: 24px;
    }
    
    .dot {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      background: ${COLORS.accent};
    }
    
    .dot.active {
      background: ${COLORS.primary};
      width: 16px;
      height: 16px;
    }
    
    .brand {
      font-size: 28px;
      color: ${COLORS.accent};
      font-weight: 500;
      letter-spacing: 2px;
    }
    
    /* 卡片阴影效果 */
    .card-shadow {
      position: absolute;
      top: 60px;
      left: 40px;
      right: 40px;
      bottom: 60px;
      background: white;
      border-radius: 20px;
      box-shadow: 0 8px 30px ${COLORS.shadow};
      z-index: -1;
    }
  </style>
</head>
<body>
  <div class="top-bar"></div>
  <div class="card-shadow"></div>
  
  <div class="container">
    <div class="page-label">${index}/${total}</div>
    
    ${isFirstCard ? `<div class="title">${title}</div>` : ''}
    
    <div class="content">
      ${content.replace(/\n/g, '<br>')}
    </div>
    
    <div class="decoration">
      <div class="dots">
        ${[0, 1, 2].map(i => 
          `<div class="dot ${i === (index - 1) % 3 ? 'active' : ''}"></div>`
        ).join('')}
      </div>
      <div class="brand">SnapDesign</div>
    </div>
  </div>
</body>
</html>
  `.trim();
}

/**
 * 主函数
 */
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args[0] === '--help') {
    console.log(`
📸 SnapDesign RedNote - 小红书卡片生成器

使用方法:
  node generate.js "你的文本内容" [选项]

选项:
  --title "标题"       设置卡片标题（显示在第一张）
  --output <目录>      输出目录 (默认: ./output)
  --single            生成单张卡片（不分块）

示例:
  node generate.js "如何高效学习？\\n第一步：选择方向\\n第二步：持续练习\\n第三步：总结复盘"
  node generate.js "内容" --title "学习指南" --output ./my-cards
    `);
    return;
  }

  let content = args[0];
  let title = '';
  let outputDir = './output';
  let single = false;

  // 解析参数
  for (let i = 1; i < args.length; i++) {
    if (args[i] === '--title' && args[i + 1]) {
      title = args[++i];
    } else if (args[i] === '--output' && args[i + 1]) {
      outputDir = args[++i];
    } else if (args[i] === '--single') {
      single = true;
    }
  }

  // 创建输出目录
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // 分块内容
  const blocks = single ? [content] : splitContent(content);
  
  console.log(`\n📝 准备生成 ${blocks.length} 张卡片...\n`);

  // 启动浏览器
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  try {
    // 生成每张卡片
    for (let i = 0; i < blocks.length; i++) {
      const html = generateHTML(blocks[i], i + 1, blocks.length, title);
      const page = await browser.newPage();
      
      await page.setViewport({
        width: 1080,
        height: 1440,
        deviceScaleFactor: 2
      });
      
      await page.setContent(html);
      
      const outputPath = path.join(outputDir, `card-${i + 1}.png`);
      await page.screenshot({
        path: outputPath,
        type: 'png',
        omitBackground: false
      });
      
      await page.close();
      
      console.log(`✅ 卡片 ${i + 1}/${blocks.length} 已生成: ${outputPath}`);
    }
  } finally {
    await browser.close();
  }

  console.log(`\n🎉 完成！共生成 ${blocks.length} 张卡片，保存在: ${outputDir}/\n`);
}

// 运行
if (require.main === module) {
  main().catch(err => {
    console.error('❌ 错误:', err.message);
    process.exit(1);
  });
}

module.exports = { splitContent, generateHTML };
