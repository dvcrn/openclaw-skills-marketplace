---
name: jisu-hotsearch
description: "使用极速数据微博/百度/抖音热搜榜单 API 获取当前热搜榜单及排名、标题、链接、指数等信息。"
---

## 极速数据微博/百度/抖音热搜榜单（Jisu Hotsearch）

基于 [微博百度热搜榜单 API](https://www.jisuapi.com/api/hotsearch/) 的 OpenClaw 技能，支持：

- **微博热搜**（`/hotsearch/weibo`）
- **百度热搜**（`/hotsearch/baidu`）
- **抖音热搜**（`/hotsearch/douyin`）

返回每条热搜的排名、标题、链接、指数、更新时间，可用于回答「现在微博/百度/抖音上有什么热搜」「帮我列出当前前 10 条热搜标题和链接」等问题。

使用技能前需要申请数据，申请地址：https://www.jisuapi.com/api/hotsearch/

## 环境变量配置

```bash
# Linux / macOS
export JISU_API_KEY="your_appkey_here"

# Windows PowerShell
$env:JISU_API_KEY="your_appkey_here"
```

## 脚本路径

脚本文件：`skill/hotsearch/hotsearch.py`

## 使用方式

### 1. 微博热搜（/hotsearch/weibo）

```bash
python3 skill/hotsearch/hotsearch.py weibo
```

### 2. 百度热搜（/hotsearch/baidu）

```bash
python3 skill/hotsearch/hotsearch.py baidu
```

### 3. 抖音热搜（/hotsearch/douyin）

```bash
python3 skill/hotsearch/hotsearch.py douyin
```

无需额外 JSON 参数，脚本直接输出接口 `result` 数组。

## 返回结果示例（节选）

```json
[
  {
    "sequence": "1",
    "title": "部分男性对丁真的态度",
    "link": "https://s.weibo.com/weibo?q=...",
    "score": "4103153",
    "updatetime": "2020-12-09 16:59:46"
  }
]
```

常见字段说明：

| 字段名      | 类型     | 说明           |
|-------------|----------|----------------|
| sequence    | string/int | 排名          |
| title       | string   | 标题           |
| link / linkurl | string | 标题链接（字段名视接口而略有差异） |
| score       | string   | 热度/指数      |
| updatetime  | string   | 更新时间       |

## 常见错误码

业务错误码（参考官网错误码参照，常见含义为「没有信息」等）：  
接口可能返回 `status != 0`，此时脚本会包装为：

```json
{
  "error": "api_error",
  "code": 210,
  "message": "没有信息"
}
```

通用系统错误码与其它极速数据接口一致（101–108）。详见 [极速数据热搜文档](https://www.jisuapi.com/api/hotsearch/)。

## 在 OpenClaw 中的推荐用法

1. 用户提问：「现在微博/百度/抖音上有什么热搜？」  
2. 代理按平台调用对应命令，比如微博热搜：`python3 skill/hotsearch/hotsearch.py weibo`。  
3. 从返回数组中选取前 N 条（如前 10 条），读取 `title`、`link/linkurl`、`score`，用自然语言总结热点内容，并附上若干可点击的链接。  

