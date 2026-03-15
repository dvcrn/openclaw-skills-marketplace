const puppeteer = require('puppeteer');
const marked = require('marked');
const fs = require('fs');
const path = require('path');

// 每页最大行数
let MAX_LINES_PER_PAGE = 500;

/**
 * 将markdown内容按内容块和行数限制分割为多页
 * @param {string} mdContent - 原始markdown内容
 * @returns {Array<string>} 分割后的每页markdown内容
 */
function splitMarkdownIntoPages(mdContent) {
  const lines = mdContent.split('\n');
  const pages = [];
  let currentPage = [];
  let currentLineCount = 0;
  let inCodeBlock = false;
  let inTable = false;
  let currentCodeBlock = [];
  let currentTable = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    
    // 检测代码块边界
    if (line.trim().startsWith('```')) {
      if (inCodeBlock) {
        // 结束代码块
        currentCodeBlock.push(line);
        const codeBlockLines = currentCodeBlock.length;
        
        // 检查当前页是否能容纳整个代码块
        if (currentLineCount + codeBlockLines <= MAX_LINES_PER_PAGE) {
          currentPage.push(...currentCodeBlock);
          currentLineCount += codeBlockLines;
        } else {
          // 不能容纳，先保存当前页，再开启新页
          if (currentPage.length > 0) {
            pages.push(currentPage.join('\n'));
            currentPage = [];
            currentLineCount = 0;
          }
          currentPage.push(...currentCodeBlock);
          currentLineCount += codeBlockLines;
        }
        
        currentCodeBlock = [];
        inCodeBlock = false;
      } else {
        // 开始代码块
        inCodeBlock = true;
        currentCodeBlock.push(line);
      }
      continue;
    }

    // 如果在代码块中，继续累积
    if (inCodeBlock) {
      currentCodeBlock.push(line);
      continue;
    }

    // 检测表格边界
    const isTableLine = line.includes('|') && line.trim().startsWith('|') && line.trim().endsWith('|');
    const isTableSeparator = isTableLine && line.includes('---') && line.split('|').every(cell => cell.trim().match(/^-+$/));
    
    if (isTableLine || isTableSeparator) {
      if (!inTable) {
        inTable = true;
        currentTable = [];
      }
      currentTable.push(line);
      
      // 检查是否是表格的最后一行（下一行不是表格行）
      const nextLine = lines[i + 1] || '';
      const isNextLineTable = nextLine.includes('|') && nextLine.trim().startsWith('|') && nextLine.trim().endsWith('|');
      
      if (!isNextLineTable) {
        // 结束表格
        const tableLines = currentTable.length;
        
        // 检查当前页是否能容纳整个表格
        if (currentLineCount + tableLines <= MAX_LINES_PER_PAGE) {
          currentPage.push(...currentTable);
          currentLineCount += tableLines;
        } else {
          // 不能容纳，先保存当前页，再开启新页
          if (currentPage.length > 0) {
            pages.push(currentPage.join('\n'));
            currentPage = [];
            currentLineCount = 0;
          }
          currentPage.push(...currentTable);
          currentLineCount += tableLines;
        }
        
        currentTable = [];
        inTable = false;
      }
      continue;
    }

    // 如果在表格中，继续累积
    if (inTable) {
      currentTable.push(line);
      continue;
    }

    // 普通行处理
    // 检查当前行加入后是否超过行数限制
    if (currentLineCount + 1 > MAX_LINES_PER_PAGE) {
      // 超过限制，先保存当前页
      pages.push(currentPage.join('\n'));
      currentPage = [];
      currentLineCount = 0;
    }
    
    currentPage.push(line);
    currentLineCount += 1;
  }

  // 处理剩余的代码块
  if (inCodeBlock && currentCodeBlock.length > 0) {
    const codeBlockLines = currentCodeBlock.length;
    if (currentLineCount + codeBlockLines > MAX_LINES_PER_PAGE && currentPage.length > 0) {
      pages.push(currentPage.join('\n'));
      currentPage = [];
      currentLineCount = 0;
    }
    currentPage.push(...currentCodeBlock);
    currentLineCount += codeBlockLines;
  }

  // 处理剩余的表格
  if (inTable && currentTable.length > 0) {
    const tableLines = currentTable.length;
    if (currentLineCount + tableLines > MAX_LINES_PER_PAGE && currentPage.length > 0) {
      pages.push(currentPage.join('\n'));
      currentPage = [];
      currentLineCount = 0;
    }
    currentPage.push(...currentTable);
    currentLineCount += tableLines;
  }

  // 处理剩余的普通内容
  if (currentPage.length > 0) {
    pages.push(currentPage.join('\n'));
  }

  return pages;
}

/**
 * 写入日志文件
 * @param {string} outputPath - 输出图片路径
 * @param {object} logInfo - 日志信息
 */
function writeLog(outputPath, logInfo) {
  // 日志文件路径：和图片同目录，同名.log后缀
  const logPath = outputPath.replace(path.extname(outputPath), '.log');
  
  const logContent = `=== 图片生成日志 ===
生成时间: ${new Date().toLocaleString('zh-CN')}
输入文件: ${logInfo.inputPath || '动态内容'}
输出图片: ${outputPath}
图片大小: ${logInfo.fileSize || '0'} KB
生成耗时: ${logInfo.duration || '0'} ms
内容长度: ${logInfo.contentLength || '0'} 字符
图片高度: ${logInfo.imageHeight || '0'} px
状态: ${logInfo.status || '成功'}
${logInfo.error ? `错误信息: ${logInfo.error.stack || logInfo.error.message}` : ''}
====================
`;

  fs.writeFileSync(logPath, logContent, 'utf8');
  console.log(`📝 日志已保存到：${logPath}`);
}

/**
 * 生成单页图片
 * @param {string} htmlContent - 页面HTML内容
 * @param {string} outputPath - 输出图片路径
 * @param {object} logInfo - 日志信息对象
 * @returns {Promise<number>} 生成的图片高度
 */
async function generateSinglePage(htmlContent, outputPath, logInfo) {
  // 完整HTML页面
  const fullHtml = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Markdown to Image</title>
  <style>
    body {
      font-family: "WenQuanYi Micro Hei", "WenQuanYi Zen Hei", "Noto Sans CJK SC", "Noto Color Emoji", -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
      padding: 40px;
      max-width: 800px;
      margin: 0 auto;
      background: white;
      color: #333;
      line-height: 1.6;
    }
    h1, h2, h3 { color: #2c3e50; margin-top: 24px; margin-bottom: 16px; }
    h1 { font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
    h2 { font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
    code { background: #f6f8fa; padding: 0.2em 0.4em; border-radius: 3px; font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace; }
    pre { background: #f6f8fa; padding: 16px; border-radius: 6px; overflow-x: auto; }
    pre code { background: none; padding: 0; }
    blockquote { border-left: 4px solid #dfe2e5; padding: 0 1em; color: #6a737d; margin: 0; }
    table { border-collapse: collapse; width: 100%; margin: 16px 0; }
    th, td { border: 1px solid #dfe2e5; padding: 6px 13px; text-align: left; }
    th { background: #f6f8fa; font-weight: 600; }
    ul, ol { padding-left: 2em; }
    li { margin: 4px 0; }
    .emoji { font-family: "Noto Color Emoji", 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol'; }
    .page-footer {
      text-align: center;
      margin-top: 20px;
      padding-top: 10px;
      border-top: 1px solid #eee;
      color: #999;
      font-size: 0.9em;
    }
  </style>
</head>
<body>
  ${htmlContent}
</body>
</html>
`;

  const browser = await puppeteer.launch({
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
    headless: true
  });
  
  const page = await browser.newPage();
  await page.setContent(fullHtml, { waitUntil: 'networkidle0' });
  
  // 获取内容高度
  const bodyHandle = await page.$('body');
  const { height } = await bodyHandle.boundingBox();
  await bodyHandle.dispose();
  const imageHeight = Math.ceil(height);
  
  // 设置视口
  await page.setViewport({
    width: 900,
    height: imageHeight,
    deviceScaleFactor: 2
  });
  
  // 截图
  await page.screenshot({
    path: outputPath,
    fullPage: true,
    type: 'png'
  });
  
  await browser.close();
  
  // 获取文件大小
  const stats = fs.statSync(outputPath);
  const fileSize = Math.round(stats.size / 1024);
  
  return { height: imageHeight, size: fileSize };
}

/**
 * markdown转图片工具（支持分页）
 * @param {string} mdContent - markdown内容
 * @param {string} outputPath - 输出图片路径
 * @returns {Promise<Array<string>>} 生成的图片路径列表
 */
async function md2img(mdContent, outputPath, inputPath = null) {
  const startTime = Date.now();
  const logInfo = {
    inputPath: inputPath,
    contentLength: mdContent.length,
    status: '成功',
    pages: []
  };

  try {
    console.log(`🚀 开始生成图片：${outputPath}`);
    console.log(`📄 内容长度：${mdContent.length} 字符`);

    // 分割为多页
    const pages = splitMarkdownIntoPages(mdContent);
    const totalPages = pages.length;
    console.log(`📑 内容已分割为 ${totalPages} 页`);
    
    if (totalPages === 0) {
      throw new Error('内容为空，无法生成图片');
    }

    const generatedPaths = [];
    let totalHeight = 0;
    let totalSize = 0;

    // 生成每页图片
    for (let i = 0; i < totalPages; i++) {
      const pageNum = i + 1;
      const pageContent = pages[i];
      
      // 添加页脚
      const pageContentWithFooter = totalPages > 1 
        ? `${pageContent}\n\n<div class="page-footer">第 ${pageNum} 页 / 共 ${totalPages} 页</div>`
        : pageContent;
      
      // 转换为HTML
      const htmlContent = marked.parse(pageContentWithFooter);
      
      // 生成输出路径
      let pageOutputPath;
      if (totalPages === 1) {
        pageOutputPath = outputPath;
      } else {
        const ext = path.extname(outputPath);
        const baseName = path.basename(outputPath, ext);
        const dirName = path.dirname(outputPath);
        pageOutputPath = path.join(dirName, `${baseName}_${pageNum}${ext}`);
      }
      
      console.log(`🖨️  正在生成第 ${pageNum}/${totalPages} 页：${pageOutputPath}`);
      
      const { height, size } = await generateSinglePage(htmlContent, pageOutputPath, logInfo);
      
      generatedPaths.push(pageOutputPath);
      totalHeight += height;
      totalSize += size;
      
      logInfo.pages.push({
        pageNum,
        path: pageOutputPath,
        height,
        size
      });
      
      console.log(`✅ 第 ${pageNum}/${totalPages} 页生成完成，高度：${height} px，大小：${size} KB`);
    }

    // 计算耗时
    const duration = Date.now() - startTime;
    logInfo.duration = duration;
    logInfo.imageHeight = totalHeight;
    logInfo.fileSize = totalSize;
    
    console.log(`✅ 所有页面生成完成，总高度：${totalHeight} px，总大小：${totalSize} KB`);
    console.log(`⏱️  总生成耗时：${duration} ms`);

    // 写入日志
    writeLog(outputPath, logInfo);

    return generatedPaths;
  } catch (err) {
    logInfo.status = '失败';
    logInfo.error = err;
    logInfo.duration = Date.now() - startTime;
    
    // 写入错误日志
    writeLog(outputPath, logInfo);
    
    console.error(`❌ 转换失败：${err.message}`);
    throw err;
  }
}

// 如果直接运行脚本，从命令行参数获取输入和输出
if (require.main === module) {
  const args = process.argv.slice(2);
  if (args.length < 2) {
    console.error('使用方法: node md_to_png.js <输入markdown文件> <输出图片路径> [每页最大行数，默认500]');
    process.exit(1);
  }
  
  const inputPath = args[0];
  const outputPath = args[1];
  
  // 支持自定义每页最大行数
  if (args[2]) {
    const customMaxLines = parseInt(args[2], 10);
    if (!isNaN(customMaxLines) && customMaxLines > 0) {
      MAX_LINES_PER_PAGE = customMaxLines;
      console.log(`🔧 自定义每页最大行数：${MAX_LINES_PER_PAGE}`);
    }
  }
  
  const mdContent = fs.readFileSync(inputPath, 'utf8');
  
  md2img(mdContent, outputPath, inputPath)
    .then((generatedPaths) => {
      if (generatedPaths.length === 1) {
        console.log(`✅ 转换成功！图片已保存到：${generatedPaths[0]}`);
      } else {
        console.log(`✅ 转换成功！共生成 ${generatedPaths.length} 页：`);
        generatedPaths.forEach((path, index) => {
          console.log(`   ${index + 1}. ${path}`);
        });
      }
      process.exit(0);
    })
    .catch(err => {
      console.error('❌ 转换失败：', err);
      process.exit(1);
    });
}

module.exports = md2img;
