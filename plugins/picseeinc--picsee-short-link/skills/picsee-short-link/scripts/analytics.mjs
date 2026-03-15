#!/usr/bin/env node
// Get link analytics (requires authentication)

import https from 'https';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { getToken } from './lib/keychain.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const configPath = path.join(__dirname, '..', 'config.json');

const encodeId = process.argv[2];

if (!encodeId) {
  console.error('Usage: node analytics.mjs <ENCODE_ID>');
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

const options = {
  hostname: 'api.pics.ee',
  path: `/v1/links/${encodeId}/overview?dailyClicks=true`,
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`
  }
};

const req = https.request(options, (res) => {
  let data = '';
  
  res.on('data', (chunk) => {
    data += chunk;
  });
  
  res.on('end', () => {
    if (res.statusCode === 200) {
      try {
        const json = JSON.parse(data);
        console.log(JSON.stringify({
          success: true,
          data: json.data
        }, null, 2));
      } catch (err) {
        console.error(JSON.stringify({
          success: false,
          error: 'Invalid API response'
        }));
        process.exit(1);
      }
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

req.end();
