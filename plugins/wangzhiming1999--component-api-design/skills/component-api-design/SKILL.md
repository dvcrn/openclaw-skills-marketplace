---
name: component-api-design
description: "Designs reusable React/Vue component APIs and file structure for clarity, flexibility, and maintainability. Use when 设计组件, 组件API, 封装组件, component design, or defining props/slots/events."
---

# 组件与 API 设计（Component & API Design）

设计易用、可扩展、易维护的组件 API 与文件结构，提升后续开发效率。

## 触发场景

- 用户说「设计这个组件」「组件怎么封装」「API 怎么定」「props 怎么设计」
- 要新建通用组件、业务组件或对现有组件做 API 升级

## 设计维度

### 1. 职责单一

- 一个组件只做一类事（展示 / 表单 / 布局 / 反馈）
- 若同时管「数据获取 + 展示 + 复杂交互」，考虑拆成容器 + 展示组件或拆子组件

### 2. Props 设计

| 原则 | 说明 |
|------|------|
| 必要才加 | 能由 children/组合表达的不要变成 prop |
| 命名一致 | 用项目约定：value/onChange、open/onOpenChange、disabled 等 |
| 类型明确 | TypeScript 定义清晰，必填/可选、联合类型写清 |
| 可控与不可控 | 若支持受控，则 value + onChange 成对；可提供 defaultValue 做非受控 |
| 避免冗余 | 能从现有 props 推导的不再单独提供（如 loading 时 disabled 可内部处理） |

### 3. 扩展方式

- **children**：默认内容区；复杂布局用 **slots/render props**（如 header、footer、itemRenderer）
- **className / style**：允许外层控制布局和主题
- **透传**：表单类组件对 **aria-*、data-*、剩余 HTML 属性** 做透传，便于无障碍与测试
- **主题/变体**：用 variant/size 等枚举优于一堆布尔 prop（如 type="primary" size="md"）

### 4. 事件与回调

- 命名：on + 动词或 on + 名词 + 动词（onChange、onSubmit、onOpenChange）
- 参数：先传「与事件强相关的数据」，再传原生 event（若需要）
- 避免在回调里强塞过多业务逻辑，保持组件「中性」

### 5. 文件与目录

- 单组件可单文件；组件带样式、类型、子组件多时可用目录：
  - `ComponentName/index.tsx`（入口）
  - `ComponentName/ComponentName.tsx`（实现）
  - `ComponentName/types.ts`
  - `ComponentName/styles.module.scss`
  - `ComponentName/SubPart.tsx`（内部子组件）
- 类型、常量、工具函数可共用的放上层或 shared

## 输出模板

```markdown
## 组件设计：{组件名}

### 职责
- 一句话描述组件用途与使用场景

### API（Props）
| 属性 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| … | … | … | … | … |

### 事件/回调
| 事件 | 参数 | 说明 |
|------|------|------|
| … | … | … |

### 插槽/扩展
- default：…
- 其他具名插槽：…

### 使用示例
\`\`\`tsx
<ComponentName ... />
\`\`\`

### 文件结构
- 路径与主要文件说明
```

## 与项目一致

- 若项目用 Radix/shadcn：对齐其「组合 + 可控」风格与命名
- 若项目用 Tailwind：组件根节点支持 `className`，内部用 `cn()` 合并
- 表单组件与现有表单库（如 react-hook-form）的 value/onChange 约定保持一致
