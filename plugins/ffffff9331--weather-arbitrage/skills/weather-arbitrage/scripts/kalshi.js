/**
 * Kalshi API 封装
 * 美国合法预测市场，CFTC监管
 */

const KALSHI_API = 'https://trading-api.kalshi.com/trade-api/v2';

/**
 * 获取天气相关市场
 */
async function getWeatherMarkets() {
  try {
    // Kalshi市场列表
    const response = await fetch(`${KALSHI_API}/markets?limit=100&status=open`);
    
    if (!response.ok) {
      console.log(`   Kalshi API返回 ${response.status}`);
      return [];
    }
    
    const text = await response.text();
    let data;
    
    try {
      data = JSON.parse(text);
    } catch (e) {
      console.log('   Kalshi API返回非JSON格式');
      return [];
    }
    
    const markets = data.markets || [];
    
    // 过滤天气相关
    const weatherKeywords = ['temperature', 'weather', 'high', 'low', 'degrees', 'fahrenheit', 'celsius'];
    
    const weatherMarkets = markets.filter(market => {
      const title = (market.title || '').toLowerCase();
      const question = (market.question || market.yes_sub_title || '').toLowerCase();
      const text = title + ' ' + question;
      return weatherKeywords.some(kw => text.includes(kw));
    });
    
    return weatherMarkets.map(market => ({
      ticker: market.ticker,
      title: market.title,
      question: market.question || market.yes_sub_title,
      yes_price: market.yes_bid || market.yes_ask,
      no_price: market.no_bid || market.no_ask,
      volume: market.volume,
      open_interest: market.open_interest,
      close_date: market.close_time || market.date_close,
      category: market.category
    }));
  } catch (error) {
    console.log('   Kalshi API失败:', error.message);
    return [];
  }
}

/**
 * 获取单个市场详情
 */
async function getMarketDetails(ticker) {
  try {
    const response = await fetch(`${KALSHI_API}/markets/${ticker}`);
    const market = await response.json();
    
    return {
      ticker: market.ticker,
      title: market.title,
      question: market.question || market.yes_sub_title,
      yes_price: market.yes_bid,
      no_price: market.no_bid,
      volume: market.volume,
      open_interest: market.open_interest,
      close_date: market.close_time,
      rules: market.rules,
      options: parseOptions(market)
    };
  } catch (error) {
    console.error('获取市场详情失败:', error.message);
    return null;
  }
}

/**
 * 解析市场选项
 */
function parseOptions(market) {
  const options = [];
  
  // Kalshi温度市场通常是区间
  // 例如: "HIGH-NYC-03MAR24-50" 表示纽约3月3日最高温50°F
  const ticker = market.ticker || '';
  const match = ticker.match(/HIGH-(\w+)-(\d+\w+)-(\d+)/);
  
  if (match) {
    options.push({
      city: match[1],
      date: match[2],
      temp_threshold: parseInt(match[3]),
      type: 'above_below'
    });
  }
  
  return options;
}

/**
 * 获取市场订单簿
 */
async function getOrderbook(ticker) {
  try {
    const response = await fetch(`${KALSHI_API}/markets/${ticker}/orderbook`);
    const data = await response.json();
    
    return {
      yes_bids: data.yes_bids || [],
      no_bids: data.no_bids || [],
      yes_asks: data.yes_asks || [],
      no_asks: data.no_asks || []
    };
  } catch (error) {
    console.error('获取订单簿失败:', error.message);
    return null;
  }
}

/**
 * 搜索温度市场
 */
async function searchTemperatureMarkets(city = null) {
  try {
    const markets = await getWeatherMarkets();
    
    // 过滤温度市场
    let tempMarkets = markets.filter(m => {
      const text = (m.title + ' ' + (m.question || '')).toLowerCase();
      return text.includes('temperature') || text.includes('high') || text.includes('low');
    });
    
    // 按城市过滤
    if (city) {
      tempMarkets = tempMarkets.filter(m => {
        const text = (m.title + ' ' + (m.question || '')).toLowerCase();
        return text.includes(city.toLowerCase());
      });
    }
    
    return tempMarkets;
  } catch (error) {
    console.error('搜索失败:', error.message);
    return [];
  }
}

module.exports = {
  getWeatherMarkets,
  getMarketDetails,
  getOrderbook,
  searchTemperatureMarkets
};
