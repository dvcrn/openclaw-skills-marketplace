# Search Pro - 免费搜索引擎


## 🎯 推荐安装场景

✅ **你应该安装这个技能，如果：**
- [ ] 你需要获取最新信息
- [ ] 你想搜索网络内容
- [ ] 你需要多引擎搜索
- [ ] 你想提取网页内容

❌ **不需要安装，如果：**
- [ ] 你不需要联网功能
- [ ] 你使用其他搜索工具

---

## ⭐ 觉得好用？

如果喜欢这个技能，请：
1. 在 ClawHub 给个 **⭐⭐⭐⭐⭐ 5 星好评**
2. 分享给其他 OpenClaw 用户
3. 提交 Issue 或 PR 改进

**你的评分对我们很重要！** 帮助更多人发现这个技能。

---

## 🔗 相关技能推荐

安装了这个技能的用户也安装了：

| 技能 | 作用 | 推荐度 |
|------|------|--------|
| [memory-enhancer](../memory-enhancer) | 增强记忆 | ⭐⭐⭐⭐⭐ |
| [auto-backup](../auto-backup) | 自动备份 | ⭐⭐⭐⭐ |
| [model-switch](../model-switch) | 模型切换 | ⭐⭐⭐⭐ |

**推荐组合安装：**
```bash
npx clawhub install openclaw-memory-enhancer
npx clawhub install openclaw-auto-backup
npx clawhub install openclaw-model-switch
```

---


**无需 API Key，安装即用！** 多引擎聚合搜索工具。

[English Version](README_EN.md)

---

## ✨ 功能特性

- 🔍 **无需配置** - 安装即用，无需 API Key
- 🚀 **国内可访问** - 支持必应中国、搜狗、360 搜索
- 📄 **内容提取** - 自动提取网页正文
- 📊 **结果去重** - 智能去重 + 相关性排序
- ⚙️ **可选配置** - 支持配置百度/Bing 等 API（可选）

---

## 🚀 安装

```bash
cd ~/.openclaw/workspace/skills
# 技能已安装在：~/.openclaw/workspace/skills/search-pro
chmod +x search-pro/scripts/*.py
```

**就这么简单！无需任何配置，立即使用！**

---

## 📖 使用

### 基本搜索（无需配置）

```bash
# 直接搜索
python3 search-pro/scripts/multi-search.py "OpenClaw 技能"

# 限制结果数
python3 search-pro/scripts/multi-search.py "OpenClaw 技能" --max-results 20

# 指定引擎
python3 search-pro/scripts/multi-search.py "OpenClaw 技能" --engine bing-cn
```

### 可用引擎

| 引擎 | 说明 | 需要 API |
|------|------|----------|
| `free` | 自动选择（默认） | ❌ 否 |
| `bing-cn` | 必应中国 | ❌ 否 |
| `sogou` | 搜狗搜索 | ❌ 否 |
| `so360` | 360 搜索 | ❌ 否 |

---

## 🎯 特点

### ✅ 无需 API Key

- 不注册任何账号
- 不配置任何 Key
- 安装后立即使用

### ✅ 国内可访问

- 必应中国（cn.bing.com）
- 搜狗搜索（sogou.com）
- 360 搜索（so.com）

### ✅ 自动降级

如果某个引擎无法访问，自动切换到备用引擎。

---

## ⚙️ 可选配置（高级）

如果想获得更稳定的搜索质量，可以配置 API Key：

### 配置百度 API

```json
{
  "baidu": {
    "enabled": true,
    "apiKey": "你的 API Key",
    "secretKey": "你的 Secret Key"
  }
}
```

**获取方式：** https://ai.baidu.com/tech/search

### 配置 Bing API

```json
{
  "bing": {
    "enabled": true,
    "apiKey": "你的 API Key"
  }
}
```

**获取方式：** https://www.microsoft.com/en-us/bing/apis/bing-web-search-api

---

## 📊 引擎对比

| 引擎 | 中文质量 | 速度 | 需要 API | 推荐度 |
|------|----------|------|----------|--------|
| **免费搜索** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ 否 | ⭐⭐⭐⭐⭐ |
| 百度 API | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ 是 | ⭐⭐⭐⭐ |
| Bing API | ⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ 是 | ⭐⭐⭐ |

---

## 🛠️ 脚本说明

| 脚本 | 功能 |
|------|------|
| `free_search.py` | 免费搜索引擎（无需 API） |
| `multi-search.py` | 命令行搜索工具 |
| `baidu_search.py` | 百度 API（可选） |
| `fallback_search.py` | 备用搜索引擎 |

---

## 💡 使用场景

### 日常搜索
```bash
python3 search-pro/scripts/multi-search.py "今天天气"
```

### 搜索小说
```bash
python3 search-pro/scripts/multi-search.py "小说 青山"
```

### 搜索技术文档
```bash
python3 search-pro/scripts/multi-search.py "Python 教程" --max-results 20
```

---

## ❓ 常见问题

### Q: 为什么搜索结果少？
A: 免费搜索有访问限制，建议配置百度 API 获得更好体验。

### Q: 搜索失败怎么办？
A: 检查网络连接，或尝试其他关键词。

### Q: 如何获得更好的搜索质量？
A: 配置百度 API（参考上文），质量提升明显。

---

## 📄 许可证

MIT-0

---

**作者：** @williamwg2025  
**版本：** 1.0.0  
**特点：** 无需 API Key，安装即用！

---

## 🔒 安全说明

### 网络访问 ⚠️
**本技能需要联网：**
- 访问搜索引擎（必应、搜狗、360 等）
- 提取网页内容
- 可选：Tavily API（需配置）

**网络权限：**
- 出站 HTTPS 请求（443 端口）
- 不监听端口
- 不运行服务器

### 文件访问
**路径：** `~/.openclaw/workspace/skills/search-pro/`

- **读取：** config/search-config.json（搜索配置和 API 密钥）
- **写入：** 当前版本不自动写入文件
- **extract.py 安全检查：**
  - ✅ 协议检查（仅 http/https）
  - ✅ IP 地址检查（私有 IP 范围）
  - ✅ DNS 解析后检查（防止 SSRF）
  - ✅ 内网域名检查（.local, .internal 等）

### 数据安全
- **不上传：** 不上传用户配置文件
- **本地存储：** 搜索历史仅保存在本地
- **隐私保护：** 搜索查询不发送到除搜索引擎外的第三方

---

**作者：** @williamwg2025  
**版本：** 1.0.1  
**许可证：** MIT-0
