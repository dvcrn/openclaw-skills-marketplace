#!/usr/bin/env node
import { marked } from 'marked';
import puppeteer from 'puppeteer-core';
import { readFileSync, writeFileSync } from 'fs';
import { resolve } from 'path';

const input = process.argv[2];
const output = process.argv[3] || input.replace(/\.md$/i, '-长图.png');

if (!input) {
  console.log('用法: md2img <输入.md> [输出.png]');
  console.log('示例: md2img 文档.md 输出长图.png');
  process.exit(1);
}

console.log(`📄 正在转换: ${input}`);

const md = readFileSync(resolve(input), 'utf-8');
const html = await marked(md);

const fullHtml = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      max-width: 800px;
      margin: 0 auto;
      padding: 40px 30px;
      background: #fff;
      color: #333;
      line-height: 1.8;
    }
    h1 {
      font-size: 32px;
      border-bottom: 3px solid #ff6b6b;
      padding-bottom: 12px;
      color: #2c3e50;
      margin-bottom: 24px;
    }
    h2 {
      font-size: 24px;
      margin-top: 32px;
      margin-bottom: 16px;
      color: #34495e;
      border-left: 4px solid #3498db;
      padding-left: 12px;
    }
    h3 {
      font-size: 20px;
      margin-top: 24px;
      margin-bottom: 12px;
      color: #7f8c8d;
    }
    p { margin: 16px 0; }
    table {
      border-collapse: collapse;
      width: 100%;
      margin: 20px 0;
      font-size: 14px;
    }
    th, td {
      border: 1px solid #e0e0e0;
      padding: 12px 14px;
      text-align: left;
    }
    th {
      background: #f8f9fa;
      font-weight: 600;
      color: #2c3e50;
    }
    tr:nth-child(even) { background: #fafafa; }
    tr:hover { background: #f5f5f5; }
    code {
      background: #f4f4f4;
      padding: 2px 6px;
      border-radius: 4px;
      font-family: 'SF Mono', Monaco, Consolas, monospace;
      font-size: 0.9em;
      color: #e74c3c;
    }
    pre {
      background: #2d2d2d;
      color: #f8f8f2;
      padding: 16px;
      border-radius: 8px;
      overflow-x: auto;
      margin: 16px 0;
    }
    pre code {
      background: none;
      padding: 0;
      color: inherit;
    }
    blockquote {
      border-left: 4px solid #3498db;
      margin: 20px 0;
      padding: 12px 20px;
      background: #f9f9f9;
      color: #666;
      border-radius: 0 8px 8px 0;
    }
    hr {
      border: none;
      border-top: 2px solid #eee;
      margin: 40px 0;
    }
    ul, ol {
      padding-left: 24px;
      margin: 16px 0;
    }
    li { margin: 8px 0; }
    a { color: #3498db; text-decoration: none; }
    a:hover { text-decoration: underline; }
    img { max-width: 100%; border-radius: 8px; margin: 16px 0; }
    strong { color: #2c3e50; }
    em { color: #7f8c8d; }
  </style>
</head>
<body>
${html}
</body>
</html>
`;

const browser = await puppeteer.launch({
  executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  headless: true,
});

const page = await browser.newPage();
await page.setContent(fullHtml, { waitUntil: 'networkidle0' });

// 获取完整内容高度
const height = await page.evaluate(() => document.documentElement.scrollHeight);

// 设置视口为内容高度
await page.setViewport({ width: 800, height });

// 截取完整页面
await page.screenshot({ path: resolve(output), fullPage: true });

await browser.close();
console.log(`✅ 长图已保存: ${output}`);
