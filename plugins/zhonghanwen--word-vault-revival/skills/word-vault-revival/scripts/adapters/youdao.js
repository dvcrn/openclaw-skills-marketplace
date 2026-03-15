function isNoiseLine(line) {
  const value = String(line || '').trim();
  if (!value) return true;
  if (/^(有道|youdao)$/iu.test(value)) return true;
  if (/^(单词本|收藏|生词本|我的单词|今日学习|复习|搜索|筛选|更多|设置)$/u.test(value)) return true;
  if (/^\d+\/\d+$/.test(value)) return true;
  return false;
}

function looksLikeWord(line) {
  const value = String(line || '').trim();
  if (!value) return false;
  if (value.length > 80) return false;
  if (/^[-–—•·.,;:()\[\]{}]+$/.test(value)) return false;
  return /^[\p{Script=Latin}\p{Script=Han}\d][\p{L}\p{M}\p{N}\p{P}\p{S}\s'-]{0,79}$/u.test(value);
}

function maybePhonetic(line) {
  const value = String(line || '').trim();
  return /^(\[[^\]]+\]|\/.+\/|(英|美)\s*\[[^\]]+\])$/u.test(value) ? value : '';
}

function looksLikeMeaning(line) {
  const value = String(line || '').trim();
  if (!value) return false;
  if (value.length > 160) return false;
  if (/^(n\.|v\.|vt\.|vi\.|adj\.|adv\.|prep\.|pron\.|num\.|art\.|int\.|abbr\.|phr\.)/i.test(value)) return true;
  if (/[\p{Script=Han}]/u.test(value)) return true;
  return value.split(/\s+/).length >= 1;
}

// 统一规则：保留原语言/左侧文本作为 word，右侧释义作为 meanings。
function normalizeItem(sourceText, targetText, extras = {}) {
  const cleanSource = String(sourceText || '').trim();
  const cleanTarget = String(targetText || '').trim();
  if (!cleanSource || !cleanTarget) return null;

  return {
    word: cleanSource,
    phonetic: extras.phonetic || '',
    meanings: cleanTarget.split(/[；;]+/).map((part) => part.trim()).filter(Boolean),
    example: extras.example || '',
    source: 'youdao',
    tags: ['saved']
  };
}

function extractYoudaoItemsFromText(text) {
  const rawLines = String(text || '')
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);

  // 先裁出真正的词条区：通常位于“所有语言”之后、“共 X 页/到第 页”之前。
  const startIdx = rawLines.findIndex((line) => /所有语言/.test(line));
  const endIdx = rawLines.findIndex((line) => /共\s*\d+\s*页|到第\s*页|到第 页/.test(line));
  const scoped = rawLines.slice(startIdx >= 0 ? startIdx + 1 : 0, endIdx >= 0 ? endIdx : rawLines.length);

  const lines = scoped
    .map((line) => line.trim())
    .filter((line) => line && !isNoiseLine(line));

  const items = [];
  const seen = new Set();

  const pushItem = (item) => {
    if (!item) return;
    const key = `${item.word}__${item.meanings.join('|')}`.toLowerCase();
    if (seen.has(key)) return;
    seen.add(key);
    items.push(item);
  };

  // 优先识别“单词行 + 释义行”这种有道单词本主结构。
  for (let i = 0; i < lines.length - 1; i += 1) {
    const word = lines[i];
    const next = lines[i + 1];
    const third = lines[i + 2] || '';
    const fourth = lines[i + 3] || '';
    const phonetic = maybePhonetic(next);
    const meaning = phonetic ? third : next;
    const example = phonetic ? (looksLikeMeaning(fourth) && !looksLikeWord(fourth) ? fourth : '') : '';

    if (!looksLikeWord(word) || !looksLikeMeaning(meaning)) continue;

    // 词条必须更像“真正单词”，释义必须更像“中文/词性说明”
    if (/^(排序方式|时间降序|语言|所有语言|共\s*\d+\s*页|到第|点击发音|词典|翻译|全部产品|个词句)$/u.test(word) || /^\d+个词句$/u.test(word)) continue;
    if (/^(排序方式|时间降序|语言|所有语言|共\s*\d+\s*页|到第|点击发音|词典|翻译|全部产品|个词句)$/u.test(meaning) || /^\d+个词句$/u.test(meaning)) continue;
    if (!/[\p{Script=Han}]|^(n\.|v\.|vt\.|vi\.|adj\.|adv\.|prep\.|pron\.|num\.|art\.|int\.|abbr\.|phr\.)/iu.test(meaning)) continue;

    pushItem(normalizeItem(word, meaning, { phonetic, example }));
    i += phonetic ? 2 : 1;
  }

  // 再兜底识别“word - meaning”同一行结构，但只接受更像词典条目的行。
  for (const line of lines) {
    const match = line.match(/^(.+?)\s*(?:[—-]|→|:|：|\|)\s*(.+)$/u);
    if (!match) continue;
    const left = match[1].trim();
    const right = match[2].trim();
    if (!looksLikeWord(left) || !looksLikeMeaning(right)) continue;
    if (/^(排序方式|时间降序|语言|所有语言|共\s*\d+\s*页|到第)$/u.test(left)) continue;
    pushItem(normalizeItem(left, right));
  }

  return items;
}

export function detectYoudaoPageFromText(text, url = '') {
  const raw = String(text || '');
  const pageItems = extractYoudaoItemsFromText(raw);
  const markerHit = ['有道', 'youdao', '单词本', '生词本', '收藏'].some((marker) => raw.includes(marker));

  return {
    platform: 'youdao',
    url,
    loggedIn: markerHit,
    pageReady: pageItems.length > 0 || markerHit,
    pageCount: pageItems.length,
    estimatedTotal: pageItems.length
  };
}

export function extractYoudaoPageFromText(text) {
  const pageItems = extractYoudaoItemsFromText(text);
  return {
    ...detectYoudaoPageFromText(text),
    pageItems,
    pageCount: pageItems.length
  };
}

export async function loadYoudaoWords(context = {}) {
  const { pageText = '', url = '' } = context;
  const detect = detectYoudaoPageFromText(pageText, url);

  if (!detect.pageReady) {
    throw new Error('有道页面尚未就绪：请先用 OpenClaw 浏览器登录有道单词本/收藏页，并导出当前页文本。');
  }

  const { pageItems } = extractYoudaoPageFromText(pageText);
  if (!pageItems.length) {
    throw new Error('有道页面已打开，但当前页没有解析出词条。');
  }

  return pageItems;
}
