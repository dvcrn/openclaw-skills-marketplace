import { pickDailyWord } from './lib/dailyPicker.js';
import { readEnvFile, readJson, readSkillConfig, resolveConfigValue, resolveSkillPath } from './lib/io.js';
import { renderWordMessage } from './lib/messageRenderer.js';

const env = readEnvFile();
const skillConfig = readSkillConfig();
const words = readJson(resolveSkillPath('data', 'words.json'), []);
if (!Array.isArray(words) || words.length === 0) {
  throw new Error('data/words.json 为空，请先运行 npm run sync');
}

const timeZone = resolveConfigValue(env.PUSH_TIMEZONE, skillConfig.timezone, 'Asia/Shanghai');
const { item, meta } = pickDailyWord(words, { timeZone });

console.log(JSON.stringify({
  item,
  meta,
  message: renderWordMessage(item, {
    title: skillConfig.title,
    subtitle: skillConfig.subtitle
  })
}, null, 2));
