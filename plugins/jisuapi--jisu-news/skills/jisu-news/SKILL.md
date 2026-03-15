---
name: jisu-news
description: "使用极速数据新闻 API 按频道获取头条、财经、体育、娱乐等热门新闻列表，并支持查询可用频道列表。"
---

# 极速数据新闻（Jisu News）

基于 [新闻 API](https://www.jisuapi.com/api/news/) 的 OpenClaw 技能，支持：

- **获取新闻**（`/news/get`）
- **获取新闻频道**（`/news/channel`）

支持频道包括：头条、新闻、财经、体育、娱乐、军事、教育、科技、NBA、股票、星座、女性、健康、育儿等。

使用技能前需要申请数据，申请地址：https://www.jisuapi.com/api/news/

> 注意：此接口返回的数据来自互联网，涉及版权请向发布方获取授权。

## 环境变量配置

```bash
# Linux / macOS
export JISU_API_KEY="your_appkey_here"

# Windows PowerShell
$env:JISU_API_KEY="your_appkey_here"
```

## 脚本路径

脚本文件：`skills/news/news.py`

## 使用方式

### 1. 获取新闻频道列表（/news/channel）

```bash
python3 skills/news/news.py channels
```

返回示例：

```json
[
  "头条",
  "新闻",
  "财经",
  "体育",
  "娱乐"
]
```

### 2. 获取指定频道新闻（/news/get）

```bash
python3 skills/news/news.py '{"channel":"头条","num":10,"start":0}'
```

请求 JSON 示例：

```json
{
  "channel": "头条",
  "num": 10,
  "start": 0
}
```

## 请求参数

### 获取新闻

| 字段名   | 类型   | 必填 | 说明                                     |
|----------|--------|------|------------------------------------------|
| channel  | string | 是   | 新闻频道（如 头条、财经、体育、娱乐 等） |
| num      | int    | 否   | 数量，默认 10，最大 40                   |
| start    | int    | 否   | 起始位置，默认 0，最大 400（类似 offset） |

### 获取频道

无需额外参数，仅需 `appkey`。

## 返回结果示例

### 获取新闻

```json
{
  "channel": "头条",
  "num": "10",
  "list": [
    {
      "title": "中国开闸放水27天解救越南旱灾",
      "time": "2016-03-16 07:23",
      "src": "中国网",
      "category": "mil",
      "pic": "http://api.jisuapi.com/news/upload/20160316/105123_31442.jpg",
      "content": "……",
      "url": "http://mil.sina.cn/zgjq/2016-03-16/detail-ifxqhmve9235380.d.html?vt=4&pos=108",
      "weburl": "http://mil.news.sina.com.cn/china/2016-03-16/doc-ifxqhmve9235380.shtml"
    }
  ]
}
```

## 常见错误码

来源于 [极速数据新闻文档](https://www.jisuapi.com/api/news/)：

| 代号 | 说明         |
|------|--------------|
| 201  | 新闻频道不存在 |
| 202  | 关键词为空    |
| 205  | 没有信息      |

系统错误码：

| 代号 | 说明                 |
|------|----------------------|
| 101  | APPKEY 为空或不存在  |
| 102  | APPKEY 已过期        |
| 103  | APPKEY 无请求权限    |
| 104  | 请求超过次数限制     |
| 105  | IP 被禁止            |

## 在 OpenClaw 中的推荐用法

1. 用户提问：「帮我看下今天有什么科技新闻？」  
2. 代理先调用：`python3 skills/news/news.py channels` 确认是否有“科技”频道；  
3. 然后构造 JSON：`{"channel":"科技","num":10,"start":0}` 并调用：  
   `python3 skills/news/news.py '{"channel":"科技","num":10,"start":0}'`  
4. 从返回列表中选取最新或最相关的几条，提取 `title/time/src/weburl` 等字段，给用户做简要摘要与链接引用，用于内部分析或进一步处理。  

