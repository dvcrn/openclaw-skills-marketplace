#!/usr/bin/env node

/**
 * News Fetcher - 新闻获取工具 v3
 * 
 * 用法:
 *   node fetch_news.mjs <url>
 *   node fetch_news.mjs <url> --method archive
 *   node fetch_news.mjs <url> --method jina
 *   node fetch_news.mjs <url> --search "关键词"
 */

import fetch from 'node-fetch';

const TAVILY_API_KEY = process.env.TAVILY_API_KEY;

const args = process.argv.slice(2);
const url = args.find(a => !a.startsWith('--'));
const methodIndex = args.indexOf('--method');
const method = methodIndex > -1 ? args[methodIndex + 1] : 'auto';
const searchIndex = args.indexOf('--search');
const searchQuery = searchIndex > -1 ? args[searchIndex + 1] : null;

if (!url && !searchQuery) {
  console.log('News Fetcher v3 - 新闻获取工具\n');
  console.log('用法:');
  console.log('  node fetch_news.mjs <url>');
  console.log('  node fetch_news.mjs <url> --method archive|jina|direct');
  console.log('  node fetch_news.mjs <url> --search "关键词"');
  console.log('\n方法说明:');
  console.log('  archive - archive.today 公开存档');
  console.log('  jina    - r.jina.ai 文本提取');
  console.log('  direct  - 直接访问');
  console.log('  auto    - 自动尝试（默认）');
  process.exit(1);
}

// 公开存档服务
const archiveServices = {
  archive: (url) => `https://archive.today/${url}`,
  wayback: (url) => `https://web.archive.org/web/${url}`,
  jina: (url) => `https://r.jina.ai/http://${url}`,
  direct: (url) => url
};

// 使用 Tavily 搜索
async function searchAlternatives(query) {
  if (!TAVILY_API_KEY) {
    throw new Error('需要设置 TAVILY_API_KEY 环境变量');
  }

  const response = await fetch('https://api.tavily.com/search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${TAVILY_API_KEY}`
    },
    body: JSON.stringify({
      query: `${query} (site:bbc.com OR site:reuters.com OR site:apnews.com OR site:aljazeera.com)`,
      max_results: 10
    })
  });

  const data = await response.json();
  return data.results || [];
}

// 直接获取
async function fetchDirect(targetUrl) {
  const response = await fetch(targetUrl, {
    headers: {
      'User-Agent': 'Mozilla/5.0 (compatible; NewsFetcher/3.0)'
    }
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  const text = await response.text();
  return { raw_content: text };
}

// 尝试获取内容
async function tryFetch(originalUrl, methodName) {
  const targetUrl = archiveServices[methodName](originalUrl);
  
  console.log(`  尝试 ${methodName}: ${targetUrl.substring(0, 60)}...`);
  
  try {
    let result;
    
    if (methodName === 'direct') {
      result = await fetchDirect(targetUrl);
    } else if (methodName === 'jina') {
      const response = await fetch(targetUrl);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const text = await response.text();
      result = { raw_content: text };
    } else {
      // archive.today 等存档服务
      result = await fetchDirect(targetUrl);
    }
    
    if (result.raw_content && result.raw_content.length > 300) {
      return {
        success: true,
        method: methodName,
        content: result.raw_content,
        length: result.raw_content.length
      };
    }
    
    return { success: false, reason: '内容不足' };
  } catch (err) {
    return { success: false, reason: err.message };
  }
}

// 主函数
async function main() {
  console.log('━'.repeat(50));
  console.log('📰 News Fetcher v3 - 公开存档访问');
  console.log('━'.repeat(50) + '\n');

  // 搜索模式
  if (searchQuery) {
    console.log(`🔍 搜索相关文章: "${searchQuery}"\n`);
    const results = await searchAlternatives(searchQuery);
    
    if (results.length === 0) {
      console.log('❌ 未找到相关文章');
      return;
    }
    
    console.log(`✓ 找到 ${results.length} 篇相关文章:\n`);
    results.forEach((r, i) => {
      console.log(`${i + 1}. ${r.title || '无标题'}`);
      console.log(`   📎 ${r.url}`);
      if (r.content) {
        console.log(`   📝 ${r.content.substring(0, 100)}...`);
      }
      console.log('');
    });
    return;
  }

  // 获取模式
  console.log(`🔗 原始链接: ${url}`);
  console.log(`🎯 方法: ${method}\n`);

  // 确定要尝试的方法
  const methodsToTry = method === 'auto' 
    ? ['archive', 'wayback', 'jina', 'direct'] 
    : [method];

  // 尝试每个方法
  for (const m of methodsToTry) {
    const result = await tryFetch(url, m);
    
    if (result.success) {
      console.log(`\n✅ 成功获取 (${result.method})`);
      console.log(`   📊 ${result.length} 字符\n`);
      console.log('─'.repeat(50));
      console.log('📄 文章内容:\n');
      console.log(result.content);
      return;
    }
    
    console.log(`   ❌ ${result.reason}`);
  }

  // 全部失败
  console.log('\n' + '─'.repeat(50));
  console.log('❌ 所有方法都失败了\n');
  console.log('💡 建议:');
  console.log('   1. 搜索替代信源（BBC/Reuters/AP）');
  console.log('   2. 手动访问 archive.today');
  console.log('   3. 查看其他媒体报道同一事件');
}

main().catch(err => {
  console.error('\n❌ 错误:', err.message);
  process.exit(1);
});
