#!/usr/bin/env node

const WebSocket = require('ws');
const axios = require('axios');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// 从 workspace 配置文件加载配置
const CONFIG_PATH = path.join(process.env.HOME || '/root', '.openclaw/workspace/open-qq-config.json');

function loadConfig() {
  try {
    if (!fs.existsSync(CONFIG_PATH)) {
      console.error(`❌ 配置文件不存在：${CONFIG_PATH}`);
      console.error('请复制 open-qq-config.json.example 到 ~/.openclaw/workspace/open-qq-config.json 并填写配置');
      process.exit(1);
    }
    const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
    
    if (!config.qq?.appId || !config.qq?.token || !config.qq?.appSecret) {
      console.error('❌ 配置文件中缺少必需的 QQ 凭据 (qq.appId, qq.token, qq.appSecret)');
      process.exit(1);
    }
    
    return config;
  } catch (error) {
    console.error('❌ 读取配置文件失败:', error.message);
    process.exit(1);
  }
}

const config = loadConfig();
const QQBotLogger = require('./logger');
const logger = new QQBotLogger(config);

class QQBot {
  constructor(config) {
    this.appId = config.qq.appId;
    this.token = config.qq.token;
    this.appSecret = config.qq.appSecret;
    this.botConfig = config.bot || {};
    this.ws = null;
    this.sessionId = null;
    this.lastSeq = 0;
  }

  async getAccessToken(retryCount = 0) {
    logger.log('Requesting access token from QQ API', { appId: this.appId });
    
    try {
      const response = await axios.post(
        'https://bots.qq.com/app/getAppAccessToken',
        { appId: this.appId, clientSecret: this.appSecret },
        { timeout: 30000 }
      );
      
      logger.log('Access token received successfully', { expiresIn: response.data.expires_in });
      logger.logApiCall('getAppAccessToken', { appId: this.appId }, response);
      
      return response.data.access_token;
    } catch (error) {
      logger.error('Failed to get access token', error);
      
      if (retryCount < 3) {
        logger.log(`Retrying access token request (${retryCount + 1}/3)`);
        await new Promise(resolve => setTimeout(resolve, 2000 * (retryCount + 1)));
        return this.getAccessToken(retryCount + 1);
      }
      
      throw error;
    }
  }

  async sendToOpenClawAndWait(messageData) {
    const message = messageData.content.trim();
    
    logger.log('Sending message to OpenClaw session', {
      userId: messageData.author.id,
      groupId: messageData.group_id || 'direct',
      message,
    });
    
    try {
      const isPrivate = messageData.msg_type === 'private';
      const openId = isPrivate 
        ? messageData.author.user_openid 
        : messageData.group_openid;
      
      let sessionLabel = isPrivate 
        ? `qq-private-${openId}` 
        : `qq-group-${openId}`;
      
      sessionLabel = sessionLabel.replace(/[^a-zA-Z0-9-]/g, '');
      
      const senderId = isPrivate 
        ? (messageData.author.user_openid || 'unknown_user')
        : (messageData.author.member_openid || 'unknown_member');
      
      const senderPrefix = isPrivate 
        ? `[QQ User: ${senderId}] `
        : `[QQ Member: ${senderId}] `;
      
      const messageWithSender = `${senderPrefix}${message}`;
      
      const openclaw = spawn('openclaw', [
        'agent',
        '--session-id', sessionLabel,
        '--message', messageWithSender
      ]);
      
      const stdoutChunks = [];
      const stderrChunks = [];
      
      openclaw.stdout.on('data', (chunk) => stdoutChunks.push(chunk));
      openclaw.stderr.on('data', (chunk) => stderrChunks.push(chunk));
      
      const exitCode = await new Promise((resolve) => {
        openclaw.on('close', resolve);
        openclaw.on('error', () => resolve(1));
      });
      
      const output = Buffer.concat(stdoutChunks).toString().trim();
      const errorOutput = Buffer.concat(stderrChunks).toString().trim();
      
      logger.log('OpenClaw raw output', {
        outputLength: output.length,
        errorLength: errorOutput.length,
        exitCode
      });
      
      // 处理回复
      let openclawReply = output || errorOutput;
      openclawReply = openclawReply.replace(/^```[\s\S]*?\n/, '').replace(/```$/, '').trim();
      
      if (!openclawReply || openclawReply.trim() === '') {
        openclawReply = '🤖 抱歉，机器人没有返回内容！';
      }
      
      logger.log('OpenClaw reply received', {
        replyLength: openclawReply.length,
        sessionLabel,
        exitCode
      });
      
      logger.logOpenClawInteraction(messageWithSender, openclawReply);
      
      return openclawReply;
    } catch (error) {
      logger.error('OpenClaw session failed', { error: error.message });
      return '🤖 抱歉，机器人处理消息时出错了！请稍后再试。';
    }
  }

  async sendReply(messageData, content, retryCount = 0) {
    try {
      const accessToken = await this.getAccessToken();
      const isGroup = messageData.msg_type === 'group';
      
      logger.log('Sending reply to QQ', {
        content,
        target: isGroup ? `group:${messageData.group_id}` : `user:${messageData.author.id}`
      });
      
      const url = isGroup
        ? `https://api.sgroup.qq.com/v2/groups/${messageData.group_id}/messages`
        : `https://api.sgroup.qq.com/v2/users/${messageData.author.id}/messages`;
      
      const body = isGroup
        ? { content, msg_id: messageData.id }
        : { content };
      
      const response = await axios.post(url, body, {
        headers: {
          'Authorization': `QQBot ${accessToken}`,
          'Content-Type': 'application/json'
        },
        timeout: 10000
      });
      
      logger.log(`${isGroup ? 'Group' : 'Private'} reply sent successfully`, {
        [isGroup ? 'groupId' : 'userId']: isGroup ? messageData.group_id : messageData.author.id,
        messageId: response.data?.id
      });
      
      logger.logApiCall('sendMessage', {
        target: isGroup ? `group:${messageData.group_id}` : `user:${messageData.author.id}`,
        content
      }, response);
      
    } catch (error) {
      if (retryCount < 2) {
        logger.log(`Retrying message send (${retryCount + 1}/2)`);
        await new Promise(resolve => setTimeout(resolve, 1000 * (retryCount + 1)));
        return this.sendReply(messageData, content, retryCount + 1);
      }
      
      logger.error('Failed to send reply to QQ after retries', error);
    }
  }

  async handleMessage(event) {
    const isPrivate = event.t === 'C2C_MESSAGE_CREATE';
    const isGroupAt = event.t === 'GROUP_AT_MESSAGE_CREATE';
    
    if (!isPrivate && !isGroupAt) {
      logger.log('Unhandled event type', { eventType: event.t });
      return;
    }
    
    // 记录消息
    const msgData = event.d;
    logger.log(`${isPrivate ? 'Private' : 'Group @'} message received from QQ`, {
      eventType: event.t,
      messageId: msgData.id,
      content: msgData.content,
      authorId: isPrivate ? msgData.author.user_openid : msgData.author.member_openid,
      ...(isGroupAt && { groupId: msgData.group_openid }),
      timestamp: msgData.timestamp
    });
    
    // 标记消息类型
    msgData.msg_type = isPrivate ? 'private' : 'group';
    if (isPrivate) {
      msgData.author.id = msgData.author.user_openid;
    } else {
      msgData.group_id = msgData.group_openid;
    }
    
    // 获取回复并发送
    const reply = await this.sendToOpenClawAndWait(msgData);
    await this.sendReply(msgData, reply);
  }

  async connect() {
    const accessToken = await this.getAccessToken();
    
    // 获取 WebSocket 连接参数
    const wsParams = await axios.get('https://api.sgroup.qq.com/gateway/bot', {
      headers: { 'Authorization': `QQBot ${accessToken}` }
    });
    
    const wsUrl = `${wsParams.data.url}?compress=0`;
    console.log('🔗 Connecting to QQ WebSocket:', wsUrl);
    
    this.ws = new WebSocket(wsUrl);
    
    this.ws.on('open', () => {
      console.log('✅ WebSocket connected');
    });
    
    this.ws.on('message', async (data) => {
      const event = JSON.parse(data);
      logger.log('Received WebSocket message', { 
        op: event.op, 
        t: event.t,
        hasD: !!event.d,
        dKeys: event.d ? Object.keys(event.d) : []
      });
      
      // HELLO 事件
      if (event.op === 10) {
        this.sessionId = event.d.session_id;
        this.lastSeq = 0;
        logger.log('Received HELLO event from QQ gateway', {
          sessionId: this.sessionId,
          lastSeq: this.lastSeq
        });
        
        this.ws.send(JSON.stringify({
          op: 2, // IDENTIFY
          d: {
            token: `QQBot ${accessToken}`,
            intents: (1 << 0) | (1 << 25), // 私域完整权限
            shard: [0, 1],
            properties: { os: 'linux', browser: 'openclaw' }
          }
        }));
        logger.log('Sent IDENTIFY payload to QQ gateway');
        
      } else if (event.op === 11) {
        // HEARTBEAT ACK
        logger.log('Heartbeat ACK received from QQ gateway');
        
      } else if (event.op === 0 && event.t) {
        // 消息事件
        await this.handleMessage(event);
        
      } else {
        // 其他事件
        logger.log('Non-message event received', { op: event.op, t: event.t });
      }
    });
    
    this.ws.on('error', (error) => {
      logger.error('WebSocket error', error);
    });
    
    this.ws.on('close', (code, reason) => {
      console.log(`❌ WebSocket disconnected (code: ${code}), reconnecting...`);
      logger.log('WebSocket disconnected', { code, reason: reason?.toString() });
      setTimeout(() => this.connect(), this.botConfig.reconnectDelay || 5000);
    });
    
    // 启动心跳
    const heartbeatInterval = this.botConfig.heartbeatInterval || 30000;
    this.heartbeatInterval = setInterval(() => {
      if (this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ op: 1, d: this.lastSeq }));
        console.log('💓 Sending heartbeat');
      }
    }, heartbeatInterval);
    
    // 启动完成提示
    console.log('');
    console.log('✅ QQ Bot 已就绪，可以接收消息了！');
    console.log('');
    logger.log('QQ Bot started successfully', {
      appId: this.appId,
      heartbeatInterval,
      reconnectDelay: this.botConfig.reconnectDelay || 5000
    });
  }
}

// 启动机器人
console.log('🚀 正在启动 QQ Bot...');
const bot = new QQBot(config);
bot.connect().catch((error) => {
  console.error('❌ 启动失败:', error.message);
  process.exit(1);
});

// 优雅关闭处理
let isShuttingDown = false;

process.on('SIGTERM', handleShutdown);
process.on('SIGINT', handleShutdown);

async function handleShutdown() {
  if (isShuttingDown) return;
  isShuttingDown = true;
  
  console.log('');
  console.log('🛑 正在关闭 QQ Bot...');
  logger.log('Shutting down QQ Bot');
  
  // 关闭 WebSocket 连接
  if (bot.ws) {
    bot.ws.removeAllListeners('close');
    bot.ws.close();
  }
  
  // 停止心跳
  if (bot.heartbeatInterval) {
    clearInterval(bot.heartbeatInterval);
  }
  
  // 等待一下确保连接关闭
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  console.log('✅ QQ Bot 已关闭');
  logger.log('QQ Bot shutdown complete');
  process.exit(0);
}
