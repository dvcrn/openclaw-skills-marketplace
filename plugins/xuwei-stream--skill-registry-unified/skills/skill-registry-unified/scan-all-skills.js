const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

const SKILLS_DIR = path.resolve(__dirname, '../../skills');
const REGISTRY_PATH = path.resolve(__dirname, '../../REGISTRY.md');

const CATEGORIES = ['开发与运维', '内容创作', '办公自动化', '数据科学', '搜索研究', '营销销售', '视觉设计', '教育学习', 'AI与LLMs', '智能家居', '安全合规', '通信协作', '投资理财', '新闻资讯', '其他'];

const CAT_MAP = {
  'stock':'投资理财','crypto':'投资理财','binance':'投资理财',
  'news':'新闻资讯','hn':'新闻资讯','bbc':'新闻资讯',
  'search':'搜索研究','brave':'搜索研究','tavily':'搜索研究',
  'github':'开发与运维','git':'开发与运维','code':'开发与运维','playwright':'开发与运维',
  'feishu':'办公自动化','todoist':'办公自动化','trello':'办公自动化',
  'homeassistant':'智能家居','home':'智能家居',
  'blog-writer':'内容创作','tweet':'内容创作','write':'内容创作',
  'ai':'AI与LLMs','llm':'AI与LLMs','gpt':'AI与LLMs',
  'security':'安全合规','audit':'安全合规'
};

function scanAllSkills() {
  const skills = [];
  const dirs = fs.readdirSync(SKILLS_DIR);
  for (const dir of dirs) {
    const skillDir = path.join(SKILLS_DIR, dir);
    if (!fs.statSync(skillDir).isDirectory()) continue;
    if (dir === 'scripts' || dir === 'node_modules') continue;
    const skillMdPath = path.join(skillDir, 'SKILL.md');
    if (!fs.existsSync(skillMdPath)) continue;
    try {
      const content = fs.readFileSync(skillMdPath, 'utf8');
      const yS = content.indexOf('---') + 3;
      const yE = content.indexOf('---', yS);
      if (yS < 3 || yE < yS) continue;
      const meta = yaml.load(content.slice(yS, yE));
      if (!meta) continue;
      const name = meta.name || dir;
      const desc = meta.description || '';
      let triggers = meta.triggers || [];
      if (!Array.isArray(triggers)) triggers = [];
      if (triggers.length === 0) {
        triggers = name.toLowerCase().replace(/[^a-z]/g,' ').split(/\s+/).filter(w=>w.length>2).slice(0,3);
      }
      let category = '其他';
      const allText = (name+' '+desc).toLowerCase();
      for (const [k,c] of Object.entries(CAT_MAP)) { if(allText.includes(k)){category=c;break;} }
      skills.push({name,triggers,description:desc.substring(0,40),category});
    } catch(e){}
  }
  return skills;
}

function generateRegistry(skills) {
  const byCat = {}; CATEGORIES.forEach(c=>byCat[c]=[]);
  skills.forEach(s=>{if(byCat[s.category])byCat[s.category].push(s);});
  let out = `# Skill Registry\n> Last updated: ${new Date().toISOString().split('T')[0]}\n\n`;
  for(const cat of CATEGORIES){
    if(!byCat[cat]||byCat[cat].length===0) continue;
    out += `## ${cat}\n\n|Skill|触发词|描述|\n|-------|--------|------|\n`;
    byCat[cat].forEach(s=>{out+=`|${s.name}|${s.triggers.join('、')||'-'}|${s.description}|\n`;});
    out+='\n';
  }
  return out;
}

const skills = scanAllSkills();
console.log(`扫描 ${skills.length} 个skills`);
fs.writeFileSync(REGISTRY_PATH, generateRegistry(skills));
console.log('REGISTRY.md已更新');
