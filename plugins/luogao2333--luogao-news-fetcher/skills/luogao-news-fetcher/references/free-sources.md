# 免费新闻源与 RSS

## 推荐免费信源

### 国际通讯社（完全免费）

| 媒体 | 网址 | RSS | 特点 |
|------|------|-----|------|
| BBC News | bbc.com | ✅ | 国际新闻最全面 |
| Reuters | reuters.com | ✅ | 财经+国际 |
| AP News | apnews.com | ✅ | 美联社 |
| AFP | afp.com | ✅ | 法新社 |
| Al Jazeera | aljazeera.com | ✅ | 中东专家 |
| Deutsche Welle | dw.com | ✅ | 德国视角 |

### 美国媒体（部分免费）

| 媒体 | 免费程度 | RSS | 备注 |
|------|---------|-----|------|
| NPR | 免费 | ✅ | 广播新闻 |
| ProPublica | 免费 | ✅ | 调查报道 |
| PBS NewsHour | 免费 | ✅ | 深度报道 |
| CNN | 部分免费 | ✅ | 有限制 |
| Vox | 部分免费 | ✅ | 解释性新闻 |

### 财经媒体

| 媒体 | 免费程度 | RSS | 备注 |
|------|---------|-----|------|
| Yahoo Finance | 免费 | ✅ | 综合财经 |
| MarketWatch | 部分 | ✅ | 道琼斯旗下 |
| CoinDesk | 免费 | ✅ | 加密货币 |
| TechCrunch | 部分 | ✅ | 科技 |

---

## RSS 订阅

### 什么是 RSS

RSS (Really Simple Syndication) 是一种订阅格式，可以在不访问网站的情况下获取最新内容。

### RSS 阅读器

**推荐工具:**
- Feedly (feedly.com) - 在线 + App
- Inoreader (inoreader.com) - 功能强大
- NetNewsWire (Mac/iOS) - 原生体验
- FreshRSS (freshrss.org) - 自托管

### 常用 RSS 源

```
# 国际新闻
https://feeds.bbci.co.uk/news/rss.xml
https://www.reuters.com/rssFeed/worldNews
https://rss.nytimes.com/services/xml/rss/nyt/World.xml

# 财经
https://feeds.bbci.co.uk/news/business/rss.xml
https://www.reuters.com/rssFeed/businessNews

# 科技
https://feeds.feedburner.com/TechCrunch
https://www.wired.com/feed/rss

# 中文
https://feeds.bbci.co.uk/zhongsimps/rss.xml
https://www.bbc.com/zhongwen/simp/rss.xml
```

### Email 转 RSS

**工具:** 
- rss.app - 将 email newsletter 转为 RSS
- Feedly - 内置 newsletter to RSS 功能

**使用场景:**
- 订阅记者/机构的 email newsletter
- 保持邮箱清洁
- 集中阅读

---

## 搜索技巧

### Google 搜索免费版本

```
# 搜索免费转载
"{文章标题}" site:reddit.com OR site:hn.algolia.com

# 搜索替代信源
"{标题关键词}" (site:bbc.com OR site:reuters.com OR site:apnews.com)

# 搜索 PDF 版本
"{标题}" filetype:pdf

# 搜索 Twitter 讨论
"{标题}" site:twitter.com OR site:x.com
```

### Twitter/X 获取

**技巧:**
1. 搜索文章标题
2. 找记者/媒体账号
3. 他们经常发布文章链接
4. 有时附有 "gift link"（免费访问）

---

## 文本提取工具

### r.jina.ai

**URL 格式:** `https://r.jina.ai/http://{原文链接}`

**功能:**
- 将网页转为纯文本
- 移除广告、图片、脚本
- 适合打印和阅读

**命令行:**
```bash
curl "https://r.jina.ai/http://example.com/article"
```

### Reader Mode

**浏览器内置:**
- Safari: 视图 → 显示阅读器
- Chrome: 侧边栏 → 阅读模式
- Firefox: 地址栏右侧阅读器图标

**强制开启:**
某些网站可以设置为始终使用阅读模式打开

---

## 公开存档服务

### Wayback Machine

**URL:** `https://web.archive.org/`

**使用:**
1. 访问网站
2. 粘贴 URL
3. 查看历史快照

**API:**
```
https://archive.org/wayback/available?url={encoded_url}
```

**浏览器扩展:** Wayback Machine (official)

### Google Cache

**方法 1:** 搜索 `cache:{原文链接}`

**方法 2:** 
```
https://webcache.googleusercontent.com/search?q=cache:{原文链接}
```

**注意:** 并非所有页面都有缓存

### Archive.today

**别名:** archive.is / archive.ph

**使用:** `https://archive.today/{原文链接}`

---

## 免费 API 资源

### 新闻 API

| API | 免费额度 | 特点 |
|-----|---------|------|
| NewsAPI.org | 100 请求/天 | 全球新闻源 |
| Guardian Open Platform | 免费 | 卫报内容 |
| Newsdata.io | 200 请求/天 | 多语言 |
| GNews | 100 请求/天 | 实时新闻 |

### 学术资源

**Unpaywall:** 自动查找学术论文免费版本

**Google Scholar:** 搜索 `[PDF]` 标签

---

_最后更新: 2026-03-10_
