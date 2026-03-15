---
name: playwright-scraper
description: "Playwright网页爬取技能。使用真实浏览器操作（点击、滚动、等待JS渲染）来爬取复杂动态网页。支持多Tab、懒加载、SPA单页应用。适用于会议议程、展会信息等公开信息型网站。"
---

# Playwright 网页爬取技能

## 功能概述

使用Playwright进行真实浏览器操作，爬取复杂动态网页。

### 核心能力
- ✅ **真实浏览器操作** - 点击、滚动、输入、等待
- ✅ **处理复杂SPA** - 单页应用、多Tab、懒加载
- ✅ **AI自动生成脚本** - 无需提前准备，实时分析页面结构
- ✅ **持久化Chrome Profile** - 复用登录状态
- ✅ **数据结构化输出** - 自动整理成Markdown/JSON

### 对比优势

| 工具 | 局限性 | Playwright优势 |
|------|--------|----------------|
| **n8n** | 无法处理JS渲染 | ✅ 完整JS渲染支持 |
| **Apify** | 需要现成actor | ✅ AI实时生成脚本 |
| **Bright Data** | 按量计费 | ✅ 本地运行，免费 |

### 适用场景
- ✅ **公开信息型网站** - 会议日程、展会信息
- ✅ **多Tab懒加载页面** - 需点击切换的内容
- ✅ **SPA单页应用** - JavaScript异步加载

### 不适用场景
- ⚠️ **反爬机制强的网站** - 需要复杂验证
- ⚠️ **需多轮调试的场景** - 效率不高
- ⚠️ **生产环境** - 需要高度稳定性

---

## 使用方式

### 1. 基本爬取（单页面）
```
官家，请帮我爬取这个页面：https://example.com
等JS渲染完成后提取所有内容
保存成Markdown
```

### 2. 多Tab爬取
```
官家，请爬取MWC巴展议程：
- 页面有5个日期Tab（PRE、MON、TUE、WED、THU）
- 需要点击每个Tab获取数据
- 按日期分别保存
```

### 3. 懒加载内容
```
官家，请爬取这个页面：
- 需要滚动到底部才能加载完整内容
- 等待所有内容加载完成
- 提取所有session数据
```

---

## 技术实现

### Playwright核心API

#### 1. 启动浏览器
```javascript
const { chromium } = require('playwright');

const browser = await chromium.launch({
  headless: false, // 或true
  channel: 'chrome'
});

const context = await browser.newContext({
  viewport: { width: 1920, height: 1080 }
});

const page = await context.newPage();
```

#### 2. 导航和等待
```javascript
await page.goto(url, { waitUntil: 'networkidle' });
await page.waitForLoadState('domcontentloaded');
await page.waitForSelector('selector');
```

#### 3. DOM操作
```javascript
// 点击
await page.click('button');
await page.click('text=Monday');

// 滚动
await page.evaluate(() => {
  window.scrollTo(0, document.body.scrollHeight);
});

// 等待
await page.waitForTimeout(2000);
```

#### 4. 数据提取
```javascript
const data = await page.evaluate(() => {
  const items = Array.from(document.querySelectorAll('.item'));
  return items.map(item => ({
    title: item.querySelector('.title').textContent,
    time: item.querySelector('.time').textContent,
    location: item.querySelector('.location').textContent
  }));
});
```

#### 5. 持久化Profile
```javascript
const context = await chromium.launchPersistentContext(
  './user-data',
  { headless: false, channel: 'chrome' }
);
```

---

## 实战案例

### 案例1：MWC巴展议程爬取

**需求**：
- 5个日期Tab（PRE、MON、TUE、WED、THU）
- 每个Tab有懒加载
- 数据通过JS异步请求

**实现步骤**：
```javascript
// 1. 导航到页面
await page.goto('https://mwcbarcelona.com/agenda');

// 2. 等待页面加载
await page.waitForLoadState('networkidle');

// 3. 循环处理每个Tab
const tabs = ['PRE', 'MON', 'TUE', 'WED', 'THU'];
for (const tab of tabs) {
  // 点击Tab
  await page.click(`text=${tab}`);
  
  // 等待内容加载
  await page.waitForTimeout(2000);
  
  // 滚动到底部（触发懒加载）
  await page.evaluate(() => {
    window.scrollTo(0, document.body.scrollHeight);
  });
  
  // 等待懒加载完成
  await page.waitForTimeout(3000);
  
  // 提取数据
  const sessions = await page.evaluate(() => {
    const items = Array.from(document.querySelectorAll('.session'));
    return items.map(item => ({
      title: item.querySelector('.title').textContent,
      time: item.querySelector('.time').textContent,
      location: item.querySelector('.location').textContent,
      speakers: item.querySelector('.speakers').textContent
    }));
  });
  
  // 保存到文件
  const markdown = sessions.map(s => 
    `## ${s.title}\n- 时间: ${s.time}\n- 地点: ${s.location}\n- 演讲者: ${s.speakers}\n`
  ).join('\n');
  
  fs.writeFileSync(`mwc-${tab}.md`, markdown);
}
```

**关键点**：
- ✅ 等待网络空闲（networkidle）
- ✅ 点击后等待内容加载
- ✅ 滚动触发懒加载
- ✅ 等待懒加载完成
- ✅ 数据结构化提取

---

## 最佳实践

### 1. 等待策略
```javascript
// ❌ 不推荐：固定等待
await page.waitForTimeout(5000);

// ✅ 推荐：智能等待
await page.waitForLoadState('networkidle');
await page.waitForSelector('.item', { state: 'visible' });
await page.waitForFunction(() => {
  return document.querySelectorAll('.item').length > 10;
});
```

### 2. 错误处理
```javascript
try {
  await page.click('button');
  await page.waitForSelector('.result', { timeout: 10000 });
} catch (error) {
  console.error('操作失败:', error.message);
  // 截图调试
  await page.screenshot({ path: 'error.png' });
}
```

### 3. 性能优化
```javascript
// 阻止不必要的资源加载
await page.route('**/*.{png,jpg,jpeg,gif,svg}', route => route.abort());
await page.route('**/*.css', route => route.abort());
```

### 4. 反爬应对
```javascript
// 设置用户代理
await page.setExtraHTTPHeaders({
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)...'
});

// 禁用webdriver标识
await page.evaluateOnNewDocument(() => {
  Object.defineProperty(navigator, 'webdriver', {
    get: () => false,
  });
});
```

---

## 调试技巧

### 1. 截图
```javascript
await page.screenshot({ path: 'debug.png', fullPage: true });
```

### 2. 打印HTML
```javascript
const html = await page.content();
console.log(html);
```

### 3. 打印特定元素
```javascript
const element = await page.$('.item');
const html = await element.innerHTML();
console.log(html);
```

### 4. 控制台日志
```javascript
page.on('console', msg => {
  console.log('PAGE LOG:', msg.text());
});
```

---

## 注意事项

### 安全提示
- ⚠️ 仅爬取公开信息
- ⚠️ 遵守robots.txt
- ⚠️ 不要过度请求，避免给服务器造成压力
- ⚠️ 敏感数据不要保存

### 法律风险
- ⚠️ 确保爬取行为合法
- ⚠️ 不要爬取版权内容
- ⚠️ 不要绕过付费墙
- ⚠️ 不要爬取个人隐私数据

### 技术限制
- ⚠️ 反爬机制强的网站可能失败
- ⚠️ 需要复杂验证的平台不适用
- ⚠️ 页面结构变化需重新调试

---

## 安装依赖

```bash
npm install playwright
npx playwright install chromium
```

---

## 参考资料

- [Playwright官方文档](https://playwright.dev/)
- [OpenClaw + Playwright文章](https://example.com)
- [MWC议程爬取案例](./examples/mwc-agenda.js)

---

**创建时间**: 2026-02-27
**版本**: 1.0.0
**维护者**: 米粒儿（AI Agent）
