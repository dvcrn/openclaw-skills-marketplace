#!/usr/bin/env node
// Shorten URL with PicSee (authenticated or unauthenticated mode)

import https from 'https';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { getToken } from './lib/keychain.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const configPath = path.join(__dirname, '..', 'config.json');

const url = process.argv[2];

if (!url) {
  console.error('Usage: node shorten.mjs <URL>');
  process.exit(1);
}

// Validate URL
try {
  new URL(url);
} catch {
  console.error(JSON.stringify({
    success: false,
    error: 'Invalid URL format'
  }));
  process.exit(1);
}

// Read config to determine mode
let configMode = 'not-configured';
if (fs.existsSync(configPath)) {
  try {
    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    configMode = config.mode || 'not-configured';
  } catch {
    // Invalid config, treat as not-configured
  }
}

// Determine auth mode with graceful fallback
let token = null;
let useAuth = false;

if (configMode === 'authenticated') {
  token = getToken();
  if (token) {
    useAuth = true;
  }
  // If token not found in Keychain, gracefully fallback to unauthenticated
} else if (configMode === 'unauthenticated') {
  useAuth = false;
} else {
  // not-configured: default to unauthenticated
  useAuth = false;
}

const requestData = JSON.stringify({
  url: url,
  domain: 'pse.is',
  externalId: 'openclaw'
});

const options = useAuth ? {
  hostname: 'api.pics.ee',
  path: '/v1/links',
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(requestData)
  }
} : {
  hostname: 'chrome-ext.picsee.tw',
  path: '/v1/links',
  method: 'POST',
  headers: {
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
    if (res.statusCode === 200 || res.statusCode === 201) {
      try {
        const json = JSON.parse(data);
        const shortUrl = json.data?.picseeUrl || json.picseeUrl;
        
        console.log(JSON.stringify({
          success: true,
          shortUrl: shortUrl,
          encodeId: json.data?.encodeId || json.encodeId,
          mode: useAuth ? 'authenticated' : 'unauthenticated'
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

req.write(requestData);
req.end();
