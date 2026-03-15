#!/usr/bin/env node
/**
 * 每日热搜速览推送脚本
 * 抓取微博、知乎、百度、B站热搜并发送到 Discord
 */

const https = require('https');

// Discord 子区 ID
const THREAD_ID = "1482024661033287771";

// API Base URL
const API_BASE = "https://60s.viki.moe/v2";

// 平台配置
const platforms = [
  { name: '微博热搜', key: 'weibo', emoji: '🔥', format: formatWeibo },
  { name: '知乎热榜', key: 'zhihu', emoji: '💡', format: formatZhihu },
  { name: '百度热搜', key: 'baidu/hot', emoji: '🔍', format: formatBaidu },
  { name: 'B站热门', key: 'bili', emoji: '📺', format: formatBili }
];

// HTTP GET 请求
function fetch(url) {
  return new Promise((resolve, reject) => {
    https.get(url, { timeout: 10000 }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(e);
        }
      });
    }).on('error', reject);
  });
}

// 格式化微博热搜
function formatWeibo(data) {
  if (!data?.data?.length) return [];
  return data.data.slice(0, 5).map((item, i) => {
    const hot = Math.floor(item.hot_value / 10000);
    return `**${i + 1}.** [${item.title}](${item.link}) \`${hot}万\``;
  });
}

// 格式化知乎热榜
function formatZhihu(data) {
  if (!data?.data?.length) return [];
  return data.data.slice(0, 5).map((item, i) => {
    const title = item.title.length > 40 ? item.title.slice(0, 40) : item.title;
    const hot = item.hot_value_desc?.replace('热度', '').trim() || '';
    return `**${i + 1}.** [${title}](${item.link}) \`${hot}\``;
  });
}

// 格式化百度热搜
function formatBaidu(data) {
  if (!data?.data?.length) return [];
  return data.data.slice(0, 5).map((item, i) => {
    const hot = item.score_desc || '';
    return `**${i + 1}.** [${item.title}](${item.url}) \`${hot}\``;
  });
}

// 格式化B站热门
function formatBili(data) {
  if (!data?.data?.length) return [];
  return data.data.slice(0, 5).map((item, i) => {
    return `**${i + 1}.** [${item.title}](${item.link})`;
  });
}

// 主函数
async function main() {
  console.log('🚀 开始获取热搜数据...\n');

  const date = new Date();
  const dateStr = date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'Asia/Shanghai'
  });

  let message = `📅 **${dateStr}** 每日热搜速览\n\n`;

  for (const platform of platforms) {
    console.log(`📡 获取 ${platform.name}...`);
    try {
      const url = `${API_BASE}/${platform.key}`;
      const data = await fetch(url);
      const lines = platform.format(data);

      if (lines.length > 0) {
        message += `**${platform.emoji} ${platform.name} TOP 5**\n`;
        message += lines.join('\n') + '\n\n';
      }
    } catch (e) {
      console.error(`❌ ${platform.name} 获取失败:`, e.message);
    }
  }

  message += '---\n_由 OpenClaw 自动推送_';

  console.log('\n📄 生成的消息:');
  console.log('─'.repeat(40));
  console.log(message);
  console.log('─'.repeat(40));

  // 输出到文件供 message tool 读取
  const fs = require('fs');
  const outputPath = '/tmp/hot-topics-message.md';
  fs.writeFileSync(outputPath, message);
  console.log(`\n✅ 消息已保存到: ${outputPath}`);
  console.log(`📍 Discord 子区 ID: ${THREAD_ID}`);

  return { message, threadId: THREAD_ID };
}

main().catch(console.error);
