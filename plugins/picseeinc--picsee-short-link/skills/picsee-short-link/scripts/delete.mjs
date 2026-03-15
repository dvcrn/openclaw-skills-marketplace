#!/usr/bin/env node
// Delete or recover short link (requires authentication)

import https from 'https';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { getToken } from './lib/keychain.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const configPath = path.join(__dirname, '..', 'config.json');

const encodeId = process.argv[2];
const action = process.argv[3] || 'delete'; // 'delete' or 'recover'

if (!encodeId) {
  console.error('Usage: node delete.mjs <ENCODE_ID> [action]');
  console.error('action: delete (default) | recover');
  process.exit(1);
}

if (action !== 'delete' && action !== 'recover') {
  console.error('Invalid action. Use: delete or recover');
  process.exit(1);
}

// Check config
let configMode = 'not-configured';
if (fs.existsSync(configPath)) {
  try {
    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    configMode = config.mode || 'not-configured';
  } catch {
    // Invalid config
  }
}

if (configMode !== 'authenticated') {
  console.error(JSON.stringify({
    success: false,
    error: 'This feature requires authentication. Run: node auth.mjs <TOKEN>'
  }));
  process.exit(1);
}

const token = getToken();
if (!token) {
  console.error(JSON.stringify({
    success: false,
    error: 'Token not found in Keychain. Please re-authenticate: node auth.mjs <TOKEN>'
  }));
  process.exit(1);
}

const requestData = JSON.stringify({ value: action });

const options = {
  hostname: 'api.pics.ee',
  path: `/v2/links/${encodeId}/delete`,
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(requestData)
  }
};

const req = https.request(options, (res) => {
  let data = '';
  
  res.on('data', (chunk) => {
    data += chunk;
  });
  
  res.on('end', () => {
    if (res.statusCode === 200) {
      console.log(JSON.stringify({
        success: true,
        message: `Link ${action}d successfully`
      }, null, 2));
    } else {
      console.error(JSON.stringify({
        success: false,
        error: 'API request failed',
        statusCode: res.statusCode,
        body: data
      }));
      process.exit(1);
    }
  });
});

req.on('error', (err) => {
  console.error(JSON.stringify({
    success: false,
    error: err.message
  }));
  process.exit(1);
});

req.write(requestData);
req.end();
