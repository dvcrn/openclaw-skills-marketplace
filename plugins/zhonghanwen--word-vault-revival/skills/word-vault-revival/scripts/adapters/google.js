function normalizeDirectionItem(sourceText, direction, targetText) {
  const dir = String(direction || '').trim();
  const source = String(sourceText || '').trim();
  const target = String(targetText || '').trim();

  if (!source || !target) return null;

  return {
    word: source,
    meanings: [target],
    source: 'google',
    tags: ['saved'],
    direction: dir
  };
}

function dedupeItems(items) {
  const seen = new Map();
  for (const item of items) {
    if (!item?.word) continue;
    const key = `${item.direction || ''}||${String(item.word).trim().toLowerCase()}`;
    if (!seen.has(key)) {
      seen.set(key, {
        ...item,
        meanings: [...new Set(item.meanings || [])]
      });
      continue;
    }
    const prev = seen.get(key);
    prev.meanings = [...new Set([...(prev.meanings || []), ...(item.meanings || [])])];
    seen.set(key, prev);
  }
  return [...seen.values()];
}

function extractGoogleItemsFromText(text) {
  const lines = String(text || '')
    .split('\n')
    .map((s) => s.trim())
    .filter(Boolean);

  const start = lines.findIndex((s) => /^第\s*\d+-\d+\s*个短语（共\s*\d+\s*个）$/.test(s));
  const relevant = start >= 0 ? lines.slice(start + 1) : lines;
  const items = [];

  for (let i = 0; i < relevant.length - 4; i += 1) {
    const a = relevant[i];
    const b = relevant[i + 1];
    const c = relevant[i + 2];
    const d = relevant[i + 3];
    const e = relevant[i + 4];

    if (b.includes('→') && c === 'star' && a === d) {
      const item = normalizeDirectionItem(a, b, e);
      if (item) items.push(item);
    }
  }

  return dedupeItems(items);
}

function walk(value, visit) {
  visit(value);
  if (Array.isArray(value)) {
    for (const item of value) walk(item, visit);
  } else if (value && typeof value === 'object') {
    for (const child of Object.values(value)) walk(child, visit);
  }
}

function parseGoogleItemsFromInitData(raw) {
  const items = [];
  const seenTriples = new Set();

  walk(raw, (node) => {
    if (!Array.isArray(node) || node.length < 5) return;
    const [id, srcLang, dstLang, sourceText, targetText] = node;
    if (typeof id !== 'string' || id.length < 6) return;
    if (typeof srcLang !== 'string' || typeof dstLang !== 'string') return;
    if (typeof sourceText !== 'string' || typeof targetText !== 'string') return;

    const direction = `${languageLabel(srcLang)} → ${languageLabel(dstLang)}`;
    const key = `${srcLang}|${dstLang}|${sourceText}|${targetText}`;
    if (seenTriples.has(key)) return;
    seenTriples.add(key);

    const item = normalizeDirectionItem(sourceText, direction, targetText);
    if (item) items.push(item);
  });

  return dedupeItems(items);
}

function languageLabel(code) {
  const map = {
    en: '英语',
    'zh-CN': '中文（简体）',
    fr: '法语',
    de: '德语',
    ja: '日语',
    ceb: '宿务语',
    id: '印尼语'
  };
  return map[code] || code;
}

export function buildGoogleLoginGuide() {
  return {
    platform: 'google',
    title: 'Google 收藏词登录引导',
    steps: [
      '用 OpenClaw 浏览器打开 Google 翻译已保存页面',
      '手动登录你的 Google 账号',
      '确认左侧/侧边栏能看到“已保存”',
      '登录完成后回复：登录好了'
    ],
    targetUrl: 'https://translate.google.com/saved?sl=en&tl=zh-CN&op=translate'
  };
}

export function detectGoogleSavedPageFromText(text, url = '') {
  const raw = String(text || '');
  const countMatch = raw.match(/第\s*(\d+)-(\d+)\s*个短语（共\s*(\d+)\s*个）/);
  const hasSaved = raw.includes('已保存');
  const hasDirection = raw.includes('→') || raw.includes('AF_initDataCallback');
  const hasListShape = raw.includes('star') || raw.includes('translate.google.com/saved') || raw.includes('"en","zh-CN"');
  const pageReady = Boolean((countMatch || raw.includes('AF_initDataCallback')) && hasDirection && (hasSaved || hasListShape));

  return {
    platform: 'google',
    url,
    loggedIn: raw.includes('Google 账号') || raw.includes('已保存') || raw.includes('AF_initDataCallback'),
    pageReady,
    itemCountText: countMatch ? countMatch[0] : '',
    estimatedTotal: countMatch ? Number(countMatch[3]) : 0
  };
}

export function extractGoogleSavedPageFromText(text) {
  const raw = String(text || '');
  const detect = detectGoogleSavedPageFromText(raw);

  let pageItems = [];
  let mode = 'text';

  const initDataMatch = raw.match(/AF_initDataCallback\((\{[\s\S]*?key:\s*['"]ds:1['"][\s\S]*?\})\);?/);
  if (initDataMatch) {
    try {
      // eslint-disable-next-line no-new-func
      const payload = Function(`return (${initDataMatch[1]});`)();
      pageItems = parseGoogleItemsFromInitData(payload);
      mode = 'initData';
    } catch {
      pageItems = [];
    }
  }

  if (!pageItems.length) {
    pageItems = extractGoogleItemsFromText(raw);
    mode = 'text';
  }

  return {
    ...detect,
    mode,
    pageItems,
    pageCount: pageItems.length
  };
}

export async function loadGoogleWords(context = {}) {
  const { pageText = '', url = '' } = context;
  const detect = detectGoogleSavedPageFromText(pageText, url);

  if (!detect.pageReady) {
    throw new Error('Google 页面尚未就绪：请先用 OpenClaw 浏览器登录 Google 翻译，并打开已保存页面。');
  }

  const { pageItems } = extractGoogleSavedPageFromText(pageText);
  if (!pageItems.length) {
    throw new Error('Google 已保存页面已识别，但当前页没有解析出词条。');
  }

  return pageItems;
}
