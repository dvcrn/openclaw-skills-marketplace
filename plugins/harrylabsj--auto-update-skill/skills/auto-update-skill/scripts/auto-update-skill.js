#!/usr/bin/env node

/**
 * Auto Update Skill CLI
 * 
 * 命令行工具，用于手动检查和管理 skill 更新
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');
const {
  checkAndPrompt,
  getCurrentVersion,
  getLatestVersion,
  getUpdateType,
  backupSkill,
  performUpdate,
  rollbackSkill,
  loadConfig,
  log
} = require('../lib/checker');

const CONFIG_PATH = path.join(process.env.HOME, '.openclaw', 'auto-update-skill.json');
const BACKUP_DIR = path.join(process.env.HOME, '.openclaw', 'skill-backups');

// 创建 readline 接口
function createRL() {
  return readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
}

// 询问用户
function ask(rl, question) {
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      resolve(answer.trim());
    });
  });
}

// 检查命令
async function checkCommand(skillName, options = {}) {
  if (skillName) {
    // 检查指定 skill
    const current = getCurrentVersion(skillName);
    const latest = getLatestVersion(skillName);
    
    if (!current) {
      console.log(`❌ ${skillName} 未安装`);
      return;
    }
    
    if (!latest) {
      console.log(`❌ 无法获取 ${skillName} 最新版本`);
      return;
    }
    
    const type = getUpdateType(current, latest);
    
    if (type === 'none') {
      console.log(`✅ ${skillName} 已是最新版本 ${current}`);
    } else {
      console.log(`📦 ${skillName} 有更新:`);
      console.log(`   当前: ${current}`);
      console.log(`   最新: ${latest}`);
      console.log(`   类型: ${type}`);
    }
  } else {
    // 检查所有 skills
    console.log('检查所有 skills...\n');
    
    try {
      const { execSync } = require('child_process');
      const output = execSync('clawhub list', { encoding: 'utf8' });
      const lines = output.split('\n');
      const skills = [];
      
      for (const line of lines) {
        const match = line.match(/^(\S+)\s+(\d+\.\d+\.\d+)$/);
        if (match) {
          skills.push({ name: match[1], version: match[2] });
        }
      }
      
      console.log(`已安装 ${skills.length} 个 skills:\n`);
      
      let hasUpdate = false;
      for (const skill of skills) {
        const latest = getLatestVersion(skill.name);
        if (latest) {
          const type = getUpdateType(skill.version, latest);
          if (type !== 'none') {
            console.log(`📦 ${skill.name}: ${skill.version} → ${latest} (${type})`);
            hasUpdate = true;
          } else if (options.verbose) {
            console.log(`✅ ${skill.name}: ${skill.version} (最新)`);
          }
        }
      }
      
      if (!hasUpdate) {
        console.log('所有 skills 都是最新版本 ✅');
      }
    } catch (e) {
      console.error('获取 skill 列表失败:', e.message);
    }
  }
}

// 更新命令
async function updateCommand(skillName, options = {}) {
  const rl = createRL();
  
  try {
    if (skillName) {
      // 更新指定 skill
      const current = getCurrentVersion(skillName);
      const latest = getLatestVersion(skillName);
      
      if (!current) {
        console.log(`❌ ${skillName} 未安装`);
        return;
      }
      
      if (!latest) {
        console.log(`❌ 无法获取 ${skillName} 最新版本`);
        return;
      }
      
      const type = getUpdateType(current, latest);
      
      if (type === 'none') {
        console.log(`✅ ${skillName} 已是最新版本 ${current}`);
        return;
      }
      
      // 询问确认（非强制模式）
      if (!options.force && options.interactive !== false) {
        console.log(`\n📦 ${skillName} ${current} → ${latest} (${type})`);
        const answer = await ask(rl, `确认升级? [Y/n]: `);
        if (answer.toLowerCase() === 'n') {
          console.log('已取消');
          return;
        }
      }
      
      // 执行更新
      if (backupSkill(skillName, current)) {
        if (performUpdate(skillName, latest)) {
          console.log(`✅ ${skillName} 升级成功`);
        } else {
          console.log(`❌ 升级失败，正在回滚...`);
          rollbackSkill(skillName, current);
        }
      }
    } else {
      // 批量更新
      console.log('批量更新功能需要指定 skill 名称');
      console.log('使用: auto-update-skill update <skill-name>');
      console.log('或使用: auto-update-skill update --all');
    }
  } finally {
    rl.close();
  }
}

// 配置命令
async function configCommand(subCommand, ...args) {
  const config = loadConfig();
  
  switch (subCommand) {
    case 'blacklist':
      if (args[0] === 'add' && args[1]) {
        if (!config.blacklist.includes(args[1])) {
          config.blacklist.push(args[1]);
          saveConfig(config);
          console.log(`✅ 已将 ${args[1]} 加入黑名单`);
        } else {
          console.log(`${args[1]} 已在黑名单中`);
        }
      } else if (args[0] === 'remove' && args[1]) {
        config.blacklist = config.blacklist.filter(n => n !== args[1]);
        saveConfig(config);
        console.log(`✅ 已将 ${args[1]} 从黑名单移除`);
      } else if (args[0] === 'list') {
        console.log('黑名单:');
        config.blacklist.forEach(n => console.log(`  - ${n}`));
      } else {
        console.log('用法:');
        console.log('  auto-update-skill config blacklist add <skill>');
        console.log('  auto-update-skill config blacklist remove <skill>');
        console.log('  auto-update-skill config blacklist list');
      }
      break;
      
    case 'auto':
      if (args[0] === 'patch' || args[0] === 'minor' || args[0] === 'major') {
        const enabled = args[1] === 'true' || args[1] === 'on' || args[1] === 'yes';
        config.autoUpgrade[args[0]] = enabled;
        saveConfig(config);
        console.log(`${args[0]} 版本自动升级: ${enabled ? '开启' : '关闭'}`);
      } else {
        console.log('用法: auto-update-skill config auto <patch|minor|major> <true|false>');
      }
      break;
      
    default:
      console.log('当前配置:');
      console.log(JSON.stringify(config, null, 2));
  }
}

// 保存配置
function saveConfig(config) {
  try {
    fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
  } catch (e) {
    console.error('保存配置失败:', e.message);
  }
}

// 备份命令
async function backupCommand(subCommand, ...args) {
  if (subCommand === 'list') {
    try {
      if (!fs.existsSync(BACKUP_DIR)) {
        console.log('暂无备份');
        return;
      }
      
      const backups = fs.readdirSync(BACKUP_DIR);
      if (backups.length === 0) {
        console.log('暂无备份');
        return;
      }
      
      console.log('备份列表:');
      backups.forEach(b => {
        const stat = fs.statSync(path.join(BACKUP_DIR, b));
        const date = stat.mtime.toISOString().split('T')[0];
        console.log(`  - ${b} (${date})`);
      });
    } catch (e) {
      console.error('读取备份失败:', e.message);
    }
  } else if (subCommand === 'cleanup') {
    const keep = parseInt(args.find(a => !a.startsWith('--')) || '10');
    console.log(`保留最近 ${keep} 个备份（待实现）`);
  } else {
    console.log('用法:');
    console.log('  auto-update-skill backup list');
    console.log('  auto-update-skill backup cleanup [数量]');
  }
}

// 回滚命令
async function rollbackCommand(skillName, ...args) {
  if (!skillName) {
    console.log('用法: auto-update-skill rollback <skill-name> --version <version>');
    return;
  }
  
  const versionIndex = args.indexOf('--version');
  const version = versionIndex >= 0 ? args[versionIndex + 1] : null;
  
  if (!version) {
    console.log('请指定版本号: --version <version>');
    return;
  }
  
  const rl = createRL();
  const answer = await ask(rl, `确认将 ${skillName} 回滚到 ${version}? [y/N]: `);
  rl.close();
  
  if (answer.toLowerCase() === 'y') {
    if (rollbackSkill(skillName, version)) {
      console.log(`✅ ${skillName} 已回滚到 ${version}`);
    } else {
      console.log(`❌ 回滚失败`);
    }
  } else {
    console.log('已取消');
  }
}

// 刷新缓存
async function refreshCommand() {
  const cacheDir = path.join(process.env.HOME, '.openclaw', 'skill-update-cache');
  
  try {
    if (fs.existsSync(cacheDir)) {
      fs.rmSync(cacheDir, { recursive: true });
      console.log('✅ 缓存已清除');
    } else {
      console.log('没有缓存需要清除');
    }
  } catch (e) {
    console.error('清除缓存失败:', e.message);
  }
}

// 主函数
async function main() {
  const args = process.argv.slice(2);
  const command = args[0] || 'help';
  
  switch (command) {
    case 'check':
      await checkCommand(args[1], { verbose: args.includes('--verbose') });
      break;
      
    case 'update':
      await updateCommand(args[1], {
        force: args.includes('--force'),
        interactive: !args.includes('--no-interactive')
      });
      break;
      
    case 'config':
      await configCommand(args[1], ...args.slice(2));
      break;
      
    case 'backup':
      await backupCommand(args[1], ...args.slice(2));
      break;
      
    case 'rollback':
      await rollbackCommand(args[1], ...args.slice(2));
      break;
      
    case 'refresh':
      await refreshCommand();
      break;
      
    default:
      console.log(`
Auto Update Skill - 智能 Skill 更新工具

核心功能：在 skill 被触发时自动检查并提示更新

用法:
  auto-update-skill check [skill-name] [--verbose]
    检查更新，不执行升级

  auto-update-skill update <skill-name> [--force]
    执行更新（交互式确认）

  auto-update-skill config
    查看当前配置

  auto-update-skill config blacklist add <skill>
    添加 skill 到黑名单（不检查更新）

  auto-update-skill config blacklist remove <skill>
    从黑名单移除

  auto-update-skill config auto <patch|minor|major> <true|false>
    设置自动升级策略

  auto-update-skill backup list
    列出备份

  auto-update-skill rollback <skill> --version <version>
    回滚到指定版本

  auto-update-skill refresh
    清除版本缓存

更新原则:
  - Patch (1.0.1→1.0.2): 自动升级
  - Minor (1.1→1.2): 建议升级
  - Major (1→2): 需确认后升级
  - 升级前自动备份，失败自动回滚
`);
  }
}

main().catch(e => {
  console.error('错误:', e.message);
  process.exit(1);
});
