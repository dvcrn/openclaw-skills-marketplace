# 📸 SnapDesign RedNote - 小红书卡片生成器

> 一键将长文本转换成精美的小红书风格卡片，900×1198px 高清分辨率，咖色系设计，支持 AI 智能排版

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 📸 示例效果

<div align="center">
  <img src="assets/example-1.png" width="280" alt="示例1"/>
  <img src="assets/example-2.png" width="280" alt="示例2"/>
  <img src="assets/example-3.png" width="280" alt="示例3"/>
</div>

## ✨ 特点

- 🎨 **小红书风格**: 咖色系 + 纸质感，完美适配小红书审美
- 📐 **完美比例**: 3:4 (1080x1440px) 无需裁剪直接发布
- 🤖 **智能分块**: 自动识别段落、列表，合理分页
- 🎭 **精美排版**: 标题、正文、装饰元素协调统一
- ⚡ **一键生成**: 几秒钟生成多张卡片

## 🚀 快速开始

### 安装依赖

```bash
cd snapdesign-rednote
npm install
```

### 基础使用

```bash
# 简单文本
node scripts/generate.js "你的内容"

# 带标题
node scripts/generate.js "你的内容" --title "主题标题"

# 多段文本（自动分页）
node scripts/generate.js "如何学习编程？
第一步：打好基础
第二步：多写代码
第三步：参与开源" --title "学习指南"
```

## 📊 使用示例

### 示例1: 知识总结

```bash
node scripts/generate.js "Python学习笔记
第一步：掌握基础语法，变量、函数、类
第二步：学习标准库，os、sys、json
第三步：实战项目，爬虫、数据分析
第四步：深入框架，Django、Flask
第五步：持续学习，关注新特性" --title "Python学习路线"
```

**输出**: 6张卡片，第一张是标题页，后面5张每张一个要点

### 示例2: 生活分享

```bash
node scripts/generate.js "今天的早餐太好吃了！
燕麦牛奶，营养健康
全麦面包，饱腹感强
水果沙拉，维生素满满
黑咖啡，提神醒脑" --title "元气早餐"
```

### 示例3: 工作总结

```bash
node scripts/generate.js "本周工作总结：
完成了3个需求开发
修复了5个bug
写了2篇技术文档
参加了团队分享会" --title "周报" --output ./weekly-report
```

## ⚙️ 高级选项

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `--title` | 卡片标题（显示在第一张） | 无 | `--title "我的主题"` |
| `--output` | 输出目录 | `./output` | `--output ./my-cards` |
| `--single` | 不分块，生成单张卡片 | false | `--single` |

## 🎨 设计规范

### 配色方案

- **主色**: `#8B7355` (咖啡棕) - 标题、强调
- **背景**: `#FFF8F0` (纸质米白) - 温暖舒适
- **强调**: `#D4A574` (浅咖) - 装饰元素
- **文字**: `#4A3F35` (深咖) - 正文内容

### 尺寸规格

- **卡片尺寸**: 1080 x 1440 px (3:4)
- **DPI**: 2x (高清)
- **格式**: PNG
- **文件大小**: 约 90-100KB/张

## 💡 最佳实践

### 文本长度建议

- **标题**: 6-12个字最佳
- **每个要点**: 20-60个字
- **卡片数量**: 3-9张为宜

### 内容结构

✅ **推荐**:
```
主题/引言
第一点
第二点
第三点
总结
```

✅ **推荐**:
```
如何XXX？
• 方法一
• 方法二
• 方法三
```

❌ **不推荐**:
- 单个段落超长（>200字）
- 没有分段的大段文字
- 过于复杂的列表嵌套

## 📱 发布到小红书

1. **打开小红书APP** → 点击发布
2. **选择图片** → 选中生成的所有卡片
3. **调整顺序** → 确保第一张是标题页
4. **添加文案** → 简短介绍 + hashtag
5. **发布** → 完成！

### 推荐Hashtag

```
#干货分享 #知识笔记 #学习打卡 
#实用技巧 #生活指南 #成长笔记
```

## 🔧 开发相关

### 项目结构

```
snapdesign-rednote/
├── scripts/
│   └── generate.js      # 主生成脚本
├── output/              # 默认输出目录
├── package.json
├── SKILL.md            # OpenClaw Skill 定义
└── README.md
```

### 技术栈

- **Node.js** - 运行环境
- **Puppeteer** - 浏览器自动化
- **HTML/CSS** - 卡片渲染

### 自定义修改

如需调整配色、字体、布局，编辑 `scripts/generate.js`:

```javascript
// 修改配色
const COLORS = {
  primary: '#8B7355',      // 主色
  background: '#FFF8F0',   // 背景
  accent: '#D4A574',       // 强调色
  text: '#4A3F35'          // 文字
};
```

## 📦 发布到ClawHub

```bash
# 登录ClawHub
clawhub login

# 发布Skill
clawhub publish . --slug snapdesign-rednote --name "SnapDesign RedNote" --version 1.0.0
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 License

MIT © 宝强

---

**Made with ❤️ by 宝强 | Powered by OpenClaw**
