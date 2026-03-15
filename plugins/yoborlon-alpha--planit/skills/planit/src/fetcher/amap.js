'use strict';

/**
 * Amap (高德) POI Fetcher
 * REST API v3 — key read from local config, never hardcoded.
 *
 * Fetches:
 *   - Hotels (type 100100) for a city
 *   - Attractions (type 110000) for a city
 */

const https = require('https');
const { getAmapKey } = require('./config');
const cache = require('./cache');

const BASE = 'https://restapi.amap.com/v3/place/text';

// POI type codes
const POI_TYPE = {
  hotel:      '100100',  // 宾馆酒店
  attraction: '110000',  // 风景名胜
  food:       '050000',  // 餐饮服务
};

// Star rating keywords → stars number
const STAR_KEYWORDS = [
  { re: /五星|5星|豪华/, stars: 5 },
  { re: /四星|4星|高档/, stars: 4 },
  { re: /三星|3星|舒适/, stars: 3 },
  { re: /二星|2星|经济/, stars: 2 },
];

function guessStars(name, type_desc = '') {
  const text = name + type_desc;
  for (const { re, stars } of STAR_KEYWORDS) {
    if (re.test(text)) return stars;
  }
  return 3; // default
}

function guessPrice(stars) {
  return { 5: 1200, 4: 600, 3: 350, 2: 180, 1: 100 }[stars] || 300;
}

/**
 * Perform HTTPS GET and return parsed JSON body.
 */
function get(url) {
  return new Promise((resolve, reject) => {
    const req = https.get(url, {
      headers: { 'User-Agent': 'PlanIt/1.0' },
      timeout: 8000,
    }, (res) => {
      const chunks = [];
      res.on('data', (c) => chunks.push(c));
      res.on('end', () => {
        try { resolve(JSON.parse(Buffer.concat(chunks).toString('utf8'))); }
        catch (e) { reject(new Error(`JSON parse error: ${e.message}`)); }
      });
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('timeout')); });
  });
}

/**
 * Search Amap POI.
 */
async function searchPOI(city, keywords, types, page = 1) {
  const key = getAmapKey();
  if (!key) throw new Error('Amap key not configured');

  const params = new URLSearchParams({
    key,
    keywords,
    city,
    types,
    offset: '20',
    page: String(page),
    extensions: 'all',
    output: 'JSON',
    citylimit: 'true',
  });

  const data = await get(`${BASE}?${params}`);
  if (data.status !== '1') throw new Error(`Amap API error: ${data.info}`);
  return data.pois || [];
}

/**
 * Fetch hotels for a city from Amap.
 * Returns normalized hotel objects.
 */
async function fetchHotels(city, limit = 10) {
  const cacheKey = cache.key('amap_hotels', city);
  const cached = cache.get(cacheKey);
  if (cached) return { hotels: cached, fromCache: true };

  const pois = await searchPOI(city, '', POI_TYPE.hotel);
  // Sort by rating desc (biz_ext.rating is a string like "4.5")
  pois.sort((a, b) => {
    const ra = parseFloat(a.biz_ext?.rating || '0');
    const rb = parseFloat(b.biz_ext?.rating || '0');
    return rb - ra;
  });

  const hotels = pois.slice(0, limit).map((p, i) => {
    const stars = guessStars(p.name, p.type);
    const rating = parseFloat(p.biz_ext?.rating || '0') || (4.0 + Math.random() * 0.8);
    return {
      id: `amap_${p.id}`,
      name: p.name,
      stars,
      location: p.adname || city,
      address: p.address || '',
      tags: (p.type || '').split(';').filter(Boolean).slice(0, 3),
      pricePerNight: guessPrice(stars),
      rating: Math.round(rating * 10) / 10,
      features: buildFeatures(p),
      tel: p.tel || '',
      location_xy: p.location || '',
      source: 'amap',
    };
  });

  cache.set(cacheKey, hotels, cache.TTL.hotels);
  return { hotels, fromCache: false };
}

/**
 * Fetch attractions for a city from Amap.
 * Returns normalized attraction objects.
 */
async function fetchAttractions(city, limit = 10) {
  const cacheKey = cache.key('amap_attractions', city);
  const cached = cache.get(cacheKey);
  if (cached) return { attractions: cached, fromCache: true };

  const pois = await searchPOI(city, '景区 公园 博物馆', POI_TYPE.attraction);
  pois.sort((a, b) => {
    const ra = parseFloat(a.biz_ext?.rating || '0');
    const rb = parseFloat(b.biz_ext?.rating || '0');
    return rb - ra;
  });

  const attractions = pois.slice(0, limit).map((p, i) => {
    const price = parseInt(p.biz_ext?.cost || '0', 10) || 0;
    return {
      id: `amap_${p.id}`,
      name: p.name,
      category: mapCategory(p.type),
      duration: 120,                          // default 2h; no API field
      price,
      tags: (p.type || '').split(';').filter(Boolean).slice(0, 3),
      suitable: ['general', 'family', 'couple', 'elderly', 'friends'],
      tips: p.address ? `位于 ${p.address}` : '',
      tel: p.tel || '',
      location_xy: p.location || '',
      source: 'amap',
    };
  });

  cache.set(cacheKey, attractions, cache.TTL.attractions);
  return { attractions, fromCache: false };
}

function buildFeatures(poi) {
  const feats = [];
  if (poi.biz_ext?.parking_type) feats.push('停车场');
  if (poi.tel) feats.push('可电话预约');
  if (poi.address) feats.push(poi.adname || '');
  return feats.filter(Boolean).slice(0, 4);
}

function mapCategory(typeStr = '') {
  if (/博物馆/.test(typeStr)) return '博物馆';
  if (/公园/.test(typeStr)) return '公园';
  if (/寺|庙|教堂/.test(typeStr)) return '宗教/文化';
  if (/古迹|遗址/.test(typeStr)) return '历史/文化';
  if (/山|峰|谷/.test(typeStr)) return '自然';
  if (/湖|江|海|河/.test(typeStr)) return '自然/水域';
  return '景区';
}

module.exports = { fetchHotels, fetchAttractions };
