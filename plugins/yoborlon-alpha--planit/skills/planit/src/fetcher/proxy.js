'use strict';

/**
 * Proxy client — all data requests go through the PlanIt proxy server.
 * Set PLANIT_PROXY_URL in env or ~/.openclaw/data/planit/config.json.
 *
 * If proxy is unreachable, each caller falls back to mock data.
 */

const https = require('https');
const http  = require('http');
const { getProxyUrl } = require('./config');

/**
 * POST JSON to the proxy server.
 * @param {string} path  - e.g. '/api/trains'
 * @param {object} body
 * @returns {Promise<object|null>} response JSON, or null on failure
 */
async function proxyPost(path, body) {
  const base = getProxyUrl();
  if (!base) return null;

  const url = new URL(path, base);
  const payload = JSON.stringify(body);
  const secret  = process.env.PLANIT_SECRET || '';

  return new Promise((resolve) => {
    const lib = url.protocol === 'https:' ? https : http;
    const req = lib.request({
      hostname: url.hostname,
      port:     url.port || (url.protocol === 'https:' ? 443 : 80),
      path:     url.pathname + url.search,
      method:   'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(payload),
        'X-Planit-Secret': secret,
      },
      timeout: 10000,
    }, (res) => {
      const chunks = [];
      res.on('data', (c) => chunks.push(c));
      res.on('end', () => {
        try { resolve(JSON.parse(Buffer.concat(chunks).toString('utf8'))); }
        catch { resolve(null); }
      });
    });
    req.on('error', () => resolve(null));
    req.on('timeout', () => { req.destroy(); resolve(null); });
    req.write(payload);
    req.end();
  });
}

/**
 * Fetch trains via proxy.
 * @returns {Promise<Array|null>} trains array, or null to trigger fallback
 */
async function fetchTrainsViaProxy(fromCity, toCity, date, intent = {}, userId = 'anonymous') {
  const res = await proxyPost('/api/trains', { from: fromCity, to: toCity, date, userId, queryText: intent.rawText, intent });
  if (!res?.ok || !res.trains?.length) return null;
  return res.trains;
}

/**
 * Fetch hotels via proxy.
 * @returns {Promise<Array|null>}
 */
async function fetchHotelsViaProxy(city, userId = 'anonymous') {
  const res = await proxyPost('/api/hotels', { city, userId });
  if (!res?.ok || !res.hotels?.length) return null;
  return res.hotels;
}

/**
 * Fetch attractions via proxy.
 * @returns {Promise<Array|null>}
 */
async function fetchAttractionsViaProxy(city, group = 'general', userId = 'anonymous') {
  const res = await proxyPost('/api/attractions', { city, group, userId });
  if (!res?.ok || !res.attractions?.length) return null;
  return res.attractions;
}

/**
 * Log a booking event to proxy.
 */
async function logBookingViaProxy(userId, itemType, itemId, itemName, destination) {
  await proxyPost('/api/log/booking', { userId, itemType, itemId, itemName, destination });
}

module.exports = {
  fetchTrainsViaProxy,
  fetchHotelsViaProxy,
  fetchAttractionsViaProxy,
  logBookingViaProxy,
};
