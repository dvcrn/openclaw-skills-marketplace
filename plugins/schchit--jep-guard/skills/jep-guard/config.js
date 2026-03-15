/**
 * JEP Guard v1.0.2 - Configuration handler
 */

const fs = require('fs').promises;
const path = require('path');

const CONFIG_PATH = path.join(process.env.HOME || '.', '.jep-guard-config.json');

async function readConfig() {
  try {
    const data = await fs.readFile(CONFIG_PATH, 'utf8');
    return JSON.parse(data);
  } catch {
    return {
      logLevel: 'minimal',
      jepPrivateKey: null,
      logPath: path.join(process.env.HOME || '.', '.jep-guard-audit.log')
    };
  }
}

async function saveConfig(config) {
  await fs.writeFile(CONFIG_PATH, JSON.stringify(config, null, 2));
}

module.exports = async function configure(args, context) {
  const config = await readConfig();
  
  if (args.length === 0) {
    // Show current config (hide private key)
    const display = { ...config };
    if (display.jepPrivateKey) {
      display.jepPrivateKey = '[CONFIGURED]';
    }
    return {
      output: JSON.stringify(display, null, 2),
      type: 'json'
    };
  }
  
  const command = args[0];
  
  if (command === 'set' && args.length >= 3) {
    const key = args[1];
    const value = args.slice(2).join(' ');
    
    if (key === 'logLevel') {
      if (['minimal', 'normal', 'verbose'].includes(value)) {
        config.logLevel = value;
        await saveConfig(config);
        await context.ui.notify(`Log level set to ${value}`);
        return { output: `✅ Log level: ${value}` };
      }
      return { output: '❌ Invalid level. Use: minimal, normal, verbose' };
    }
    
    if (key === 'logPath') {
      config.logPath = value;
      await saveConfig(config);
      return { output: `✅ Log path: ${value}` };
    }
  }
  
  if (command === 'show') {
    // Show recent logs (redacted)
    try {
      const logs = await fs.readFile(config.logPath, 'utf8');
      const lines = logs.split('\n').filter(l => l).slice(-10);
      return { output: lines.join('\n') };
    } catch {
      return { output: 'No logs found' };
    }
  }
  
  return {
    output: 'Commands:\n' +
            '  config                  - Show current config\n' +
            '  config set logLevel X   - Set level (minimal/normal/verbose)\n' +
            '  config show             - Show recent logs\n' +
            '  keygen                  - Generate JEP keys\n' +
            '  export                  - Export audit logs'
  };
};
