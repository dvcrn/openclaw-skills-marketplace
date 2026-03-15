#!/usr/bin/env node
/**
 * Amazon Ads — Request SP Campaigns Report (Step 1)
 * Requests an async report and saves reportId to tmp file. Exits immediately.
 *
 * Usage: node scripts/request-report.js [--days 7]
 */

const fs   = require('fs');
const path = require('path');
const https = require('https');

const HOME      = process.env.HOME || require('os').homedir();
const ADS_PATH  = process.env.AMAZON_ADS_PATH || `${HOME}/amazon-ads-api.json`;
const PENDING   = path.join(HOME, '.openclaw/workspace/tmp/amazon-report-pending.json');

const args    = process.argv.slice(2);
const getArg  = (n) => { const i = args.indexOf(n); return i >= 0 ? args[i+1] : null; };
const DAYS    = parseInt(getArg('--days') || '7', 10);

function dateStr(offsetDays = 0) {
  const d = new Date();
  d.setUTCDate(d.getUTCDate() + offsetDays);
  return d.toISOString().slice(0, 10); // YYYY-MM-DD
}

function apiPost(hostname, pathStr, body, headers) {
  return new Promise((resolve, reject) => {
    const payload = JSON.stringify(body);
    const req = https.request({
      hostname, path: pathStr, method: 'POST',
      headers: {
        'Content-Type': 'application/vnd.createasyncreportrequest.v3+json',
        'Content-Length': Buffer.byteLength(payload),
        ...headers,
      },
    }, res => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => {
        try { resolve({ status: res.statusCode, body: JSON.parse(d) }); }
        catch (e) { resolve({ status: res.statusCode, body: d }); }
      });
    });
    req.on('error', reject);
    req.write(payload);
    req.end();
  });
}

async function getLwaToken(creds) {
  const params = new URLSearchParams({
    grant_type: 'refresh_token',
    refresh_token: creds.refreshToken,
    client_id: creds.lwaClientId,
    client_secret: creds.lwaClientSecret,
  });
  return new Promise((resolve, reject) => {
    const payload = params.toString();
    const req = https.request({
      hostname: 'api.amazon.com', path: '/auth/o2/token', method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'Content-Length': Buffer.byteLength(payload) },
    }, res => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => {
        try {
          const t = JSON.parse(d);
          if (!t.access_token) throw new Error('LWA token refresh failed: ' + d.slice(0, 200));
          resolve(t.access_token);
        } catch (e) { reject(e); }
      });
    });
    req.on('error', reject);
    req.write(payload);
    req.end();
  });
}

async function main() {
  const creds = JSON.parse(fs.readFileSync(ADS_PATH, 'utf8'));
  // Support both pre-refreshed accessToken and LWA refresh flow
  let accessToken = creds.accessToken;
  if (!accessToken && creds.refreshToken) {
    console.log('🔑 Refreshing LWA access token...');
    accessToken = await getLwaToken(creds);
  }
  const { profileId, region } = creds;
  if (!accessToken || !profileId) throw new Error('amazon-ads-api.json missing accessToken or profileId');

  const endpoint = region === 'NA' ? 'advertising-api.amazon.com'
                 : region === 'FE' ? 'advertising-api-fe.amazon.com'
                 : 'advertising-api-eu.amazon.com'; // default EU (UAE = EU region)

  const startDate = dateStr(-DAYS);
  const endDate   = dateStr(-1); // yesterday

  // Store clientId for API headers (lwaClientId field)
  const clientId = creds.clientId || creds.lwaClientId || '';

  console.log(`📊 Requesting SP Campaigns report (${startDate} → ${endDate})...`);

  const { status, body } = await apiPost(endpoint, '/reporting/reports', {
    name: `SP Campaigns ${startDate} to ${endDate}`,
    startDate,
    endDate,
    configuration: {
      adProduct: 'SPONSORED_PRODUCTS',
      groupBy: ['campaign'],
      columns: ['campaignName', 'campaignId', 'impressions', 'clicks', 'spend', 'purchases7d', 'sales7d'],
      reportTypeId: 'spCampaigns',
      timeUnit: 'SUMMARY',
      format: 'GZIP_JSON',
    },
  }, {
    Authorization: `Bearer ${accessToken}`,
    'Amazon-Advertising-API-ClientId': clientId,
    'Amazon-Advertising-API-Scope': String(profileId),
  });

  if (status !== 200 && status !== 202) {
    throw new Error(`Report request failed (${status}): ${JSON.stringify(body).slice(0, 300)}`);
  }

  const reportId = body.reportId;
  if (!reportId) throw new Error('No reportId in response: ' + JSON.stringify(body).slice(0, 200));

  const pending = { reportId, requestedAt: new Date().toISOString(), startDate, endDate, days: DAYS };
  fs.mkdirSync(path.dirname(PENDING), { recursive: true });
  fs.writeFileSync(PENDING, JSON.stringify(pending, null, 2));

  console.log(`✅ Report requested`);
  console.log(`   reportId:    ${reportId}`);
  console.log(`   pendingFile: ${PENDING}`);
  console.log(`   Next step:   node scripts/poll-report.js   (run in ~1-2 min)`);
}

main().catch(e => { console.error('❌', e.message); process.exit(1); });
