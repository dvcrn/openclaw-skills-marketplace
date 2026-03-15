#!/usr/bin/env node
/**
 * NoteX 上下文沉淀与写入脚本
 *
 * 功能：
 * 1) 新建 Notebook 并写入首个 Source（可选标题与正文）
 * 2) 向已有的 Notebook 追加新的 Source
 *
 * 用法示例：
 *   # 若已设置环境变量 XG_USER_TOKEN/XG_USER_ID/XG_USER_PERSONID，可省略 --key
 *   # 方式1：提供 CWork Key（推荐，自动获取 token）
 *   # 新建笔记本并存入内容：
 *   node notex-save-context.js --mode create --key CWORK_KEY --title "今日重点" --content "核心运营数据分析结论..."
 *   
 *   # 向现有笔记本追加内容：
 *   node notex-save-context.js --mode append --key CWORK_KEY --notebook-id nb_xxx --title "补充资料" --content "细节1..."
 *
 */

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

    if (payload && typeof payload === 'object') {
      if ('resultCode' in payload) {
        if (payload.resultCode !== 1) {
          throw new Error(payload.resultMsg || `API error (${payload.resultCode})`);
        }
        return payload.data;
      }
      if ('success' in payload) {
        if (!payload.success) {
          throw new Error(payload.error || payload.message || 'API error (success=false)');
        }
        return payload.data !== undefined ? payload.data : payload;
      }
    }

    return payload;
  } finally {
    clearTimeout(timeout);
  }
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

async function createNotebook(args) {
  const baseUrl = getBaseUrl(args);
  const headers = buildHeaders(args);
  const title = args.title || '无标题笔记本';
  const content = args.content || '';

  console.log(`[create] 正在新建笔记本...`);

  // 1. 获取用户的根目录 ID
  const rootIdUrl = buildApiUrl(baseUrl, '/api/notex/root-id');
  const rootIdData = await requestJson(rootIdUrl, {
    method: 'GET',
    headers,
    timeoutMs: 30000
  });

  const rootId = rootIdData.rootNotebookId;
  if (!rootId) {
    throw new Error('无法获取 Root Notebook ID，导致创建失败');
  }

  // 2. 在根目录下创建真正的 NoteX 表单/笔记本
  const createUrl = buildApiUrl(baseUrl, '/api/notex/notebooks');
  const createBody = {
    name: title,
    parentNotebookId: rootId
  };

  const notebookData = await requestJson(createUrl, {
    method: 'POST',
    headers,
    body: createBody,
    timeoutMs: 60000
  });

  const notebookId = notebookData.id || notebookData.notebookId;
  console.log(`🎉 成功新建 Notebook！`);
  console.log(`   Notebook ID: ${notebookId}`);

  // 3. 如果有内容，则向刚创建的笔记本下级写入来源（Source）
  if (content && notebookId) {
    console.log(`[create] 正在尝试将初始化内容存为源文件...`);
    const sourceUrl = buildApiUrl(baseUrl, `/api/notebooks/${notebookId}/sources`);
    const sourceBody = {
      title: `关于 ${title} 的资料`,
      type: 'text',
      content_text: content
    };

    const sourceData = await requestJson(sourceUrl, {
      method: 'POST',
      headers,
      body: sourceBody,
      timeoutMs: 60000
    });
    console.log(`✨ 成功存入预设笔记内容 (Source ID: ${sourceData.sourceId || sourceData.id})`);
  }
}

async function appendSource(args) {
  const baseUrl = getBaseUrl(args);
  const headers = buildHeaders(args);
  const notebookId = args['notebook-id'];
  const title = args.title || '追加资料';
  const content = args.content || '';

  if (!notebookId) {
    throw new Error('追加模式 (--mode append) 必须提供 --notebook-id');
  }

  // 根据后端实际提供的路由结构进行调整。此处假设为 POST /api/notebooks/{notebookId}/sources
  const url = buildApiUrl(baseUrl, `/api/notebooks/${notebookId}/sources`);
  console.log(`[append] 正在向 Notebook (${notebookId}) 追加来源...`);

  const body = {
    title: title,
    type: 'text',
    content_text: content
  };

  const data = await requestJson(url, {
    method: 'POST',
    headers,
    body,
    timeoutMs: 60000
  });

  console.log(`🎉 成功追加 Source！`);
  console.log(`   Source ID: ${data.id || data.sourceId || '未知'}`);
}

function printUsage() {
  console.log(`
用法:
  # 推荐使用 CWork Key（自动鉴权）
  node notex-save-context.js --mode create --key <CWorkKey> --title "知识库" --content "内容片段"
  node notex-save-context.js --mode append --key <CWorkKey> --notebook-id <nbId> --title "追加节点" --content "核心摘要"

可选参数:
  --key <CWorkKey>            CWork Key（推荐）
  --mode <create|append>      create=新建笔记本并保存内容，append=追加来源到已有笔记本
  --notebook-id <id>          目标笔记本 ID（mode=append 时必填）
  --title <text>              笔记本或来源标题
  --content <text>            要保存的长文本内容
  
  --base-url <url>            生产地址（仅支持 https://notex.aishuo.co/noteX 或 /noteX/api）
  `);
}

async function main() {
  const args = parseArgs();

  if (args.help) {
    printUsage();
    return;
  }

  const mode = args.mode;

  if (mode !== 'create' && mode !== 'append') {
    printUsage();
    throw new Error(`缺少或不支持的 mode: ${mode}`);
  }

  await resolveAuthContext(args);

  if (mode === 'create') {
    await createNotebook(args);
  } else if (mode === 'append') {
    await appendSource(args);
  }
}

main().catch((error) => {
  console.error(`❌ ${error.message}`);
  process.exit(1);
});
