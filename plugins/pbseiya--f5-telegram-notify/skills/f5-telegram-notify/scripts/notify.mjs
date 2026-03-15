#!/usr/bin/env node

/**
 * F5-TTS Telegram Notification Script
 * ส่งการแจ้งเตือน Telegram เมื่อ training เสร็จหรือล้มเหลว
 */

import { readFile } from 'fs/promises';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// Telegram config
const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const CHAT_ID = process.env.TELEGRAM_CHAT_ID;

// Parse arguments
const args = process.argv.slice(2);
const [status, message, modelName, checkpointPath] = args;

if (!status || !message) {
  console.error('Usage: node notify.mjs <status> <message> [model_name] [checkpoint_path]');
  console.error('Status: success | error | start');
  process.exit(1);
}

// Validate status
const validStatuses = ['success', 'error', 'start'];
if (!validStatuses.includes(status)) {
  console.error(`Invalid status: ${status}. Must be one of: ${validStatuses.join(', ')}`);
  process.exit(1);
}

// Build message
const emoji = {
  success: '✅',
  error: '❌',
  start: '🚀'
};

const statusText = {
  success: 'Training สำเร็จ!',
  error: 'Training ล้มเหลว!',
  start: 'เริ่ม Training แล้ว'
};

let fullMessage = `<b>${emoji[status]} ${statusText[status]}</b>\n\n`;
fullMessage += `<code>${message}</code>`;

if (modelName) {
  fullMessage += `\n\n📦 Model: <code>${modelName}</code>`;
}

if (checkpointPath && status === 'success') {
  fullMessage += `\n💾 Checkpoint: <code>${checkpointPath}</code>`;
}

fullMessage += `\n\n⏰ ${new Date().toLocaleString('th-TH', { timeZone: 'Asia/Bangkok' })}`;

// Load .env from multiple possible locations
async function loadEnv() {
  const possiblePaths = [
    join(__dirname, '../../.env'),  // workspace/.env
    '/home/seiya/projects/openclaw/.env',  // openclaw project .env
    join(process.cwd(), '.env'),  // current dir .env
  ];
  
  for (const envPath of possiblePaths) {
    try {
      const envContent = await readFile(envPath, 'utf-8');
      const lines = envContent.split('\n');
      
      for (const line of lines) {
        const [key, value] = line.split('=');
        if (key === 'TELEGRAM_BOT_TOKEN' && !process.env.TELEGRAM_BOT_TOKEN) {
          process.env.TELEGRAM_BOT_TOKEN = value?.trim();
        }
        if (key === 'TELEGRAM_CHAT_ID' && !process.env.TELEGRAM_CHAT_ID) {
          process.env.TELEGRAM_CHAT_ID = value?.trim();
        }
      }
      
      if (process.env.TELEGRAM_BOT_TOKEN && process.env.TELEGRAM_CHAT_ID) {
        console.log(`Loaded config from: ${envPath}`);
        return;
      }
    } catch (err) {
      // Try next path
    }
  }
  
  console.error('Warning: Could not load .env file from any location, using environment variables only');
}

// Send to Telegram
async function sendTelegram() {
  const token = process.env.TELEGRAM_BOT_TOKEN;
  const chatId = process.env.TELEGRAM_CHAT_ID;
  
  if (!token || !chatId) {
    console.error('Error: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set');
    process.exit(1);
  }
  
  const url = `https://api.telegram.org/bot${token}/sendMessage`;
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        chat_id: chatId,
        text: fullMessage,
        parse_mode: 'HTML'
      })
    });
    
    const result = await response.json();
    
    if (result.ok) {
      console.log('✅ Sent Telegram notification successfully');
      console.log(JSON.stringify({ status: 'success', message_id: result.result.message_id }, null, 2));
      process.exit(0);
    } else {
      console.error('❌ Telegram API error:', result);
      process.exit(1);
    }
  } catch (err) {
    console.error('❌ Failed to send Telegram notification:', err.message);
    process.exit(1);
  }
}

// Main
async function main() {
  await loadEnv();
  await sendTelegram();
}

main();
