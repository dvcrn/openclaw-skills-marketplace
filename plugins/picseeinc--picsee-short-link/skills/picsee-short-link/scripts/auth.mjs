#!/usr/bin/env node
// Store PicSee API token securely (AES-256 encrypted, cross-platform)

import https from 'https';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { setToken } from './lib/keychain.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const configPath = path.join(__dirname, '..', 'config.json');

const token = process.argv[2];

if (!token) {
  console.error('Usage: node auth.mjs <API_TOKEN>');
  process.exit(1);
}

// Verify token by calling API
const options = {
  hostname: 'api.pics.ee',
  path: '/v2/my/api/status',
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
        
        // Store token in Keychain
        setToken(token);
        
        // Write config.json
        const config = {
          mode: 'authenticated',
          setupDate: new Date().toISOString().split('T')[0]
        };
        fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
        
        console.log(JSON.stringify({
          success: true,
          plan: json.data?.plan || 'unknown',
          quota: json.data?.quota || 0,
          message: 'Token stored securely'
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
        error: 'Invalid token',
        statusCode: res.statusCode
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
