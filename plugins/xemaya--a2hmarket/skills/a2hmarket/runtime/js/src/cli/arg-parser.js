function parseOptions(args) {
  const rest = Array.isArray(args) ? [...args] : [];
  const options = {};
  for (let i = 0; i < rest.length; i += 1) {
    const raw = rest[i];
    if (!raw.startsWith("--")) continue;
    const key = raw.slice(2);
    const maybeValue = rest[i + 1];
    if (maybeValue == null || String(maybeValue).startsWith("--")) {
      options[key] = true;
      continue;
    }
    options[key] = maybeValue;
    i += 1;
  }
  return options;
}

module.exports = {
  parseOptions,
};
