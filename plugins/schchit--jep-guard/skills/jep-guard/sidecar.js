/**
 * JEP Guard v1.0.2 - Complete Fix
 * Fixed issues:
 * 1. Privacy: Configurable logging levels with defaults to minimal
 * 2. Environment: Proper JSON serialization for auth tokens
 * 3. Keys: Removed ALL placeholder keys - no signing without real key
 */

const fs = require('fs').promises;
const crypto = require('crypto');
const path = require('path');

const HIGH_RISK_COMMANDS = ['rm', 'rmdir', 'mv', 'cp', 'format', 'dd', 'truncate'];
const CONFIG_PATH = path.join(process.env.HOME || '.', '.jep-guard-config.json');
const DEFAULT_LOG_PATH = path.join(process.env.HOME || '.', '.jep-guard-audit.log');

// Try to load JEP SDK quietly - no errors if not found
let jepSdk;
try {
  jepSdk = require('@jep-eth/sdk');
} catch {
  // SDK not available - JEP features disabled
}

/**
 * Read config with defaults
 */
async function readConfig() {
  try {
    const data = await fs.readFile(CONFIG_PATH, 'utf8');
    return JSON.parse(data);
  } catch {
    // Default: minimal logging, no key, warn on install
    return {
      logLevel: 'minimal',
      jepPrivateKey: null,
      warnOnInstall: true,
      logPath: DEFAULT_LOG_PATH
    };
  }
}

/**
 * Save config
 */
async function saveConfig(config) {
  await fs.writeFile(CONFIG_PATH, JSON.stringify(config, null, 2));
}

/**
 * Safely parse auth token from environment
 * Fixes issue #2: Environment values are strings, not objects
 */
function parseAuthToken(envValue) {
  if (!envValue) return null;
  
  // If it's already an object (unlikely but possible)
  if (typeof envValue === 'object' && envValue !== null) {
    return envValue;
  }
  
  // Try to parse as JSON string
  if (typeof envValue === 'string') {
    try {
      const parsed = JSON.parse(envValue);
      // Validate it has the expected structure
      if (parsed && typeof parsed === 'object' && 
          parsed.id && typeof parsed.expires === 'number') {
        return parsed;
      }
    } catch {
      // Not valid JSON, ignore
    }
  }
  
  return null;
}

/**
 * Generate JEP receipt - ONLY with real key
 * Fixes issue #3: No placeholder keys, no signing without valid key
 */
async function generateJEPReceipt(action, context, config) {
  // No key = no receipt
  if (!jepSdk || !config.jepPrivateKey) {
    return { hasReceipt: false };
  }
  
  try {
    // Validate private key format (hex string)
    let privateKey;
    try {
      privateKey = Buffer.from(config.jepPrivateKey, 'hex');
      if (privateKey.length !== 32) {
        throw new Error('Invalid key length');
      }
    } catch {
      // Key is invalid, disable it
      config.jepPrivateKey = null;
      await saveConfig(config);
      return { hasReceipt: false, error: 'Invalid private key' };
    }
    
    const receipt = jepSdk.createReceipt({
      actor: context.user,
      decisionHash: crypto.createHash('sha256')
        .update(JSON.stringify(action))
        .digest('hex'),
      authorityScope: 'clawbot-command',
      valid: {
        from: Math.floor(Date.now() / 1000),
        until: Math.floor(Date.now() / 1000) + 86400 * 30 // 30 days
      }
    });
    
    const signed = await jepSdk.signReceipt(receipt, privateKey);
    const hash = await jepSdk.hashReceipt(receipt);
    
    return {
      hasReceipt: true,
      receiptHash: hash,
      signed: signed
    };
  } catch (e) {
    return { hasReceipt: false, error: e.message };
  }
}

/**
 * Log action with privacy controls
 * Fixes issue #1: Configurable logging levels, defaults to minimal
 */
async function logAction(command, args, auth, context, config) {
  // Base log entry - always include command name
  const logEntry = {
    timestamp: new Date().toISOString(),
    command: command,
    user: context.user,
    sessionId: auth?.id || crypto.randomUUID()
  };
  
  // Add arguments based on log level
  if (config.logLevel === 'verbose') {
    // Verbose: log everything (high risk)
    logEntry.args = args;
    logEntry.warning = 'VERBOSE MODE: Arguments may contain sensitive data';
  } else if (config.logLevel === 'normal') {
    // Normal: log args but try to redact common sensitive patterns
    const redactedArgs = args.map(arg => {
      const sensitivePatterns = [
        /token/i, /key/i, /secret/i, /pass/i, /auth/i,
        /^-[Hh]$/, /authorization/i, /bearer/i
      ];
      if (sensitivePatterns.some(p => p.test(arg))) {
        return '[REDACTED]';
      }
      return arg;
    });
    logEntry.args = redactedArgs;
  } // minimal: no args at all
  
  // Add JEP receipt if available (and key exists)
  if (config.jepPrivateKey) {
    const jep = await generateJEPReceipt({ command, args }, context, config);
    if (jep.hasReceipt) {
      logEntry.jepReceiptHash = jep.receiptHash;
    }
  }
  
  // Write to log file
  const logLine = JSON.stringify(logEntry) + '\n';
  const logPath = config.logPath || DEFAULT_LOG_PATH;
  
  try {
    await fs.appendFile(logPath, logLine);
  } catch (e) {
    // Fail silently - logging should not block execution
    console.error('Failed to write audit log:', e.message);
  }
  
  return logEntry;
}

/**
 * Main hook
 */
module.exports = async function beforeCommand(command, args, context) {
  const config = await readConfig();
  
  // Parse auth token safely (fixes issue #2)
  const authToken = parseAuthToken(context.env.JEP_TEMP_AUTH);
  
  // Always log (with privacy controls)
  await logAction(command, args, authToken, context, config);
  
  // Only intercept high-risk commands
  if (!HIGH_RISK_COMMANDS.includes(command)) {
    return { allow: true };
  }
  
  // Check for valid auth token
  if (authToken && authToken.expires > Math.floor(Date.now() / 1000)) {
    return { allow: true };
  }
  
  // Ask for confirmation
  const displayCmd = config.logLevel === 'minimal' 
    ? command 
    : `${command} ${args.join(' ')}`;
  
  const choice = await context.ui.confirm({
    title: '⚠️ High-Risk Operation',
    message: `Execute: ${displayCmd}`,
    buttons: ['✅ Allow Once', '🚫 Deny', '⚙️ Settings']
  });
  
  if (choice === '✅ Allow Once') {
    // Create new auth token (always store as JSON string - fixes issue #2)
    const newToken = {
      id: crypto.randomUUID(),
      expires: Math.floor(Date.now() / 1000) + 300, // 5 minutes
      command: command,
      createdAt: new Date().toISOString()
    };
    
    return {
      allow: true,
      env: { 
        JEP_TEMP_AUTH: JSON.stringify(newToken) // Always string
      }
    };
  }
  
  if (choice === '⚙️ Settings') {
    // Quick settings menu
    const newLevel = config.logLevel === 'minimal' ? 'normal' : 
                     config.logLevel === 'normal' ? 'verbose' : 'minimal';
    config.logLevel = newLevel;
    await saveConfig(config);
    await context.ui.notify(`Log level set to ${newLevel}`);
  }
  
  return { allow: false, reason: 'User denied' };
};
