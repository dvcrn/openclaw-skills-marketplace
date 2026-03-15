---
name: youtube-title-optimizer
description: "Youtube Title Optimizer"
---

# YouTube 标题优化 - 视频标题优化器

## 概述
基于 YouTube 算法和 SEO 最佳实践，生成高点击率、高搜索排名的视频标题。兼顾搜索流量和推荐流量。

## 定价
- **按次收费：** ¥5/次
- **包月订阅：** ¥99/月（无限次）

## 功能特性
- 🔍 SEO 关键词优化
- 📊 CTR 预测评分
- 🎯 A/B 测试标题变体
- 📈 竞争对手分析
- 🏷️ 标签和描述建议

## 使用方式
```bash
# 基础使用
/youtube-title "视频内容描述"

# 指定关键词
/youtube-title "Python 教程" --keywords "python,编程，入门"

# 竞品分析
/youtube-title "健身教程" --analyze @competitor

# 批量生成
/youtube-title "美食教程" --count 5
```

## 输出格式
```markdown
## 🎬 YouTube 标题优化方案

### 🏆 推荐标题（CTR 预测：8.5%）
"Python 入门教程 2026｜从零到能写项目（附源码）"

### 📋 备选标题
1. "学会 Python 只要 7 天？这个教程太狠了"
2. "Python 新手必看！避开这 5 个坑"
3. "我靠 Python 副业月入 3 万，教程来了"

### 🔍 SEO 关键词
- 主关键词：Python 教程 (搜索量：50K/月)
- 长尾词：Python 入门 2026, Python 项目实战

### 🏷️ 标签建议
#Python #编程 #教程 #程序员 #副业

### 📝 描述模板
[前 2 行包含核心关键词]
[时间戳目录]
[相关链接和资源]
```

## 技术实现
- YouTube Data API 集成
- 关键词搜索量分析
- CTR 预测模型
- 竞品标题分析

## 相关文件
- `index.js` - 主逻辑实现
- `README.md` - 详细文档
