#!/usr/bin/env node
import { readJson, resolveSkillPath } from './lib/io.js';
import { getPlatformState, loadRuntimeConfig } from './platform-runtime.js';

const runtime = loadRuntimeConfig();
const words = readJson(resolveSkillPath('data', 'words.json'), []);
const sendState = readJson(resolveSkillPath('data', 'send-state.json'), {});

const status = {
  title: runtime.title,
  subtitle: runtime.subtitle,
  timezone: runtime.timezone,
  push: {
    channel: runtime.push.channel,
    target: runtime.push.target,
    time: runtime.skillConfig.dailyPush?.time || '09:00',
    dedupeSameDay: runtime.skillConfig.dailyPush?.dedupeSameDay ?? true
  },
  words: Array.isArray(words) ? words.length : 0,
  lastSent: sendState.lastSentAt || '',
  browserFirst: true,
  storageMode: 'per-platform-files-plus-aggregate',
  platforms: Object.fromEntries(
    Object.values(runtime.platforms).map((platform) => {
      const state = getPlatformState(platform);
      const libraryPath = resolveSkillPath('data', 'platforms', `${platform.key}.json`);
      const libraryWords = readJson(libraryPath, []);
      return [platform.key, {
        enabled: state.enabled,
        savedUrl: state.savedUrl,
        cacheFile: state.cachePath,
        cacheExists: state.cacheExists,
        libraryFile: libraryPath,
        wordCount: Array.isArray(libraryWords) ? libraryWords.length : 0,
        nextAction: state.nextAction
      }];
    })
  )
};

console.log(JSON.stringify(status, null, 2));
