'use strict';

/**
 * Itinerary Orchestrator
 * Combines parsed intent + data + personalization into a timeline-format travel plan.
 */

const { getTransportOptions, getHotels, getAttractions } = require('./data');
const { getPreviousHotelBookings } = require('./storage');

/**
 * Budget tiers for hotel filtering.
 * budget -> max price per night
 */
const BUDGET_PRICE_LIMITS = {
  budget: 400,
  mid: 1200,
  luxury: Infinity,
};

/**
 * Filter and sort hotels by budget and personalization history.
 */
function rankHotels(hotels, budget, previouslyBookedIds) {
  const maxPrice = BUDGET_PRICE_LIMITS[budget] || BUDGET_PRICE_LIMITS.mid;

  // Filter by budget
  let filtered = hotels.filter((h) => h.pricePerNight <= maxPrice);
  if (filtered.length === 0) filtered = hotels; // fallback: show all if none match

  // Score: previously booked = 1000 bonus, then sort by rating desc
  const scored = filtered.map((h) => ({
    ...h,
    score: (previouslyBookedIds.includes(h.id) ? 1000 : 0) + h.rating * 10,
    previouslyBooked: previouslyBookedIds.includes(h.id),
  }));

  return scored.sort((a, b) => b.score - a.score);
}

/**
 * Pick attractions for each day, avoiding repeats.
 * Returns array of days, each with array of attraction objects.
 */
function planDays(attractions, group, duration) {
  const days = [];
  // Group-suitable first
  const suitable = attractions.filter(
    (a) => a.suitable.includes(group) || a.suitable.includes('general')
  );
  const rest = attractions.filter(
    (a) => !suitable.includes(a)
  );
  const pool = [...suitable, ...rest];

  let idx = 0;
  for (let d = 0; d < duration; d++) {
    const dayAttractions = [];
    let totalMinutes = 0;
    // Fill each day with ~5-6 hours of attractions
    while (idx < pool.length && totalMinutes < 360) {
      dayAttractions.push(pool[idx]);
      totalMinutes += pool[idx].duration;
      idx++;
    }
    days.push(dayAttractions);
  }

  return days;
}

/**
 * Format minutes as "X小时Y分钟"
 */
function formatDuration(minutes) {
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  if (h === 0) return `${m}分钟`;
  if (m === 0) return `${h}小时`;
  return `${h}小时${m}分钟`;
}

/**
 * Add YYYY-MM-DD + N days
 */
function addDays(dateStr, n) {
  const d = new Date(dateStr);
  d.setDate(d.getDate() + n);
  return d.toISOString().slice(0, 10);
}

/**
 * Generate group-specific tips.
 */
function getGroupTips(group) {
  const tips = {
    elderly: ['建议选无障碍设施酒店', '景区选步行量少的路线', '避免爬山或长时间站立', '携带常用药品'],
    family_kids: ['选有儿童设施的酒店', '景区购票注意儿童票', '备好防晒和驱蚊', '行程不宜过满'],
    couple: ['可安排一顿浪漫烛光晚餐', '选景色好的观景台', '日落时分最适合拍照'],
    friends: ['可安排夜生活或酒吧', '分摊费用提前规划', '团体票可能更划算'],
    business: ['选交通便利的商务酒店', '保留足够时间处理工作', '高铁商务座舒适'],
    solo: ['注意个人安全', '可加入当地旅游团', '独自旅行更灵活'],
    family: ['提前预订家庭房', '景区注意老人和小孩步行距离', '自驾更便利'],
    general: ['提前查看景区开放时间', '旺季提前预订', '备好雨具'],
  };
  return tips[group] || tips.general;
}

/**
 * Build a complete itinerary.
 * @param {object} intent - From parser.parse()
 * @param {string} userId - For personalization
 * @returns {Promise<object>} OpenClaw itinerary JSON
 */
async function buildItinerary(intent, userId) {
  const {
    destination,
    origin,
    departureDate,
    departureDateLabel,
    duration,
    returnDate,
    group,
    groupLabel,
    budget,
    budgetLabel,
    rawText,
  } = intent;

  // --- Transport (async: real 12306 data with mock fallback) ---
  const [transports, returnTransports] = await Promise.all([
    getTransportOptions(origin, destination, departureDate),
    getTransportOptions(destination, origin, returnDate),
  ]);

  // Use first transport as primary recommendation
  const primaryTransport = transports[0];
  const primaryReturnTransport = returnTransports[0];

  // --- Hotels + Attractions (async: proxy → Amap → mock) ---
  const [allHotels, allAttractions] = await Promise.all([
    getHotels(destination, userId),
    getAttractions(destination, group, userId),
  ]);
  const previouslyBooked = getPreviousHotelBookings(userId, destination);
  const rankedHotels = rankHotels(allHotels, budget, previouslyBooked);
  const dayPlans = planDays(allAttractions, group, duration);

  // --- Build Timeline ---
  const timeline = [];

  // Day 1: Departure + arrival + check-in
  timeline.push({
    day: 1,
    date: departureDate,
    label: `第1天 · 出发日`,
    events: [
      {
        time: primaryTransport.departureTime,
        type: 'transport',
        title: `乘坐${primaryTransport.name}前往${destination}`,
        description: `${origin} → ${destination}，车次/航班：${primaryTransport.trainNo || primaryTransport.flightNo || '-'}，历时约${formatDuration(primaryTransport.duration)}`,
        detail: primaryTransport,
        icon: primaryTransport.type === 'flight' ? '✈️' : '🚄',
      },
      {
        time: primaryTransport.arrivalTime,
        type: 'arrival',
        title: `抵达${destination}`,
        description: `到达${destination}，前往酒店办理入住`,
        icon: '📍',
      },
      {
        time: addTimeStr(primaryTransport.arrivalTime, 60),
        type: 'hotel_checkin',
        title: `入住酒店`,
        description: `推荐：${rankedHotels[0].name}（${rankedHotels[0].location}）¥${rankedHotels[0].pricePerNight}/晚`,
        detail: rankedHotels[0],
        icon: '🏨',
      },
      ...(dayPlans[0] && dayPlans[0].length > 0
        ? dayPlans[0].slice(0, 1).map((a) => ({
            time: addTimeStr(primaryTransport.arrivalTime, 150),
            type: 'attraction',
            title: `游览 ${a.name}`,
            description: `${a.category}｜建议游览${formatDuration(a.duration)}｜${a.tips}`,
            detail: a,
            icon: '🎯',
          }))
        : []),
      {
        time: '19:00',
        type: 'meal',
        title: `晚餐`,
        description: `品尝${destination}当地特色美食`,
        icon: '🍽️',
      },
    ],
  });

  // Middle days
  for (let d = 1; d < duration - 1; d++) {
    const dayAttractions = dayPlans[d] || [];
    timeline.push({
      day: d + 1,
      date: addDays(departureDate, d),
      label: `第${d + 1}天 · 深度游览`,
      events: [
        {
          time: '08:00',
          type: 'meal',
          title: '早餐',
          description: '享用酒店早餐或前往附近早餐店',
          icon: '☕',
        },
        ...dayAttractions.map((a, i) => ({
          time: addTimeStr('09:00', i * (a.duration + 30)),
          type: 'attraction',
          title: `游览 ${a.name}`,
          description: `${a.category}｜建议游览${formatDuration(a.duration)}${a.price > 0 ? `｜门票¥${a.price}` : '｜免费'}｜${a.tips}`,
          detail: a,
          icon: '🎯',
        })),
        {
          time: '12:30',
          type: 'meal',
          title: '午餐',
          description: `${destination}特色午餐`,
          icon: '🍜',
        },
        {
          time: '19:00',
          type: 'meal',
          title: '晚餐',
          description: '当地特色晚餐，享受夜晚氛围',
          icon: '🍽️',
        },
      ],
    });
  }

  // Last day: checkout + return
  if (duration > 1) {
    const lastDayAttractions = dayPlans[duration - 1] || [];
    timeline.push({
      day: duration,
      date: returnDate,
      label: `第${duration}天 · 返程日`,
      events: [
        {
          time: '08:00',
          type: 'meal',
          title: '早餐',
          description: '最后一顿当地早餐，细品慢享',
          icon: '☕',
        },
        ...lastDayAttractions.slice(0, 1).map((a) => ({
          time: '09:30',
          type: 'attraction',
          title: `游览 ${a.name}`,
          description: `${a.category}｜${a.tips}`,
          detail: a,
          icon: '🎯',
        })),
        {
          time: '12:00',
          type: 'hotel_checkout',
          title: '酒店退房',
          description: '整理行李，办理退房',
          icon: '🧳',
        },
        {
          time: primaryReturnTransport.departureTime,
          type: 'transport',
          title: `乘坐${primaryReturnTransport.name}返回${origin}`,
          description: `${destination} → ${origin}，历时约${formatDuration(primaryReturnTransport.duration)}`,
          detail: primaryReturnTransport,
          icon: primaryReturnTransport.type === 'flight' ? '✈️' : '🚄',
        },
        {
          time: primaryReturnTransport.arrivalTime,
          type: 'arrival',
          title: `抵达${origin}`,
          description: '安全到家，旅途圆满结束！',
          icon: '🏠',
        },
      ],
    });
  }

  // --- Build Summary ---
  const summary = {
    title: `${destination}${duration}日游`,
    subtitle: `${departureDateLabel}出发 · ${groupLabel} · ${budgetLabel}`,
    origin,
    destination,
    departureDate,
    returnDate,
    duration,
    group,
    groupLabel,
    budget,
    budgetLabel,
    estimatedCost: estimateCost(primaryTransport, rankedHotels[0], duration, group),
    tips: getGroupTips(group),
  };

  // --- Final Output (OpenClaw itinerary format) ---
  return {
    type: 'itinerary',
    version: '1.0',
    meta: {
      skillName: 'planit',
      generatedAt: new Date().toISOString(),
      userId,
      query: rawText,
    },
    summary,
    transport: {
      outbound: transports,
      inbound: returnTransports,
    },
    hotels: rankedHotels,
    timeline,
    actions: [
      {
        id: 'book_transport',
        label: '预订交通',
        type: 'booking',
        payload: { itemType: 'transport', item: primaryTransport },
      },
      {
        id: 'book_hotel',
        label: `预订 ${rankedHotels[0].name}`,
        type: 'booking',
        payload: {
          itemType: 'hotel',
          item: rankedHotels[0],
          destination,
          duration,
        },
      },
    ],
  };
}

/**
 * Estimate total cost for the trip.
 */
function estimateCost(transport, hotel, duration, group) {
  const personCount = { elderly: 2, family_kids: 3, couple: 2, friends: 4, business: 1, solo: 1, family: 4, general: 2 }[group] || 2;
  const transportCost = transport.price * personCount * 2; // round trip
  const hotelCost = hotel.pricePerNight * (duration - 1) * (personCount >= 3 ? 2 : 1); // double rooms
  const foodCost = 150 * personCount * duration; // 150/person/day
  const attractionCost = 200 * personCount; // rough estimate
  const total = transportCost + hotelCost + foodCost + attractionCost;
  return {
    transport: transportCost,
    hotel: hotelCost,
    food: foodCost,
    attractions: attractionCost,
    total,
    perPerson: Math.round(total / personCount),
    personCount,
    currency: 'CNY',
  };
}

/**
 * Add minutes to HH:MM string.
 */
function addTimeStr(timeStr, minutes) {
  const [h, m] = timeStr.split(':').map(Number);
  const total = h * 60 + m + minutes;
  const newH = Math.floor(total / 60) % 24;
  const newM = total % 60;
  return `${String(newH).padStart(2, '0')}:${String(newM).padStart(2, '0')}`;
}

module.exports = { buildItinerary };
