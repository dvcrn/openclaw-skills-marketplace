const fs = require('fs');
const path = require('path');
const { getStpAssetsDir, ensureDir } = require('./storage');

function getLockDir(lockName) {
  const lockRoot = path.join(getStpAssetsDir(), '.locks');
  ensureDir(lockRoot);
  return path.join(lockRoot, String(lockName) + '.lock');
}

function isStale(lockDir, staleMs) {
  try {
    const st = fs.statSync(lockDir);
    return (Date.now() - st.mtimeMs) > staleMs;
  } catch (e) {
    return false;
  }
}

function acquireLock(lockName, opts) {
  const o = opts || {};
  const staleMs = Number(o.staleMs || 2 * 60 * 60 * 1000);
  const lockDir = getLockDir(lockName);
  const ownerFile = path.join(lockDir, 'owner.json');

  function tryCreate() {
    try {
      fs.mkdirSync(lockDir);
      fs.writeFileSync(ownerFile, JSON.stringify({
        pid: process.pid,
        lock: lockName,
        acquired_at: new Date().toISOString(),
      }, null, 2), 'utf8');
      return { ok: true, lockDir };
    } catch (e) {
      if (e && e.code === 'EEXIST') return { ok: false, reason: 'exists' };
      return { ok: false, reason: 'error', error: e };
    }
  }

  let first = tryCreate();
  if (first.ok) return first;
  if (first.reason === 'exists' && isStale(lockDir, staleMs)) {
    try { fs.rmSync(lockDir, { recursive: true, force: true }); } catch (e) { /* best effort */ }
    first = tryCreate();
    if (first.ok) return first;
  }
  return { ok: false, reason: first.reason || 'locked' };
}

function releaseLock(lockState) {
  if (!lockState || !lockState.lockDir) return;
  try { fs.rmSync(lockState.lockDir, { recursive: true, force: true }); } catch (e) { /* best effort */ }
}

async function withFileLock(lockName, fn, opts) {
  const lk = acquireLock(lockName, opts);
  if (!lk.ok) {
    return { __lock_skipped: true, lock: lockName, reason: lk.reason || 'locked' };
  }
  try {
    return await fn();
  } finally {
    releaseLock(lk);
  }
}

module.exports = {
  acquireLock,
  releaseLock,
  withFileLock,
};
