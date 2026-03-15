#!/usr/bin/env node
// Setup unauthenticated mode (user chose not to provide token)

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const configPath = path.join(__dirname, '..', 'config.json');

const config = {
  mode: 'unauthenticated',
  setupDate: new Date().toISOString().split('T')[0]
};

fs.writeFileSync(configPath, JSON.stringify(config, null, 2));

console.log(JSON.stringify({
  success: true,
  mode: 'unauthenticated',
  message: 'Setup complete. You can create short links in unauthenticated mode.'
}, null, 2));
