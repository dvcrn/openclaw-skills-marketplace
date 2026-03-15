import fs from 'fs';
import { readEnvFile, readSkillConfig, resolveConfigValue, resolveSkillPath } from './lib/io.js';

export function loadRuntimeConfig() {
  const env = readEnvFile();
  const skillConfig = readSkillConfig();
  const platforms = skillConfig.platforms || {};

  return {
    env,
    skillConfig,
    title: skillConfig.title || '多平台收藏词复活计划',
    subtitle: skillConfig.subtitle || '支持 Google / 有道｜每天 1 词，不让收藏吃灰',
    timezone: resolveConfigValue(env.PUSH_TIMEZONE, skillConfig.timezone, 'Asia/Shanghai'),
    push: {
      channel: resolveConfigValue(env.PUSH_CHANNEL, skillConfig.push?.channel, ''),
      target: resolveConfigValue(env.PUSH_TARGET, skillConfig.push?.target, ''),
      sendCommand: resolveConfigValue(env.OPENCLAW_SEND_COMMAND, skillConfig.push?.sendCommand, '')
    },
    platforms: {
      google: {
        key: 'google',
        label: platforms.google?.label || 'Google Translate',
        enabled: platforms.google?.enabled ?? true,
        savedUrl: resolveConfigValue(env.GOOGLE_SAVED_URL, platforms.google?.savedUrl, 'https://translate.google.com/saved?sl=en&tl=zh-CN&op=translate'),
        pageTextFile: resolveConfigValue(env.GOOGLE_PAGE_TEXT_FILE, platforms.google?.pageTextFile, './data/cache/google-page.txt')
      },
      youdao: {
        key: 'youdao',
        label: platforms.youdao?.label || '有道词典',
        enabled: platforms.youdao?.enabled ?? true,
        savedUrl: resolveConfigValue(env.YOUDAO_SAVED_URL, platforms.youdao?.savedUrl, 'https://dict.youdao.com/webwordbook/wordlist'),
        pageTextFile: resolveConfigValue(env.YOUDAO_PAGE_TEXT_FILE, platforms.youdao?.pageTextFile, './data/cache/youdao-page.txt')
      }
    }
  };
}

export function getSelectedSources(config, argv = []) {
  const cliSources = argv.map((item) => String(item).trim()).filter(Boolean);
  if (cliSources.length) return cliSources;

  const envSources = String(config.env.WORD_SOURCES || '').trim();
  if (envSources) {
    return envSources.split(',').map((item) => item.trim()).filter(Boolean);
  }

  return Object.values(config.platforms)
    .filter((platform) => platform.enabled)
    .map((platform) => platform.key);
}

export function getPlatformState(platformConfig) {
  const cachePath = resolveSkillPath(platformConfig.pageTextFile);
  return {
    ...platformConfig,
    cachePath,
    cacheExists: fs.existsSync(cachePath),
    nextAction: fs.existsSync(cachePath)
      ? '可直接同步'
      : `先用 OpenClaw 浏览器打开 ${platformConfig.label} 收藏页，确认已登录后再抓取当前页`
  };
}
