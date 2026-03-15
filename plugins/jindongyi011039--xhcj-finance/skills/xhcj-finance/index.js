#!/usr/bin/env node

const { Command } = require('commander');
const axios = require('axios');

const program = new Command();

// 从环境变量获取API密钥
const apiKey = process.env['XHCJ_API_KEY'];

// 验证API密钥
if (!apiKey) {
  console.error('Error: XHCJ_API_KEY environment variable is not set');
  process.exit(1);
}

// 验证API密钥格式（假设API密钥是32位的十六进制字符串）
if (!/^xhcj_[0-9a-zA-Z]{32}$/.test(apiKey)) { 
  console.error('Error: Invalid XHCJ_API_KEY format');
  process.exit(1);
}

// 安全存储API密钥
const secureApiKey = apiKey;

// 安全日志记录函数
function secureLog(message) {
  // 替换API密钥为掩码
  return message.replace(new RegExp(secureApiKey, 'g'), '***API_KEY_MASKED***');
}

// 记录程序启动信息
console.log('Xinhua Finance API CLI tool started');
console.log(`API key loaded: ${secureLog(apiKey)} ✓`);
console.log('API client initialized: ✓');

// 创建axios实例
const apiClient = axios.create({
  baseURL: 'https://xhcj-h5-zg.cnfin.com/xhcj-bun/func/openclaw', // 假设的API基础URL
  headers: {
    'Authorization': `Bearer ${secureApiKey}`,  
    'Content-Type': 'application/json'
  }
});

program
  .name('xhcj-finance') 
  .description('Xinhua Finance API CLI tool')
  .version('1.0.0');

// 行情数据命令
program
  .command('market')
  .description('Query market data')
  .option('--symbol <symbol>', 'A股股票代码，如000001.SZ')
  .action(async (options) => {
    if (!options.symbol) {
      console.error('Error: --symbol is required');
      return;
    }

    try {
      const response = await apiClient.post('/finance-data', {
        path: 'real',
        params: {
          symbol: options.symbol
        }
      });
      console.log('Market data:', JSON.stringify(response.data.data, null, 2));
    } catch (error) {
      // 安全处理错误，避免API密钥泄露
      if (error.response) {
        console.error('Error fetching market data: API request failed with status', error.response.status);
      } else if (error.request) {
        console.error('Error fetching market data: No response received from server');
      } else {
        console.error('Error fetching market data:', error.message);
      }
    }
  });

// 行情Kline数据命令
program
  .command('kline')
  .description('Query market kline data')
  .option('--symbol <symbol>', 'A股股票代码，如000001.SZ')
  .action(async (options) => {
    if (!options.symbol) {
      console.error('Error: --symbol is required');
      return;
    }

    try {
      const response = await apiClient.post('/finance-data', {
        path: 'kline',
        params: {
          symbol: options.symbol
        }
      });
      console.log('Kline data:', JSON.stringify(response.data.data, null, 2));
    } catch (error) {
      // 安全处理错误，避免API密钥泄露
      if (error.response) {
        console.error('Error fetching kline data: API request failed with status', error.response.status);
      } else if (error.request) {
        console.error('Error fetching kline data: No response received from server');
      } else {
        console.error('Error fetching kline data:', error.message);
      }
    }
  });

// 股票代码查询命令
program
  .command('symbol')
  .description('Query stock symbol')
  .option('--name <name>', '股票名称模糊查询，如"中国平安"，也可以是股票代码如"601318"')
  .action(async (options) => {
    if (!options.name) {
      console.error('Error: --name is required');
      return;
    }

    try {
      const response = await apiClient.post('/finance-data', {
        path: 'query_code',
        params: {
          name: options.name
        }
      });
      console.log('Symbol data:', JSON.stringify(response.data.data, null, 2));
    } catch (error) {
      // 安全处理错误，避免API密钥泄露
      if (error.response) {
        console.error('Error fetching symbol data: API request failed with status', error.response.status);
      } else if (error.request) {
        console.error('Error fetching symbol data: No response received from server');
      } else {
        console.error('Error fetching symbol data:', error.message);
      }
    }
  });

// 资讯命令
program
  .command('news')
  .description('Get news')
  .option('--category <category>', '新闻资讯分类：1-股票 2-商品期货 3-外汇 4-债券 5-宏观 9-全部, default 9', '9') 
  .option('--limit <number>', 'Limit results, default 10, max 20', '10')
  .action(async (options) => {
    try {
      const response = await apiClient.post('/finance-data', {
        path: 'news', 
        params: {
          category: options.category,
          limit: options.limit
        }
      });
      console.log('News:', JSON.stringify(response.data.data, null, 2));
    } catch (error) {
      // 安全处理错误，避免API密钥泄露
      if (error.response) {
        console.error('Error fetching news: API request failed with status', error.response.status);
      } else if (error.request) {
        console.error('Error fetching news: No response received from server');
      } else {
        console.error('Error fetching news:', error.message);
      }
    }
  });

program.parse(process.argv);
