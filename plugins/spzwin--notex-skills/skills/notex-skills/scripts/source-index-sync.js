#!/usr/bin/env node
/**
 * Notebook/Source 索引同步脚本
 *
 * 功能：
 * 1) 全量拉取索引树并落盘（覆盖写，保证全量刷新）
 * 2) 按 notebookId/sourceId 拉取来源最小详情（ID + 名称）并落盘
 * 3) 可配置定时轮询，持续全量刷新索引
 *
 * 用法示例：
 *   # 若已设置环境变量 XG_USER_TOKEN/XG_USER_ID/XG_USER_PERSONID，可省略 --key
 *   # 方式1（默认）：提供 CWork Key，脚本自动完成授权
 *   node source-index-sync.js --mode index --base-url https://notex.aishuo.co/noteX --key CWORK_KEY
 *   node source-index-sync.js --mode detail --base-url https://notex.aishuo.co/noteX --key CWORK_KEY --notebook-id nb_xxx
 *   node source-index-sync.js --mode detail --base-url https://notex.aishuo.co/noteX --key CWORK_KEY --source-id src_xxx
 *   node source-index-sync.js --mode index --base-url https://notex.aishuo.co/noteX --key CWORK_KEY --interval-minutes 60
 *
 */

const fs = require('fs');
const path = require('path');
const AUTH_CONFIG = {};
const PROD_NOTEX_HOST = 'notex.aishuo.co';
const PROD_NOTEX_BASE_URL = 'https://notex.aishuo.co/noteX';

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

function toPositiveInt(value, fallback) {
  const num = Number(value);
  if (!Number.isFinite(num) || num <= 0) return fallback;
  return Math.floor(num);
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function requestJson(url, options = {}) {
  const controller = new AbortController();
  const timeoutMs = options.timeoutMs || 60000;
  const timeout = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      method: options.method || 'GET',
      headers: options.headers || {},
      body: options.body ? JSON.stringify(options.body) : undefined,
      signal: controller.signal,
    });

    const text = await response.text();
    let payload = {};
    if (text) {
      try {
        payload = JSON.parse(text);
      } catch (error) {
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
    clearTimeout(timeout);
  }
}

async function writeJson(filePath, data) {
  await fs.promises.mkdir(path.dirname(filePath), { recursive: true });
  await fs.promises.writeFile(filePath, JSON.stringify(data, null, 2), 'utf8');
}

function buildHeaders(args) {
  if (!args['user-id']) {
    throw new Error('缺少 user-id：必须先通过环境变量或 CWork Key 获取 x-user-id');
  }
  if (!args['access-token']) {
    throw new Error('缺少 access-token：必须先通过环境变量或 CWork Key 获取 access-token');
  }
  if (!args['person-id']) {
    throw new Error('缺少 personId：必须先通过环境变量或 CWork Key 获取 personId');
  }
  const headers = {
    'Content-Type': 'application/json',
    'x-user-id': args['user-id'],
    'access-token': args['access-token'],
    'personId': args['person-id'],
  };
  headers.authorization = args['authorization'] || 'skill';
  return headers;
}

function normalizeProdBaseUrl(rawBaseUrl) {
  let parsed;
  try {
    parsed = new URL(rawBaseUrl);
  } catch {
    throw new Error(`base-url 非法：${rawBaseUrl}`);
  }

  if (parsed.protocol !== 'https:') {
    throw new Error('base-url 必须使用 https 协议');
  }
  if (parsed.hostname !== PROD_NOTEX_HOST) {
    throw new Error(`base-url 必须使用生产域名 ${PROD_NOTEX_HOST}`);
  }

  const pathname = parsed.pathname.replace(/\/+$/, '');
  if (!pathname || pathname === '/') {
    return `${parsed.origin}/noteX`;
  }
  if (pathname === '/noteX' || pathname === '/noteX/api') {
    return `${parsed.origin}${pathname}`;
  }
  throw new Error('base-url 路径仅支持 /noteX 或 /noteX/api');
}

function getBaseUrl(args) {
  const base = args['base-url'] || process.env.NOTEX_API_BASE_URL || PROD_NOTEX_BASE_URL;
  return normalizeProdBaseUrl(base);
}

function buildApiUrl(baseUrl, apiPath) {
  const normalizedApiPath = apiPath.startsWith('/api/') ? apiPath : `/api${apiPath}`;
  if (/\/noteX\/api$/i.test(baseUrl) || /\/api$/i.test(baseUrl)) {
    return `${baseUrl}${normalizedApiPath.replace(/^\/api/i, '')}`;
  }
  if (/\/noteX$/i.test(baseUrl)) {
    return `${baseUrl}${normalizedApiPath}`;
  }
  throw new Error(`不支持的 base-url: ${baseUrl}`);
}

async function exchangeTokenByKey(cworkKey) {
  const url = `${PROD_NOTEX_BASE_URL}/api/user/nologin/appkey?appKey=${encodeURIComponent(cworkKey)}`;
  const data = await requestJson(url, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
    timeoutMs: 30000,
  });

  if (!data || !data['access-token'] || !data.userId || !data.personId) {
    throw new Error('CWork Key 换 token 失败：返回字段不完整');
  }

  return {
    accessToken: data['access-token'],
    userId: data.userId,
    personId: data.personId,
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

/**
 * 统一鉴权预检：
 * 1) 优先使用环境变量 XG_USER_TOKEN/XG_USER_ID/XG_USER_PERSONID
 * 2) 其次使用 --key（CWork Key）完成授权
 */
async function resolveAuthContext(args) {
  const envAuth = getEnvAuthContext();
  if (envAuth) {
    console.log('[auth] 使用环境变量鉴权 (XG_USER_TOKEN/XG_USER_ID/XG_USER_PERSONID)');
    args['access-token'] = envAuth.accessToken;
    args['user-id'] = envAuth.userId;
    args['person-id'] = envAuth.personId;
    return;
  }

  if (!args.key) {
    throw new Error('缺少鉴权参数：请提供环境变量 (XG_USER_TOKEN/XG_USER_ID/XG_USER_PERSONID) 或 --key（推荐）');
  }

  console.log('[auth] 使用 CWork Key 换取 token...');
  const auth = await exchangeTokenByKey(args.key);

  args['access-token'] = auth.accessToken;
  args['user-id'] = auth.userId;
  args['person-id'] = auth.personId;
  console.log(`[auth] 鉴权成功，userId=${args['user-id']}`);
}

function collectTreeStats(tree) {
  let notebookCount = 0;
  let sourceCount = 0;

  function walk(nodes) {
    if (!Array.isArray(nodes)) return;
    for (const node of nodes) {
      notebookCount += 1;
      sourceCount += Array.isArray(node.sources) ? node.sources.length : 0;
      walk(node.children);
    }
  }

  walk(tree);
  return { notebookCount, sourceCount };
}

async function refreshIndexOnce(args) {
  const baseUrl = getBaseUrl(args);
  const type = args.type || 'all';
  const validTypes = new Set(['all', 'owned', 'collaborated']);
  if (!validTypes.has(type)) {
    throw new Error(`非法 type: ${type}（仅支持 all | owned | collaborated）`);
  }
  const headers = buildHeaders(args);
  const cacheDir = args['cache-dir']
    ? path.resolve(args['cache-dir'])
    : path.resolve(__dirname, '../cache/notebook-source-index');

  const url = buildApiUrl(baseUrl, `/api/notebooks/sources/index-tree?type=${encodeURIComponent(type)}`);
  const data = await requestJson(url, { headers, timeoutMs: 120000 });

  const outputPath = args.output
    ? path.resolve(args.output)
    : path.join(cacheDir, args['user-id'], 'index-tree.json');

  await writeJson(outputPath, data);
  const stats = collectTreeStats(data.tree);
  console.log(`[index] 全量刷新完成: ${outputPath}`);
  console.log(`[index] notebooks=${stats.notebookCount}, sources=${stats.sourceCount}, generatedAt=${data.generatedAt}`);
}

async function fetchDetailsOnce(args) {
  const baseUrl = getBaseUrl(args);
  const headers = buildHeaders(args);
  const notebookId = args['notebook-id'] || '';
  const sourceId = args['source-id'] || '';

  if (!notebookId && !sourceId) {
    throw new Error('detail 模式必须提供 --notebook-id 或 --source-id');
  }

  const cacheDir = args['cache-dir']
    ? path.resolve(args['cache-dir'])
    : path.resolve(__dirname, '../cache/notebook-source-index');

  const query = new URLSearchParams();
  if (notebookId) query.set('notebookId', notebookId);
  if (sourceId) query.set('sourceId', sourceId);

  const url = buildApiUrl(baseUrl, `/api/notebooks/sources/details?${query.toString()}`);
  const data = await requestJson(url, { headers, timeoutMs: 120000 });

  const defaultFile = sourceId
    ? `source-${sourceId}.json`
    : `notebook-${notebookId}.json`;
  const outputPath = args.output
    ? path.resolve(args.output)
    : path.join(cacheDir, args['user-id'], 'details', defaultFile);

  await writeJson(outputPath, data);
  console.log(`[detail] 最小详情已写入: ${outputPath}`);
  console.log(`[detail] mode=${data.mode}, notebook=${data.notebook?.id || '-'}`);
}

function printUsage() {
  console.log(`
用法:
  # 默认：使用 CWork Key（自动完成授权）
  node source-index-sync.js --mode index  --base-url https://notex.aishuo.co/noteX --key <CWorkKey> [--type all]
  node source-index-sync.js --mode detail --base-url https://notex.aishuo.co/noteX --key <CWorkKey> --notebook-id <nbId>
  node source-index-sync.js --mode detail --base-url https://notex.aishuo.co/noteX --key <CWorkKey> --source-id <srcId>

可选参数:
  --key <CWorkKey>            CWork Key（推荐；脚本内部自动换取授权）
  --base-url <url>            生产地址（仅支持 https://notex.aishuo.co/noteX 或 /noteX/api）
  --authorization <value>     透传 authorization（例如 skill）
  --person-id <id>            透传 personId
  --type <all|owned|collaborated>  index 模式下的可见范围，默认 all
  --cache-dir <path>          本地缓存根目录（默认: docs/skills/cache/notebook-source-index）
  --output <path>             指定输出文件
  --interval-minutes <n>      仅 index 模式生效，按分钟持续全量刷新
`);
}

async function main() {
  const args = parseArgs();
  const mode = args.mode || 'index';

  if (mode !== 'index' && mode !== 'detail') {
    printUsage();
    throw new Error(`不支持的 mode: ${mode}`);
  }

  await resolveAuthContext(args);

  if (mode === 'index') {
    const intervalMinutes = toPositiveInt(args['interval-minutes'], 0);
    if (intervalMinutes <= 0) {
      await refreshIndexOnce(args);
      return;
    }

    const intervalMs = intervalMinutes * 60 * 1000;
    console.log(`[index] 已进入定时全量刷新模式，每 ${intervalMinutes} 分钟执行一次`);
    while (true) {
      try {
        await refreshIndexOnce(args);
      } catch (error) {
        console.error(`[index] 刷新失败: ${error.message}`);
      }
      await sleep(intervalMs);
    }
  }

  if (mode === 'detail') {
    await fetchDetailsOnce(args);
    return;
  }
}

main().catch((error) => {
  console.error(`❌ ${error.message}`);
  process.exit(1);
});
