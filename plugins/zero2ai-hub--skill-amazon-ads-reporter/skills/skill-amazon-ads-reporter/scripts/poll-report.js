#!/usr/bin/env node
/**
 * Amazon Ads — Poll + Download SP Campaigns Report (Step 2)
 * Reads reportId from tmp file, polls until COMPLETED, downloads + parses.
 * Filters out PAUSED campaigns. Prints performance table.
 *
 * Usage: node scripts/poll-report.js
 */

const fs    = require('fs');
const path  = require('path');
const https = require('https');
const zlib  = require('zlib');

const HOME      = process.env.HOME || require('os').homedir();
const ADS_PATH  = process.env.AMAZON_ADS_PATH || `${HOME}/amazon-ads-api.json`;
const PENDING   = path.join(HOME, '.openclaw/workspace/tmp/amazon-report-pending.json');
const LATEST    = path.join(HOME, '.openclaw/workspace/tmp/amazon-report-latest.json');

const MAX_ATTEMPTS = 20;
const POLL_INTERVAL_MS = 30000; // 30s

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function apiGet(hostname, pathStr, headers) {
  return new Promise((resolve, reject) => {
    const req = https.request({ hostname, path: pathStr, method: 'GET', headers }, res => {
      const chunks = [];
      res.on('data', c => chunks.push(c));
      res.on('end', () => {
        const buf = Buffer.concat(chunks);
        try { resolve({ status: res.statusCode, body: JSON.parse(buf.toString()), raw: buf }); }
        catch { resolve({ status: res.statusCode, body: buf.toString(), raw: buf }); }
      });
    });
    req.on('error', reject);
    req.end();
  });
}

function downloadBuffer(url) {
  return new Promise((resolve, reject) => {
    const get = (u) => {
      const mod = u.startsWith('https') ? https : require('http');
      mod.get(u, res => {
        if ([301,302,303,307,308].includes(res.statusCode) && res.headers.location) {
          return get(res.headers.location);
        }
        const chunks = [];
        res.on('data', c => chunks.push(c));
        res.on('end', () => resolve(Buffer.concat(chunks)));
        res.on('error', reject);
      }).on('error', reject);
    };
    get(url);
  });
}

function gunzip(buf) {
  return new Promise((resolve, reject) => zlib.gunzip(buf, (err, result) => err ? reject(err) : resolve(result)));
}

function printTable(rows) {
  const cols = ['Campaign', 'Impressions', 'Clicks', 'CTR%', 'Spend(AED)', 'Sales(AED)', 'ACOS%'];
  const widths = cols.map(c => c.length);
  rows.forEach(r => {
    widths[0] = Math.max(widths[0], r.campaignName.slice(0, 40).length);
  });
  const hr = widths.map(w => '─'.repeat(w + 2)).join('┼');
  const fmt = (val, w) => String(val).padStart(w);
  console.log('\n' + cols.map((c,i) => c.padEnd(widths[i])).join(' │ '));
  console.log(hr);
  rows.forEach(r => {
    const ctr   = r.clicks > 0 ? ((r.clicks / r.impressions) * 100).toFixed(2) : '0.00';
    const acos  = r.sales7d > 0 ? ((r.spend / r.sales7d) * 100).toFixed(1) : 'n/a';
    const row   = [
      r.campaignName.slice(0, 40).padEnd(widths[0]),
      fmt(r.impressions.toLocaleString(), widths[1]),
      fmt(r.clicks.toLocaleString(), widths[2]),
      fmt(ctr, widths[3]),
      fmt(r.spend.toFixed(2), widths[4]),
      fmt(r.sales7d.toFixed(2), widths[5]),
      fmt(acos, widths[6]),
    ];
    console.log(row.join(' │ '));
  });
  console.log('');
}

async function getActiveCampaignIds(creds, endpoint) {
  try {
    const { status, body } = await apiGet(endpoint, '/sp/campaigns/list', {
      Authorization: `Bearer ${creds.accessToken}`,
      'Amazon-Advertising-API-ClientId': creds.clientId || creds.lwaClientId || '',
      'Amazon-Advertising-API-Scope': String(creds.profileId),
      'Content-Type': 'application/json',
    });
    if (status !== 200) {
      console.warn(`  ⚠️  Could not fetch active campaigns list (HTTP ${status}) — showing all`);
      return null;
    }
    // body may be array or { campaigns: [...] }
    const list = Array.isArray(body) ? body : (body.campaigns || []);
    if (list.length === 0) {
      console.warn('  ⚠️  Empty campaigns list from API — showing all');
      return null;
    }
    return new Set(
      list.filter(c => c.state?.toUpperCase() !== 'PAUSED').map(c => String(c.campaignId))
    );
  } catch (e) {
    console.warn('  ⚠️  Could not fetch active campaigns list:', e.message, '— showing all');
    return null; // null = show all
  }
}

async function main() {
  if (!fs.existsSync(PENDING)) {
    console.error(`❌ No pending report found at ${PENDING}`);
    console.error('   Run request-report.js first.');
    process.exit(1);
  }

  const pending = JSON.parse(fs.readFileSync(PENDING, 'utf8'));
  const { reportId, startDate, endDate } = pending;
  console.log(`🔄 Polling reportId: ${reportId} (${startDate} → ${endDate})`);

  const creds = JSON.parse(fs.readFileSync(ADS_PATH, 'utf8'));
  // Support both pre-refreshed accessToken and LWA refresh flow
  let accessToken = creds.accessToken;
  if (!accessToken && creds.refreshToken) {
    console.log('🔑 Refreshing LWA access token...');
    accessToken = await (async () => {
      const { default: https2 } = await import('https');
      const params = `grant_type=refresh_token&refresh_token=${encodeURIComponent(creds.refreshToken)}&client_id=${encodeURIComponent(creds.lwaClientId)}&client_secret=${encodeURIComponent(creds.lwaClientSecret)}`;
      return new Promise((resolve, reject) => {
        const req = https2.request({
          hostname: 'api.amazon.com', path: '/auth/o2/token', method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'Content-Length': Buffer.byteLength(params) },
        }, res => {
          let d = '';
          res.on('data', c => d += c);
          res.on('end', () => {
            const t = JSON.parse(d);
            if (!t.access_token) reject(new Error('LWA failed: ' + d.slice(0,200)));
            else resolve(t.access_token);
          });
        });
        req.on('error', reject);
        req.write(params);
        req.end();
      });
    })();
  }
  const { profileId, region } = creds;
  const clientId = creds.clientId || creds.lwaClientId || '';
  const endpoint = region === 'NA' ? 'advertising-api.amazon.com'
                 : region === 'FE' ? 'advertising-api-fe.amazon.com'
                 : 'advertising-api-eu.amazon.com';

  const authHeaders = {
    Authorization: `Bearer ${accessToken}`,
    'Amazon-Advertising-API-ClientId': clientId,
    'Amazon-Advertising-API-Scope': String(profileId),
  };

  let attempt = 0;
  let reportMeta = null;

  while (attempt < MAX_ATTEMPTS) {
    attempt++;
    process.stdout.write(`  Attempt ${attempt}/${MAX_ATTEMPTS}... `);

    const { status, body } = await apiGet(endpoint, `/reporting/reports/${reportId}`, authHeaders);

    if (status !== 200) {
      console.log(`HTTP ${status}`);
      if (attempt < MAX_ATTEMPTS) await sleep(POLL_INTERVAL_MS);
      continue;
    }

    const state = body.status || body.state || '';
    console.log(state);

    if (state === 'COMPLETED') { reportMeta = body; break; }
    if (state === 'FAILED') throw new Error('Report generation failed: ' + JSON.stringify(body).slice(0, 200));

    if (attempt < MAX_ATTEMPTS) await sleep(POLL_INTERVAL_MS);
  }

  if (!reportMeta) throw new Error('Timed out waiting for report after 10 minutes');

  const downloadUrl = reportMeta.url || reportMeta.location;
  if (!downloadUrl) throw new Error('No download URL in completed report: ' + JSON.stringify(reportMeta).slice(0,200));

  console.log('\n📥 Downloading report...');
  const compressed = await downloadBuffer(downloadUrl);
  const decompressed = await gunzip(compressed);
  const rows = JSON.parse(decompressed.toString());

  console.log(`   ${rows.length} campaign rows received`);

  // Filter out paused campaigns
  console.log('🔍 Fetching active campaign list to filter paused...');
  const activeIds = await getActiveCampaignIds({ ...creds, accessToken, clientId }, endpoint);
  const filtered = activeIds
    ? rows.filter(r => activeIds.has(String(r.campaignId)))
    : rows;
  console.log(`   ${filtered.length} active campaigns (${rows.length - filtered.length} paused filtered out)`);

  // Sort by spend desc
  filtered.sort((a, b) => (b.spend || 0) - (a.spend || 0));

  printTable(filtered);

  // Summary totals
  const totals = filtered.reduce((acc, r) => ({
    impressions: acc.impressions + (r.impressions || 0),
    clicks: acc.clicks + (r.clicks || 0),
    spend: acc.spend + (r.spend || 0),
    purchases: acc.purchases + (r.purchases7d || 0),
    sales: acc.sales + (r.sales7d || 0),
  }), { impressions: 0, clicks: 0, spend: 0, purchases: 0, sales: 0 });

  const totalAcos = totals.sales > 0 ? ((totals.spend / totals.sales) * 100).toFixed(1) : 'n/a';
  console.log(`📊 TOTALS: ${totals.impressions.toLocaleString()} impr | ${totals.clicks.toLocaleString()} clicks | ${totals.spend.toFixed(2)} AED spend | ${totals.sales.toFixed(2)} AED sales | ACOS ${totalAcos}%`);

  // Save result
  const result = { generatedAt: new Date().toISOString(), startDate, endDate, campaigns: filtered, totals };
  fs.mkdirSync(path.dirname(LATEST), { recursive: true });
  fs.writeFileSync(LATEST, JSON.stringify(result, null, 2));
  console.log(`\n✅ Saved to ${LATEST}`);

  // Cleanup pending file
  fs.unlinkSync(PENDING);
  console.log(`🧹 Cleaned up pending file`);
}

main().catch(e => { console.error('❌', e.message); process.exit(1); });
