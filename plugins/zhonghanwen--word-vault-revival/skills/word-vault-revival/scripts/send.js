import { execFileSync, execSync } from 'child_process';
import { pickDailyWord } from './lib/dailyPicker.js';
import { readEnvFile, readJson, readSkillConfig, resolveConfigValue, resolveSkillPath, writeJson } from './lib/io.js';
import { renderWordMessage } from './lib/messageRenderer.js';

const env = readEnvFile();
const skillConfig = readSkillConfig();
const config = buildRuntimeConfig(env, skillConfig);
const words = readJson(resolveSkillPath('data', 'words.json'), []);
if (!Array.isArray(words) || words.length === 0) {
  throw new Error('data/words.json 为空，请先运行 npm run sync');
}

const { item, meta } = pickDailyWord(words, {
  timeZone: config.PUSH_TIMEZONE || 'Asia/Shanghai'
});
const message = renderWordMessage(item, {
  title: config.title,
  subtitle: config.subtitle
});
const payload = {
  channel: config.PUSH_CHANNEL || '',
  target: config.PUSH_TARGET || '',
  word: item.word,
  message,
  meta,
  title: config.title,
  subtitle: config.subtitle
};

const statePath = resolveSkillPath('data', 'send-state.json');
const todayKey = getTodayKey(config.PUSH_TIMEZONE || 'Asia/Shanghai');
const state = readJson(statePath, {});
const dedupeEnabled = String(config.PUSH_DEDUPE_SAME_DAY || 'true') !== 'false';
if (dedupeEnabled && state.lastSentDay === todayKey && state.lastSentWord === item.word) {
  console.log(JSON.stringify({
    ok: true,
    skipped: true,
    reason: 'already-sent-today',
    payload
  }, null, 2));
  process.exit(0);
}

const commandTemplate = (config.OPENCLAW_SEND_COMMAND || '').trim();
if (commandTemplate) {
  const command = commandTemplate
    .replaceAll('{{message}}', shellEscape(message))
    .replaceAll('{{channel}}', shellEscape(payload.channel))
    .replaceAll('{{target}}', shellEscape(payload.target))
    .replaceAll('{{word}}', shellEscape(payload.word));

  execSync(command, { stdio: 'inherit', shell: '/bin/zsh' });
  persistState();
  process.exit(0);
}

if (payload.channel && payload.target && hasOpenClawCli()) {
  execFileSync('openclaw', [
    'message', 'send',
    '--channel', payload.channel,
    '--to', payload.target,
    '--message', payload.message
  ], { stdio: 'inherit' });
  persistState();
  process.exit(0);
}

console.log(JSON.stringify(payload, null, 2));

function persistState() {
  writeJson(statePath, {
    lastSentAt: new Date().toISOString(),
    lastSentDay: todayKey,
    lastSentWord: item.word,
    channel: payload.channel,
    target: payload.target
  });
}

function buildRuntimeConfig(env, skillConfig) {
  return {
    ...env,
    title: skillConfig.title || '多平台收藏词复活计划',
    subtitle: skillConfig.subtitle || '支持 Google / 有道｜每天 1 词，不让收藏吃灰',
    PUSH_TIMEZONE: resolveConfigValue(env.PUSH_TIMEZONE, skillConfig.timezone, 'Asia/Shanghai'),
    PUSH_CHANNEL: resolveConfigValue(env.PUSH_CHANNEL, skillConfig.push?.channel, ''),
    PUSH_TARGET: resolveConfigValue(env.PUSH_TARGET, skillConfig.push?.target, ''),
    OPENCLAW_SEND_COMMAND: resolveConfigValue(env.OPENCLAW_SEND_COMMAND, skillConfig.push?.sendCommand, ''),
    PUSH_DEDUPE_SAME_DAY: String(skillConfig.dailyPush?.dedupeSameDay ?? true)
  };
}

function getTodayKey(timeZone) {
  return new Intl.DateTimeFormat('en-CA', {
    timeZone,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }).format(new Date());
}

function hasOpenClawCli() {
  try {
    execFileSync('openclaw', ['--help'], { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
}

function shellEscape(value) {
  return `'${String(value).replaceAll(`'`, `'\\''`)}'`;
}
