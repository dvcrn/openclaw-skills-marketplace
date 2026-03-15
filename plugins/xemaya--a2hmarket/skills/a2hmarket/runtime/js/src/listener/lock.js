const fs = require("node:fs");
const path = require("node:path");

function ensureParent(filePath) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
}

function pidAlive(pid) {
  if (!Number.isFinite(pid) || pid <= 0) return false;
  try {
    process.kill(pid, 0);
    return true;
  } catch {
    return false;
  }
}

function checkListenerStatus(lockPath) {
  if (!fs.existsSync(lockPath)) {
    return { running: false, pid: null, lockPath };
  }
  
  const rawPid = String(fs.readFileSync(lockPath, "utf8") || "").trim();
  const pid = Number.parseInt(rawPid, 10);
  
  if (!Number.isFinite(pid) || pid <= 0) {
    return { running: false, pid: null, lockPath, stale: true };
  }
  
  const alive = pidAlive(pid);
  return { 
    running: alive, 
    pid: alive ? pid : null, 
    lockPath,
    stale: !alive 
  };
}

function cleanStaleLock(lockPath) {
  const status = checkListenerStatus(lockPath);
  if (status.stale) {
    fs.rmSync(lockPath, { force: true });
    return true;
  }
  return false;
}

function acquireSingleInstanceLock(lockPath) {
  ensureParent(lockPath);
  
  // First, try to clean up stale lock
  if (fs.existsSync(lockPath)) {
    const existing = Number.parseInt(String(fs.readFileSync(lockPath, "utf8") || "").trim(), 10);
    if (pidAlive(existing)) {
      throw new Error(`listener already running (lock: ${lockPath}, pid=${existing})`);
    }
    // Remove stale lock before attempting atomic create
    try {
      fs.rmSync(lockPath, { force: true });
    } catch {}
  }
  
  // Use atomic exclusive create (O_EXCL) to prevent race condition
  let fd;
  try {
    fd = fs.openSync(lockPath, "wx");
    fs.writeSync(fd, `${process.pid}\n`);
    fs.closeSync(fd);
  } catch (err) {
    if (err.code === "EEXIST") {
      // Another process created the lock between our check and create
      const existing = Number.parseInt(String(fs.readFileSync(lockPath, "utf8") || "").trim(), 10);
      throw new Error(`listener already running (lock: ${lockPath}, pid=${existing || "unknown"})`);
    }
    throw err;
  }
  
  return {
    release() {
      if (!fs.existsSync(lockPath)) return;
      const current = Number.parseInt(String(fs.readFileSync(lockPath, "utf8") || "").trim(), 10);
      if (current === process.pid) {
        fs.rmSync(lockPath, { force: true });
      }
    },
  };
}

module.exports = {
  acquireSingleInstanceLock,
  checkListenerStatus,
  cleanStaleLock,
  pidAlive,
};
