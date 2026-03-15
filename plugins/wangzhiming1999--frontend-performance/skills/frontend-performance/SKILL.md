---
name: frontend-performance
description: "Analyzes and improves frontend performance: LCP, FCP, CLS, bundle size, lazy loading, and runtime efficiency. Use when 性能优化, 首屏慢, 卡顿, 打包体积, performance optimization, or improving Core Web Vitals."
---

# 前端性能优化（Frontend Performance）

围绕加载性能与运行性能，给出可落地的优化方案与优先级。

## 触发场景

- 用户说「性能优化」「首屏慢」「页面卡顿」「打包体积大」「LCP/FCP 差」
- 提供 Lighthouse 报告、Performance 录屏或具体慢的页面/操作

## 分析维度

### 1. 加载性能（LCP / FCP / TTI）

| 问题 | 常见原因 | 优化方向 |
|------|----------|----------|
| LCP 慢 | 大图、阻塞渲染、服务端慢 | 图片优化、优先关键资源、SSR/预取 |
| FCP 慢 | JS/CSS 阻塞、首屏依赖多 | 拆包、关键 CSS 内联、延迟非关键 |
| TTI 长 | 主线程长任务、大 bundle | 代码分割、懒加载、减少主线程工作 |

### 2. 体验稳定性（CLS / 卡顿）

| 问题 | 常见原因 | 优化方向 |
|------|----------|----------|
| CLS 高 | 无尺寸图片/字体、动态插入内容 | 宽高比/尺寸、font-display、预留占位 |
| 滚动/操作卡顿 | 重排多、长任务、大列表 | 虚拟列表、防抖节流、requestAnimationFrame、减少 reflow |

### 3. 资源与打包

| 问题 | 优化方向 |
|------|----------|
| JS 体积大 | 按路由/按需拆包、tree-shaking、替换大依赖、分析 bundle |
| 图片大 | 格式（WebP/AVIF）、尺寸、懒加载、CDN |
| 请求多 | 合并、缓存策略、预连接/preload |

## 执行流程

### 1. 现状量化

- 若有 Lighthouse：记录 LCP/FCP/CLS/TTI 与 Speed Index
- 若有具体慢的操作：描述操作 + 主观耗时或 Performance 时长
- 若有 bundle 诉求：给出当前主要 chunk 体积

### 2. 找瓶颈

- 加载：Network 看瀑布图、哪些请求阻塞或过大
- 运行时：Performance 录屏看长任务、布局/样式计算
- 打包：用分析工具（如 `@next/bundle-analyzer`）看大模块

### 3. 列方案并标性价比

每个方案注明：
- **收益**：预期提升的指标或体感
- **成本**：改动量、风险、依赖
- **优先级**：高/中/低（高收益低成本优先）

### 4. 给出落地顺序

- 先做「快速见效」：如图片尺寸、font-display、关键 CSS、首屏懒加载
- 再做「中等改动」：路由级拆包、虚拟列表、缓存策略
- 最后考虑「大改动」：架构调整、SSR、边缘渲染等

## 输出模板

```markdown
## 性能优化报告

### 现状
- 指标或现象：…
- 主要瓶颈：…

### 优化方案（按优先级）
| 方案 | 收益 | 成本 | 优先级 |
|------|------|------|--------|
| 1. … | … | … | 高/中/低 |
| 2. … | … | … | … |

### 建议落地顺序
1. …
2. …

### 验证方式
- 优化后建议复测：Lighthouse、Performance、关键操作耗时
```

## 项目相关

- Next.js：用 `dynamic` 懒加载、Image 组件、分析 `next/bundle-analyzer`
- React：避免在渲染里创建新对象/函数导致子组件无效重渲染，必要时 memo/useMemo/useCallback
- 长列表：优先虚拟滚动（如 react-window、tanstack-virtual）再考虑分页
