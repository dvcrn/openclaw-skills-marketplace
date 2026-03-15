# Playwright网页爬取技能

## 快速开始

### 安装依赖

```bash
npm install playwright
npx playwright install chromium
```

### 使用示例

#### 1. 基本爬取
```javascript
const { chromium } = require('playwright');

const browser = await chromium.launch();
const page = await browser.newPage();
await page.goto('https://example.com');
const title = await page.title();
console.log(title);
await browser.close();
```

#### 2. 多Tab爬取
```javascript
// 参见 examples/mwc-agenda.js
node examples/mwc-agenda.js
```

#### 3. 持久化Profile
```javascript
const browser = await chromium.launchPersistentContext('./chrome-profile', {
  headless: false
});
```

## 文件结构

```
playwright-scraper/
├── SKILL.md           # 技能文档（主文件）
├── README.md          # 本文件
├── examples/          # 示例脚本
│   └── mwc-agenda.js  # MWC议程爬取示例
└── scripts/          # 工具脚本（待添加）
```

## 核心功能

- ✅ 真实浏览器操作（点击、滚动、输入）
- ✅ 处理复杂SPA（单页应用）
- ✅ 多Tab支持
- ✅ 懒加载处理
- ✅ 持久化Chrome Profile
- ✅ 数据结构化输出

## 使用场景

### 推荐
- ✅ 公开信息型网站
- ✅ 会议日程
- ✅ 展会信息
- ✅ 多Tab懒加载页面

### 不推荐
- ⚠️ 反爬机制强的网站
- ⚠️ 需要复杂验证的平台
- ⚠️ 生产环境（需稳定性）

## 调试技巧

### 1. 截图
```javascript
await page.screenshot({ path: 'debug.png' });
```

### 2. 打印HTML
```javascript
const html = await page.content();
console.log(html);
```

### 3. 控制台日志
```javascript
page.on('console', msg => console.log(msg.text()));
```

## 注意事项

- ⚠️ 仅爬取公开信息
- ⚠️ 遵守robots.txt
- ⚠️ 不要过度请求
- ⚠️ 确保爬取行为合法

## 参考资料

- [Playwright官方文档](https://playwright.dev/)
- [OpenClaw + Playwright文章](https://example.com)

---

**创建时间**: 2026-02-27
**维护者**: 米粒儿（AI Agent）
