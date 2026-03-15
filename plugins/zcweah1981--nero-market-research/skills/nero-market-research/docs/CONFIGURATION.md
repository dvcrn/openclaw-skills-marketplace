# 配置说明

本文档详细说明所有配置参数。

---

## 📄 配置文件

配置文件位于：`~/.nero-market-research/config.json`

---

## ⚙️ 配置参数

### 1. Notion 配置

```json
{
  "notion": {
    "api_key": "ntn_xxx",
    "database_id": "xxx-xxx-xxx",
    "daily_report_db_id": "xxx-xxx-xxx"
  }
}
```

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `api_key` | string | ✅ | Notion API Key（以 `ntn_` 开头）|
| `database_id` | string | ✅ | 商机池数据库 ID |
| `daily_report_db_id` | string | ✅ | 每日报告数据库 ID |

**获取方式**：
1. **API Key**: [Notion Developers](https://www.notion.so/my-integrations)
2. **Database ID**: 从数据库 URL 复制
   - URL 格式：`https://www.notion.so/your-workspace/DATABASE_ID?v=...`

---

### 2. 翻译配置

```json
{
  "translation": {
    "api_url": "https://translate.example.com",
    "api_token": "xxx",
    "cache_dir": "memory/translation_cache"
  }
}
```

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `api_url` | string | ✅ | LibreTranslate API 地址 |
| `api_token` | string | ❌ | API Token（公共实例不需要）|
| `cache_dir` | string | ❌ | 翻译缓存目录 |

**公共实例**：
- `https://translate.example.com`
- `https://libretranslate.com`

**本地实例**：
- `http://localhost:5000`

---

### 3. 搜索配置

```json
{
  "search": {
    "primary_url": "http://localhost:8080",
    "fallback_url": "https://search.example.com",
    "api_token": "xxx",
    "timeout": 20,
    "engines": ["duckduckgo", "google", "startpage"]
  }
}
```

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `primary_url` | string | ✅ | 主 SearXNG 地址 |
| `fallback_url` | string | ❌ | 备用 SearXNG 地址 |
| `api_token` | string | ❌ | API Token |
| `timeout` | number | ❌ | 超时时间（秒），默认 20 |
| `engines` | array | ❌ | 搜索引擎列表 |

**推荐引擎**：
- `duckduckgo` - 稳定
- `google` - 质量高
- `startpage` - 隐私友好
- `reddit` - Reddit 专用
- `github` - GitHub 专用

---

### 4. 执行配置

```json
{
  "execution": {
    "timezone": "Asia/Shanghai",
    "daily_report_time": "21:00",
    "weekly_mvp_time": "Monday 02:00",
    "cleanup_time": "Monday 04:00",
    "execution_interval_hours": 1,
    "max_concurrent_miners": 1
  }
}
```

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `timezone` | string | ❌ | 时区，默认 `Asia/Shanghai` |
| `daily_report_time` | string | ❌ | 每日报告时间，默认 `21:00` |
| `weekly_mvp_time` | string | ❌ | 每周 MVP 时间，默认 `Monday 02:00` |
| `cleanup_time` | string | ❌ | 清理时间，默认 `Monday 04:00` |
| `execution_interval_hours` | number | ❌ | 执行间隔（小时），默认 1 |
| `max_concurrent_miners` | number | ❌ | 最大并发数，默认 1 |

---

### 5. 评分配置

```json
{
  "scoring": {
    "min_score_to_keep": 50,
    "kill_switch_enabled": true,
    "playbook_tags": [
      "Micro-SaaS",
      "生态插件",
      "高价竞品平替",
      "API/自动化胶水"
    ]
  }
}
```

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `min_score_to_keep` | number | ❌ | 最低保留分数，默认 50 |
| `kill_switch_enabled` | boolean | ❌ | 启用一票否决，默认 true |
| `playbook_tags` | array | ❌ | 商业打法标签 |

---

### 6. Telegram 配置（可选）

```json
{
  "telegram": {
    "enabled": false,
    "bot_token": "xxx",
    "chat_id": "xxx"
  }
}
```

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `enabled` | boolean | ❌ | 是否启用，默认 false |
| `bot_token` | string | ❌ | Telegram Bot Token |
| `chat_id` | string | ❌ | Chat ID |

---

### 7. 日志配置

```json
{
  "logging": {
    "level": "INFO",
    "log_dir": "logs",
    "max_log_files": 30
  }
}
```

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `level` | string | ❌ | 日志级别，默认 INFO |
| `log_dir` | string | ❌ | 日志目录 |
| `max_log_files` | number | ❌ | 最大日志文件数 |

**日志级别**：
- `DEBUG` - 详细调试信息
- `INFO` - 一般信息
- `WARNING` - 警告
- `ERROR` - 错误

---

### 8. 数据源配置

```json
{
  "data_sources": {
    "reddit": {
      "enabled": true,
      "subreddits_file": "config/reddit_mines.json",
      "keywords_file": "config/keywords.json"
    },
    "twitter": {
      "enabled": true,
      "keywords_file": "config/twitter_keywords.json"
    },
    "github": {
      "enabled": true,
      "repos_file": "config/github_repos.json"
    },
    "producthunt": {
      "enabled": true,
      "products_file": "config/producthunt_products.json"
    },
    "other": {
      "enabled": true,
      "platforms_file": "config/other_platforms.json"
    }
  }
}
```

---

## 🔧 高级配置

### 自定义关键词

编辑 `config/keywords.json`：

```json
{
  "pain_keywords": {
    "tier_1_golden": [
      "I wish there was",
      "Looking for a tool"
    ]
  }
}
```

### 自定义矿区

编辑 `config/reddit_mines.json`：

```json
{
  "reddit_mines": {
    "tier_1_daily": [
      "startups",
      "Entrepreneur"
    ]
  }
}
```

---

## 📚 相关文档

- [安装指南](SETUP_GUIDE.md)
- [使用手册](USAGE.md)
- [API参考](API_REFERENCE.md)
