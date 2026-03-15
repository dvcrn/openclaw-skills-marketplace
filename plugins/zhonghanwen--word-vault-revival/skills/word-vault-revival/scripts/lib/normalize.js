export function normalizeWordItem(item, fallbackSource = 'unknown') {
  if (!item || typeof item !== 'object') return null;

  const word = String(item.word || item.term || '').trim();
  if (!word) return null;

  const meanings = Array.isArray(item.meanings)
    ? item.meanings
    : item.meaning
      ? [item.meaning]
      : item.translation
        ? [item.translation]
        : [];

  return {
    word,
    phonetic: item.phonetic ? String(item.phonetic).trim() : '',
    meanings: meanings.map((value) => String(value).trim()).filter(Boolean),
    example: item.example ? String(item.example).trim() : '',
    source: String(item.source || fallbackSource || 'unknown').trim(),
    tags: Array.isArray(item.tags) ? item.tags.map((tag) => String(tag).trim()).filter(Boolean) : [],
    updatedAt: item.updatedAt || new Date().toISOString()
  };
}

export function dedupeWords(items) {
  const map = new Map();

  for (const item of items) {
    if (!item) continue;
    const key = item.word.toLowerCase();
    if (!map.has(key)) {
      map.set(key, item);
      continue;
    }

    const existing = map.get(key);
    map.set(key, {
      ...existing,
      phonetic: existing.phonetic || item.phonetic,
      meanings: unique([...existing.meanings, ...item.meanings]),
      example: existing.example || item.example,
      source: existing.source || item.source,
      tags: unique([...(existing.tags || []), ...(item.tags || [])]),
      updatedAt: newest(existing.updatedAt, item.updatedAt)
    });
  }

  return [...map.values()].sort((a, b) => a.word.localeCompare(b.word));
}

function unique(values) {
  return [...new Set(values.filter(Boolean))];
}

function newest(a, b) {
  return [a, b].filter(Boolean).sort().slice(-1)[0] || new Date().toISOString();
}
