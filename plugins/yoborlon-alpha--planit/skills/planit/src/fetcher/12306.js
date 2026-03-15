'use strict';

/**
 * 12306 Train Fetcher
 * Uses the public leftTicket/query endpoint — no API key required.
 * Falls back to mock data if the request fails.
 */

const https = require('https');
const { getStation } = require('./stations');
const cache = require('./cache');

const BASE_URL = 'https://kyfw.12306.cn';

// Seat type codes → human-readable names
const SEAT_TYPE_MAP = {
  O: '二等座',
  M: '一等座',
  P: '特等座',
  9: '商务座',
  6: '软卧',
  4: '软座',
  3: '硬卧',
  1: '硬座',
  F: '餐车',
};

/**
 * Perform an HTTPS GET and return parsed JSON.
 */
function httpsGet(url, headers = {}) {
  return new Promise((resolve, reject) => {
    const req = https.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'X-Requested-With': 'XMLHttpRequest',
        ...headers,
      },
      timeout: 8000,
    }, (res) => {
      const chunks = [];
      res.on('data', (c) => chunks.push(c));
      res.on('end', () => {
        try {
          resolve(JSON.parse(Buffer.concat(chunks).toString('utf8')));
        } catch (e) {
          reject(new Error(`JSON parse failed: ${e.message}`));
        }
      });
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('Request timed out')); });
  });
}

/**
 * Parse a single train row from 12306 response into a normalized object.
 * Each row is a pipe-delimited string with fixed field positions.
 *
 * Key field indices (0-based):
 *   3  = train_no (internal)
 *   4  = train number (G/D/K/Z/T...)
 *   6  = from station code
 *   7  = to station code
 *   8  = departure station code (start of segment)
 *   9  = arrival station code (end of segment)
 *   13 = departure time (HH:MM)
 *   14 = arrival time (HH:MM)
 *   15 = duration (HH:MM)
 *   26 = 无座 ticket count
 *   29 = 硬座
 *   28 = 软座
 *   33 = 硬卧
 *   23 = 软卧
 *   21 = 高级软卧
 *   30 = 二等座
 *   31 = 一等座
 *   32 = 特等座
 *   25 = 动卧
 *   9  = remark
 */
function parseTrainRow(row, fromCity, toCity, date) {
  const f = row.split('|');
  const trainNo = f[3];
  const trainCode = f[4];         // e.g. G7356
  const departTime = f[13];      // HH:MM
  const arriveTime = f[14];      // HH:MM
  const durationStr = f[15];     // HH:MM
  const fromStationName = f[6];
  const toStationName = f[7];

  if (!trainCode || !departTime || !arriveTime) return null;

  // Duration in minutes
  const [dh, dm] = durationStr.split(':').map(Number);
  const duration = dh * 60 + (dm || 0);

  // Determine train type
  const prefix = trainCode[0];
  const typeMap = {
    G: 'high_speed', D: 'high_speed', C: 'high_speed',
    Z: 'express', T: 'express', K: 'express',
  };
  const subtype = typeMap[prefix] || 'regular';
  const typeName = subtype === 'high_speed' ? '高铁' : prefix === 'Z' ? '直达特快' : prefix === 'T' ? '特快' : '快车';

  // Seat availability (ticket count string or number)
  const seatTypes = [];
  const addSeat = (label, idx) => {
    const val = f[idx];
    if (val && val !== '' && val !== '无' && val !== '--') {
      seatTypes.push({ type: label, available: val === '有' ? '有票' : val });
    }
  };
  addSeat('二等座', 30);
  addSeat('一等座', 31);
  addSeat('特等座', 32);
  addSeat('商务座', 25);  // 动卧/商务混用
  addSeat('软卧', 23);
  addSeat('硬卧', 33);
  addSeat('软座', 28);
  addSeat('硬座', 29);
  addSeat('无座', 26);

  return {
    type: subtype === 'high_speed' ? 'train' : 'train',
    subtype,
    name: typeName,
    trainNo: trainCode,
    internalNo: trainNo,
    from: fromCity,
    to: toCity,
    fromStation: fromStationName,
    toStation: toStationName,
    departureTime: departTime,
    arrivalTime: arriveTime,
    duration,
    durationLabel: durationStr,
    date,
    seatTypes,
    source: '12306',
  };
}

/**
 * Fetch trains from 12306 for a given route and date.
 * Results are cached for 30 minutes.
 *
 * @param {string} fromCity - e.g. '上海'
 * @param {string} toCity   - e.g. '杭州'
 * @param {string} date     - 'YYYY-MM-DD'
 * @returns {Promise<Array>} array of normalized train objects
 */
async function fetchTrains(fromCity, toCity, date) {
  const fromStation = getStation(fromCity);
  const toStation   = getStation(toCity);

  if (!fromStation || !toStation) {
    return { trains: [], error: `未找到站点代码：${!fromStation ? fromCity : toCity}` };
  }

  const cacheKey = cache.key('12306', fromStation.code, toStation.code, date);
  const cached = cache.get(cacheKey);
  if (cached) {
    return { trains: cached, fromCache: true };
  }

  const url = `${BASE_URL}/otn/leftTicket/query?leftTicketDTO.train_date=${date}&leftTicketDTO.from_station=${fromStation.code}&leftTicketDTO.to_station=${toStation.code}&purpose_codes=ADULT`;

  let data;
  try {
    data = await httpsGet(url);
  } catch (err) {
    return { trains: [], error: `12306 请求失败: ${err.message}` };
  }

  if (!data?.data?.result || !Array.isArray(data.data.result)) {
    return { trains: [], error: '12306 返回数据格式异常' };
  }

  const trains = data.data.result
    .map((row) => parseTrainRow(row, fromCity, toCity, date))
    .filter(Boolean)
    .sort((a, b) => a.departureTime.localeCompare(b.departureTime));

  // Cache successful results
  cache.set(cacheKey, trains, cache.TTL.trains);

  return { trains, fromStation, toStation };
}

/**
 * High-level: get top N train options for a route.
 * Filters to high-speed trains first; falls back to all trains.
 *
 * @param {string} fromCity
 * @param {string} toCity
 * @param {string} date
 * @param {number} limit
 * @returns {Promise<{ trains: Array, meta: object }>}
 */
async function getTrainOptions(fromCity, toCity, date, limit = 4) {
  const result = await fetchTrains(fromCity, toCity, date);

  if (result.error) {
    return { trains: [], error: result.error, source: '12306' };
  }

  const all = result.trains;
  // Prefer high-speed
  const highSpeed = all.filter((t) => t.subtype === 'high_speed');
  const pool = highSpeed.length > 0 ? highSpeed : all;

  // Pick morning, midday, afternoon, evening options
  const picked = pickDiverseTimes(pool, limit);

  return {
    trains: picked,
    total: all.length,
    highSpeedCount: highSpeed.length,
    fromCache: result.fromCache || false,
    source: '12306',
    fromStation: result.fromStation,
    toStation: result.toStation,
  };
}

/**
 * Pick up to N trains spread across different departure time slots.
 */
function pickDiverseTimes(trains, n) {
  if (trains.length <= n) return trains;
  const slots = [
    (t) => t.departureTime < '10:00',  // morning
    (t) => t.departureTime >= '10:00' && t.departureTime < '13:00', // late morning
    (t) => t.departureTime >= '13:00' && t.departureTime < '17:00', // afternoon
    (t) => t.departureTime >= '17:00', // evening
  ];
  const picked = [];
  for (const slot of slots) {
    if (picked.length >= n) break;
    const match = trains.find((t) => slot(t) && !picked.includes(t));
    if (match) picked.push(match);
  }
  // Fill remaining from front
  for (const t of trains) {
    if (picked.length >= n) break;
    if (!picked.includes(t)) picked.push(t);
  }
  return picked;
}

module.exports = { getTrainOptions, fetchTrains };
