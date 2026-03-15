#!/usr/bin/env node

/**
 * SnapDesign RedNote v2.0
 * AI驱动的小红书卡片生成器
 * - 使用Kimi K2.5进行内容提炼和排版
 * - 支持智能图片生成（可选）
 * - 高级Tailwind CSS排版
 */

const fs = require('fs');
const path = require('path');

// ===== 配置 =====
const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY || '';
// 使用Claude 3.5 Sonnet - 更适合HTML生成任务
const OPENROUTER_HTML_MODEL = 'anthropic/claude-3.5-sonnet';
const OPENROUTER_IMAGE_MODEL = 'seedream-4.5';

const COLORS = {
  background: '#FFFCF8',
  text: '#664A42',
  textDark: '#3E2723',
  accent1: '#D4A574',
  accent2: '#E8B4A0',
  accent3: '#A8B5A0'
};

// ===== Prompt构建 =====
function buildRedNotePrompt(text, wantsImages = false, cardCount = 3) {
  const imageInstruction = wantsImages 
    ? `IMAGES: Use <div data-img-placeholder="[[LOADING_IMAGE_PLACEHOLDER]]" class="w-full aspect-[3/4] bg-gray-200 bg-center bg-cover bg-no-repeat"></div>` 
    : '';

  return `Create ${cardCount} Xiaohongshu cards (3:4) from: "${text}"

OUTPUT: Start with <div class="w-full flex flex-col items-center gap-[20px] bg-[#F5F5F5] py-8">
NO markdown blocks, NO explanations, ONLY HTML with Tailwind classes.

${imageInstruction}

CARD STRUCTURE (CRITICAL - Follow exactly):
<div class="relative w-[900px] h-[1198px] bg-[${COLORS.background}] flex flex-col justify-start py-[84px] px-[76px] overflow-hidden shadow-lg border border-neutral-200 rounded-lg">
  <!-- Content goes here -->
  <!-- Use flex flex-col gap-4 for spacing between elements -->
  <!-- NO additional padding inside content -->
</div>

COLORS (5 max):
- Card Background: ${COLORS.background}
- Text: ${COLORS.text} or ${COLORS.textDark}, at least 1rem in font size
- Accent: ${COLORS.accent1}, ${COLORS.accent2}, or ${COLORS.accent3}, ${COLORS.textDark}, atmost 2 accent colors in one card
- 适当的分区分块或者流程图等，可视化的展示，分块的内容可以有适当的背景色或者描边比如 ${COLORS.accent1} 0.3 opacity, ${COLORS.textDark} 等

TEXT WRAPPING:
- titles/headings on the first card: MUST be 72px font size (high-res: 900x1198)
- ALL short text (<50 chars): MUST include "whitespace-nowrap" class
- Long paragraphs (>50 chars): Use "whitespace-normal break-all" for Chinese
- Use explicit width classes: w-full, w-[900px], etc.
- Spacing: Use gap-8, gap-12, space-y-8 for consistent spacing (double for high-res)
- Font sizes: text-6xl (72px), text-4xl (48px), text-2xl (32px), text-xl (24px)
- NO inline styles except background-image

LAYOUT RULES (CRITICAL):
- ${cardCount} separate cards, each complete & independent
- Each card must be self-contained with proper overflow-hidden
- High-res layout: use larger font sizes (text-4xl instead of text-xl)
- Use flex flex-col with gap-8 or gap-12 for vertical spacing
- Use user's language only (no auto-translation)
- NO emojis
- **每一页能排满就排满，排不下再去下一页**
- **主动精简和提炼关键点，不是把所有文字直接写上去**
- **用标签、卡片框、箭头等视觉元素增强可读性**

FOOTER:
- Add text "www.snapdesign.app" at bottom right of each card
- Use text-[20px] text-[#8B7355] (咖色水印)
- Position: absolute bottom-12 right-16`;
}

// ===== 系统指令 =====
function getSystemInstruction() {
  return `You are a world-class UI/UX designer and expert Tailwind CSS developer specializing in Xiaohongshu (小红书) card designs.

CRITICAL TECHNICAL REQUIREMENTS:
1. You MUST use Tailwind CSS utility classes for ALL styling
2. You MUST output ONLY valid HTML with Tailwind classes - NO explanatory text, NO markdown code blocks
3. You MUST start your response directly with the opening <div> tag
4. You MUST use ONLY Tailwind utility classes - NO inline styles except for background-image
5. You MUST follow the exact structure and classes specified in the prompt

DESIGN EXPERTISE:
Your designs are known for:
- Paper-style aesthetic with warm, inviting colors (${COLORS.background} background)
- Clean typography with coffee-colored text (${COLORS.text}, ${COLORS.textDark})
- Perfect 3:4 aspect ratio (aspect-[3/4]) for mobile viewing
- Highlighted key points with bold text and color accents
- Professional yet approachable style
- Generous padding (px-10 to px-12) to prevent text from touching edges
- Proper text sizing to prevent unwanted line breaks
- **内容提炼和重组，而不是简单的文本搬运**
- **使用视觉元素：标签、卡片框、箭头、图标**

TAILWIND CSS MASTERY:
- Layout: flex, flex-col, items-center, justify-center, gap-4, space-y-4
- Sizing: w-[900px], h-[1198px], aspect-[3/4], h-auto
- Spacing: p-4, px-10, py-6, m-4, gap-[20px]
- Typography: text-3xl, text-xl, text-base, font-bold, font-medium, whitespace-nowrap
- Colors: bg-[${COLORS.background}], text-[${COLORS.text}], text-[${COLORS.textDark}]
- Borders: border, border-neutral-200, rounded-lg
- Shadows: shadow-lg
- Overflow: overflow-hidden

You create static, beautiful card designs that capture attention and convey information effectively using ONLY Tailwind CSS utility classes.`;
}

// ===== API调用 =====
async function generateHtmlWithKimi(prompt, systemInstruction) {
  if (!OPENROUTER_API_KEY) {
    throw new Error('OPENROUTER_API_KEY环境变量未设置');
  }

  const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
      'HTTP-Referer': 'https://snapdesign.app',
      'X-Title': 'SnapDesign RedNote'
    },
    body: JSON.stringify({
      model: OPENROUTER_HTML_MODEL,
      messages: [
        { role: 'system', content: systemInstruction },
        { role: 'user', content: prompt }
      ],
      temperature: 0.7,
      max_tokens: 4000
    })
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Kimi API错误: ${error}`);
  }

  const data = await response.json();
  
  if (!data.choices || !data.choices[0] || !data.choices[0].message) {
    throw new Error(`Kimi API响应格式错误: ${JSON.stringify(data)}`);
  }
  
  const message = data.choices[0].message;
  
  // Kimi K2.5是推理模型，内容可能在reasoning字段
  let content = message.content;
  
  if (!content && message.reasoning) {
    content = message.reasoning;
  }
  
  if (!content && message.reasoning_details && message.reasoning_details.length > 0) {
    content = message.reasoning_details.map(d => d.text).join('');
  }
  
  return content;
}

// ===== HTML to Image转换 =====
async function htmlToImage(html, outputPath) {
  const puppeteer = require('puppeteer');
  
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
    }
  </style>
</head>
<body>
  ${html}
</body>
</html>
  `;

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
      
      const cardPath = outputPath.replace('.png', `-${i + 1}.png`);
      
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

// ===== 检测用户意图 =====
function detectUserIntent(text) {
  const imageKeywords = ['配图', '插图', '图片', '图像', '背景', '配个图'];
  const noImageKeywords = ['不要图', '无图', '不需要图片', '纯文字'];
  
  const wantsImages = imageKeywords.some(kw => text.includes(kw));
  const rejectsImages = noImageKeywords.some(kw => text.includes(kw));
  
  return { wantsImages, rejectsImages };
}

// ===== 主函数 =====
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args[0] === '--help') {
    console.log(`
📸 SnapDesign RedNote v2.0 - AI驱动的小红书卡片生成器

使用方法:
  node generate-v2.js "你的文本内容" [选项]

选项:
  --title "标题"       设置卡片标题
  --output <目录>      输出目录 (默认: ./output-v2)
  --cards <数量>       生成卡片数量 (默认: 自动)
  --with-images       强制生成配图

环境变量:
  OPENROUTER_API_KEY   OpenRouter API密钥 (必需)

示例:
  export OPENROUTER_API_KEY="your-key"
  node generate-v2.js "如何高效学习？第一步：选择方向..." --title "学习指南"

注意:
  - 需要OpenRouter API密钥
  - 使用Kimi K2.5模型进行内容提炼
  - 自动优化排版和视觉效果
    `);
    return;
  }

  let content = args[0];
  let title = '';
  let outputDir = './output-v2';
  let cardCount = null;
  let forceImages = false;

  // 解析参数
  for (let i = 1; i < args.length; i++) {
    if (args[i] === '--title' && args[i + 1]) {
      title = args[++i];
    } else if (args[i] === '--output' && args[i + 1]) {
      outputDir = args[++i];
    } else if (args[i] === '--cards' && args[i + 1]) {
      cardCount = parseInt(args[++i]);
    } else if (args[i] === '--with-images') {
      forceImages = true;
    }
  }

  // 创建输出目录
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // 检查API密钥
  if (!OPENROUTER_API_KEY) {
    console.error('❌ 错误: 请设置 OPENROUTER_API_KEY 环境变量');
    console.error('   export OPENROUTER_API_KEY="your-key"');
    process.exit(1);
  }

  // 添加标题到内容
  const fullText = title ? `${title}\n\n${content}` : content;

  // 检测用户意图
  const { wantsImages, rejectsImages } = detectUserIntent(fullText);
  const needImages = forceImages || (wantsImages && !rejectsImages);

  // 估算卡片数量
  if (!cardCount) {
    const textLength = fullText.length;
    cardCount = Math.min(Math.max(Math.ceil(textLength / 150), 3), 9);
  }

  console.log(`\n📝 AI正在生成 ${cardCount} 张卡片...\n`);
  console.log(`🤖 使用模型: ${OPENROUTER_HTML_MODEL}`);
  console.log(`🎨 配图模式: ${needImages ? '开启' : '关闭'}\n`);

  try {
    // 生成HTML
    const prompt = buildRedNotePrompt(fullText, needImages, cardCount);
    const systemInstruction = getSystemInstruction();
    
    console.log('⏳ 正在调用Kimi AI...');
    const html = await generateHtmlWithKimi(prompt, systemInstruction);
    
    if (!html) {
      throw new Error('Kimi AI返回空内容');
    }
    
    // 清理HTML（移除markdown标记）
    const cleanHtml = html.replace(/```html/g, '').replace(/```/g, '').trim();
    
    // 保存HTML（用于调试）
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
  ${cleanHtml}
</body>
</html>
    `;
    fs.writeFileSync(htmlPath, fullHtml);
    console.log(`✅ HTML已保存: ${htmlPath}`);
    
    // 转换为图片
    console.log('\n🎨 正在生成图片...\n');
    const count = await htmlToImage(cleanHtml, path.join(outputDir, 'card.png'));
    
    console.log(`\n🎉 完成！共生成 ${count} 张卡片`);
    console.log(`📁 保存位置: ${outputDir}/\n`);
    
  } catch (error) {
    console.error('❌ 错误:', error.message);
    if (error.message.includes('API')) {
      console.error('\n💡 提示: 请检查OPENROUTER_API_KEY是否正确');
    }
    process.exit(1);
  }
}

// 运行
if (require.main === module) {
  main().catch(err => {
    console.error('❌ 错误:', err.message);
    process.exit(1);
  });
}

module.exports = { buildRedNotePrompt, getSystemInstruction };
