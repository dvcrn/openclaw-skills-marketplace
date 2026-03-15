#!/usr/bin/env node
/**
 * NoteX 链接补 token 并可选自动打开浏览器
 *
 * 用法示例：
 *   # 推荐：提供 CWork Key，脚本自动换取 token
 *   node notex-open-link.js --key CWORK_KEY
 *
 *   # 若已设置环境变量 XG_USER_TOKEN/XG_USER_ID/XG_USER_PERSONID，可省略 --key
 *
 *   # 自动打开浏览器（可选）
 *   node notex-open-link.js --key CWORK_KEY --auto-open true
 *
 */

const { spawn } = require('child_process');

const AUTH_CONFIG = {};

const PROD_NOTEX_HOST = 'notex.aishuo.co';
const DEFAULT_NOTEX_HOME_URL = 'https://notex.aishuo.co/';

function parseArgs() {
  const args = process.argv.slice(2);
  const result = {};
  for (let i = 0; i < args.length; i += 1) {
    const key = args[i];
    if (!key.startsWith('--')) continue;
    const normalized = key.replace(/^--/, '');
    const next = args[i + 1];
    if (!next || next.startsWith('--')) {
      result[normalized] = 'true';
      continue;
    }
    result[normalized] = next;
    i += 1;
  }
  return result;
}

function parseBool(value, fallback = false) {
  if (value === undefined) return fallback;
  const normalized = String(value).trim().toLowerCase();
  if (['1', 'true', 'yes', 'y', 'on'].includes(normalized)) return true;
  if (['0', 'false', 'no', 'n', 'off'].includes(normalized)) return false;
  return fallback;
}

async function requestJson(url, options = {}) {
  const controller = new AbortController();
  const timeoutMs = options.timeoutMs || 30000;
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      method: options.method || 'GET',
      headers: options.headers || {},
      signal: controller.signal,
    });
    const text = await response.text();
    let payload = {};
    if (text) {
      try {
        payload = JSON.parse(text);
      } catch {
        throw new Error(`响应不是合法 JSON: ${text.slice(0, 200)}`);
      }
    }

    if (!response.ok) {
      const msg = payload.resultMsg || payload.error || response.statusText;
      throw new Error(`HTTP ${response.status}: ${msg}`);
    }

    if (payload && typeof payload === 'object' && 'resultCode' in payload) {
      if (payload.resultCode !== 1) {
        throw new Error(payload.resultMsg || `API error (${payload.resultCode})`);
      }
      return payload.data;
    }

    return payload;
  } finally {
    clearTimeout(timer);
  }
}

async function exchangeTokenByKey(cworkKey) {
  const url = `https://notex.aishuo.co/noteX/api/user/nologin/appkey?appKey=${encodeURIComponent(cworkKey)}`;
  const data = await requestJson(url, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
    timeoutMs: 30000,
  });

  if (!data || !data['access-token'] || !data.userId) {
    throw new Error('CWork Key 换 token 失败：返回字段不完整');
  }

  return {
    accessToken: data['access-token'],
    userId: data.userId,
  };
}

function getEnvAuthContext() {
  const envToken = process.env.XG_USER_TOKEN;
  const envUserId = process.env.XG_USER_ID;
  const envPersonId = process.env.XG_USER_PERSONID || process.env.XG_USER_PERSIONID;
  if (envToken && envUserId && envPersonId) {
    return { accessToken: envToken, userId: envUserId, personId: envPersonId };
  }
  return null;
}

async function resolveAccessToken(args) {
  const envAuth = getEnvAuthContext();
  if (envAuth) {
    return {
      accessToken: envAuth.accessToken,
      source: 'env',
      userId: envAuth.userId,
    };
  }

  if (!args.key) {
    throw new Error('缺少鉴权参数：请提供环境变量 (XG_USER_TOKEN/XG_USER_ID/XG_USER_PERSONID) 或 --key（推荐）');
  }

  const data = await exchangeTokenByKey(args.key);
  return {
    accessToken: data.accessToken,
    source: 'exchanged-by-key',
    userId: data.userId,
  };
}

function normalizeNotexUrl(rawUrl) {
  let parsed;
  try {
    parsed = new URL(rawUrl);
  } catch {
    throw new Error(`URL 非法：${rawUrl}`);
  }

  if (parsed.protocol !== 'https:') {
    throw new Error('URL 必须使用 https 协议');
  }
  if (parsed.hostname !== PROD_NOTEX_HOST) {
    throw new Error(`URL 必须使用生产域名 ${PROD_NOTEX_HOST}`);
  }
  const pathname = parsed.pathname.replace(/\/+$/, '') || '/';
  if (pathname !== '/') {
    throw new Error('URL 仅支持 NoteX 首页路由：https://notex.aishuo.co/');
  }
  return parsed;
}

function buildAuthorizedUrl(rawUrl, token) {
  const url = normalizeNotexUrl(rawUrl);
  url.pathname = '/';
  url.search = '';
  url.searchParams.set('token', token);
  return url.toString();
}

async function openInBrowser(url) {
  const platform = process.platform;

  let cmd = '';
  let cmdArgs = [];
  if (platform === 'darwin') {
    cmd = 'open';
    cmdArgs = [url];
  } else if (platform === 'win32') {
    cmd = 'cmd';
    cmdArgs = ['/c', 'start', '', url];
  } else {
    cmd = 'xdg-open';
    cmdArgs = [url];
  }

  return new Promise((resolve) => {
    const child = spawn(cmd, cmdArgs, { detached: true, stdio: 'ignore' });
    child.on('error', () => resolve(false));
    child.unref();
    resolve(true);
  });
}

function printUsage() {
  console.log(`
用法:
  # 推荐：使用 CWork Key 自动换取 token
  node notex-open-link.js --key <CWorkKey>

  # 若已设置环境变量 XG_USER_TOKEN/XG_USER_ID/XG_USER_PERSONID，可省略 --key

  # 自动打开浏览器（可选）
  node notex-open-link.js --key <CWorkKey> --auto-open true

可选参数:
  --url <NoteXUrl>            可选，默认 https://notex.aishuo.co/（仅支持首页路由）
  --key <CWorkKey>            CWork Key（推荐）
  --auto-open <true|false>    是否自动打开浏览器（默认 false）
`);
}

async function main() {
  const args = parseArgs();
  const rawUrl = args.url || DEFAULT_NOTEX_HOME_URL;

  const auth = await resolveAccessToken(args);
  const finalUrl = buildAuthorizedUrl(rawUrl, auth.accessToken);

  const autoOpen = parseBool(args['auto-open'], false);
  let opened = false;
  if (autoOpen) {
    opened = await openInBrowser(finalUrl);
  }

  const output = {
    url: finalUrl,
    opened,
    authSource: auth.source,
  };

  console.log(`[open-link] 已生成可访问链接：${finalUrl}`);
  if (autoOpen) {
    console.log(opened ? '[open-link] 已尝试自动打开浏览器' : '[open-link] 自动打开浏览器失败，请手动打开链接');
  }
  console.log(JSON.stringify(output, null, 2));
}

main().catch((error) => {
  console.error(`❌ ${error.message}`);
  process.exit(1);
});
