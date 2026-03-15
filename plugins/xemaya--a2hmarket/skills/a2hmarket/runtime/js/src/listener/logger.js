function nowIso() {
  const now = new Date();
  const utc8Ms = now.getTime() + (8 * 60 * 60 * 1000);
  const beijing = new Date(utc8Ms);
  const year = beijing.getUTCFullYear();
  const month = String(beijing.getUTCMonth() + 1).padStart(2, '0');
  const day = String(beijing.getUTCDate()).padStart(2, '0');
  const hours = String(beijing.getUTCHours()).padStart(2, '0');
  const minutes = String(beijing.getUTCMinutes()).padStart(2, '0');
  const seconds = String(beijing.getUTCSeconds()).padStart(2, '0');
  const ms = String(beijing.getUTCMilliseconds()).padStart(3, '0');
  return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}.${ms}+08:00`;
}

function createLogger(verbose) {
  const allowDebug = Boolean(verbose);
  return {
    info(msg) {
      process.stdout.write(`${nowIso()} INFO a2hmarket-listener - ${msg}\n`);
    },
    warn(msg) {
      process.stdout.write(`${nowIso()} WARN a2hmarket-listener - ${msg}\n`);
    },
    error(msg) {
      process.stderr.write(`${nowIso()} ERROR a2hmarket-listener - ${msg}\n`);
    },
    debug(msg) {
      if (!allowDebug) return;
      process.stdout.write(`${nowIso()} DEBUG a2hmarket-listener - ${msg}\n`);
    },
  };
}

module.exports = {
  createLogger,
};
