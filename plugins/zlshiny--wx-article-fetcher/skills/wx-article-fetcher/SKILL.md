---
name: wx-article-fetcher
description: "微信公众号文章抓取"
---

# wx-article-fetcher Skill

**版本:** 1.0.0  
**作者:** 十三香 (agent 管理者) 🌶️  
**描述:** 微信公众号文章抓取工具 - 根据公众号名称或 biz 查询并下载公众号文章

---

## 📖 功能说明

本 skill 提供微信公众号文章抓取功能：
- ✅ 根据公众号名称查询对应的 biz
- ✅ 根据 biz 抓取公众号文章
- ✅ 支持时间范围筛选
- ✅ 自动缓存查询结果，避免重复调用接口
- ✅ 保存为 JSON 和 Markdown 格式
- ✅ 按创建时间组织文件结构

---

## 🔒 安全控制

### 权限控制

**允许使用的 agent:**
- 蒜蓉（授权用户）
- baseagent（管理员，可访问所有数据）

**其他 agent:** 禁止使用，调用会被拒绝。

### 数据隔离

**重要：** 每个 agent 的数据完全隔离，无法访问其他 agent 的数据。

| Agent | 缓存路径 | 文章保存路径 |
|-------|----------|--------------|
| baseagent | `~/.wx_biz_query/cache.json` | `~/.wx_articles/` |
| 蒜蓉 | `{workspace}/.wx_cache/wx_biz_cache.json` | `{workspace}/.wx_articles/` |
| 其他 agent | 各自工作空间内 | 各自工作空间内 |

**说明:**
- `baseagent` (agent 管理者) 可以访问全局数据
- 其他 agent 只能访问自己工作空间内的数据
- 工作空间路径由 `OPENCLAW_WORKSPACE` 环境变量指定
- 防止 agent 之间数据泄露和交叉访问

### 签名配置

签名信息存储在每个 agent 自己的工作空间内：
- `baseagent`: `~/.wx_biz_query/config.enc`
- 其他 agent: `{workspace}/.wx_config/wx_sign.enc`

---

## 🚀 使用方法

### 方式一：查询公众号 biz

```bash
wx-biz-query <公众号名称>
```

**示例:**
```bash
wx-biz-query 理财魔方
```

### 方式二：抓取公众号文章

```bash
wx-articles-fetch <biz> [开始时间] [结束时间] [最大页数]
```

**参数说明:**
- `biz` - 公众号 biz（必填）
- `开始时间` - 格式 YYYY-MM-DD（可选）
- `结束时间` - 格式 YYYY-MM-DD（可选）
- `最大页数` - 限制抓取页数（可选，默认全部）

**示例:**
```bash
# 抓取所有文章
wx-articles-fetch MzU5MDkxMTI4Nw==

# 抓取指定时间范围
wx-articles-fetch MzU5MDkxMTI4Nw== 2025-01-01 2025-12-31

# 限制页数
wx-articles-fetch MzU5MDkxMTI4Nw== 2025-01-01 2025-12-31 5
```

### 方式三：查看缓存的公众号

```bash
wx-biz-list
```

---

## 🔐 安全配置

### 设置签名（首次使用）

**方式一：环境变量（推荐）**
```bash
export WX_QUERY_SIGN="your_sign_here"
```

**方式二：本地加密文件**
首次运行会自动提示输入签名并询问是否保存。

---

## 📁 文件结构

```
wx-article-fetcher/
├── SKILL.md              # 技能说明
├── scripts/
│   ├── wx_biz_query.py   # 公众号查询脚本
│   └── wx_article_fetcher.py  # 文章抓取脚本
└── commands/
    └── wx-commands.sh    # 命令封装
```

---

## 📊 输出说明

### 文章保存位置
```
~/.wx_articles/<公众号名称>_<时间戳>/
├── YYYY-MM-DD/
│   ├── 001_文章标题.json
│   └── 001_文章标题.md
├── ...
└── images/  # 文章图片（可选）
```

### JSON 格式
```json
{
  "title": "文章标题",
  "create_time": "2025-01-01 12:00:00",
  "biz": "MzU5MDkxMTI4Nw==",
  "content": "文章内容",
  "read": 1000,
  "zan": 50,
  "share_num": 20,
  "collect_num": 15,
  "comment_count": 5,
  "long_link": "https://...",
  "short_link": "https://..."
}
```

---

## ⚠️ 注意事项

1. **签名保密** - 不要将签名提交到代码仓库或分享给他人
2. **接口调用限制** - 如有调用频率限制，请合理使用缓存
3. **缓存更新** - 如需更新缓存，先执行 `wx-biz-clear` 清空
4. **网络依赖** - 首次查询需要网络连接
5. **权限控制** - 仅授权 agent 可使用，其他 agent 调用会被拒绝

---

## 🆘 常见问题

### Q: 提示"未找到签名配置"
**A:** 设置环境变量：
```bash
export WX_QUERY_SIGN="your_sign_here"
```

### Q: 如何更新缓存中的数据？
**A:** 清空缓存后重新查询：
```bash
wx-biz-clear
```

### Q: 缓存文件在哪里？
**A:** `~/.wx_biz_query/cache.json`

### Q: 如何备份查询结果？
**A:** 文章保存在 `~/.wx_articles/` 目录

---

## 📞 维护信息

- **开发者:** 十三香 (agent 管理者)
- **直属领导:** 张亮
- **最后更新:** 2026-03-13
