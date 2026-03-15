---
name: cn-web-search
description: "中文网页搜索 - 聚合 13+ 免费搜索引擎，包含公众号文章搜索"
---

# 中文网页搜索 (CN Web Search)

多引擎聚合搜索，**全部免费，无需 API Key**。

## 引擎总览

| 类别 | 引擎 | 说明 |
|------|------|------|
| 公众号 | 搜狗微信、必应索引 | ⭐ |
| 中文 | 360、搜狗、必应 | 主+备用 |
| 英文 | DDG、Qwant、Startpage、必应 | 主+备用 |
| 技术 | Stack Overflow、GitHub Trending | ⭐ |
| 专用 | Hacker News、Reddit、ArXiv | API |
| 投资 | 东方财富 | A股 |
| 深度 | 财新 | 财经 |
| 知识 | Wolfram Alpha | 计算 |

---

## 1. 公众号搜索

### 1.1 搜狗微信

```
https://weixin.sogou.com/weixin?type=2&query=QUERY&page=1
```

### 1.2 必应公众号索引

```
https://cn.bing.com/search?q=site:mp.weixin.qq.com+QUERY
```

---

## 2. 中文搜索

### 2.1 360 搜索

```
https://m.so.com/s?q=QUERY
```

### 2.2 搜狗网页

```
https://www.sogou.com/web?query=QUERY
```

### 2.3 必应中文

```
https://cn.bing.com/search?q=QUERY
```

---

## 3. 英文搜索

### 3.1 DuckDuckGo Lite

```
https://lite.duckduckgo.com/lite/?q=QUERY
```

### 3.2 Qwant

```
https://www.qwant.com/?q=QUERY&t=web
```

### 3.3 Startpage

```
https://www.startpage.com/do/search?q=QUERY&cluster=web
```

### 3.4 必应英文

```
https://www.bing.com/search?q=QUERY
```

---

## 4. 技术/社区/学术

### 4.1 Hacker News

```
https://hn.algolia.com/api/v1/search?query=QUERY&tags=story&hitsPerPage=10
```

### 4.2 Reddit

```
https://www.reddit.com/search.json?q=QUERY&limit=10
```

### 4.3 ArXiv

```
http://export.arxiv.org/api/query?search_query=all:QUERY&max_results=5
```

### 4.4 Stack Overflow

```
https://stackoverflow.com/search?q=QUERY
```

### 4.5 GitHub Trending

```
https://github.com/trending?since=weekly
```

---

## 5. 其他专用

### 5.1 东方财富

```
https://search.eastmoney.com/search?keyword=QUERY
```

### 5.2 财新

```
https://search.caixin.com/search/?keyword=QUERY
```

### 5.3 Wolfram Alpha

```
https://www.wolframalpha.com/input?i=QUERY
```

---

## 使用示例

```
web_fetch(url="https://m.so.com/s?q=英伟达财报", extractMode="text", maxChars=12000)
web_fetch(url="https://lite.duckduckgo.com/lite/?q=AI+news", extractMode="text", maxChars=8000)
web_fetch(url="https://weixin.sogou.com/weixin?type=2&query=英伟达&page=1", extractMode="text", maxChars=10000)
```

---

## 更新日志

### v0.9.0
- ✅ 移除付费引擎，全部免费

### v0.8.0
- ❌（已跳过）

### v0.7.0
- ✅ 公众号搜索

### v0.6.0
- ✅ 财新 + Wolfram Alpha
