/**
 * 测试并调试 Alpha Vantage 历史数据
 */

import { AlphaVantageAPI } from './src/api/AlphaVantage.js';

console.log('🔍 调试 Alpha Vantage 历史数据\n');

const alphaVantage = new AlphaVantageAPI({
  apiKey: '9Z6PTPL7AB5M5DN3'
});

// 测试获取历史数据
console.log('📊 请求 TSLA 历史数据...');
const result = await alphaVantage.getHistory('TSLA', '1mo');

console.log('\n返回结果:');
console.log(JSON.stringify(result, null, 2));

if (result.success && result.data.quotes && result.data.quotes.length > 0) {
  console.log('\n✅ 数据格式正确');
  console.log(`第一条数据:`, result.data.quotes[0]);
} else {
  console.log('\n❌ 数据格式有问题');
}
