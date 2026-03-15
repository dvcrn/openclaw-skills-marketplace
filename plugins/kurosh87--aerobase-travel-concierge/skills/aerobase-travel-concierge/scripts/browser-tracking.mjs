#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const TRACK_FILE = path.join(process.env.HOME || '/root', 'aerobase-browser-searches.json');

const DEFAULT_DATA = {
  date: new Date().toISOString().split('T')[0],
  count: 0,
  searches: [],
  blockedUntil: null
};

function readData() {
  try {
    if (fs.existsSync(TRACK_FILE)) {
      const data = JSON.parse(fs.readFileSync(TRACK_FILE, 'utf8'));
      const today = new Date().toISOString().split('T')[0];
      if (data.date !== today) {
        return { ...DEFAULT_DATA, date: today };
      }
      return data;
    }
  } catch (e) {}
  return { ...DEFAULT_DATA };
}

function writeData(data) {
  fs.writeFileSync(TRACK_FILE, JSON.stringify(data, null, 2));
}

const args = process.argv.slice(2);
const command = args[0] || 'check';

const data = readData();

if (command === 'check') {
  const today = new Date().toISOString().split('T')[0];
  if (data.date !== today) {
    data.date = today;
    data.count = 0;
    data.searches = [];
    data.blockedUntil = null;
  }
  
  if (data.blockedUntil && new Date(data.blockedUntil) > new Date()) {
    console.log('BLOCKED');
    console.log(data.blockedUntil);
    process.exit(1);
  }
  
  if (data.count >= 10) {
    console.log('LIMIT_REACHED');
    console.log(data.count);
    process.exit(1);
  }
  
  console.log('OK');
  console.log(data.count);
  process.exit(0);
}

if (command === 'increment') {
  const search = args.slice(1).join(' ');
  data.count++;
  data.searches.push({
    site: search || 'unknown',
    timestamp: new Date().toISOString()
  });
  writeData(data);
  console.log('OK');
  console.log(data.count);
  process.exit(0);
}

if (command === 'block') {
  const hours = parseInt(args[1]) || 24;
  data.blockedUntil = new Date(Date.now() + hours * 60 * 60 * 1000).toISOString();
  writeData(data);
  console.log('BLOCKED_UNTIL');
  console.log(data.blockedUntil);
  process.exit(0);
}

console.log('Usage: browser-tracking.js [check|increment|block]');
process.exit(1);
