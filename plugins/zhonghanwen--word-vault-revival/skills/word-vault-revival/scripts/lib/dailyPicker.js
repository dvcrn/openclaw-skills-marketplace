function hashString(input) {
  let hash = 2166136261;
  for (let i = 0; i < input.length; i += 1) {
    hash ^= input.charCodeAt(i);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}

function getDayNumber(date, timeZone = 'UTC') {
  const formatter = new Intl.DateTimeFormat('en-CA', {
    timeZone,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
  const [year, month, day] = formatter.format(date).split('-').map(Number);
  return Math.floor(Date.UTC(year, month - 1, day) / 86400000);
}

export function pickDailyWord(words, options = {}) {
  const { date = new Date(), timeZone = 'UTC' } = options;
  if (!Array.isArray(words) || words.length === 0) {
    throw new Error('词库为空，无法选择今日词');
  }

  const dayNumber = getDayNumber(date, timeZone);
  const cycleLength = words.length;
  const cycle = Math.floor(dayNumber / cycleLength);
  const offset = hashString(`word-vault-revival:${cycle}:${cycleLength}`) % cycleLength;
  const position = dayNumber % cycleLength;
  const index = (offset + position) % cycleLength;

  return {
    item: words[index],
    meta: {
      dayNumber,
      cycle,
      offset,
      index,
      cycleLength
    }
  };
}
