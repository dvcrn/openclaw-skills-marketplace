/**
 * Utility functions for secure private key input
 */

const readline = require('readline');
const fs = require('fs');
const path = require('path');

/**
 * Read private key from environment variable or prompt user
 * @param {string} envVar - Environment variable name
 * @param {string} prompt - Prompt message
 * @returns {Promise<string>}
 */
async function getPrivateKey(envVar, prompt) {
  // Check environment variable first
  if (process.env[envVar]) {
    console.log(`✅ Using ${envVar} from environment`);
    return process.env[envVar];
  }

  // Prompt user for private key
  return new Promise((resolve, reject) => {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    rl.question(prompt + ': ', (answer) => {
      rl.close();

      if (!answer || answer.trim() === '') {
        reject(new Error('Private key is required'));
      } else {
        resolve(answer.trim());
      }
    });
  });
}

/**
 * Read private key from file
 * @param {string} filePath - Path to private key file
 * @returns {Promise<string>}
 */
async function getPrivateKeyFromFile(filePath) {
  return new Promise((resolve, reject) => {
    if (!fs.existsSync(filePath)) {
      reject(new Error(`Private key file not found: ${filePath}`));
      return;
    }

    fs.readFile(filePath, 'utf8', (err, data) => {
      if (err) {
        reject(err);
      } else {
        resolve(data.trim());
      }
    });
  });
}

/**
 * Save private key to encrypted file (optional)
 * @param {string} privateKey - Private key to save
 * @param {string} filePath - Path to save
 * @returns {Promise<void>}
 */
async function savePrivateKey(privateKey, filePath) {
  return new Promise((resolve, reject) => {
    // In production, you should encrypt the private key
    // For now, we'll just save it with restricted permissions
    fs.writeFile(filePath, privateKey, { mode: 0o600 }, (err) => {
      if (err) {
        reject(err);
      } else {
        console.log(`✅ Private key saved to: ${filePath}`);
        resolve();
      }
    });
  });
}

module.exports = {
  getPrivateKey,
  getPrivateKeyFromFile,
  savePrivateKey
};
