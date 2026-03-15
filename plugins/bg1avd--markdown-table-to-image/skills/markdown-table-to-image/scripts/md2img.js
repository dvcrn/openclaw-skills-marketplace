#!/usr/bin/env node

/**
 * Markdown 表格转图片 v1.0.1
 * 
 * 流程：
 * 1. 解析 Markdown 表格
 * 2. 生成 HTML（单元格内容居中对齐）
 * 3. 用 wkhtmltoimage 输出为图片
 */

const fs = require('fs');
const { execSync } = require('child_process');
const path = require('path');
const os = require('os');

// 解析 Markdown 表格
function parseMarkdownTable(text) {
    const lines = text.trim().split('\n');
    const headers = [];
    const rows = [];
    
    for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) continue;
        // 跳过分隔行
        if (/^[\|\-\s:]+$/.test(trimmed)) continue;
        
        if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
            const cells = trimmed.slice(1, -1).split('|').map(c => c.trim());
            if (cells.length > 0) {
                if (headers.length === 0) {
                    headers.push(...cells);
                } else {
                    rows.push(cells);
                }
            }
        }
    }
    
    return { headers, rows };
}

// 生成 HTML
function generateHtml(headers, rows) {
    let tableContent = '';
    
    // 表头
    tableContent += '<tr>\n';
    for (const h of headers) {
        tableContent += `    <th>${h}</th>\n`;
    }
    tableContent += '</tr>\n';
    
    // 数据行
    for (const row of rows) {
        tableContent += '<tr>\n';
        for (const cell of row) {
            tableContent += `    <td>${cell}</td>\n`;
        }
        tableContent += '</tr>\n';
    }
    
    return `<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
body {
    font-family: 'Noto Sans CJK SC', 'Microsoft YaHei', 'PingFang SC', sans-serif;
    background: #1a1a2e;
    padding: 20px;
    display: flex;
    justify-content: center;
}
table {
    border-collapse: collapse;
    background: #16213e;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}
th {
    background: #0f3460;
    color: #e94560;
    padding: 15px 20px;
    text-align: center;
    font-size: 18px;
    font-weight: bold;
}
td {
    color: #fff;
    padding: 12px 20px;
    text-align: center;
    font-size: 16px;
    border-bottom: 1px solid #0f3460;
}
tr:last-child td {
    border-bottom: none;
}
</style>
</head>
<body>
<table>
${tableContent}</table>
</body>
</html>`;
}

// 主函数
function main() {
    const args = process.argv.slice(2);
    
    if (args.length < 2) {
        console.error('用法: md2img.js "表格内容" output.png [宽度]');
        process.exit(1);
    }
    
    const tableText = args[0];
    const outputFile = args[1];
    const width = args[2] || '900';
    
    // 解析表格
    const { headers, rows } = parseMarkdownTable(tableText);
    
    if (headers.length === 0) {
        console.error('错误: 没有找到有效表格');
        process.exit(1);
    }
    
    // 生成 HTML
    const html = generateHtml(headers, rows);
    
    // 写临时 HTML 文件
    const tempFile = path.join(os.tmpdir(), `table_${Date.now()}.html`);
    fs.writeFileSync(tempFile, html, 'utf-8');
    
    try {
        // 用 wkhtmltoimage 生成图片
        execSync(`wkhtmltoimage --quality 100 --width ${width} ${tempFile} ${outputFile}`, {
            stdio: 'inherit'
        });
        
        console.log(`Saved: ${outputFile}`);
    } finally {
        // 删除临时文件
        if (fs.existsSync(tempFile)) {
            fs.unlinkSync(tempFile);
        }
    }
}

main();
