/**
 * YahooClaw 技能试用演示
 * 展示核心功能
 */

import yahooclaw from './src/index.js';

console.log('🦞 YahooClaw v0.0.2 技能试用\n');
console.log('=' .repeat(60));
console.log('功能演示：股价查询、技术指标、新闻聚合\n');

// 演示 1: 股价查询
console.log('📈 1. 实时股价查询');
console.log('-'.repeat(60));

const stocks = [
  { symbol: 'AAPL', name: 'Apple' },
  { symbol: 'TSLA', name: 'Tesla' },
  { symbol: 'NVDA', name: 'NVIDIA' },
  { symbol: 'MSFT', name: 'Microsoft' }
];

for (const stock of stocks) {
  try {
    const quote = await yahooclaw.getQuote(stock.symbol);
    if (quote.success) {
      const changeIcon = quote.data.change >= 0 ? '📈' : '📉';
      console.log(`${changeIcon} ${stock.name} (${stock.symbol})`);
      console.log(`   价格：$${quote.data.price.toFixed(2)}`);
      console.log(`   涨跌：${quote.data.change >= 0 ? '+' : ''}${quote.data.change.toFixed(2)} (${quote.data.changePercent.toFixed(2)}%)`);
      console.log(`   数据源：${quote.source || 'Unknown'}`);
      console.log('');
    } else {
      console.log(`⚠️  ${stock.name}: ${quote.message}\n`);
    }
  } catch (error) {
    console.log(`❌ ${stock.name}: ${error.message}\n`);
  }
}

// 演示 2: 技术指标分析
console.log('📊 2. 技术指标分析');
console.log('-'.repeat(60));

try {
  const tech = await yahooclaw.getTechnicalIndicators('NVDA', '1mo', ['MA', 'RSI', 'MACD']);
  
  if (tech.success) {
    console.log('🎯 NVIDIA (NVDA) 技术分析:\n');
    
    if (tech.data.indicators.MA) {
      console.log('移动平均线:');
      if (tech.data.indicators.MA.MA5) {
        console.log(`  MA5:  $${tech.data.indicators.MA.MA5.value} (${tech.data.indicators.MA.MA5.trend})`);
      }
      if (tech.data.indicators.MA.MA20) {
        console.log(`  MA20: $${tech.data.indicators.MA.MA20.value} (${tech.data.indicators.MA.MA20.trend})`);
      }
    }
    
    if (tech.data.indicators.RSI) {
      console.log('\n相对强弱指标:');
      console.log(`  RSI14: ${tech.data.indicators.RSI.RSI14} (${tech.data.indicators.RSI.signal})`);
    }
    
    if (tech.data.indicators.MACD) {
      console.log('\nMACD:');
      console.log(`  MACD 线：${tech.data.indicators.MACD.macdLine}`);
      console.log(`  信号线：${tech.data.indicators.MACD.signalLine || 'N/A'}`);
      console.log(`  趋势：${tech.data.indicators.MACD.trend}`);
      if (tech.data.indicators.MACD.crossover) {
        console.log(`  交叉：${tech.data.indicators.MACD.crossover}`);
      }
    }
    
    if (tech.data.analysis) {
      console.log('\n🎯 综合信号:');
      console.log(`  信号：${tech.data.analysis.signal}`);
      console.log(`  置信度：${tech.data.analysis.confidence}%`);
      console.log(`  建议：${tech.data.analysis.recommendation}`);
    }
  } else {
    console.log(`⚠️  暂时无法获取技术指标：${tech.message}`);
  }
} catch (error) {
  console.log(`❌ 错误：${error.message}`);
}

// 演示 3: 新闻聚合
console.log('\n\n📰 3. 新闻聚合');
console.log('-'.repeat(60));

try {
  const news = await yahooclaw.getNews('MSFT', { limit: 5, sentiment: true });
  
  if (news.success) {
    console.log(`📰 Microsoft (MSFT) 最新新闻:\n`);
    console.log(`条数：${news.data.news.length}`);
    console.log(`整体情感：${news.data.overallSentiment}`);
    console.log(`利好：${news.data.sentimentStats.positive} | 利空：${news.data.sentimentStats.negative} | 中性：${news.data.sentimentStats.neutral}\n`);
    
    if (news.data.news.length > 0) {
      news.data.news.forEach((item, index) => {
        const sentimentIcon = item.sentiment?.label === 'POSITIVE' ? '✅' : 
                             item.sentiment?.label === 'NEGATIVE' ? '❌' : '➖';
        console.log(`${index + 1}. ${sentimentIcon} ${item.title}`);
        console.log(`   来源：${item.publisher}`);
        console.log(`   情感：${item.sentiment?.label || 'N/A'} (得分：${item.sentiment?.score || 'N/A'})`);
        console.log('');
      });
    } else {
      console.log('⚠️  暂无新闻（可能是 API 限流）');
    }
  } else {
    console.log(`⚠️  暂时无法获取新闻：${news.message}`);
  }
} catch (error) {
  console.log(`❌ 错误：${error.message}`);
}

// 总结
console.log('=' .repeat(60));
console.log('✅ 演示完成！\n');
console.log('💡 使用说明:');
console.log('   1. 在 OpenClaw 对话中直接说:');
console.log('      "查询 AAPL 股价"');
console.log('      "分析 NVDA 技术指标"');
console.log('      "看看 MSFT 的新闻"');
console.log('');
console.log('   2. 或在代码中使用:');
console.log('      import yahooclaw from "./skills/yahooclaw/src/index.js";');
console.log('      const quote = await yahooclaw.getQuote("AAPL");');
console.log('');
console.log('⚠️  注意事项:');
console.log('   - Yahoo Finance 限流时自动切换到 Alpha Vantage');
console.log('   - Alpha Vantage 免费额度：500 次/天');
console.log('   - 缓存有效期：5 分钟');
console.log('=' .repeat(60));
