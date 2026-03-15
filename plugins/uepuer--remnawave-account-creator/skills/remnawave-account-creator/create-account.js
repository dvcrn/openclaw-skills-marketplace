#!/usr/bin/env node

/**
 * Remnawave 账号创建脚本
 * 
 * 用法:
 * node create-account.js \
 *   --username jim_pc \
 *   --email jim@codeforce.tech \
 *   --device-limit 1 \
 *   --traffic-gb 100 \
 *   --traffic-reset WEEKLY \
 *   --expire-days 365 \
 *   --squad "Ops Debugging" \
 *   --cc crads@codeforce.tech
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// 配置文件路径
const CONFIG_DIR = path.join(__dirname, '../../config');
const REMNAWAVE_CONFIG = path.join(CONFIG_DIR, 'remnawave.json');
const SQUADS_CONFIG = path.join(CONFIG_DIR, 'remnawave-squads.json');
const SMTP_CONFIG = path.join(CONFIG_DIR, 'smtp.json');

// 解析命令行参数
const args = process.argv.slice(2);
const params = {
  username: null,
  email: null,
  deviceLimit: 1,
  trafficGb: 100,
  trafficReset: 'WEEKLY',
  expireDays: 365,
  squad: null,
  cc: null
};

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--username' && args[i + 1]) params.username = args[++i];
  else if (args[i] === '--email' && args[i + 1]) params.email = args[++i];
  else if (args[i] === '--device-limit' && args[i + 1]) params.deviceLimit = parseInt(args[++i]);
  else if (args[i] === '--traffic-gb' && args[i + 1]) params.trafficGb = parseInt(args[++i]);
  else if (args[i] === '--traffic-reset' && args[i + 1]) params.trafficReset = args[++i];
  else if (args[i] === '--expire-days' && args[i + 1]) params.expireDays = parseInt(args[++i]);
  else if (args[i] === '--squad' && args[i + 1]) params.squad = args[++i];
  else if (args[i] === '--cc' && args[i + 1]) params.cc = args[++i];
}

// 验证必填参数
if (!params.username || !params.email) {
  console.error('❌ 错误：缺少必填参数');
  console.error('用法：node create-account.js --username <用户名> --email <邮箱> [其他选项]');
  console.error('\n必填参数:');
  console.error('  --username    账号用户名');
  console.error('  --email       用户邮箱');
  console.error('\n可选参数:');
  console.error('  --device-limit    设备限制 (默认：1)');
  console.error('  --traffic-gb      流量限制 GB (默认：100)');
  console.error('  --traffic-reset   流量重置周期 (默认：WEEKLY)');
  console.error('  --expire-days     过期天数 (默认：365)');
  console.error('  --squad           内部分组名称');
  console.error('  --cc              邮件抄送地址');
  process.exit(1);
}

// 读取配置文件
function readConfig(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    return JSON.parse(content);
  } catch (error) {
    console.error(`❌ 读取配置文件失败：${filePath}`);
    console.error(error.message);
    process.exit(1);
  }
}

// 调用 Remnawave API
function callApi(method, endpoint, data = null) {
  return new Promise((resolve, reject) => {
    const remnawaveConfig = readConfig(REMNAWAVE_CONFIG);
    const url = new URL(endpoint, remnawaveConfig.apiBaseUrl);
    
    const options = {
      hostname: url.hostname,
      port: 443,
      path: url.pathname + url.search,
      method: method,
      headers: {
        'Authorization': `Bearer ${remnawaveConfig.apiToken}`,
        'Content-Type': 'application/json'
      },
      rejectUnauthorized: remnawaveConfig.sslRejectUnauthorized !== false
    };
    
    const req = https.request(options, (res) => {
      let responseData = '';
      res.on('data', (chunk) => responseData += chunk);
      res.on('end', () => {
        try {
          const response = JSON.parse(responseData);
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(response);
          } else {
            reject(new Error(`API 错误：${res.statusCode} - ${JSON.stringify(response)}`));
          }
        } catch (error) {
          reject(new Error(`解析响应失败：${responseData}`));
        }
      });
    });
    
    req.on('error', reject);
    
    if (data) {
      req.write(JSON.stringify(data));
    }
    
    req.end();
  });
}

// 获取组 UUID（需要完整 UUID 格式）
function getSquadUuids(squadName) {
  if (!squadName) {
    // 默认分配到 Default-Squad
    return ["751440da-da97-4bc9-8a18-1074994189d1"];
  }
  
  const squadsConfig = readConfig(SQUADS_CONFIG);
  
  // 检查是否是完整 UUID
  if (squadName.includes('-')) {
    return [squadName];
  }
  
  // 从配置中查找
  const squadUuid = squadsConfig.squads[squadName.trim()];
  
  if (!squadUuid) {
    console.warn(`⚠️ 警告：找不到组 "${squadName}"，将分配到 Default-Squad`);
    return ["751440da-da97-4bc9-8a18-1074994189d1"];
  }
  
  // 如果配置的是短 UUID，需要补全为完整 UUID
  if (squadUuid.length < 36) {
    console.warn(`⚠️ 警告：组 UUID 格式不正确，需要完整 UUID 格式`);
    console.warn(`   当前：${squadUuid}`);
    console.warn(`   需要：xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`);
    return ["751440da-da97-4bc9-8a18-1074994189d1"];
  }
  
  return [squadUuid];
}

// 创建账号
async function createAccount() {
  console.log('🚀 开始创建 Remnawave 账号...\n');
  
  // 计算参数
  const trafficLimitBytes = params.trafficGb * 1024 * 1024 * 1024;
  const expireDate = new Date();
  expireDate.setDate(expireDate.getDate() + params.expireDays);
  const expireAt = expireDate.toISOString();
  
  const squadUuids = getSquadUuids(params.squad);
  
  // 流量重置策略映射
  const strategyMap = {
    'NO_RESET': 'NO_RESET',
    '不重置': 'NO_RESET',
    '每天': 'DAY',
    'DAILY': 'DAY',
    'DAY': 'DAY',
    '每周': 'WEEK',
    'WEEKLY': 'WEEK',
    'WEEK': 'WEEK',
    '每月': 'MONTH',
    'MONTHLY': 'MONTH',
    'MONTH': 'MONTH'
  };
  
  const trafficLimitStrategy = strategyMap[params.trafficReset?.toUpperCase()] || 'NO_RESET';
  
  const requestData = {
    username: params.username,
    email: params.email,
    hwidDeviceLimit: params.deviceLimit,
    trafficLimitBytes: trafficLimitBytes,
    trafficLimitStrategy: trafficLimitStrategy,
    expireAt: expireAt,
    activeInternalSquads: squadUuids  // ✅ 正确参数名
  };
  
  console.log('📋 账号信息:');
  console.log(`  用户名：${params.username}`);
  console.log(`  邮箱：${params.email}`);
  console.log(`  设备限制：${params.deviceLimit} 台`);
  console.log(`  流量限制：${params.trafficGb}GB`);
  console.log(`  流量重置：${params.trafficReset || 'NO_RESET'}`);
  console.log(`  过期时间：${expireDate.toISOString().split('T')[0]}`);
  if (params.squad) console.log(`  内部分组：${params.squad} ✅`);
  if (params.cc) console.log(`  邮件抄送：${params.cc}`);
  console.log('');
  
  try {
    // 调用 API 创建账号
    console.log('📡 调用 Remnawave API...');
    const response = await callApi('POST', '/api/users', requestData);
    
    const account = response.response;
    console.log('✅ 账号创建成功!\n');
    
    console.log('📋 账号详情:');
    console.log(`  UUID: ${account.uuid}`);
    console.log(`  短 UUID: ${account.shortUuid}`);
    console.log(`  状态：${account.status}`);
    console.log(`  VLESS UUID: ${account.vlessUuid}`);
    console.log(`  Trojan 密码：${account.trojanPassword}`);
    console.log(`  SS 密码：${account.ssPassword}`);
    console.log(`  订阅地址：${account.subscriptionUrl}`);
    console.log('');
    
    // 发送邮件
    console.log('📧 准备发送开通邮件...');
    await sendEmail(account);
    
    console.log('\n✅ 全部完成!\n');
    return account;
    
  } catch (error) {
    console.error('❌ 创建账号失败:', error.message);
    process.exit(1);
  }
}

// 发送邮件
async function sendEmail(account) {
  const { exec } = require('child_process');
  const util = require('util');
  const execPromise = util.promisify(exec);
  
  const sendEmailScript = path.join(CONFIG_DIR, 'send-template-email.js');
  const tutorialUrl = 'https://rjdx19yd9zo.sg.larksuite.com/docx/EwMLdN3asoQ44FxOlN6lQ6frgdh?from=from_copylink';
  const downloadUrl = 'https://v2raytun.com/';
  const sendDate = new Date().toISOString().split('T')[0];
  
  const vars = {
    recipient_name: params.username,
    account_name: params.username,
    subscription_url: account.subscriptionUrl,
    tutorial_url: tutorialUrl,
    download_url: downloadUrl,
    send_date: sendDate
  };
  
  let command = `node "${sendEmailScript}"`;
  command += ` --to "${params.email}"`;
  command += ` --template remnawave-account-created`;
  command += ` --vars '${JSON.stringify(vars)}'`;
  
  if (params.cc) {
    command += ` --cc "${params.cc}"`;
  }
  
  try {
    const { stdout, stderr } = await execPromise(command);
    console.log(stdout);
    if (stderr) console.error(stderr);
  } catch (error) {
    console.error('❌ 邮件发送失败:', error.message);
    if (error.stdout) console.log(error.stdout);
    if (error.stderr) console.error(error.stderr);
  }
}

// 主函数
createAccount();
