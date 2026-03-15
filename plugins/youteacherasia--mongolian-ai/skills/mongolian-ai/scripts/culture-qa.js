#!/usr/bin/env node

/**
 * 蒙古文化问答脚本
 * 基于毅金云 API 实现蒙古族文化、历史知识问答
 * 
 * 使用方法:
 *   node culture-qa.js "问题"
 */

const https = require('https');

// 配置
const API_KEY = process.env.MENGGUYU_API_KEY || '';
const API_BASE = 'https://api.mengguyu.cn';

/**
 * 调用文化问答 API
 * @param {string} question - 问题
 */
async function askCulture(question) {
  if (!API_KEY) {
    console.error('❌ 错误：请设置 MENGGUYU_API_KEY 环境变量');
    process.exit(1);
  }

  // TODO: 根据实际 API 文档调整请求格式
  const postData = JSON.stringify({
    question: question,
    category: 'culture', // 文化类
  });

  const options = {
    hostname: 'api.mengguyu.cn',
    port: 443,
    path: '/v1/culture/qa', // TODO: 确认实际 API 路径
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Length': Buffer.byteLength(postData),
    },
  };

  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        if (res.statusCode === 200) {
          try {
            const result = JSON.parse(data);
            resolve(result.answer || result.text || result);
          } catch (e) {
            resolve(data);
          }
        } else {
          reject(new Error(`API 请求失败：${res.statusCode} - ${data}`));
        }
      });
    });

    req.on('error', (e) => {
      reject(new Error(`请求错误：${e.message}`));
    });

    req.write(postData);
    req.end();
  });
}

/**
 * 解析命令行参数
 */
function parseArgs() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
    console.log(`
蒙古文化问答工具

用法:
  node culture-qa.js "问题"

示例:
  node culture-qa.js "蒙古族有哪些传统节日？"
  node culture-qa.js "成吉思汗是谁？"
  node culture-qa.js "那达慕大会是什么时候？"

环境变量:
  MENGGUYU_API_KEY  毅金云 API Key
`);
    process.exit(args.length === 0 ? 1 : 0);
  }

  return { question: args.join(' ') };
}

/**
 * 主函数
 */
async function main() {
  const config = parseArgs();

  try {
    console.log('🤔 思考中...');
    const result = await askCulture(config.question);
    console.log(`💡 回答：${result}`);
  } catch (error) {
    console.error(`❌ ${error.message}`);
    process.exit(1);
  }
}

// 运行
main();
