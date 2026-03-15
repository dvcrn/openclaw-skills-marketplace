#!/usr/bin/env node
import fs from 'fs';
import { execFileSync } from 'child_process';
import { readJson, resolveSkillPath } from './lib/io.js';
import { getPlatformState, loadRuntimeConfig } from './platform-runtime.js';

const runtime = loadRuntimeConfig();
const envPath = resolveSkillPath('.env');
const envExamplePath = resolveSkillPath('.env.example');
const configPath = resolveSkillPath('config', 'platforms.json');
const wordsPath = resolveSkillPath('data', 'words.json');
const words = readJson(wordsPath, []);
const nodeMajor = Number(process.versions.node.split('.')[0] || 0);
const openClawAvailable = hasOpenClawCli();

const result = {
  ok: true,
  title: runtime.title,
  subtitle: runtime.subtitle,
  checks: {
    node: {
      ok: nodeMajor >= 18,
      current: process.version,
      required: '>=18'
    },
    openclawCli: {
      ok: openClawAvailable,
      required: true
    },
    envSource: {
      ok: fs.existsSync(envPath) || fs.existsSync(envExamplePath),
      using: fs.existsSync(envPath) ? '.env' : '.env.example',
      path: fs.existsSync(envPath) ? envPath : envExamplePath
    },
    config: {
      ok: fs.existsSync(configPath),
      path: configPath
    },
    aggregateWords: {
      ok: Array.isArray(words) && words.length > 0,
      count: Array.isArray(words) ? words.length : 0,
      path: wordsPath
    },
    push: {
      channel: runtime.push.channel || '',
      targetConfigured: Boolean(String(runtime.push.target || '').trim()),
      sendCommandConfigured: Boolean(String(runtime.push.sendCommand || '').trim())
    },
    platforms: Object.fromEntries(
      Object.values(runtime.platforms).map((platform) => {
        const state = getPlatformState(platform);
        const libraryPath = resolveSkillPath('data', 'platforms', `${platform.key}.json`);
        const libraryWords = readJson(libraryPath, []);

        return [platform.key, {
          enabled: platform.enabled,
          savedUrl: platform.savedUrl,
          cacheExists: state.cacheExists,
          cachePath: state.cachePath,
          libraryCount: Array.isArray(libraryWords) ? libraryWords.length : 0,
          nextAction: state.nextAction
        }];
      })
    )
  },
  nextSteps: buildNextSteps()
};

if (!result.checks.node.ok || !result.checks.config.ok || !result.checks.envSource.ok) {
  result.ok = false;
}

console.log(JSON.stringify(result, null, 2));

function buildNextSteps() {
  const steps = [];

  if (!fs.existsSync(envPath)) {
    steps.push('如需自定义推送目标或时区，先复制 .env.example 为 .env 再修改。');
  }

  if (!openClawAvailable) {
    steps.push('先确认本机可以使用 OpenClaw CLI，否则浏览器工作流和发送命令都无法直接跑通。');
  }

  for (const platform of Object.values(runtime.platforms)) {
    const state = getPlatformState(platform);
    if (platform.enabled && !state.cacheExists) {
      steps.push(state.nextAction);
    }
  }

  if (!Array.isArray(words) || words.length === 0) {
    steps.push('抓到页面缓存后，运行 npm run sync、npm run sync:google 或 npm run sync:youdao 生成词库。');
  } else {
    steps.push('运行 npm run test-message 预览今日单词。');
  }

  if (!String(runtime.push.target || '').trim()) {
    steps.push('如果要正式发送消息，请先配置 PUSH_TARGET 或 push.target。');
  } else {
    steps.push('确认预览无误后，运行 npm run send。');
  }

  return [...new Set(steps)];
}

function hasOpenClawCli() {
  try {
    execFileSync('openclaw', ['--help'], { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
}
