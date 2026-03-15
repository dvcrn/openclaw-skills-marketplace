# Design Inspiration Collection Skills - ClawHub Package

> 打包时间：2026年03月11日 21:30  
> 版本：1.0.0

---

## 📦 包含内容

此包包含以下技能，可直接上传到 ClawHub：

### 1. design-inspiration-collector (推荐)
**完整的多平台设计灵感收集技能**

- **功能**：搜索 Pinterest、Dribbble、Behance 三个平台
- **输出**：生成飞书文档（命名格式：关键词+日期时间）
- **触发词**：找灵感、收集灵感、设计参考、UI参考、视觉灵感

#### 特点：
- ✅ 三平台同时搜索
- ✅ 自动生成飞书文档
- ✅ 相关度星级评分
- ✅ 相关方向推荐
- ✅ 趋势分析摘要

#### 依赖：
```bash
pip install tavily-python playwright
playwright install chromium
export TAVILY_API_KEY="your-api-key"
```

---

### 2. pinterest-inspiration-collector (旧版)
**仅搜索 Pinterest 的简化版**

- **功能**：仅搜索 Pinterest 平台
- **输出**：Markdown 报告
- **状态**：建议使用 design-inspiration-collector 替代

---

## 🚀 快速开始

### 安装到 OpenClaw

```bash
# 方式1：使用 .skill 文件
clawhub install design-inspiration-collector.skill

# 方式2：复制文件夹
cp -r design-inspiration-collector ~/.openclaw/workspace/skills/
```

### 使用方法

在聊天中输入：
- "帮我收集医疗App的设计灵感"
- "搜索上传文件的UI参考"
- "找一些AI界面的视觉灵感"

---

## 📁 文件结构

```
clawhub_packages/
├── README.md                          # 本文件
├── design-inspiration-collector/      # 主技能
│   ├── SKILL.md                       # 技能定义
│   └── scripts/
│       └── design_collector.py        # 主脚本
└── pinterest-inspiration-collector/   # 旧版技能
    ├── SKILL.md
    └── scripts/
        └── search_pinterest.py
```

---

## 🎯 上传 ClawHub 指南

1. 访问 https://clawhub.com
2. 点击「发布技能」
3. 选择 `design-inspiration-collector` 文件夹
4. 填写信息：
   - **名称**：design-inspiration-collector
   - **版本**：1.0.0
   - **标签**：design, inspiration, pinterest, dribbble, behance, ui
   - **描述**：多平台设计灵感收集技能，支持 Pinterest、Dribbble、Behance

---

## 📚 使用示例

### 示例 1：医疗App设计
```
用户：帮我收集医疗App的设计灵感

助手：
✅ 飞书文档已创建！

**文档名称**：医疗App设计灵感_20260311_170245
**文档链接**：https://feishu.cn/docx/xxx

共收集 15 条设计灵感

📌 相关方向推荐：
1. AI问诊助手 - 智能问诊、症状分析
2. 健康追踪 - 运动记录、睡眠监测
3. 远程医疗 - 视频问诊、处方管理
```

### 示例 2：上传文件UI
```
用户：帮我搜索上传文件的设计样式

助手：
✅ 飞书文档已创建！

**文档名称**：上传文件设计样式_20260311_2042
**文档链接**：https://feishu.cn/docx/xxx

📊 趋势概览：
- 简洁直观的按钮设计
- 拖拽上传功能
- 进度指示器
- 用户友好的反馈
```

---

## 🔧 技术说明

### Tavily API
用于搜索三个设计平台的内容。需要 API Key：
- 免费额度：每月 1000 次搜索
- 注册：https://tavily.com

### Feishu API
用于创建飞书文档。需要配置飞书应用权限。

### Playwright (可选)
用于截图功能。由于反爬虫限制，截图可能失败，但不影响核心功能。

---

## 📝 更新日志

### v1.0.0 (2026-03-11)
- ✅ 初始版本
- ✅ 支持三平台搜索
- ✅ 飞书文档自动生成
- ✅ 相关方向推荐

---

## 🤝 贡献

欢迎提交 PR 改进此技能！

---

*Made with ❤️ by AI Assistant*