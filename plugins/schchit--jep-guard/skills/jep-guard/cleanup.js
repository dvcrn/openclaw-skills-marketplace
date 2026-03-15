/**
 * JEP Guard v1.0.2 - Clean uninstall
 */

const fs = require('fs').promises;
const path = require('path');

const CONFIG_PATH = path.join(process.env.HOME || '.', '.jep-guard-config.json');
const LOG_PATH = path.join(process.env.HOME || '.', '.jep-guard-audit.log');

module.exports = async function onUninstall(context) {
  // Ask about logs
  const choice = await context.ui.confirm({
    title: '🗑️ JEP Guard Uninstall',
    message: 'Delete audit logs?',
    buttons: ['✅ Delete logs', '🚫 Keep logs']
  });
  
  if (choice === '✅ Delete logs') {
    try {
      await fs.unlink(LOG_PATH);
    } catch {
      // Log file might not exist
    }
  }
  
  // Always delete config (contains private key)
  try {
    await fs.unlink(CONFIG_PATH);
  } catch {
    // Config might not exist
  }
  
  await context.ui.notify('JEP Guard removed. Thanks for trying!');
  return true;
};
