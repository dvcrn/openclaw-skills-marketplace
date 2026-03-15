---
name: xiaohongshu-generator
description: "Generate stunning Xiaohongshu (RedNote) infographic images from Markdown. 7.2K Stars! Beautiful templates for social media. Each call charges 0.001 USDT."
homepage: https://github.com/jimliu/baoyu-skills
---

# Xiaohongshu Image Generator

## 功能

Generate beautiful Xiaohongshu (RedNote) infographic images. **7.2K Stars on GitHub!** The #1 tool for Chinese social media visuals.

### 风格 (9 styles)

| 风格 | 描述 |
|------|------|
| cute | 可爱甜美 |
| fresh | 小清新 |
| warm | 温暖治愈 |
| bold | 大胆醒目 |
| minimal | 简约现代 |
| retro | 复古怀旧 |
| pop | 波普艺术 |
| notion | 笔记风 |
| chalkboard | 黑板风 |

### 布局 (6 layouts)

| 布局 | 适用场景 |
|------|----------|
| sparse (稀疏) | 1-2点, 封面/引用 |
| balanced (均衡) | 3-4点, 常规内容 |
| dense (密集) | 5-8点, 知识卡片 |
| list (列表) | 4-7点, 清单/排行 |
| comparison (对比) | 2边, 前后/优缺点 |
| flow (流程) | 3-6步, 过程/时间线 |

## 使用方法

```json
{
  "action": "generate",
  "content": "# 今日分享\n\n- 第一点\n- 第二点\n- 第三点",
  "style": "cute",
  "layout": "balanced"
}
```

## 安装

```bash
npm install -g baoyu
```

## 使用

```bash
/baoyu-xhs-images content.md --style cute --layout balanced
```

## 价格

每次调用: **0.001 USDT**

## Stars

**7.2K Stars** ⭐⭐⭐⭐⭐ on GitHub!

## Use Cases

- **小红书笔记配图**: 一键生成精美笔记封面
- **朋友圈海报**: 生日、节日祝福海报
- **知识卡片**: 学习笔记、知识整理
- **产品介绍**: 电商主图、详情页
- **旅行分享**: 旅行攻略、日记配图
- **美食打卡**: 餐厅推荐、菜谱分享
