export function renderWordMessage(item, options = {}) {
  const lines = [];
  const title = String(options.title || '').trim();
  const subtitle = String(options.subtitle || '').trim();

  if (title) lines.push(`✨ ${title}`);
  if (subtitle) lines.push(subtitle);
  if (title || subtitle) lines.push('');

  lines.push(`📚 今日单词：${item.word}`);

  if (item.phonetic) {
    lines.push(`🔊 音标：${item.phonetic}`);
  }

  if (item.meanings?.length) {
    lines.push(`📝 释义：${item.meanings.join(' / ')}`);
  }

  if (item.example) {
    lines.push(`💡 例句：${item.example}`);
  }

  lines.push(`🏷️ 来源：${item.source || 'unknown'}`);
  if (item.tags?.length) {
    lines.push(`🗂️ 标签：${item.tags.join(', ')}`);
  }

  lines.push('');
  lines.push('今天只记这一个，别贪多。');
  return lines.join('\n');
}
