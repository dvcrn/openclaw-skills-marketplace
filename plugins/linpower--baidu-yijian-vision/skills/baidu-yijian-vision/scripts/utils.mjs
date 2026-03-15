#!/usr/bin/env node

import https from 'https';
import http from 'http';
import fs from 'fs';
import path from 'path';

export const REGISTRY_FILENAME = '.claude/yijian-skills.local.md';

const REGISTRY_HEADER = `---
description: Yijian skills registry
---
# Yijian Skills Registry

`;

/**
 * Read the registry from the project directory.
 * Returns { skills: {} } if the file doesn't exist.
 */
export function readRegistry(projectDir) {
  const filePath = path.join(projectDir, REGISTRY_FILENAME);
  if (!fs.existsSync(filePath)) {
    return { skills: {} };
  }
  const content = fs.readFileSync(filePath, 'utf-8');
  const jsonMatch = content.match(/```json\s*\n([\s\S]*?)\n```/);
  if (!jsonMatch) {
    return { skills: {} };
  }
  try {
    return JSON.parse(jsonMatch[1]);
  } catch {
    return { skills: {} };
  }
}

/**
 * Write the registry to the project directory.
 * Creates the .claude directory if it doesn't exist.
 */
export function writeRegistry(projectDir, registry) {
  const dirPath = path.join(projectDir, '.claude');
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
  const filePath = path.join(projectDir, REGISTRY_FILENAME);
  const content = REGISTRY_HEADER + '```json\n' + JSON.stringify(registry, null, 2) + '\n```\n';
  fs.writeFileSync(filePath, content, 'utf-8');
}

/**
 * Make an HTTPS (or HTTP) request. Returns a Promise that resolves to { statusCode, headers, body }.
 */
export function httpsRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const parsedUrl = new URL(url);
    const mod = parsedUrl.protocol === 'https:' ? https : http;
    const reqOptions = {
      hostname: parsedUrl.hostname,
      port: parsedUrl.port || (parsedUrl.protocol === 'https:' ? 443 : 80),
      path: parsedUrl.pathname + parsedUrl.search,
      method: options.method || 'GET',
      headers: options.headers || {},
    };

    const req = mod.request(reqOptions, (res) => {
      const chunks = [];
      res.on('data', (chunk) => chunks.push(chunk));
      res.on('end', () => {
        const body = Buffer.concat(chunks).toString('utf-8');
        resolve({ statusCode: res.statusCode, headers: res.headers, body });
      });
    });

    req.on('error', reject);

    if (options.body) {
      req.write(options.body);
    }
    req.end();
  });
}

/**
 * Get the API key from environment. Throws if not set.
 */
export function getApiKey() {
  const key = process.env.YIJIAN_API_KEY;
  if (!key) {
    throw new Error('YIJIAN_API_KEY environment variable is not set. Please configure it in ~/.claude/settings.json under "env".');
  }
  return key;
}

/**
 * Construct the metadata URL for a given ep-id.
 */
export function metadataUrl(epId) {
  return `https://yijian-next.cloud.baidu.com/api/skills/v1/${epId}/metadata`;
}

/**
 * Construct the run URL for a given ep-id.
 */
export function runUrl(epId) {
  return `https://yijian-next.cloud.baidu.com/api/skills/v1/${epId}/run`;
}
