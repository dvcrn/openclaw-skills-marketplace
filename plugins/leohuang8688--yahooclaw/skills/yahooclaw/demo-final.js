/**
 * YahooClaw 快速演示
 * 展示核心功能
 */

import yahooclaw from './src/index.js';

console.log('🦞 YahooClaw 快速演示\n');
console.log('=' .repeat(60));

// 演示 1: 股价查询
console.log('\n📈 1. 股价查询（AAPL, TSLA, NVDA）');
const stocks = ['AAPL', 'TSLA', 'NVDA'];

for (const symbol of stocks) {
  try {
    const quote = await yahooclaw.getQuote(symbol);
    if (quote.success) {
      console.log(`✅ ${symbol}: $${quote.data.price} (${quote.data.change > 0 ? '+' : ''}${quote.data.changePercent}%)`);
    } else {
      console.log(`⚠️  ${symbol}: 暂时无法获取数据`);
    }
  } catch (error) {
    console.log(`⚠️  ${symbol}: ${error.message}`);
  }
}

// 演示 2: 技术指标
console.log('\n📊 2. 技术指标分析（NVDA）');
try {
  const tech = await yahooclaw.getTechnicalIndicators('NVDA', '1mo', ['MA', 'RSI']);
  if (tech.success) {
    console.log(`✅ NVDA 技术分析:`);
    if (tech.data.indicators.MA?.MA5) {
      console.log(`   MA5: $${tech.data.indicators.MA.MA5.value} (${tech.data.indicators.MA.MA5.trend})`);
    }
    if (tech.data.indicators.RSI?.RSI14) {
      console.log(`   RSI: ${tech.data.indicators.RSI.RSI14} (${tech.data.indicators.RSI.signal})`);
    }
    if (tech.data.analysis) {
      console.log(`   信号：${tech.data.analysis.signal} (${tech.data.analysis.confidence}%)`);
    }
  } else {
    console.log(`⚠️  暂时无法获取技术指标`);
  }
} catch (error) {
  console.log(`⚠️  错误：${error.message}`);
}

// 演示 3: 新闻聚合
console.log('\n📰 3. 新闻聚合（MSFT）');
try {
  const news = await yahooclaw.getNews('MSFT', { limit: 3, sentiment: true });
  if (news.success) {
    console.log(`✅ MSFT: ${news.data.news.length} 条新闻`);
    console.log(`   整体情感：${news.data.overallSentiment}`);
    console.log(`   利好：${news.data.sentimentStats.positive} | 利空：${news.data.sentimentStats.negative}`);
  } else {
    console.log(`⚠️  暂时无法获取新闻`);
  }
} catch (error) {
  console.log(`⚠️  错误：${error.message}`);
}

console.log('\n' + '='.repeat(60));
console.log('✅ 演示完成！');
console.log('\n💡 提示:');
console.log('   - Yahoo Finance 限流时自动切换到 Alpha Vantage');
console.log('   - 缓存功能减少 API 调用（5 分钟 TTL）');
console.log('   - 配置 API Key 获得更高限额：ALPHA_VANTAGE_API_KEY');
