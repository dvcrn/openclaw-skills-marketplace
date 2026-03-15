/**
 * Polymarket API 封装
 * 获取天气预测市场数据
 */

const POLYMARKET_CLOB_API = 'https://clob.polymarket.com';

/**
 * 获取天气相关的预测市场（活跃市场）
 */
async function getWeatherMarkets() {
  try {
    // 只获取活跃、未关闭的市场
    const response = await fetch(`${POLYMARKET_CLOB_API}/markets?closed=false&active=true&limit=100`);
    const data = await response.json();
    
    // 处理不同的数据格式
    let markets = [];
    if (Array.isArray(data)) {
      markets = data;
    } else if (data && Array.isArray(data.data)) {
      markets = data.data;
    } else if (data && Array.isArray(data.markets)) {
      markets = data.markets;
    }
    
    // 过滤天气相关市场
    const weatherKeywords = ['temperature', 'temp', 'weather', 'rain', 'snow', 'climate', 'celsius', 'fahrenheit', '°F', '°C', 'highest', 'lowest'];
    
    const weatherMarkets = markets.filter(market => {
      const text = (market.question || market.title || market.name || '').toLowerCase();
      return weatherKeywords.some(kw => text.includes(kw.toLowerCase()));
    });
    
    return weatherMarkets.map(market => ({
      condition_id: market.condition_id || market.id,
      question: market.question || market.title,
      title: market.title,
      volume: market.volume || market.total_volume,
      outcomes: market.outcomes || market.tokens?.map(t => t.outcome),
      active: market.active !== false
    }));
  } catch (error) {
    console.error('获取市场失败:', error.message);
    return [];
  }
}

/**
 * 获取单个市场的赔率
 */
async function getMarketOdds(conditionId) {
  try {
    // 获取市场详情
    const marketResponse = await fetch(`${POLYMARKET_CLOB_API}/markets/${conditionId}`);
    const market = await marketResponse.json();
    
    // 获取订单簿（赔率）
    const orderbookResponse = await fetch(`${POLYMARKET_CLOB_API}/book?condition_id=${conditionId}`);
    const orderbook = await orderbookResponse.json();
    
    // 解析赔率
    const odds = [];
    
    if (orderbook && orderbook.assets) {
      for (const asset of orderbook.assets) {
        const bestBid = asset.bids?.[0];
        if (bestBid) {
          odds.push({
            outcome: asset.outcome || asset.token_id,
            probability: Math.round(parseFloat(bestBid.price) * 100),
            price: parseFloat(bestBid.price),
            token_id: asset.token_id
          });
        }
      }
    }
    
    // 如果没有orderbook，尝试从market解析
    if (odds.length === 0 && market.outcome_prices) {
      for (let i = 0; i < (market.outcomes || []).length; i++) {
        odds.push({
          outcome: market.outcomes[i],
          probability: Math.round(parseFloat(market.outcome_prices[i]) * 100),
          price: parseFloat(market.outcome_prices[i])
        });
      }
    }
    
    return {
      condition_id: conditionId,
      question: market.question || market.title,
      title: market.title,
      odds: odds,
      outcomes: market.outcomes,
      volume: market.volume
    };
  } catch (error) {
    console.error('获取赔率失败:', error.message);
    return {
      condition_id: conditionId,
      question: 'Unknown',
      odds: []
    };
  }
}

/**
 * 搜索特定关键词的市场
 */
async function searchMarkets(keyword) {
  try {
    const response = await fetch(`${POLYMARKET_CLOB_API}/markets?keyword=${encodeURIComponent(keyword)}`);
    const data = await response.json();
    return data || [];
  } catch (error) {
    console.error('搜索失败:', error.message);
    return [];
  }
}

/**
 * 通过事件slug获取市场详情
 */
async function getMarketBySlug(slug) {
  try {
    // 尝试从events API获取
    const eventsResponse = await fetch(`${POLYMARKET_CLOB_API}/events?slug=${slug}`);
    const eventsData = await eventsResponse.json();
    
    if (eventsData && eventsData.length > 0) {
      const event = eventsData[0];
      return {
        condition_id: event.condition_id,
        question: event.title || event.question,
        title: event.title,
        odds: parseEventOdds(event),
        outcomes: event.outcomes,
        volume: event.volume
      };
    }
    
    // 回退到markets API
    const marketsResponse = await fetch(`${POLYMARKET_CLOB_API}/markets?slug=${slug}`);
    const marketsData = await marketsResponse.json();
    
    if (marketsData && marketsData.data && marketsData.data.length > 0) {
      const market = marketsData.data[0];
      return {
        condition_id: market.condition_id,
        question: market.question || market.title,
        title: market.title,
        odds: parseMarketOdds(market),
        outcomes: market.tokens?.map(t => t.outcome),
        volume: market.volume
      };
    }
    
    return null;
  } catch (error) {
    console.error('获取市场失败:', error.message);
    return null;
  }
}

/**
 * 解析事件赔率
 */
function parseEventOdds(event) {
  const odds = [];
  
  if (event.markets && event.markets.length > 0) {
    for (const market of event.markets) {
      if (market.tokens) {
        for (const token of market.tokens) {
          odds.push({
            outcome: token.outcome,
            probability: Math.round(parseFloat(token.price || 0) * 100),
            price: parseFloat(token.price || 0),
            token_id: token.token_id
          });
        }
      }
    }
  }
  
  return odds;
}

/**
 * 解析市场赔率
 */
function parseMarketOdds(market) {
  const odds = [];
  
  if (market.tokens) {
    for (const token of market.tokens) {
      odds.push({
        outcome: token.outcome,
        probability: Math.round(parseFloat(token.price || 0) * 100),
        price: parseFloat(token.price || 0),
        token_id: token.token_id
      });
    }
  }
  
  return odds;
}

/**
 * 获取今天/明天的温度市场
 */
async function getTemperatureMarkets(city = null, date = null) {
  try {
    const today = new Date();
    const dateStr = date || `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
    
    // 构建搜索关键词
    const keywords = city 
      ? [`${city.toLowerCase()}`, 'temperature', dateStr.replace(/-/g, ' ')]
      : ['highest temperature', dateStr.replace(/-/g, ' ')];
    
    // 获取活跃市场
    const response = await fetch(`${POLYMARKET_CLOB_API}/markets?closed=false&active=true&limit=200`);
    const data = await response.json();
    
    let markets = data?.data || data || [];
    if (!Array.isArray(markets)) markets = [];
    
    // 过滤温度市场
    const tempMarkets = markets.filter(market => {
      const question = (market.question || market.title || '').toLowerCase();
      return question.includes('temperature') && 
             (question.includes('highest') || question.includes('lowest')) &&
             !market.closed;
    }).map(market => ({
      condition_id: market.condition_id,
      question: market.question || market.title,
      slug: market.market_slug,
      outcomes: market.tokens?.map(t => ({
        outcome: t.outcome,
        probability: Math.round(parseFloat(t.price || 0) * 100)
      })),
      accepting_orders: market.accepting_order_timestamp !== null
    }));
    
    return tempMarkets;
  } catch (error) {
    console.error('获取温度市场失败:', error.message);
    return [];
  }
}

module.exports = {
  getWeatherMarkets,
  getMarketOdds,
  searchMarkets,
  getMarketBySlug,
  getTemperatureMarkets
};
