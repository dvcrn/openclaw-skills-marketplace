import fs from 'fs';
import { loadGoogleWords, detectGoogleSavedPageFromText } from './adapters/google.js';
import { loadYoudaoWords, detectYoudaoPageFromText } from './adapters/youdao.js';
import { dedupeWords } from './lib/normalize.js';
import { readJson, resolveSkillPath, writeJson } from './lib/io.js';
import { getPlatformState, getSelectedSources, loadRuntimeConfig } from './platform-runtime.js';

const runtime = loadRuntimeConfig();
const sources = getSelectedSources(runtime, process.argv.slice(2));

const loaders = {
  google: syncGoogle,
  youdao: syncYoudao
};

const warnings = [];
const sourceSummaries = [];
const aggregatePath = resolveSkillPath('data', 'words.json');
const aggregateBeforeSync = readJson(aggregatePath, []);
const platformLibraries = loadPlatformLibraries(runtime, aggregateBeforeSync);

for (const source of sources) {
  const loader = loaders[source];
  const platformState = getPlatformState(runtime.platforms[source] || { key: source, label: source, pageTextFile: `./data/cache/${source}-page.txt`, savedUrl: '' });

  if (!loader) {
    warnings.push(`未知词源：${source}`);
    continue;
  }

  try {
    const result = await loader(platformState);
    const normalizedItems = dedupeWords(result.items);
    platformLibraries[source] = normalizedItems;
    writeJson(getPlatformWordsPath(source), normalizedItems);
    sourceSummaries.push({
      source,
      label: platformState.label,
      total: normalizedItems.length,
      note: result.note || '',
      savedUrl: platformState.savedUrl,
      cachePath: platformState.cachePath,
      nextAction: result.nextAction || '',
      storage: getPlatformWordsPath(source)
    });
  } catch (error) {
    warnings.push(`${source}: ${error.message}`);
    sourceSummaries.push({
      source,
      label: platformState.label,
      total: Array.isArray(platformLibraries[source]) ? platformLibraries[source].length : 0,
      note: '',
      savedUrl: platformState.savedUrl,
      cachePath: platformState.cachePath,
      nextAction: platformState.nextAction,
      storage: getPlatformWordsPath(source)
    });
  }
}

const normalized = dedupeWords(Object.values(platformLibraries).flat());
writeJson(aggregatePath, normalized);

console.log(JSON.stringify({
  ok: normalized.length > 0,
  total: normalized.length,
  previousTotal: Array.isArray(aggregateBeforeSync) ? aggregateBeforeSync.length : 0,
  sources,
  output: aggregatePath,
  perPlatform: Object.fromEntries(
    Object.entries(platformLibraries).map(([source, items]) => [source, Array.isArray(items) ? items.length : 0])
  ),
  sourceSummaries,
  warnings,
  title: runtime.title,
  subtitle: runtime.subtitle,
  browserFirst: true,
  storageMode: 'per-platform-files-plus-aggregate'
}, null, 2));

if (normalized.length === 0) {
  process.exitCode = 1;
}

function loadPlatformLibraries(config, aggregateWords) {
  const result = {};
  const knownPlatforms = Object.keys(config.platforms || {});

  for (const platform of knownPlatforms) {
    const platformPath = getPlatformWordsPath(platform);
    const platformWords = readJson(platformPath, null);

    if (Array.isArray(platformWords)) {
      result[platform] = dedupeWords(platformWords);
      continue;
    }

    const migrated = Array.isArray(aggregateWords)
      ? dedupeWords(aggregateWords.filter((item) => String(item?.source || '').trim() === platform))
      : [];

    result[platform] = migrated;
    if (migrated.length > 0) {
      writeJson(platformPath, migrated);
    }
  }

  return result;
}

function getPlatformWordsPath(source) {
  return resolveSkillPath('data', 'platforms', `${source}.json`);
}

async function syncGoogle(platform) {
  const pageText = readPageText(platform);
  const detect = detectGoogleSavedPageFromText(pageText, platform.savedUrl);

  if (!detect.pageReady) {
    throw new Error([
      'Google 页面未就绪。',
      `请先用 OpenClaw 浏览器打开：${platform.savedUrl}`,
      '如果还没登录，就先登录；登录后再抓取当前收藏页。'
    ].join(' '));
  }

  const items = await loadGoogleWords({ pageText, url: platform.savedUrl });
  return {
    items,
    note: detect.itemCountText || 'google current page synced',
    nextAction: '当前版本基于页面缓存同步；如需更多词条，请继续在浏览器中翻页并补充缓存后再同步'
  };
}

async function syncYoudao(platform) {
  const pageText = readPageText(platform);
  const detect = detectYoudaoPageFromText(pageText, platform.savedUrl);

  if (!detect.pageReady) {
    throw new Error([
      '有道页面未就绪。',
      `请先用 OpenClaw 浏览器打开：${platform.savedUrl}`,
      '如果还没登录，就先登录；登录后进入单词本/收藏页再抓取。'
    ].join(' '));
  }

  const items = await loadYoudaoWords({ pageText, url: platform.savedUrl });
  return {
    items,
    note: detect.pageCount ? `youdao current page items: ${detect.pageCount}` : 'youdao current page synced',
    nextAction: '当前版本基于页面缓存同步；如需更多词条，请继续在浏览器中翻页并补充缓存后再同步'
  };
}

function readPageText(platform) {
  if (!platform.cacheExists) {
    throw new Error(`当前还没有抓到 ${platform.label} 的收藏页缓存。请先打开 ${platform.savedUrl} 并抓取当前页。`);
  }

  return fs.readFileSync(platform.cachePath, 'utf8');
}
