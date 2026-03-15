/**
 * Auto Update Checker - 按需更新检查器
 * 
 * 核心逻辑：
 * 1. 在 skill 被触发时检查更新
 * 2. 根据版本变化分级处理
 * 3. 缓存结果避免频繁请求
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const CACHE_DIR = path.join(process.env.HOME, '.openclaw', 'skill-update-cache');
const LOG_PATH = path.join(process.env.HOME, '.openclaw', 'logs', 'auto-update-skill.log');
const CONFIG_PATH = path.join(process.env.HOME, '.openclaw', 'auto-update-skill.json');

// 默认配置
const DEFAULT_CONFIG = {
  mode: 'interactive',
  cacheDuration: 24 * 60 * 60 * 1000, // 24小时
  autoUpgrade: {
    patch: true,
    minor: false,
    major: false
  },
  remindInterval: 7 * 24 * 60 * 60 * 1000, // 7天
  blacklist: [],
  quietHours: {
    start: '22:00',
    end: '08:00'
  }
};

// 日志
function log(level, message) {
  const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
  const line = `[${timestamp}] ${level}: ${message}`;
  
  // 控制台输出（根据级别）
  if (level === 'ERROR') console.error(line);
  else if (level === 'WARN') console.warn(line);
  else console.log(line);
  
  // 写入日志
  try {
    const logDir = path.dirname(LOG_PATH);
    if (!fs.existsSync(logDir)) fs.mkdirSync(logDir, { recursive: true });
    fs.appendFileSync(LOG_PATH, line + '\n');
  } catch (e) {}
}

// 加载配置
function loadConfig() {
  try {
    if (fs.existsSync(CONFIG_PATH)) {
      const userConfig = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
      return { ...DEFAULT_CONFIG, ...userConfig };
    }
  } catch (e) {
    log('WARN', `加载配置失败: ${e.message}`);
  }
  return DEFAULT_CONFIG;
}

// 解析版本
function parseVersion(version) {
  const parts = version.split('.').map(Number);
  return {
    major: parts[0] || 0,
    minor: parts[1] || 0,
    patch: parts[2] || 0,
    raw: version
  };
}

// 比较版本
function compareVersion(v1, v2) {
  const a = parseVersion(v1);
  const b = parseVersion(v2);
  
  if (a.major !== b.major) return a.major > b.major ? 1 : -1;
  if (a.minor !== b.minor) return a.minor > b.minor ? 1 : -1;
  if (a.patch !== b.patch) return a.patch > b.patch ? 1 : -1;
  return 0;
}

// 获取更新类型
function getUpdateType(current, latest) {
  const c = parseVersion(current);
  const l = parseVersion(latest);
  
  if (l.major > c.major) return 'major';
  if (l.minor > c.minor) return 'minor';
  if (l.patch > c.patch) return 'patch';
  return 'none';
}

// 获取 skill 当前版本
function getCurrentVersion(skillName) {
  try {
    const output = execSync('clawhub list', { encoding: 'utf8' });
    const lines = output.split('\n');
    
    for (const line of lines) {
      const match = line.match(new RegExp(`^${skillName}\\s+(\\d+\\.\\d+\\.\\d+)$`));
      if (match) return match[1];
    }
  } catch (e) {
    log('ERROR', `获取 ${skillName} 当前版本失败: ${e.message}`);
  }
  return null;
}

// 获取 skill 最新版本
function getLatestVersion(skillName) {
  try {
    const output = execSync(`clawhub inspect ${skillName} 2>/dev/null || echo "{}"`, { encoding: 'utf8' });
    const info = JSON.parse(output);
    return info.version || null;
  } catch (e) {
    return null;
  }
}

// 缓存相关
function getCachePath(skillName) {
  if (!fs.existsSync(CACHE_DIR)) {
    fs.mkdirSync(CACHE_DIR, { recursive: true });
  }
  return path.join(CACHE_DIR, `${skillName}.json`);
}

function getCachedVersion(skillName) {
  try {
    const cachePath = getCachePath(skillName);
    if (!fs.existsSync(cachePath)) return null;
    
    const cache = JSON.parse(fs.readFileSync(cachePath, 'utf8'));
    const config = loadConfig();
    
    // 检查缓存是否过期
    if (Date.now() - cache.timestamp > config.cacheDuration) {
      return null;
    }
    
    return cache;
  } catch (e) {
    return null;
  }
}

function setCachedVersion(skillName, version, skipped = false) {
  try {
    const cachePath = getCachePath(skillName);
    const cache = {
      skillName,
      version,
      timestamp: Date.now(),
      skipped,
      skippedAt: skipped ? Date.now() : null
    };
    fs.writeFileSync(cachePath, JSON.stringify(cache, null, 2));
  } catch (e) {
    log('WARN', `缓存写入失败: ${e.message}`);
  }
}

// 检查是否在安静时段
function isQuietHours(config) {
  const now = new Date();
  const currentTime = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
  
  const { start, end } = config.quietHours;
  
  if (start < end) {
    return currentTime >= start && currentTime <= end;
  } else {
    // 跨天的情况（如 22:00 - 08:00）
    return currentTime >= start || currentTime <= end;
  }
}

// 检查是否应该提醒（跳过间隔）
function shouldRemind(skillName, config) {
  try {
    const cachePath = getCachePath(skillName);
    if (!fs.existsSync(cachePath)) return true;
    
    const cache = JSON.parse(fs.readFileSync(cachePath, 'utf8'));
    
    // 如果用户跳过了，检查是否过了 remindInterval
    if (cache.skipped && cache.skippedAt) {
      return Date.now() - cache.skippedAt > config.remindInterval;
    }
    
    return true;
  } catch (e) {
    return true;
  }
}

// 备份 skill
function backupSkill(skillName, version) {
  try {
    const backupDir = path.join(process.env.HOME, '.openclaw', 'skill-backups');
    const skillPath = path.join(process.env.HOME, '.openclaw', 'skills', skillName);
    const backupPath = path.join(backupDir, `${skillName}@${version}`);
    
    if (!fs.existsSync(backupDir)) {
      fs.mkdirSync(backupDir, { recursive: true });
    }
    
    if (fs.existsSync(skillPath)) {
      execSync(`cp -r "${skillPath}" "${backupPath}"`);
      log('INFO', `备份 ${skillName}@${version} 成功`);
      return true;
    }
  } catch (e) {
    log('ERROR', `备份 ${skillName} 失败: ${e.message}`);
  }
  return false;
}

// 执行更新
function performUpdate(skillName, version) {
  try {
    log('INFO', `正在更新 ${skillName} 到 ${version}...`);
    execSync(`clawhub update ${skillName} --version ${version}`, { encoding: 'utf8' });
    log('INFO', `${skillName} 更新成功`);
    return true;
  } catch (e) {
    log('ERROR', `更新 ${skillName} 失败: ${e.message}`);
    return false;
  }
}

// 回滚
function rollbackSkill(skillName, version) {
  try {
    const backupPath = path.join(process.env.HOME, '.openclaw', 'skill-backups', `${skillName}@${version}`);
    const skillPath = path.join(process.env.HOME, '.openclaw', 'skills', skillName);
    
    if (!fs.existsSync(backupPath)) {
      log('ERROR', `备份不存在: ${backupPath}`);
      return false;
    }
    
    execSync(`rm -rf "${skillPath}"`);
    execSync(`cp -r "${backupPath}" "${skillPath}"`);
    log('INFO', `回滚 ${skillName} 到 ${version} 成功`);
    return true;
  } catch (e) {
    log('ERROR', `回滚 ${skillName} 失败: ${e.message}`);
    return false;
  }
}

// 主检查函数
async function checkAndPrompt(skillName, options = {}) {
  const config = loadConfig();
  const { interactive = true, quiet = false } = options;
  
  // 检查黑名单
  if (config.blacklist.includes(skillName)) {
    log('DEBUG', `${skillName} 在黑名单中，跳过检查`);
    return { shouldUpdate: false, reason: 'blacklisted' };
  }
  
  // 获取当前版本
  const currentVersion = getCurrentVersion(skillName);
  if (!currentVersion) {
    log('WARN', `无法获取 ${skillName} 当前版本`);
    return { shouldUpdate: false, reason: 'not_installed' };
  }
  
  // 检查缓存
  const cached = getCachedVersion(skillName);
  let latestVersion;
  
  if (cached && cached.version) {
    latestVersion = cached.version;
    log('DEBUG', `使用缓存版本: ${latestVersion}`);
  } else {
    latestVersion = getLatestVersion(skillName);
    if (latestVersion) {
      setCachedVersion(skillName, latestVersion);
    }
  }
  
  if (!latestVersion) {
    log('WARN', `无法获取 ${skillName} 最新版本`);
    return { shouldUpdate: false, reason: 'fetch_failed' };
  }
  
  // 比较版本
  const cmp = compareVersion(latestVersion, currentVersion);
  if (cmp <= 0) {
    log('DEBUG', `${skillName} 已是最新版本 ${currentVersion}`);
    return { shouldUpdate: false, currentVersion, latestVersion, reason: 'up_to_date' };
  }
  
  // 获取更新类型
  const updateType = getUpdateType(currentVersion, latestVersion);
  
  // 检查是否应该提醒
  if (!shouldRemind(skillName, config)) {
    log('DEBUG', `${skillName} 跳过提醒（用户近期已拒绝）`);
    return { shouldUpdate: false, currentVersion, latestVersion, updateType, reason: 'remind_delayed' };
  }
  
  // 安静时段不提醒
  if (isQuietHours(config) && interactive) {
    log('DEBUG', '当前为安静时段，跳过提醒');
    return { shouldUpdate: false, currentVersion, latestVersion, updateType, reason: 'quiet_hours' };
  }
  
  // 根据更新类型处理
  const result = {
    skillName,
    currentVersion,
    latestVersion,
    updateType,
    shouldUpdate: false
  };
  
  // Patch 自动升级
  if (updateType === 'patch' && config.autoUpgrade.patch) {
    if (!quiet) console.log(`[ℹ️] ${skillName} ${currentVersion} → ${latestVersion} (patch)，自动升级中...`);
    
    if (backupSkill(skillName, currentVersion)) {
      if (performUpdate(skillName, latestVersion)) {
        result.shouldUpdate = true;
        result.success = true;
        if (!quiet) console.log(`[✓] ${skillName} 已升级，继续执行任务...`);
      } else {
        rollbackSkill(skillName, currentVersion);
        result.success = false;
        if (!quiet) console.log(`[✗] ${skillName} 升级失败，已回滚，继续执行当前版本...`);
      }
    }
    return result;
  }
  
  // Minor 建议升级
  if (updateType === 'minor') {
    if (!interactive) {
      if (config.autoUpgrade.minor) {
        // 自动升级
        if (backupSkill(skillName, currentVersion) && performUpdate(skillName, latestVersion)) {
          result.shouldUpdate = true;
          result.success = true;
        }
      }
      return result;
    }
    
    if (!quiet) {
      console.log(`\n[📦] ${skillName} 有更新: ${currentVersion} → ${latestVersion}`);
      console.log(`     更新类型: minor（新功能，向后兼容）`);
    }
    
    // 这里应该询问用户，但在自动化环境中可能需要其他方式
    // 简化处理：非交互模式下跳过
    return { ...result, shouldUpdate: false, reason: 'needs_confirmation' };
  }
  
  // Major 需确认
  if (updateType === 'major') {
    if (!quiet) {
      console.log(`\n[⚠️] ${skillName} 重大版本更新: ${currentVersion} → ${latestVersion}`);
      console.log(`     ⚠️ 此更新包含重大变更，可能影响现有功能`);
      console.log(`     建议查看更新文档后再决定\n`);
    }
    
    return { ...result, shouldUpdate: false, reason: 'major_needs_confirmation' };
  }
  
  return result;
}

// 导出
module.exports = {
  checkAndPrompt,
  getCurrentVersion,
  getLatestVersion,
  getUpdateType,
  compareVersion,
  parseVersion,
  backupSkill,
  performUpdate,
  rollbackSkill,
  loadConfig,
  log
};
