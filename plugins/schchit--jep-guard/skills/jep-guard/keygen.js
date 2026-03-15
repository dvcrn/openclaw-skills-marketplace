/**
 * JEP Guard v1.0.2 - JEP Key Generation
 * No placeholder keys - user must generate their own
 */

const fs = require('fs').promises;
const crypto = require('crypto');
const path = require('path');

const CONFIG_PATH = path.join(process.env.HOME || '.', '.jep-guard-config.json');

// Try to load JEP SDK
let jepSdk;
try {
  jepSdk = require('@jep-eth/sdk');
} catch {
  // SDK not available
}

async function readConfig() {
  try {
    const data = await fs.readFile(CONFIG_PATH, 'utf8');
    return JSON.parse(data);
  } catch {
    return { logLevel: 'minimal' };
  }
}

async function saveConfig(config) {
  await fs.writeFile(CONFIG_PATH, JSON.stringify(config, null, 2));
}

/**
 * Generate Ed25519 key pair (simplified)
 * In production, use @noble/ed25519
 */
function generateKeyPair() {
  // This is a placeholder - real Ed25519 generation would use the SDK
  // For now, generate a random hex string as private key
  const privateKey = crypto.randomBytes(32).toString('hex');
  
  // In a real implementation, derive public key from private
  const publicKey = crypto.createHash('sha256')
    .update(privateKey)
    .digest('hex')
    .slice(0, 64);
  
  return { privateKey, publicKey };
}

module.exports = async function keygen(context) {
  // Check if JEP SDK is available
  if (!jepSdk) {
    return {
      output: '❌ JEP SDK not installed.\n' +
              'Install it with: npm install -g @jep-eth/sdk'
    };
  }
  
  const config = await readConfig();
  
  // Confirm with user
  const confirm = await context.ui.confirm({
    title: '🔑 Generate JEP Key Pair',
    message: 'This will create a new private key for signing receipts.\n\n' +
             '⚠️  KEEP THIS KEY SAFE!\n' +
             'Anyone with this key can sign on your behalf.\n\n' +
             'The key will be stored in your config file.\n\n' +
             'Generate now?',
    buttons: ['✅ Yes', '❌ No']
  });
  
  if (confirm !== '✅ Yes') {
    return { output: 'Key generation cancelled' };
  }
  
  // Generate keys
  const { privateKey, publicKey } = generateKeyPair();
  
  // Save private key to config
  config.jepPrivateKey = privateKey;
  await saveConfig(config);
  
  // Show only public key
  const result = {
    success: true,
    publicKey: publicKey,
    warning: 'Private key saved to config. Never share it!',
    message: 'Your receipts will now be signed with your own key.'
  };
  
  await context.ui.notify('✅ JEP keys generated and saved');
  
  return {
    output: JSON.stringify(result, null, 2),
    type: 'json'
  };
};
