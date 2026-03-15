'use strict';

/**
 * Intent Parser
 * Extracts destination, date, traveler group, and budget from natural language input.
 */

// Known cities and their aliases
const CITY_ALIASES = {
  '杭州': '杭州',
  '上海': '上海',
  '北京': '北京',
  '苏州': '苏州',
  '南京': '南京',
  '成都': '成都',
  '西安': '西安',
  '广州': '广州',
  '深圳': '深圳',
  '厦门': '厦门',
  '青岛': '青岛',
  '丽江': '丽江',
  '三亚': '三亚',
  '桂林': '桂林',
  '武汉': '武汉',
  '重庆': '重庆',
  '张家界': '张家界',
  '黄山': '黄山',
  '西湖': '杭州',
};

// Day-of-week mapping (0=Sunday)
const WEEKDAY_MAP = {
  '周日': 0, '星期日': 0, '周天': 0,
  '周一': 1, '星期一': 1,
  '周二': 2, '星期二': 2,
  '周三': 3, '星期三': 3,
  '周四': 4, '星期四': 4,
  '周五': 5, '星期五': 5,
  '周六': 6, '星期六': 6,
};

// Relative time keywords
const RELATIVE_TIME = {
  '今天': 0,
  '明天': 1,
  '后天': 2,
  '大后天': 3,
  '下周': 7,
  '这个周末': null, // computed
  '这周末': null,
  '下个周末': null,
  '下周末': null,
};

// Traveler group patterns
const GROUP_PATTERNS = [
  { pattern: /爸妈|父母|老人|长辈|爷爷|奶奶|外公|外婆/, group: 'elderly', label: '老人出行' },
  { pattern: /孩子|小孩|宝宝|儿童|娃|宝贝/, group: 'family_kids', label: '亲子出行' },
  { pattern: /朋友|闺蜜|基友|伙伴|同学/, group: 'friends', label: '朋友出行' },
  { pattern: /老婆|老公|对象|女朋友|男朋友|蜜月|恋人|约会/, group: 'couple', label: '情侣出行' },
  { pattern: /同事|团队|公司|出差/, group: 'business', label: '商务出行' },
  { pattern: /一个人|独自|单人|单独/, group: 'solo', label: '独自出行' },
  { pattern: /全家|家人|家庭/, group: 'family', label: '家庭出行' },
];

// Budget patterns
const BUDGET_PATTERNS = [
  { pattern: /不要太贵|便宜|经济|实惠|省钱|穷游|低价/, budget: 'budget', label: '经济实惠' },
  { pattern: /奢华|豪华|高端|五星|顶级|最好的/, budget: 'luxury', label: '豪华出行' },
  { pattern: /中等|适中|一般|普通/, budget: 'mid', label: '中等消费' },
];

// Duration patterns (number of days)
const DURATION_PATTERNS = [
  { pattern: /(\d+)\s*天/, extract: (m) => parseInt(m[1]) },
  { pattern: /(\d+)\s*日/, extract: (m) => parseInt(m[1]) },
  { pattern: /一天/, extract: () => 1 },
  { pattern: /两天|2天/, extract: () => 2 },
  { pattern: /三天|3天/, extract: () => 3 },
  { pattern: /四天|4天/, extract: () => 4 },
  { pattern: /五天|5天/, extract: () => 5 },
  { pattern: /周末/, extract: () => 2 },
  { pattern: /长假|黄金周/, extract: () => 7 },
];

/**
 * Compute the next occurrence of a given weekday from today.
 * @param {number} targetDay - 0-6
 * @returns {Date}
 */
function nextWeekday(targetDay) {
  const now = new Date();
  const current = now.getDay();
  let diff = targetDay - current;
  if (diff <= 0) diff += 7; // always future
  const result = new Date(now);
  result.setDate(now.getDate() + diff);
  result.setHours(0, 0, 0, 0);
  return result;
}

/**
 * Compute upcoming Saturday (or Sunday if today is Saturday).
 */
function nextWeekend(offset = 0) {
  const now = new Date();
  const day = now.getDay();
  // Days until Saturday
  let daysUntilSat = (6 - day + 7) % 7;
  if (daysUntilSat === 0) daysUntilSat = 7; // next week's Saturday
  const sat = new Date(now);
  sat.setDate(now.getDate() + daysUntilSat + offset * 7);
  sat.setHours(0, 0, 0, 0);
  return sat;
}

/**
 * Format a Date as YYYY-MM-DD
 */
function formatDate(d) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

/**
 * Parse the departure date from the input text.
 * Returns { date: 'YYYY-MM-DD', label: string } or null.
 */
function parseDate(text) {
  const now = new Date();
  now.setHours(0, 0, 0, 0);

  // Relative keywords
  for (const [keyword, offsetDays] of Object.entries(RELATIVE_TIME)) {
    if (!text.includes(keyword)) continue;
    if (keyword === '这个周末' || keyword === '这周末') {
      const d = nextWeekend(0);
      return { date: formatDate(d), label: '这个周末' };
    }
    if (keyword === '下个周末' || keyword === '下周末') {
      const d = nextWeekend(1);
      return { date: formatDate(d), label: '下个周末' };
    }
    if (offsetDays !== null) {
      const d = new Date(now);
      d.setDate(now.getDate() + offsetDays);
      return { date: formatDate(d), label: keyword };
    }
  }

  // Weekday keywords
  for (const [keyword, dayNum] of Object.entries(WEEKDAY_MAP)) {
    if (text.includes(keyword)) {
      const d = nextWeekday(dayNum);
      return { date: formatDate(d), label: keyword };
    }
  }

  // Explicit date patterns: MM月DD日 or M/D
  const mdMatch = text.match(/(\d{1,2})月(\d{1,2})[日号]/);
  if (mdMatch) {
    const d = new Date(now.getFullYear(), parseInt(mdMatch[1]) - 1, parseInt(mdMatch[2]));
    if (d < now) d.setFullYear(d.getFullYear() + 1);
    return { date: formatDate(d), label: `${mdMatch[1]}月${mdMatch[2]}日` };
  }

  // Default: this coming weekend
  const weekend = nextWeekend(0);
  return { date: formatDate(weekend), label: '即将到来的周末' };
}

/**
 * Parse traveler group from text.
 */
function parseGroup(text) {
  for (const { pattern, group, label } of GROUP_PATTERNS) {
    if (pattern.test(text)) {
      return { group, label };
    }
  }
  return { group: 'general', label: '普通出行' };
}

/**
 * Parse budget preference from text.
 */
function parseBudget(text) {
  for (const { pattern, budget, label } of BUDGET_PATTERNS) {
    if (pattern.test(text)) {
      return { budget, label };
    }
  }
  return { budget: 'mid', label: '中等消费' };
}

/**
 * Parse trip duration from text.
 */
function parseDuration(text) {
  for (const { pattern, extract } of DURATION_PATTERNS) {
    const m = text.match(pattern);
    if (m) return extract(m);
  }
  return 2; // default 2 days
}

/**
 * Parse destination from text.
 * @returns {string|null} city name
 */
function parseDestination(text) {
  for (const [alias, city] of Object.entries(CITY_ALIASES)) {
    if (text.includes(alias)) return city;
  }
  return null;
}

/**
 * Main parse function.
 * @param {string} text - User natural language input
 * @param {string} originCity - User's home city
 * @returns {object} Parsed intent
 */
function parse(text, originCity = '上海') {
  const destination = parseDestination(text);
  const dateInfo = parseDate(text);
  const groupInfo = parseGroup(text);
  const budgetInfo = parseBudget(text);
  const duration = parseDuration(text);

  return {
    destination,
    origin: originCity,
    departureDate: dateInfo.date,
    departureDateLabel: dateInfo.label,
    duration,
    returnDate: computeReturnDate(dateInfo.date, duration),
    group: groupInfo.group,
    groupLabel: groupInfo.label,
    budget: budgetInfo.budget,
    budgetLabel: budgetInfo.label,
    rawText: text,
  };
}

function computeReturnDate(departureDateStr, duration) {
  const d = new Date(departureDateStr);
  d.setDate(d.getDate() + duration - 1);
  return formatDate(d);
}

module.exports = { parse, formatDate };
