import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const skillRoot = path.resolve(__dirname, '..', '..');

export function resolveSkillPath(...parts) {
  return path.resolve(skillRoot, ...parts);
}

export function ensureDir(filePath) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
}

export function readJson(filePath, fallback = null) {
  if (!fs.existsSync(filePath)) return fallback;
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

export function writeJson(filePath, data) {
  ensureDir(filePath);
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf8');
}

export function readEnvFile() {
  const envPath = resolveSkillPath('.env');
  const examplePath = resolveSkillPath('.env.example');
  const source = fs.existsSync(envPath) ? envPath : examplePath;
  const raw = fs.readFileSync(source, 'utf8');
  const result = {};

  for (const line of raw.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const index = trimmed.indexOf('=');
    if (index === -1) continue;
    const key = trimmed.slice(0, index).trim();
    const value = trimmed.slice(index + 1).trim();
    result[key] = value;
  }

  for (const [key, value] of Object.entries(process.env)) {
    if (typeof value !== 'string' || value.length === 0) continue;
    result[key] = value;
  }

  return result;
}

export function readSkillConfig() {
  return readJson(resolveSkillPath('config', 'platforms.json'), {
    title: '多平台收藏词复活计划',
    subtitle: '支持 Google / 有道｜每天 1 词，不让收藏吃灰',
    timezone: 'Asia/Shanghai',
    dailyPush: {
      enabled: true,
      time: '09:00',
      count: 1,
      dedupeSameDay: true
    },
    platforms: {},
    push: {}
  });
}

export function resolveConfigValue(envValue, configValue, fallback = '') {
  if (typeof envValue === 'string' && envValue.trim()) return envValue.trim();
  if (typeof configValue === 'string' && configValue.trim()) return configValue.trim();
  return fallback;
}
