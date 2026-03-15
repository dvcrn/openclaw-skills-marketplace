/**
 * JEP Guard v1.0.2 - Installation with privacy warning
 */

const fs = require('fs').promises;
const path = require('path');

const CONFIG_PATH = path.join(process.env.HOME || '.', '.jep-guard-config.json');

module.exports = async function onInstall(context) {
  // Show privacy warning (fixes issue #1)
  const warning = await context.ui.confirm({
    title: '⚠️ JEP Guard Privacy Warning',
    message: 'JEP Guard logs commands to ~/.jep-guard-audit.log\n\n' +
             'By default, ONLY command names are logged (safe).\n' +
             'You can change this in settings.\n\n' +
             'Sensitive data (passwords, tokens) may be logged if you:\n' +
             '- Set logLevel to "verbose"\n' +
             '- Use commands with sensitive arguments\n\n' +
             'Read SKILL.md for full details.\n\n' +
             'Continue installation?',
    buttons: ['✅ Yes, continue', '❌ Cancel']
  });
  
  if (warning !== '✅ Yes, continue') {
    return false;
  }
  
  // Create default config
  const config = {
    logLevel: 'minimal', // Safe default
    jepPrivateKey: null,
    warnOnInstall: true,
    logPath: path.join(process.env.HOME || '.', '.jep-guard-audit.log'),
    installedAt: new Date().toISOString()
  };
  
  await fs.writeFile(CONFIG_PATH, JSON.stringify(config, null, 2));
  
  // Show success message
  await context.ui.notify({
    title: '✅ JEP Guard Installed',
    message: 'Protection active!\n\n' +
             'Commands logged: ONLY names (safe mode)\n' +
             'To change: claw run jep-guard config\n\n' +
             'Generate keys: claw run jep-guard keygen',
    duration: 10000
  });
  
  return true;
};
