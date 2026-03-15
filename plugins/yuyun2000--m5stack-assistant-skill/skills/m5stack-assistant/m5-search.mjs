#!/usr/bin/env node
/**
 * M5Stack 文档检索快速工具
 * 用法: node m5-search.mjs <查询内容> [选项]
 * 选项:
 *   --num <数量>       返回结果数量，默认1
 *   --filter <类型>    过滤类型: product/program/arduino/uiflow/esp-idf/esphome，默认product
 *   --chip             查询芯片相关文档
 */

import https from 'https';
import { URL } from 'url';
import { mcpSearch } from './scripts/mcp.mjs';

// 解析命令行参数
const args = process.argv.slice(2);
if (args.length === 0) {
  console.log('用法: node m5-search.mjs <查询内容> [选项]');
  console.log('选项:');
  console.log('  --num <数量>       返回结果数量，默认1');
  console.log('  --filter <类型>    过滤类型: product/program/arduino/uiflow/esp-idf/esphome，默认product');
  console.log('  --chip             查询芯片相关文档');
  process.exit(1);
}

let query = '';
let num = 1;
let filter_type = 'product';
let is_chip = false;

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--num') {
    num = parseInt(args[++i]) || 1;
  } else if (args[i] === '--filter') {
    filter_type = args[++i] || 'product';
  } else if (args[i] === '--chip') {
    is_chip = true;
  } else {
    query += (query ? ' ' : '') + args[i];
  }
}

// 执行查询
console.log(`🔍 正在查询: ${query}`);
console.log(`⚙️  参数: num=${num}, filter=${filter_type}, is_chip=${is_chip}`);
console.log('='.repeat(80));

try {
  const result = await mcpSearch(query, { num, filter_type, is_chip });
  console.log('✅ 查询成功!');
  console.log('='.repeat(80));
  
  // 输出结果
  if (result && result.content && Array.isArray(result.content)) {
    result.content.forEach((item, idx) => {
      if (item.type === 'text') {
        console.log(item.text);
      }
    });
  } else {
    console.log(JSON.stringify(result, null, 2));
  }
  
  process.exit(0);
} catch (err) {
  console.error('❌ 查询失败:', err.message);
  process.exit(1);
}
