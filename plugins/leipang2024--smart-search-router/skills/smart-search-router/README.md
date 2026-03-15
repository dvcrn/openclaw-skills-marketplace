# Smart Search Router

智能搜索路由 - 根据查询复杂度自动选择 SearXNG 或 Gemini Search，优化 token 使用。

## 功能特点

- 🧠 **智能路由** - 自动判断查询复杂度（0-1）
- 💰 **节省 Token** - 简单查询使用 SearXNG，节省约 40% token
- 🎯 **高质量答案** - 复杂查询使用 Gemini Search，保证答案质量
- 🔒 **隐私保护** - SearXNG 无追踪，支持自托管
- ⚡ **自动降级** - 主引擎失败时自动切换到备用引擎

## 路由规则

| 查询类型 | 复杂度 | 使用引擎 | Token 节省 |
|----------|--------|----------|-----------|
| 简单查询 | < 0.6 | SearXNG | ~40% |
| 复杂查询 | ≥ 0.6 | Gemini Search | - |

### 简单查询示例
- "今天天气如何？"
- "有什么科技新闻？"
- "北京时间现在几点？"

### 复杂查询示例
- "比较 SearXNG 和 Gemini 的优缺点"
- "分析 AI 技术对未来就业的影响"
- "为什么量子计算如此重要？"

## 安装

```bash
clawhub install smart-search-router
```

## 配置

在 `openclaw.json` 中添加：

```json
{
  "plugins": {
    "entries": {
      "smart-search-router": {
        "enabled": true,
        "config": {
          "searxng": {
            "baseUrl": "YOUR_SEARXNG_URL",
            "engines": "google,bing,duckduckgo",
            "language": "zh-CN"
          },
          "gemini": {
            "apiKey": "YOUR_GEMINI_API_KEY"
          },
          "complexityThreshold": 0.6,
          "useGeminiForComplex": true
        }
      }
    }
  }
}
```

## 配置选项

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `searxng.baseUrl` | string | **必填** | SearXNG 实例 URL |
| `searxng.engines` | string | `google,bing,duckduckgo` | 搜索引擎列表 |
| `searxng.language` | string | `zh-CN` | 搜索语言 |
| `gemini.apiKey` | string | - | Gemini API 密钥 |
| `complexityThreshold` | number | `0.6` | 复杂度阈值（0-1） |
| `useGeminiForComplex` | boolean | `true` | 是否对复杂查询使用 Gemini |

## 使用工具

### `smart_search`

智能搜索工具，自动选择最佳搜索引擎。

**参数：**
- `query` (required): 搜索查询
- `forceEngine` (optional): 强制使用特定引擎 (`searxng` 或 `gemini`)
- `limit` (optional): 返回结果数量（默认 10）

**示例：**
```javascript
// 自动路由
smart_search({ query: "今天有什么新闻？" })

// 强制使用 SearXNG
smart_search({ query: "AI 新闻", forceEngine: "searxng" })

// 强制使用 Gemini
smart_search({ query: "分析 AI 发展趋势", forceEngine: "gemini" })
```

## 复杂度算法

复杂度评分基于以下因素：

**增加复杂度：**
- 比较类问题（compare, vs, difference）
- 分析类问题（analyze, explain, why, how）
- 多步骤问题（list...and, compare...with）
- 评价类问题（evaluate, review, pros/cons）
- 技术深度问题（technical, architecture, algorithm）
- 查询长度（>50 字符 +0.1，>80 字符 +0.1，>120 字符 +0.1）
- 疑问词（why, how +0.1）

**降低复杂度：**
- 时间/日期问题（what time, when, today）
- 天气问题（weather, temperature）
- 简单事实（what is, who is, where is）
- 新闻查询（news, latest, recent）
- 是非问题（is, are, do, does...?）

最终分数归一化到 0-1 范围。

## 技术架构

```
用户查询
    ↓
复杂度分析 (0-1)
    ↓
路由决策
    ├── < 0.6 → SearXNG (省 token)
    └── ≥ 0.6 → Gemini Search (高质量)
    ↓
返回结果
```

## 依赖

- OpenClaw ≥ 2026.3.12
- SearXNG 实例（**必填**，需自行部署或使用公共实例）
- Google Gemini API（可选，用于复杂查询）

### SearXNG 部署选项

**选项 1：自托管（推荐）**
```bash
docker run -d -p 8080:8080 searxng/searxng
```

**选项 2：使用公共实例**
- https://searx.be - 公共 SearXNG 实例列表
- 选择信任的实例并配置其 URL

**选项 3：使用 Vane 内置的 SearXNG**
- 如果已安装 Vane (Perplexica)，SearXNG 运行在容器内
- 需要暴露端口或配置容器间网络

## 许可证

MIT License

## 作者

StudioPANG

## 更新日志

### v1.0.3 (2026-03-14)
- 🔧 修复 Skill 格式问题，使用正确的 ClawHub Skill 结构
- ✅ 添加 `skill.js` 作为 Skill 入口
- ✅ 添加 `skill-manifest.json` 定义工具和配置

### v1.0.2 (2026-03-14)
- 🔒 移除所有默认 IP 地址（包括 localhost）
- ⚠️ `searxng.baseUrl` 改为必填项
- 📖 添加 SearXNG 部署指南

### v1.0.1 (2026-03-14)
- 🔒 移除默认 IP 地址，改用 `localhost` 占位符
- 增强隐私保护

### v1.0.0 (2026-03-14)
- 初始版本
- 智能路由功能
- SearXNG 和 Gemini 集成
- 自动降级机制
