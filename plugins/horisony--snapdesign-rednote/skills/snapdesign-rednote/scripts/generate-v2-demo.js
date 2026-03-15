#!/usr/bin/env node

/**
 * SnapDesign RedNote v2.0 - Demo模式
 * 无需API密钥，使用预设的专业排版模板
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

// 生成专业的HTML（模拟AI生成的效果）
function generateProfessionalHTML(text, title) {
  // 智能分块
  const lines = text.split(/\n+/).filter(l => l.trim());
  const cards = [];
  
  // 如果有标题，第一张卡片是封面
  if (title) {
    cards.push({
      type: 'cover',
      title: title,
      subtitle: lines[0] || '专业内容卡片'
    });
  }
  
  // 处理内容卡片
  lines.forEach((line, idx) => {
    if (idx === 0 && title) return; // 跳过已用作封面的行
    
    // 检测是否是列表项
    const isListItem = /^(第[一二三四五六七八九十\d]+[步点条]|[\d]+[\.、\)]|[-•])/.test(line);
    
    if (isListItem) {
      cards.push({
        type: 'list-item',
        content: line,
        index: cards.length
      });
    } else {
      cards.push({
        type: 'text',
        content: line
      });
    }
  });
  
  // 限制最多9张卡片
  const limitedCards = cards.slice(0, 9);
  const totalCards = limitedCards.length;
  
  // 生成HTML
  const cardsHtml = limitedCards.map((card, idx) => {
    if (card.type === 'cover') {
      return `
<div class="relative w-[900px] h-[1198px] bg-[#FFFCF8] flex flex-col justify-between py-[42px] px-[38px] overflow-hidden shadow-lg border border-neutral-200 rounded-lg">
  <div class="flex-1 flex flex-col justify-center items-center gap-6 w-full">
    <div class="w-20 h-20 rounded-full bg-gradient-to-br from-[#D4A574] to-[#E8B4A0] flex items-center justify-center">
      <span class="text-white text-5xl font-bold">${idx + 1}/${totalCards}</span>
    </div>
    
    <h1 class="text-7xl font-bold text-[#3E2723] text-center whitespace-normal leading-tight">
      ${card.title}
    </h1>
    
    <div class="w-32 h-1 bg-gradient-to-r from-[#D4A574] to-[#E8B4A0] rounded-full"></div>
    
    <p class="text-4xl text-[#664A42] text-center whitespace-normal mt-4">
      ${card.subtitle}
    </p>
  </div>
  
  <div class="w-full text-right text-[20px] text-[#8B7355]">
    www.snapdesign.app
  </div>
</div>`;
    }
    
    if (card.type === 'list-item') {
      const match = card.content.match(/^([^：:]+)[：:](.+)/) || 
                    card.content.match(/^(第[一二三四五六七八九十\d]+[步点条])[：:]?(.+)/) ||
                    card.content.match(/^([\d]+[\.、\)])[：:]?(.+)/);
      
      if (match) {
        const label = match[1].trim();
        const content = match[2].trim();
        
        return `
<div class="relative w-[900px] h-[1198px] bg-[#FFFCF8] flex flex-col justify-between py-[42px] px-[38px] overflow-hidden shadow-lg border border-neutral-200 rounded-lg">
  <div class="flex flex-col gap-6">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-12 h-12 rounded-lg bg-[#3E2723] flex items-center justify-center">
          <span class="text-white text-3xl font-bold">${card.index}</span>
        </div>
        <h2 class="text-5xl font-bold text-[#3E2723] whitespace-nowrap">${label}</h2>
      </div>
      <div class="w-12 h-12 rounded-full bg-[#D4A574] bg-opacity-20 flex items-center justify-center">
        <span class="text-[#3E2723] text-2xl font-bold">${idx + 1}/${totalCards}</span>
      </div>
    </div>
    
    <div class="w-full h-[2px] bg-gradient-to-r from-[#D4A574] to-transparent"></div>
    
    <div class="bg-[#D4A574] bg-opacity-10 rounded-2xl p-6 border-l-4 border-[#D4A574]">
      <p class="text-4xl text-[#3E2723] whitespace-normal leading-relaxed">
        ${content}
      </p>
    </div>
    
    <div class="flex items-center gap-2 mt-auto">
      <div class="flex-1 h-2 bg-gradient-to-r from-[#D4A574] to-[#E8B4A0] rounded-full"></div>
      <svg class="w-8 h-8 text-[#D4A574]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"/>
      </svg>
    </div>
  </div>
  
  <div class="text-[20px] text-[#8B7355] text-right mt-4">
    www.snapdesign.app
  </div>
</div>`;
      }
    }
    
    // 默认文本卡片
    return `
<div class="relative w-[900px] h-[1198px] bg-[#FFFCF8] flex flex-col justify-between py-[84px] px-[76px] overflow-hidden shadow-lg border border-neutral-200 rounded-lg">
  <div class="flex-1 flex flex-col justify-center gap-6">
    <div class="flex justify-between items-center">
      <div class="w-2 h-12 bg-gradient-to-b from-[#D4A574] to-[#E8B4A0] rounded-full"></div>
      <div class="w-10 h-10 rounded-full bg-[#D4A574] bg-opacity-20 flex items-center justify-center">
        <span class="text-[#3E2723] font-bold">${idx + 1}/${totalCards}</span>
      </div>
    </div>
    
    <p class="text-4xl text-[#3E2723] whitespace-normal leading-relaxed">
      ${card.content}
    </p>
  </div>
  
  <div class="w-full text-right text-[20px] text-[#8B7355]">
    www.snapdesign.app
  </div>
</div>`;
  }).join('\n');
  
  return `
<div class="w-full flex flex-col items-center gap-[20px] bg-[#F5F5F5] py-8">
  ${cardsHtml}
</div>`;
}

// HTML转图片
async function htmlToImage(html, outputDir) {
  const fullHtml = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { 
      font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
      background: #F5F5F5;
    }
  </style>
</head>
<body>
  ${html}
</body>
</html>`;
  
  const browser = await puppeteer.launch({ 
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  try {
    const page = await browser.newPage();
    
    // 先加载一次完整页面，提取所有卡片的HTML
    await page.setContent(fullHtml);
    await new Promise(r => setTimeout(r, 1000));
    
    const cardHtmls = await page.evaluate(() => {
      const cards = document.querySelectorAll('.w-\\[900px\\]');
      return Array.from(cards).map(card => card.outerHTML);
    });
    
    if (cardHtmls.length === 0) {
      throw new Error('未找到任何卡片');
    }
    
    // 为每张卡片创建独立页面并截图
    for (let i = 0; i < cardHtmls.length; i++) {
      const singleCardHtml = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body {
      font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
      width: 900px;
      height: 1198px;
      overflow: hidden;
      margin: 0;
      padding: 0;
    }
  </style>
</head>
<body>
  ${cardHtmls[i]}
</body>
</html>`;
      
      await page.setViewport({ width: 900, height: 1198 });
      await page.setContent(singleCardHtml);
      await new Promise(r => setTimeout(r, 1500));
      
      const cardPath = path.join(outputDir, `card-${i + 1}.png`);
      
      await page.screenshot({
        path: cardPath,
        type: 'png',
        clip: { x: 0, y: 0, width: 900, height: 1198 },
        omitBackground: false
      });
      
      console.log(`✅ 卡片 ${i + 1}/${cardHtmls.length} 已生成: ${cardPath}`);
    }
    
    return cardHtmls.length;
  } finally {
    await browser.close();
  }
}

// 主函数
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args[0] === '--help') {
    console.log(`
📸 SnapDesign RedNote v2.0 - Demo模式

特点:
  ✅ 无需API密钥
  ✅ 专业级排版
  ✅ 模拟AI效果

使用:
  node generate-v2-demo.js "内容" [--title "标题"] [--output ./output-demo]

示例:
  node generate-v2-demo.js "如何学习？\\n第一步：打基础\\n第二步：多练习\\n第三步：总结" --title "学习方法"
    `);
    return;
  }

  let content = args[0];
  let title = '';
  let outputDir = './output-v2-demo';

  for (let i = 1; i < args.length; i++) {
    if (args[i] === '--title' && args[i + 1]) {
      title = args[++i];
    } else if (args[i] === '--output' && args[i + 1]) {
      outputDir = args[++i];
    }
  }

  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  console.log(`\n📝 生成专业级卡片...\n`);
  console.log(`🎨 模式: Demo (无需API)`);
  console.log(`✨ 排版: AI级别\n`);

  try {
    const html = generateProfessionalHTML(content, title);
    
    // 保存HTML
    const htmlPath = path.join(outputDir, 'cards.html');
    const fullHtml = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { 
      font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
      background: #F5F5F5;
    }
  </style>
</head>
<body>
  ${html}
</body>
</html>`;
    fs.writeFileSync(htmlPath, fullHtml);
    console.log(`✅ HTML已保存: ${htmlPath}`);
    
    // 转换为图片
    console.log('\n🎨 正在生成图片...\n');
    const count = await htmlToImage(html, outputDir);
    
    console.log(`\n🎉 完成！共生成 ${count} 张专业级卡片`);
    console.log(`📁 保存位置: ${outputDir}/\n`);
    console.log(`💡 提示: 这是Demo模式的排版效果`);
    console.log(`   真实v2.0使用Kimi AI会更智能！\n`);
    
  } catch (error) {
    console.error('❌ 错误:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main().catch(err => {
    console.error('❌ 错误:', err.message);
    process.exit(1);
  });
}
