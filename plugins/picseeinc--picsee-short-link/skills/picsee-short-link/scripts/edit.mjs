#!/usr/bin/env node
// Edit short link destination (requires Advanced plan)

import https from 'https';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { getToken } from './lib/keychain.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const configPath = path.join(__dirname, '..', 'config.json');

const encodeId = process.argv[2];
const newUrl = process.argv[3];

if (!encodeId || !newUrl) {
  console.error('Usage: node edit.mjs <ENCODE_ID> <NEW_URL>');
  process.exit(1);
}

// Validate URL
try {
  new URL(newUrl);
} catch {
  console.error(JSON.stringify({
    success: false,
    error: 'Invalid URL format'
  }));
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

const requestData = JSON.stringify({ url: newUrl });

const options = {
  hostname: 'api.pics.ee',
  path: `/v2/links/${encodeId}`,
  method: 'PUT',
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
        message: 'Link updated successfully'
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
