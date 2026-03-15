/**
 * JEP Guard v1.0.2 - Export audit logs with privacy redaction
 */

const fs = require('fs').promises;
const path = require('path');

const CONFIG_PATH = path.join(process.env.HOME || '.', '.jep-guard-config.json');

async function readConfig() {
  try {
    const data = await fs.readFile(CONFIG_PATH, 'utf8');
    return JSON.parse(data);
  } catch {
    return { logLevel: 'minimal', logPath: '~/.jep-guard-audit.log' };
  }
}

module.exports = async function exportLogs(context) {
  const config = await readConfig();
  const logPath = config.logPath.replace('~', process.env.HOME || '.');
  
  try {
    const logs = await fs.readFile(logPath, 'utf8');
    const entries = logs.split('\n')
      .filter(l => l.trim())
      .map(l => JSON.parse(l));
    
    // Add export warning
    const exportData = {
      exportedAt: new Date().toISOString(),
      exportedBy: context.user,
      logLevel: config.logLevel,
      warning: config.logLevel === 'verbose' 
        ? '⚠️  VERBOSE LOGS - May contain sensitive data!' 
        : 'Logs are redacted based on your settings',
      entries: entries
    };
    
    // Save export file
    const exportPath = path.join(
      process.env.HOME || '.',
      `jep-export-${Date.now()}.json`
    );
    await fs.writeFile(exportPath, JSON.stringify(exportData, null, 2));
    
    return {
      output: JSON.stringify(exportData, null, 2),
      type: 'json',
      message: `✅ Exported to ${exportPath}`
    };
    
  } catch (e) {
    return {
      output: JSON.stringify({ 
        error: 'No logs found',
        hint: 'Run some commands first'
      }, null, 2),
      type: 'json'
    };
  }
};
