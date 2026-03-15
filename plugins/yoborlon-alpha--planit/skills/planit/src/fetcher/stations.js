'use strict';

/**
 * City → 12306 station codes mapping.
 * Each city can have multiple stations; first entry = preferred departure.
 * Codes sourced from 12306 station_name.js (official resource).
 */
const CITY_STATIONS = {
  '北京':   [{ code: 'VNP', name: '北京南站' }, { code: 'BJP', name: '北京站' }, { code: 'VAP', name: '北京西站' }],
  '上海':   [{ code: 'AOH', name: '上海虹桥站' }, { code: 'SHH', name: '上海站' }, { code: 'SNH', name: '上海南站' }],
  '杭州':   [{ code: 'HGH', name: '杭州东站' }, { code: 'HZH', name: '杭州站' }],
  '苏州':   [{ code: 'SZV', name: '苏州北站' }, { code: 'SZH', name: '苏州站' }],
  '南京':   [{ code: 'NJH', name: '南京南站' }, { code: 'NJG', name: '南京站' }],
  '成都':   [{ code: 'ICW', name: '成都东站' }, { code: 'ICD', name: '成都站' }],
  '西安':   [{ code: 'EAH', name: '西安北站' }, { code: 'XAY', name: '西安站' }],
  '广州':   [{ code: 'GZQ', name: '广州南站' }, { code: 'GZH', name: '广州站' }],
  '深圳':   [{ code: 'SZQ', name: '深圳北站' }, { code: 'SZX', name: '深圳站' }],
  '武汉':   [{ code: 'WHN', name: '武汉站' }, { code: 'WUH', name: '武昌站' }],
  '重庆':   [{ code: 'CQW', name: '重庆西站' }, { code: 'CQB', name: '重庆北站' }],
  '长沙':   [{ code: 'CSQ', name: '长沙南站' }, { code: 'CSN', name: '长沙站' }],
  '南昌':   [{ code: 'NCG', name: '南昌西站' }, { code: 'NNH', name: '南昌站' }],
  '合肥':   [{ code: 'HFH', name: '合肥南站' }, { code: 'HFW', name: '合肥站' }],
  '青岛':   [{ code: 'QDK', name: '青岛北站' }, { code: 'QDH', name: '青岛站' }],
  '济南':   [{ code: 'JNK', name: '济南西站' }, { code: 'JNA', name: '济南站' }],
  '天津':   [{ code: 'TJP', name: '天津南站' }, { code: 'TJH', name: '天津站' }],
  '郑州':   [{ code: 'ZZF', name: '郑州东站' }, { code: 'ZZH', name: '郑州站' }],
  '厦门':   [{ code: 'XMN', name: '厦门北站' }, { code: 'XMS', name: '厦门站' }],
  '福州':   [{ code: 'FZS', name: '福州南站' }, { code: 'FZH', name: '福州站' }],
  '南宁':   [{ code: 'NNZ', name: '南宁东站' }, { code: 'NNH', name: '南宁站' }],
  '桂林':   [{ code: 'GLL', name: '桂林北站' }, { code: 'GLH', name: '桂林站' }],
  '黄山':   [{ code: 'HHQ', name: '黄山北站' }],
  '张家界': [{ code: 'ZJJ', name: '张家界站' }],
  '丽江':   [{ code: 'LJG', name: '丽江站' }],
  '三亚':   [{ code: 'SYX', name: '三亚站' }],
};

/**
 * Get preferred departure station code for a city.
 * @param {string} city
 * @returns {{ code: string, name: string } | null}
 */
function getStation(city) {
  const stations = CITY_STATIONS[city];
  return stations ? stations[0] : null;
}

/**
 * Get all station codes for a city.
 */
function getAllStations(city) {
  return CITY_STATIONS[city] || [];
}

/**
 * Check if a city has known stations.
 */
function hasStation(city) {
  return !!CITY_STATIONS[city];
}

module.exports = { getStation, getAllStations, hasStation, CITY_STATIONS };
