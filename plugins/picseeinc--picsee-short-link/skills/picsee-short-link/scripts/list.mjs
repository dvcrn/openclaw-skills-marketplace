#!/usr/bin/env node
// List recent short links (requires authentication)
// Supports comprehensive query and search parameters

import https from 'https';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { getToken } from './lib/keychain.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const configPath = path.join(__dirname, '..', 'config.json');

// Parse command line arguments
function parseArgs() {
  const args = process.argv.slice(2);
  
  // Check for help flag
  if (args.includes('--help') || args.includes('-h')) {
    printUsage();
    process.exit(0);
  }
  
  // Positional arguments
  const startTime = args.find(arg => !arg.startsWith('--'));
  const limit = parseInt(args.find(arg => !arg.startsWith('--') && arg !== startTime)) || 50;
  
  // Named parameters (query params)
  const queryParams = {
    startTime,
    limit: Math.min(limit, 50), // Max 50
    isAPI: parseFlag(args, '--isAPI', false),
    isStar: parseFlag(args, '--isStar'),
    prevMapId: parseValue(args, '--prevMapId'),
    externalId: parseValue(args, '--externalId')
  };
  
  // Body parameters (search params - Advanced Plan)
  const bodyParams = {
    tag: parseValue(args, '--tag'),
    encodeId: parseValue(args, '--encodeId'),
    keyword: parseValue(args, '--keyword'),
    url: parseValue(args, '--url'),
    authorId: parseValue(args, '--authorId'),
    fbPixel: parseValue(args, '--fbPixel'),
    gTag: parseValue(args, '--gTag')
  };
  
  return { queryParams, bodyParams };
}

function parseValue(args, flag) {
  const arg = args.find(a => a.startsWith(flag + '='));
  if (!arg) return undefined;
  return arg.split('=')[1];
}

function parseFlag(args, flag, defaultVal) {
  const arg = args.find(a => a.startsWith(flag));
  if (!arg) return defaultVal;
  
  if (arg.includes('=')) {
    const value = arg.split('=')[1];
    if (value === 'true' || value === '1') return true;
    if (value === 'false' || value === '0') return false;
    return parseInt(value) || undefined;
  }
  
  return true;
}

function printUsage() {
  console.log(`
Usage: node list.mjs <START_TIME> [LIMIT] [OPTIONS]

Required:
  START_TIME              ISO8601 format: YYYY-MM-DDTHH:MM:SS
                         Use LAST DAY of month for monthly queries
                         Example: 2026-03-31T23:59:59

Optional Positional:
  LIMIT                  Number of results (1-50, default: 50)

Query Parameters:
  --isAPI=<0|1>          Filter by API-generated links (default: false)
  --isStar=<0|1>         Filter by starred links
                         0 = non-starred only
                         1 = starred only
  --prevMapId=<ID>       Get links older than this mapId
  --externalId=<ID>      Filter by external ID

Search Parameters (Advanced Plan):
  --tag=<TAG>            Search by tag (3-30 chars)
  --encodeId=<SLUG>      Search by slug (exact match)
  --keyword=<TEXT>       Search in title/description (3-30 chars)
  --url=<URL>            Search by exact destination URL
  --authorId=<ID>        Filter by author ID
  --fbPixel=<ID>         Filter by Facebook Pixel ID
  --gTag=<ID>            Filter by GTM ID

Examples:
  # Basic: List 20 links from March 2026
  node list.mjs 2026-03-31T23:59:59 20

  # Filter: Only starred links
  node list.mjs 2026-03-31T23:59:59 50 --isStar=1

  # Search: Find links with specific tag
  node list.mjs 2026-03-31T23:59:59 50 --tag=campaign

  # Search: Find links by keyword in title/description
  node list.mjs 2026-03-31T23:59:59 50 --keyword=picsee

  # Search: Find links by exact destination URL
  node list.mjs 2026-03-31T23:59:59 50 --url=https://picsee.io

  # Advanced: Multiple search criteria
  node list.mjs 2026-03-31T23:59:59 50 --tag=event --authorId=739
`);
}

// Main execution
const { queryParams, bodyParams } = parseArgs();

if (!queryParams.startTime) {
  console.error('Error: START_TIME is required\n');
  printUsage();
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

// Build query string
const queryString = Object.entries(queryParams)
  .filter(([key, value]) => value !== undefined && value !== '')
  .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
  .join('&');

// Build request body (only include non-empty search params)
const requestBody = {};
Object.entries(bodyParams).forEach(([key, value]) => {
  if (value !== undefined && value !== '') {
    requestBody[key] = value;
  }
});

const hasBodyParams = Object.keys(requestBody).length > 0;
const bodyContent = hasBodyParams ? JSON.stringify(requestBody) : '';

const options = {
  hostname: 'api.pics.ee',
  path: `/v2/links/overview?${queryString}`,
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
    ...(hasBodyParams && { 'Content-Length': Buffer.byteLength(bodyContent) })
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

if (hasBodyParams) {
  req.write(bodyContent);
}

req.end();
