#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const {spawn} = require('child_process');

const REG_FILE = path.resolve(__dirname,'../../REGISTRY.md');

function sanitizeInput(i){return i.replace(/[^a-zA-Z0-9\u4e00-\u9fa5\s\-_]/g,'').trim();}

function loadLocalRegistry(){
  const map={};
  try{
    const c = fs.readFileSync(REG_FILE,'utf8');
    const lines=c.split('\n');let inT=false;
    for(const line of lines){
      if(line.includes('|Skill|')){inT=true;continue;}
      if(inT&&line.startsWith('##')){inT=false;}
      if(inT&&line.includes('|')&&!line.includes('|---|')){
        const p=line.split('|').map(x=>x.trim()).filter(Boolean);
        if(p.length>=2){
          const skill=p[0];
          const triggers=(p[1]||'').split(/、/).map(t=>t.trim()).filter(Boolean);
          triggers.forEach(t=>{if(t&&t!=='-')map[t.toLowerCase()]=skill;});
        }
      }
    }
  }catch(e){console.error('加载失败:',e.message);}
  return map;
}

function matchLocalSkill(input){
  const s=sanitizeInput(input);
  const map=loadLocalRegistry();
  const lower=s.toLowerCase();
  const keys=Object.keys(map).sort((a,b)=>b.length-a.length);
  for(const t of keys){if(lower.includes(t))return map[t];}
  return null;
}

async function vetSkill(skill){
  console.log(`🛡️ 安全扫描: ${skill}`);
  const skillPath=path.join(__dirname,'../../skills',skill);
  if(!fs.existsSync(skillPath))return true;
  const sus=['.env','credentials.json','id_rsa','password'];
  const files=fs.readdirSync(skillPath);
  for(const f of files){
    for(const s of sus){
      if(f.toLowerCase().includes(s)){console.log(`⚠️ 可疑: ${f}`);return false;}
    }
  }
  return true;
}

function searchRemote(input){
  const s=sanitizeInput(input);
  if(!s)return null;
  return new Promise(resolve=>{
    const p=spawn('npx',['clawdhub','search',s,'--limit','3'],{timeout:30000,stdio:['pipe','pipe','pipe']});
    let o='';
    p.stdout.on('data',d=>o+=d.toString());
    p.on('close',()=>{
      const m=o.match(/\|\s*(\S+)\s+\|/);
      resolve(m?m[1]:null);
    });
  });
}

async function main(input){
  console.log(`\n📋 技能路由: "${input}"`);
  const local=matchLocalSkill(input);
  if(local){console.log(`✅ 本地匹配: ${local}`);return {type:'local',skill:local};}
  console.log('❌ 本地无匹配');
  const remote=await searchRemote(input);
  if(remote){
    console.log(`🔍 远程: ${remote}`);
    const safe=await vetSkill(remote);
    return safe?{type:'toInstall',skill:remote}:{type:'blocked'};
  }
  return {type:'none'};
}

module.exports={main,matchLocalSkill,loadLocalRegistry,vetSkill};
if(require.main===module)main(process.argv[2]||'stock').then(r=>console.log('\n结果:',r));
