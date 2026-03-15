# Playwright网页爬取技能使用指南

## 在OpenClaw中使用

### 方式1: 自然语言描述
```
官家，请帮我爬取这个网站：https://example.com
它有多个Tab，需要点击切换
等JS加载完成后提取所有数据
保存成Markdown格式
```

### 方式2: 参考示例脚本
```
官家，请参考 examples/mwc-agenda.js
帮我创建一个类似的爬虫脚本
用于爬取 [目标网站]
```

### 方式3: 直接执行脚本
```bash
node skills/playwright-scraper/examples/mwc-agenda.js
```

---

## AI自动流程

1. **分析需求** - AI理解要爬取的目标和结构
2. **生成脚本** - AI实时编写Playwright代码
3. **执行爬取** - 运行脚本，处理动态内容
4. **提取数据** - 从渲染后的DOM提取信息
5. **结构化输出** - 整理成Markdown/JSON格式

---

## 常见场景模板

### 场景1: 多Tab懒加载
```javascript
// 点击每个Tab
for (const tab of tabs) {
  await tab.click();
  await page.waitForLoadState('networkidle');
  // 提取数据
}
```

### 场景2: 无限滚动
```javascript
// 滚动到底部
while (true) {
  await page.evaluate(() => window.scrollBy(0, 1000));
  await page.waitForTimeout(1000);
  // 检查是否到底
}
```

### 场景3: 登录后爬取
```javascript
// 使用持久化Profile
const browser = await chromium.launchPersistentContext('./profile', {
  headless: false
});
// 如果未登录，手动登录一次即可
```

---

## 注意事项

### 告诉AI的信息
- ✅ 目标网站URL
- ✅ 页面结构特点（Tab、懒加载等）
- ✅ 需要提取的数据字段
- ✅ 输出格式要求

### AI会自动处理
- ✅ 等待JS渲染
- ✅ 处理异步请求
- ✅ 点击、滚动操作
- ✅ 数据提取和整理

---

## 成功率提升技巧

### 1. 提供详细信息
```
官家，这个网站：
- URL: https://example.com
- 有3个Tab：产品、服务、关于
- 每个Tab有懒加载
- 需要提取：标题、描述、价格
```

### 2. 先测试简单页面
```
官家，先帮我测试爬取这个简单页面
成功后再处理复杂的
```

### 3. 允许AI调试
```
官家，如果失败请截图
并打印页面HTML
帮我分析原因
```

---

**创建时间**: 2026-02-27
**维护者**: 米粒儿（AI Agent）
