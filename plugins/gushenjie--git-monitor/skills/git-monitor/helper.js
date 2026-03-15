#!/usr/bin/env node
/**
 * Git 项目监控助手 - 支持 GitHub、GitLab、Gitee 等所有 Git 平台
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const CONFIG_PATH = path.join(__dirname, 'config.json');
const SCRIPT_PATH = path.join(__dirname, 'monitor.sh');

// 检查是否为 verbose 模式
const VERBOSE = process.argv.includes('--verbose') || process.argv.includes('-v');

// 日志函数
function log(message) {
  if (VERBOSE) {
    console.log(message);
  }
}

// 读取配置
function loadConfig() {
  if (!fs.existsSync(CONFIG_PATH)) {
    const defaultConfig = {
      repositories: [],
      checkInterval: '6h',
      notifyChannel: 'feishu',
      maxCommitsToShow: 10,
      includeDiffSummary: true
    };
    saveConfig(defaultConfig);
    return defaultConfig;
  }
  return JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
}

// 保存配置
function saveConfig(config) {
  fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
}

// 解析仓库 URL 或简写
function parseRepoInput(input) {
  // 完整 URL
  if (input.startsWith('http://') || input.startsWith('https://')) {
    const url = new URL(input);
    const pathParts = url.pathname.replace(/\.git$/, '').split('/').filter(Boolean);
    
    if (pathParts.length < 2) {
      throw new Error('无效的仓库 URL');
    }
    
    const owner = pathParts[0];
    const repo = pathParts[1];
    const platform = url.hostname.includes('gitlab') ? 'gitlab' : 
                     url.hostname.includes('gitee') ? 'gitee' : 'github';
    
    return {
      url: input.endsWith('.git') ? input : input + '.git',
      name: `${owner}-${repo}`,
      platform,
      owner,
      repo
    };
  }
  
  // 简写格式: owner/repo 或 platform:owner/repo
  let platform = 'github';
  let repoPath = input;
  
  if (input.includes(':')) {
    [platform, repoPath] = input.split(':');
  }
  
  const [owner, repo] = repoPath.split('/');
  if (!owner || !repo) {
    throw new Error('无效的仓库格式，应为 owner/repo 或 platform:owner/repo');
  }
  
  // 构建 URL
  const platformUrls = {
    github: 'https://github.com',
    gitlab: 'https://gitlab.com',
    gitee: 'https://gitee.com'
  };
  
  const baseUrl = platformUrls[platform.toLowerCase()] || platformUrls.github;
  const url = `${baseUrl}/${owner}/${repo}.git`;
  
  return {
    url,
    name: `${owner}-${repo}`,
    platform: platform.toLowerCase(),
    owner,
    repo
  };
}

// 添加仓库
function addRepository(input, branch = 'main') {
  const config = loadConfig();
  
  try {
    const repoInfo = parseRepoInput(input);
    
    // 检查是否已存在
    const existing = config.repositories.find(r => r.url === repoInfo.url);
    if (existing) {
      console.log(`⚠️  仓库已存在: ${existing.name}`);
      return existing;
    }
    
    const localPath = path.join(
      process.env.HOME,
      '.openclaw/workspace/repos',
      repoInfo.name
    );
    
    const repo = {
      url: repoInfo.url,
      name: repoInfo.name,
      platform: repoInfo.platform,
      owner: repoInfo.owner,
      repo: repoInfo.repo,
      localPath,
      branch,
      lastChecked: null,
      lastCommit: null,
      addedAt: new Date().toISOString()
    };
    
    config.repositories.push(repo);
    saveConfig(config);
    
    console.log(`✅ 已添加仓库: ${repo.name}`);
    console.log(`   平台: ${repo.platform}`);
    console.log(`   URL: ${repo.url}`);
    console.log(`   本地路径: ${repo.localPath}`);
    
    return repo;
  } catch (error) {
    console.error(`❌ 添加失败: ${error.message}`);
    throw error;
  }
}

// 删除仓库
function removeRepository(nameOrUrl) {
  const config = loadConfig();
  
  const index = config.repositories.findIndex(r => 
    r.name === nameOrUrl || r.url === nameOrUrl || 
    `${r.owner}/${r.repo}` === nameOrUrl
  );
  
  if (index === -1) {
    console.log(`⚠️  未找到仓库: ${nameOrUrl}`);
    return false;
  }
  
  const repo = config.repositories[index];
  config.repositories.splice(index, 1);
  saveConfig(config);
  
  console.log(`✅ 已删除仓库: ${repo.name}`);
  console.log(`   提示: 本地文件未删除，位于 ${repo.localPath}`);
  
  return true;
}

// 列出所有仓库
function listRepositories() {
  const config = loadConfig();
  
  if (config.repositories.length === 0) {
    console.log('📋 当前没有监控任何仓库');
    console.log('');
    console.log('使用以下命令添加仓库:');
    console.log('  node helper.js add owner/repo');
    console.log('  node helper.js add https://github.com/owner/repo');
    console.log('  node helper.js add gitlab:owner/repo');
    return;
  }
  
  console.log(`📋 监控列表 (共 ${config.repositories.length} 个仓库):\n`);
  
  config.repositories.forEach((repo, index) => {
    console.log(`${index + 1}. 📦 ${repo.name}`);
    console.log(`   平台: ${repo.platform}`);
    console.log(`   URL: ${repo.url}`);
    console.log(`   本地: ${repo.localPath}`);
    console.log(`   分支: ${repo.branch}`);
    console.log(`   最后检查: ${repo.lastChecked || '从未检查'}`);
    console.log(`   最新 commit: ${repo.lastCommit?.substring(0, 7) || '未知'}`);
    console.log('');
  });
}

// 执行监控脚本
function checkRepository(repo) {
  const { url, name, localPath, branch = 'main' } = repo;
  
  log(`\n🔍 检查仓库: ${name}`);
  
  try {
    const output = execSync(
      `bash "${SCRIPT_PATH}" "${url}" "${name}" "${localPath}" "${branch}"`,
      { encoding: 'utf8', maxBuffer: 10 * 1024 * 1024 }
    );
    
    return parseOutput(output, repo);
  } catch (error) {
    console.error(`❌ 检查失败: ${error.message}`);
    return { hasUpdates: false, error: error.message };
  }
}

// 解析脚本输出
function parseOutput(output, repo) {
  if (output.includes('NO_UPDATES')) {
    return { hasUpdates: false, repo: repo.name };
  }
  
  if (output.includes('INITIAL_COMMIT=')) {
    const match = output.match(/INITIAL_COMMIT=([a-f0-9]+)/);
    return {
      isInitial: true,
      repo: repo.name,
      commit: match ? match[1] : null
    };
  }
  
  // 提取 commits
  const commitsMatch = output.match(/=== COMMITS_START ===\n([\s\S]*?)\n=== COMMITS_END ===/);
  const commits = commitsMatch ? parseCommits(commitsMatch[1]) : [];
  
  // 提取统计信息
  const statsMatch = output.match(/=== STATS_START ===\n([\s\S]*?)\n=== STATS_END ===/);
  const stats = statsMatch ? statsMatch[1].trim() : '';
  
  // 提取文件变更
  const filesMatch = output.match(/=== FILES_START ===\n([\s\S]*?)\n=== FILES_END ===/);
  const files = filesMatch ? parseFiles(filesMatch[1]) : [];
  
  // 提取 commit hash
  const oldCommitMatch = output.match(/OLD_COMMIT=([a-f0-9]+)/);
  const newCommitMatch = output.match(/NEW_COMMIT=([a-f0-9]+)/);
  
  return {
    hasUpdates: true,
    repo: repo.name,
    platform: repo.platform,
    owner: repo.owner,
    repoName: repo.repo,
    oldCommit: oldCommitMatch ? oldCommitMatch[1] : null,
    newCommit: newCommitMatch ? newCommitMatch[1] : null,
    commits,
    stats,
    files
  };
}

// 解析 commit 列表
function parseCommits(text) {
  return text.trim().split('\n').filter(Boolean).map(line => {
    const [hash, author, time, ...messageParts] = line.split('|');
    return {
      hash: hash?.substring(0, 7),
      fullHash: hash,
      author,
      time,
      message: messageParts.join('|')
    };
  });
}

// 解析文件变更
function parseFiles(text) {
  return text.trim().split('\n').filter(Boolean).map(line => {
    const [status, ...pathParts] = line.split('\t');
    return {
      status: status.trim(),
      path: pathParts.join('\t').trim()
    };
  });
}

// 生成摘要
function generateSummary(result) {
  if (!result.hasUpdates) {
    return `[无更新] ${result.repo} - 已是最新版本`;
  }
  
  if (result.isInitial) {
    return `[初始化] ${result.repo}\n初始 commit: ${result.commit?.substring(0, 7)}`;
  }
  
  const { repo, platform, owner, repoName, commits, stats, files, oldCommit, newCommit } = result;
  
  // 标题
  let summary = `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
  summary += `代码更新通知\n`;
  summary += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n`;
  
  // 仓库信息
  summary += `【仓库】${repo}\n`;
  summary += `【平台】${platform.toUpperCase()}\n`;
  summary += `【时间】${new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })}\n\n`;
  
  // Commits
  summary += `━━ 提交记录 (${commits.length} 个) ━━\n\n`;
  commits.slice(0, 5).forEach((c, index) => {
    summary += `${index + 1}. [${c.hash}] ${c.message}\n`;
    summary += `   作者: ${c.author} | 时间: ${c.time}\n\n`;
  });
  if (commits.length > 5) {
    summary += `... 还有 ${commits.length - 5} 个提交\n\n`;
  }
  
  // 文件变更
  const added = files.filter(f => f.status === 'A');
  const modified = files.filter(f => f.status === 'M');
  const deleted = files.filter(f => f.status === 'D');
  
  summary += `━━ 文件变更 ━━\n\n`;
  
  if (added.length > 0) {
    summary += `[新增] ${added.length} 个文件\n`;
    added.slice(0, 5).forEach(f => summary += `  + ${f.path}\n`);
    if (added.length > 5) {
      summary += `  ... 还有 ${added.length - 5} 个文件\n`;
    }
    summary += '\n';
  }
  
  if (modified.length > 0) {
    summary += `[修改] ${modified.length} 个文件\n`;
    modified.slice(0, 5).forEach(f => summary += `  * ${f.path}\n`);
    if (modified.length > 5) {
      summary += `  ... 还有 ${modified.length - 5} 个文件\n`;
    }
    summary += '\n';
  }
  
  if (deleted.length > 0) {
    summary += `[删除] ${deleted.length} 个文件\n`;
    deleted.slice(0, 5).forEach(f => summary += `  - ${f.path}\n`);
    if (deleted.length > 5) {
      summary += `  ... 还有 ${deleted.length - 5} 个文件\n`;
    }
    summary += '\n';
  }
  
  // 统计信息
  const statsLines = stats.split('\n');
  const summaryLine = statsLines[statsLines.length - 1];
  if (summaryLine) {
    summary += `━━ 代码统计 ━━\n\n`;
    summary += `${summaryLine}\n\n`;
  }
  
  // 链接
  const platformUrls = {
    github: 'https://github.com',
    gitlab: 'https://gitlab.com',
    gitee: 'https://gitee.com'
  };
  const baseUrl = platformUrls[platform] || platformUrls.github;
  const compareUrl = `${baseUrl}/${owner}/${repoName}/compare/${oldCommit?.substring(0, 7)}...${newCommit?.substring(0, 7)}`;
  
  summary += `━━ 详细信息 ━━\n\n`;
  summary += `查看完整对比: ${compareUrl}\n`;
  summary += `提交范围: ${oldCommit?.substring(0, 7)} → ${newCommit?.substring(0, 7)}\n\n`;
  summary += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
  
  return summary;
}

// 主函数
function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  if (command === 'add') {
    const input = args[1];
    const branch = args[2] || 'main';
    
    if (!input) {
      console.error('❌ 请指定仓库');
      console.log('用法: node helper.js add <repo>');
      console.log('示例:');
      console.log('  node helper.js add owner/repo');
      console.log('  node helper.js add https://github.com/owner/repo');
      console.log('  node helper.js add gitlab:owner/repo');
      console.log('  node helper.js add https://gitee.com/owner/repo');
      process.exit(1);
    }
    
    addRepository(input, branch);
    
  } else if (command === 'remove' || command === 'delete') {
    const nameOrUrl = args[1];
    
    if (!nameOrUrl) {
      console.error('❌ 请指定要删除的仓库');
      console.log('用法: node helper.js remove <name|url>');
      process.exit(1);
    }
    
    removeRepository(nameOrUrl);
    
  } else if (command === 'list') {
    listRepositories();
    
  } else if (command === 'check') {
    const config = loadConfig();
    const repoName = args[1];
    
    let repos = config.repositories;
    if (repoName) {
      repos = repos.filter(r => 
        r.name === repoName || 
        `${r.owner}/${r.repo}` === repoName
      );
      
      if (repos.length === 0) {
        console.error(`❌ 未找到仓库: ${repoName}`);
        process.exit(1);
      }
    }
    
    if (repos.length === 0) {
      console.log('📋 当前没有监控任何仓库');
      console.log('使用 node helper.js add <repo> 添加仓库');
      process.exit(0);
    }
    
    const results = repos.map(repo => {
      const result = checkRepository(repo);
      
      // 更新配置
      if (result.hasUpdates || result.isInitial) {
        repo.lastChecked = new Date().toISOString();
        if (result.newCommit) {
          repo.lastCommit = result.newCommit;
        } else if (result.commit) {
          repo.lastCommit = result.commit;
        }
      }
      
      return result;
    });
    
    saveConfig(config);
    
    // 输出结果
    console.log('\n' + '='.repeat(60));
    results.forEach(result => {
      console.log('\n' + generateSummary(result));
    });
    console.log('='.repeat(60) + '\n');
    
    // 返回 JSON 供 OpenClaw 使用
    console.log('\n=== JSON_RESULT ===');
    console.log(JSON.stringify(results, null, 2));
    
  } else if (command === 'status') {
    listRepositories();
    
  } else {
    console.log('Git 项目监控工具 - 支持 GitHub、GitLab、Gitee 等所有 Git 平台\n');
    console.log('用法:');
    console.log('  node helper.js add <repo> [branch]     - 添加监控仓库');
    console.log('  node helper.js remove <name>           - 删除监控仓库');
    console.log('  node helper.js list                    - 列出所有仓库');
    console.log('  node helper.js check [repo-name]       - 检查更新');
    console.log('  node helper.js status                  - 查看监控状态');
    console.log('');
    console.log('示例:');
    console.log('  node helper.js add anthropics/skills');
    console.log('  node helper.js add https://github.com/openai/openai-python');
    console.log('  node helper.js add gitlab:gitlab-org/gitlab');
    console.log('  node helper.js add https://gitee.com/mindspore/mindspore');
    console.log('  node helper.js check anthropics-skills');
    console.log('  node helper.js remove anthropics-skills');
  }
}

if (require.main === module) {
  main();
}

module.exports = { addRepository, removeRepository, checkRepository, generateSummary, listRepositories };
