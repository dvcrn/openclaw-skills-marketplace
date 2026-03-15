#!/usr/bin/env node
/**
 * browser-daemon.js — Persistent browser server for Clawnet.
 *
 * Keeps Chromium + Playwright alive between short-lived agent script invocations.
 * Agent scripts communicate via HTTP on localhost.
 *
 * Multi-tab: each tab has an ID. All action endpoints accept optional `tabId`.
 * If omitted, the "active" (most recently used) tab is used.
 *
 * Lifecycle:
 *   1. Agent calls launchBrowser() → detects no daemon → spawns this as detached child
 *   2. Daemon launches Chromium, opens HTTP server on a free port
 *   3. Saves { pid, port } to ~/.clawnet/daemon.json
 *   4. Agent scripts send HTTP commands (goto, snapshot, click, fill, screenshot…)
 *   5. After 5 min of inactivity → auto-shutdown
 *
 * Usage (standalone):
 *   node browser-daemon.js [--port=9222]
 */

const http   = require('node:http');
const path   = require('node:path');
const fs     = require('node:fs');
const os     = require('node:os');
const crypto = require('node:crypto');

// ── Config ──────────────────────────────────────────────────────────────────

const CLAWNET_DIR   = process.env.CLAWNET_DIR?.trim() || path.join(os.homedir(), '.clawnet');
const DAEMON_FILE   = path.join(CLAWNET_DIR, 'daemon.json');
const IDLE_TIMEOUT  = 5 * 60 * 1000; // 5 minutes
const DEFAULT_PORT  = parseInt(process.env.CN_DAEMON_PORT || '0', 10); // 0 = auto

// ── Playwright resolver (same logic as browser.js) ──────────────────────────

function _requirePlaywright() {
  const tries = [
    () => require('playwright'),
    () => require(`${__dirname}/../node_modules/playwright`),
    () => require(`${__dirname}/../../node_modules/playwright`),
    () => require(`${process.env.HOME || '/root'}/.openclaw/workspace/node_modules/playwright`),
    () => require('./node_modules/playwright'),
  ];
  for (const fn of tries) {
    try { return fn(); } catch (_) {}
  }
  throw new Error('[daemon] playwright not found');
}

// ── State ───────────────────────────────────────────────────────────────────

let _browser      = null;   // Playwright Browser (or null for persistent ctx)
let _ctx          = null;   // BrowserContext
let _launchOpts   = null;   // Options used for current launch
let _lastActivity = Date.now();
let _idleTimer    = null;
let _server       = null;
let _startedAt    = Date.now();

// ── Tab Manager ─────────────────────────────────────────────────────────────
// Maps tabId → { page, createdAt, label }
// Active tab = most recently used tab

const _tabs = new Map();
let _activeTabId = null;

function _genTabId() {
  return 't_' + crypto.randomBytes(4).toString('hex');
}

/** Register a page as a new tab, return its ID */
function _addTab(page, label = '') {
  const tabId = _genTabId();
  _tabs.set(tabId, { page, createdAt: Date.now(), label });
  _activeTabId = tabId;
  // Clean up when page closes
  page.once('close', () => {
    _tabs.delete(tabId);
    if (_activeTabId === tabId) {
      // Switch active to most recent remaining tab
      _activeTabId = _tabs.size > 0 ? [..._tabs.keys()].pop() : null;
    }
  });
  return tabId;
}

/** Resolve page from tabId (or use active tab) */
function _resolveTab(tabId) {
  const id = tabId || _activeTabId;
  if (!id) throw new Error('No tabs open');
  const entry = _tabs.get(id);
  if (!entry) throw new Error(`Tab "${id}" not found. Open tabs: ${[..._tabs.keys()].join(', ')}`);
  _activeTabId = id; // mark as active
  return entry;
}

function _resolveTabPage(tabId) {
  return _resolveTab(tabId).page;
}

// ── Idle auto-shutdown ──────────────────────────────────────────────────────

function touch() {
  _lastActivity = Date.now();
}

function startIdleTimer() {
  if (_idleTimer) clearInterval(_idleTimer);
  _idleTimer = setInterval(() => {
    if (Date.now() - _lastActivity > IDLE_TIMEOUT) {
      console.log('[daemon] Idle timeout reached — shutting down');
      shutdown();
    }
  }, 30_000);
  _idleTimer.unref();
}

async function shutdown() {
  try { fs.unlinkSync(DAEMON_FILE); } catch (_) {}
  try { if (_ctx) await _ctx.close(); } catch (_) {}
  try { if (_browser && _browser !== _ctx) await _browser.close(); } catch (_) {}
  try { if (_server) _server.close(); } catch (_) {}
  process.exit(0);
}

// ── Browser launch (reuses browser.js logic but inline) ─────────────────────

async function ensureBrowser(opts = {}) {
  // If already launched and at least one tab alive, skip
  if (_ctx && _tabs.size > 0) {
    try {
      _resolveTabPage().url(); // test if alive
      return;
    } catch (_) {
      // Dead — clear and relaunch
      _tabs.clear();
      _activeTabId = null;
      _ctx = null;
      _browser = null;
    }
  }

  const { chromium } = _requirePlaywright();
  const browserLib = require('./browser');

  const {
    country  = 'us',
    mobile   = true,
    useProxy = true,
    headless = true,
    profile  = 'default',
  } = opts;

  _launchOpts = { country, mobile, useProxy, headless, profile };

  // Ensure credentials + managed config
  try {
    await browserLib.getCredentials();
  } catch (e) {
    console.warn('[daemon] Could not fetch managed credentials:', e.message);
  }

  const device = browserLib.buildDevice(mobile, country);
  const proxy  = useProxy ? browserLib.makeProxy(null, country) : null;

  if (useProxy && !proxy && process.env.CN_NO_PROXY !== '1') {
    throw new Error('[daemon] Proxy unavailable — trial/subscription expired or registration failed.');
  }

  // Sandbox detection
  const isDocker = fs.existsSync('/.dockerenv');
  const launchArgs = [
    '--ignore-certificate-errors',
    '--disable-blink-features=AutomationControlled',
    '--disable-features=IsolateOrigins,site-per-process',
  ];
  if (isDocker || process.env.CN_CHROMIUM_NO_SANDBOX === '1') {
    launchArgs.unshift('--no-sandbox', '--disable-setuid-sandbox');
  }

  const ctxOpts = {
    ...device,
    ignoreHTTPSErrors: true,
    permissions: ['geolocation', 'notifications'],
  };
  if (proxy) ctxOpts.proxy = proxy;

  // Persistent profile
  const safeName = encodeURIComponent(profile || 'default');
  const PROFILES_DIR = path.join(CLAWNET_DIR, 'profiles');
  const profileDir = path.join(PROFILES_DIR, safeName);
  fs.mkdirSync(profileDir, { recursive: true });

  _ctx = await chromium.launchPersistentContext(profileDir, {
    headless,
    args: launchArgs,
    ...ctxOpts,
  });

  // Apply stealth scripts
  const meta = browserLib.COUNTRY_META[country.toLowerCase()] || browserLib.COUNTRY_META.us;
  await _ctx.addInitScript((m) => {
    Object.defineProperty(navigator, 'webdriver',           { get: () => false });
    Object.defineProperty(navigator, 'maxTouchPoints',      { get: () => m.mobile ? 5 : 0 });
    Object.defineProperty(navigator, 'platform',            { get: () => m.mobile ? 'iPhone' : 'Win32' });
    Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => m.mobile ? 6 : 8 });
    Object.defineProperty(navigator, 'language',            { get: () => m.locale });
    Object.defineProperty(navigator, 'languages',           { get: () => [m.locale, 'en'] });
    if (m.mobile) {
      Object.defineProperty(screen, 'width',       { get: () => 393 });
      Object.defineProperty(screen, 'height',      { get: () => 852 });
      Object.defineProperty(screen, 'availWidth',  { get: () => 393 });
      Object.defineProperty(screen, 'availHeight', { get: () => 852 });
    }
    if (window.RTCPeerConnection) {
      const OrigRTC = window.RTCPeerConnection;
      window.RTCPeerConnection = function(...args) {
        if (args[0] && args[0].iceServers) args[0].iceServers = [];
        return new OrigRTC(...args);
      };
      window.RTCPeerConnection.prototype = OrigRTC.prototype;
    }
    if (!window.chrome) window.chrome = {};
    if (!window.chrome.runtime) window.chrome.runtime = { connect: () => {}, sendMessage: () => {} };
  }, { mobile, locale: meta.locale });

  _browser = _ctx.browser();

  // Register initial page as first tab
  const initialPage = _ctx.pages()[0] || await _ctx.newPage();
  _addTab(initialPage, 'initial');

  console.log(`[daemon] Browser launched: country=${country} mobile=${mobile} proxy=${!!proxy} profile=${profile}`);
}

// ── HTTP endpoint handlers ──────────────────────────────────────────────────

async function handleLaunch(body) {
  await ensureBrowser(body);
  return { ok: true, tabId: _activeTabId, launchOpts: _launchOpts };
}

async function handleNewTab(body) {
  if (!_ctx) throw new Error('Browser not launched. Call /launch first.');
  const page = await _ctx.newPage();
  const tabId = _addTab(page, body.label || '');
  if (body.url) {
    await page.goto(body.url, {
      waitUntil: body.waitUntil || 'domcontentloaded',
      timeout: body.timeout || 60000,
    });
  }
  console.log(`[daemon] New tab ${tabId}${body.url ? ` → ${body.url}` : ''}`);
  return { ok: true, tabId };
}

function handleListTabs() {
  const tabs = [];
  for (const [id, entry] of _tabs) {
    let url = '';
    try { url = entry.page.url(); } catch (_) {}
    tabs.push({
      tabId: id,
      url,
      label: entry.label,
      active: id === _activeTabId,
      createdAt: new Date(entry.createdAt).toISOString(),
    });
  }
  return { ok: true, tabs, activeTabId: _activeTabId };
}

async function handleCloseTab(body) {
  const { tabId } = body;
  if (!tabId) return { error: 'tabId required' };
  const entry = _tabs.get(tabId);
  if (!entry) return { error: `Tab "${tabId}" not found` };
  try { await entry.page.close(); } catch (_) {}
  // _tabs.delete happens in the 'close' listener
  return { ok: true, closed: tabId };
}

async function handleSwitchTab(body) {
  const { tabId } = body;
  if (!tabId) return { error: 'tabId required' };
  if (!_tabs.has(tabId)) return { error: `Tab "${tabId}" not found` };
  _activeTabId = tabId;
  return { ok: true, activeTabId: _activeTabId };
}

async function handleGoto(body) {
  const page = _resolveTabPage(body.tabId);
  const { url, waitUntil = 'domcontentloaded', timeout = 60000 } = body;
  if (!url) return { error: 'url required' };
  const resp = await page.goto(url, { waitUntil, timeout });
  return { ok: true, tabId: body.tabId || _activeTabId, status: resp?.status(), url: page.url() };
}

async function handleSnapshot(body) {
  const page = _resolveTabPage(body.tabId);
  const { selector = 'body', interactiveOnly = false, maxLength = 20000, timeout = 5000 } = body;
  const browserLib = require('./browser');
  const result = await browserLib.snapshot(page, { selector, interactiveOnly, maxLength, timeout });
  return { ok: true, tabId: body.tabId || _activeTabId, snapshot: result };
}

async function handleSnapshotAI(body) {
  const page = _resolveTabPage(body.tabId);
  const { maxChars = 20000, timeout = 5000 } = body;
  const browserLib = require('./browser');
  const result = await browserLib.snapshotAI(page, { maxChars, timeout });
  return { ok: true, tabId: body.tabId || _activeTabId, ...result };
}

async function handleClickRef(body) {
  const page = _resolveTabPage(body.tabId);
  const { ref, timeout = 8000, button = 'left', doubleClick = false } = body;
  if (!ref) return { error: 'ref required' };
  const browserLib = require('./browser');
  await browserLib.clickRef(page, ref, { timeout, button, doubleClick });
  return { ok: true };
}

async function handleFillRef(body) {
  const page = _resolveTabPage(body.tabId);
  const { ref, value, timeout = 8000 } = body;
  if (!ref) return { error: 'ref required' };
  const browserLib = require('./browser');
  await browserLib.fillRef(page, ref, value || '', { timeout });
  return { ok: true };
}

async function handleTypeRef(body) {
  const page = _resolveTabPage(body.tabId);
  const { ref, text, slowly = false, submit = false, timeout = 8000 } = body;
  if (!ref) return { error: 'ref required' };
  const browserLib = require('./browser');
  await browserLib.typeRef(page, ref, text || '', { slowly, submit, timeout });
  return { ok: true };
}

async function handleSelectRef(body) {
  const page = _resolveTabPage(body.tabId);
  const { ref, value, timeout = 8000 } = body;
  if (!ref) return { error: 'ref required' };
  const browserLib = require('./browser');
  await browserLib.selectRef(page, ref, value, { timeout });
  return { ok: true };
}

async function handleHoverRef(body) {
  const page = _resolveTabPage(body.tabId);
  const { ref, timeout = 8000 } = body;
  if (!ref) return { error: 'ref required' };
  const browserLib = require('./browser');
  await browserLib.hoverRef(page, ref, { timeout });
  return { ok: true };
}

async function handleScreenshot(body) {
  const page = _resolveTabPage(body.tabId);
  const { fullPage = false } = body;
  const buf = await page.screenshot({ type: 'png', fullPage });
  return { ok: true, tabId: body.tabId || _activeTabId, base64: buf.toString('base64') };
}

async function handleExtractText(body) {
  const page = _resolveTabPage(body.tabId);
  const { mode = 'readability', maxChars } = body;
  const browserLib = require('./browser');
  const result = await browserLib.extractText(page, { mode, maxChars });
  return { ok: true, tabId: body.tabId || _activeTabId, ...result };
}

async function handleBatchActions(body) {
  const page = _resolveTabPage(body.tabId);
  const { actions, stopOnError = false, delayBetween = 50 } = body;
  if (!Array.isArray(actions)) return { error: 'actions array required' };
  const browserLib = require('./browser');
  const result = await browserLib.batchActions(page, actions, { stopOnError, delayBetween });
  return { ok: true, ...result };
}

async function handleEval(body) {
  const page = _resolveTabPage(body.tabId);
  const { expression } = body;
  if (!expression) return { error: 'expression required' };
  const result = await page.evaluate(expression);
  return { ok: true, result };
}

async function handleGetCookies(body) {
  const { urls } = body;
  const cookies = urls
    ? await _ctx.cookies(Array.isArray(urls) ? urls : [urls])
    : await _ctx.cookies();
  return { ok: true, cookies };
}

async function handleSetCookies(body) {
  const { cookies } = body;
  if (!cookies) return { error: 'cookies array required' };
  const arr = Array.isArray(cookies) ? cookies : [cookies];
  await _ctx.addCookies(arr);
  return { ok: true, set: arr.length };
}

async function handleClearCookies() {
  await _ctx.clearCookies();
  return { ok: true, cleared: true };
}

async function handleWait(body) {
  const page = _resolveTabPage(body.tabId);
  const { ms = 1000 } = body;
  await page.waitForTimeout(Math.min(ms, 30000));
  return { ok: true };
}

async function handleClose() {
  await shutdown();
  return { ok: true };
}

function handleHealth() {
  const tabSummary = [];
  for (const [id, entry] of _tabs) {
    let url = '';
    try { url = entry.page.url(); } catch (_) {}
    tabSummary.push({ tabId: id, url, active: id === _activeTabId });
  }
  return {
    ok: true,
    pid: process.pid,
    uptime: Math.floor((Date.now() - _startedAt) / 1000),
    idleFor: Math.floor((Date.now() - _lastActivity) / 1000),
    tabs: tabSummary,
    activeTabId: _activeTabId,
    launchOpts: _launchOpts,
  };
}

// ── Route dispatcher ────────────────────────────────────────────────────────

const ROUTES = {
  '/launch':       handleLaunch,
  '/newTab':       handleNewTab,
  '/listTabs':     handleListTabs,
  '/closeTab':     handleCloseTab,
  '/switchTab':    handleSwitchTab,
  '/goto':         handleGoto,
  '/snapshot':     handleSnapshot,
  '/snapshotAI':   handleSnapshotAI,
  '/clickRef':     handleClickRef,
  '/fillRef':      handleFillRef,
  '/typeRef':      handleTypeRef,
  '/selectRef':    handleSelectRef,
  '/hoverRef':     handleHoverRef,
  '/screenshot':   handleScreenshot,
  '/extractText':  handleExtractText,
  '/batchActions': handleBatchActions,
  '/eval':         handleEval,
  '/wait':         handleWait,
  '/getCookies':   handleGetCookies,
  '/setCookies':   handleSetCookies,
  '/clearCookies': handleClearCookies,
  '/close':        handleClose,
  '/health':       handleHealth,
};

// ── HTTP server ─────────────────────────────────────────────────────────────

function startServer(port) {
  _server = http.createServer(async (req, res) => {
    touch();

    res.setHeader('Content-Type', 'application/json');

    const url = new URL(req.url, `http://localhost:${port}`);
    const route = url.pathname;

    // GET endpoints (no body needed)
    if (req.method === 'GET') {
      const handler = { '/health': handleHealth, '/listTabs': handleListTabs }[route];
      if (handler) {
        res.writeHead(200);
        res.end(JSON.stringify(handler()));
        return;
      }
    }

    // All other routes: POST with JSON body
    if (req.method !== 'POST') {
      res.writeHead(405);
      res.end(JSON.stringify({ error: 'POST required' }));
      return;
    }

    const handler = ROUTES[route];
    if (!handler) {
      res.writeHead(404);
      res.end(JSON.stringify({ error: `Unknown route: ${route}` }));
      return;
    }

    // Parse JSON body
    let body = {};
    try {
      const chunks = [];
      for await (const chunk of req) chunks.push(chunk);
      const raw = Buffer.concat(chunks).toString();
      if (raw.trim()) body = JSON.parse(raw);
    } catch (e) {
      res.writeHead(400);
      res.end(JSON.stringify({ error: `Invalid JSON: ${e.message}` }));
      return;
    }

    try {
      const result = await handler(body);
      res.writeHead(200);
      res.end(JSON.stringify(result));
    } catch (err) {
      console.error(`[daemon] ${route} error:`, err.message);
      res.writeHead(500);
      res.end(JSON.stringify({ error: err.message }));
    }
  });

  return new Promise((resolve, reject) => {
    _server.listen(port, '127.0.0.1', () => {
      const actualPort = _server.address().port;
      console.log(`[daemon] Listening on 127.0.0.1:${actualPort}  pid=${process.pid}`);

      // Save daemon info
      fs.mkdirSync(CLAWNET_DIR, { recursive: true });
      fs.writeFileSync(DAEMON_FILE, JSON.stringify({
        pid: process.pid,
        port: actualPort,
        startedAt: new Date(_startedAt).toISOString(),
      }));

      startIdleTimer();
      resolve(actualPort);
    });
    _server.on('error', reject);
  });
}

// ── Cleanup on exit ─────────────────────────────────────────────────────────

process.on('SIGTERM', shutdown);
process.on('SIGINT',  shutdown);
process.on('uncaughtException', (err) => {
  console.error('[daemon] Uncaught exception:', err);
  shutdown();
});

// ── Main ────────────────────────────────────────────────────────────────────

async function main() {
  let port = DEFAULT_PORT;
  for (const arg of process.argv.slice(2)) {
    const m = arg.match(/^--port=(\d+)$/);
    if (m) port = parseInt(m[1], 10);
  }

  const actualPort = await startServer(port);
  console.log(`[daemon] Ready on port ${actualPort}. Idle timeout: ${IDLE_TIMEOUT / 1000}s`);
}

main().catch((err) => {
  console.error('[daemon] Fatal:', err);
  process.exit(1);
});
