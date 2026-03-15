---
name: novel-to-drama-script
description: "AI智能将小说/故事创意转化为短剧剧本。自动生成角色、分镜、对白、场景描述。基于Toonflow核心功能(3.8K Stars)。每次调用收取0.001 USDT。"
homepage: https://github.com/HBAI-Ltd/Toonflow-app
---

# AI Short Drama Script Generator (小说转剧本)

## 功能

AI智能将小说/故事创意转化为专业短剧剧本。基于**Toonflow AI短剧引擎 (3.8K Stars)** 核心功能开发。

### 核心能力

- **智能角色生成**: 分析故事设定,自动创建角色表(外貌/性格/身份)
- **结构化剧本**: 输出标准剧本格式(场景/对白/动作/音效)
- **分镜支持**: 生成每个镜头的画面描述和镜头建议
- **多风格**: 支持dramatic/comedy/romance/thriller等多种风格

## 使用方法

```json
{
  "title": "重生千金",
  "synopsis": "富家千金重生回到过去,弥补前世遗憾,揭露继母阴谋",
  "characters": "女主:聪明坚韧 重生者; 继母:阴险毒辣",
  "episodeCount": 1,
  "style": "dramatic"
}
```

## 输出示例

```json
{
  "success": true,
  "script": {
    "title": "重生千金",
    "genre": "dramatic",
    "scenes": [
      {
        "scene": 1,
        "location": "客厅-夜",
        "description": "奢华的客厅,水晶吊灯散发柔和光芒",
        "actions": [
          {"character": "女主", "action": "缓缓睁开眼睛", "dialogue": "这是...重生?"},
          {"character": "继母", "action": "端着红酒杯走近", "dialogue": "醒了?正好..."
        ]
      }
    ]
  },
  "characters": [
    {"name": "女主", "age": 25, "personality": "聪明坚韧", "appearance": "气质出众"},
    {"name": "继母", "age": 40, "personality": "阴险毒辣", "appearance": "妆容精致"}
  ]
}
```

## 价格

**每次调用: 0.001 USDT**

## 场景示例

### 1. 重生复仇类
```json
{
  "title": "重生复仇",
  "synopsis": "都市白领重生回到大学时代,阻止悲剧发生",
  "style": "dramatic"
}
```

### 2. 甜宠恋爱类
```json
{
  "title": "总裁的替身新娘",
  "synopsis": "灰姑娘意外嫁入豪门,先婚后爱的故事",
  "style": "romance"
}
```

### 3. 悬疑推理类
```json
{
  "title": "消失的凶手",
  "synopsis": "刑侦专家穿越到案发现场,追查真凶",
  "style": "thriller"
}
```

## Use Cases

- **短视频创作**: 快速生成短剧脚本,用于抖音/快手
- **小说作者**: 将小说片段改编为剧本形式
- **内容创业**: 批量生成剧本,提高创作效率
- **学习编剧**: 参考AI生成的剧本结构学习写作

## 相关项目

- [Toonflow-app](https://github.com/HBAI-Ltd/Toonflow-app) - AI短剧漫剧工具 (3.8K Stars)
- [Toonflow-web](https://github.com/HBAI-Ltd/Toonflow-web) - 前端界面
