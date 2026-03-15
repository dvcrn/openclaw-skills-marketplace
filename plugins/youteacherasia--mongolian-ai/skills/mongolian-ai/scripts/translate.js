#!/usr/bin/env node

/**
 * 蒙语翻译脚本
 * 基于毅金云 API 实现蒙汉互译
 * 
 * 使用方法:
 *   node translate.js "文本" --from mn --to zh
 *   node translate.js "文本" --from zh --to mn
 */

const https = require('https');

// 配置
const API_KEY = process.env.MENGGUYU_API_KEY || '';
const API_BASE = 'https://api.mengguyu.cn'; // TODO: 确认实际 API 地址

// 语言代码映射
const LANG_MAP = {
  'mn': 'mongolian',
  'zh': 'chinese',
  'cn': 'chinese',
};

/**
 * 调用翻译 API
 * @param {string} text - 待翻译文本
 * @param {string} from - 源语言
 * @param {string} to - 目标语言
 */
async function translate(text, from = 'mn', to = 'zh') {
  if (!API_KEY) {
    console.error('❌ 错误：请设置 MENGGUYU_API_KEY 环境变量');
    console.error('   示例：export MENGGUYU_API_KEY="your_key"');
    process.exit(1);
  }

  const fromLang = LANG_MAP[from] || from;
  const toLang = LANG_MAP[to] || to;

  // TODO: 根据实际 API 文档调整请求格式
  const postData = JSON.stringify({
    text: text,
    from: fromLang,
    to: toLang,
  });

  const options = {
    hostname: 'api.mengguyu.cn', // TODO: 确认实际 API 主机
    port: 443,
    path: '/v1/translate', // TODO: 确认实际 API 路径
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
            resolve(result.translatedText || result.text || result);
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
  const config = {
    text: '',
    from: 'mn',
    to: 'zh',
  };

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--from' && args[i + 1]) {
      config.from = args[++i];
    } else if (args[i] === '--to' && args[i + 1]) {
      config.to = args[++i];
    } else if (args[i] === '--help' || args[i] === '-h') {
      console.log(`
蒙语翻译工具

用法:
  node translate.js "文本" [选项]

选项:
  --from <lang>  源语言 (mn=蒙古语，zh=中文) 默认：mn
  --to <lang>    目标语言 (mn=蒙古语，zh=中文) 默认：zh
  --help, -h     显示帮助

示例:
  node translate.js "ᠰᠠᠶᠢᠨ ᠪᠠᠶᠢᠨᠠ ᠤᠤ" --from mn --to zh
  node translate.js "你好" --from zh --to mn

环境变量:
  MENGGUYU_API_KEY  毅金云 API Key
`);
      process.exit(0);
    } else if (!args[i].startsWith('--')) {
      config.text = args[i];
    }
  }

  if (!config.text) {
    console.error('❌ 错误：请提供要翻译的文本');
    console.error('使用 --help 查看帮助');
    process.exit(1);
  }

  return config;
}

/**
 * 主函数
 */
async function main() {
  const config = parseArgs();

  try {
    console.log(`🔄 翻译中... (${config.from} → ${config.to})`);
    const result = await translate(config.text, config.from, config.to);
    console.log(`✅ 翻译结果：${result}`);
  } catch (error) {
    console.error(`❌ ${error.message}`);
    process.exit(1);
  }
}

// 运行
main();
