# 微信公众号文章抓取 Skill

**版本:** 1.0.0  
**作者:** 十三香 (agent 管理者) 🌶️  
**发布时间:** 2026-03-13  
**Skill ID:** k978pa1fn0nrygwr5xmxvp31sd82vzdj

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

## 🔐 权限控制

**仅限授权 agent 使用:** 蒜蓉

其他 agent 调用时会被拒绝，并提示联系张亮确认。

---

## 🚀 快速开始

### 1. 安装

```bash
clawhub install wx-article-fetcher
```

### 2. 配置签名

```bash
export WX_QUERY_SIGN="your_sign_here"
```

### 3. 使用

```bash
# 查询公众号 biz
wx-biz-query 理财魔方

# 抓取文章
wx-articles-fetch MzU5MDkxMTI4Nw==

# 指定时间范围
wx-articles-fetch MzU5MDkxMTI4Nw== 2025-01-01 2025-12-31
```

---

## 📁 目录结构

```
wx-article-fetcher/
├── SKILL.md                 # 技能说明
├── INSTALL.md               # 安装说明
├── README.md                # 本文件
├── package.json             # 包配置
├── scripts/
│   ├── wx_biz_query.py      # 公众号查询脚本
│   └── wx_article_fetcher.py # 文章抓取脚本
└── commands/
    └── wx-commands.sh       # 命令封装（含权限检查）
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

### Q: 提示"权限拒绝"
**A:** 本 skill 仅限蒜蓉使用，其他 agent 需要联系张亮确认授权。

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
**A:** 文章保存在 `~/.wx_articles/` 目录，可整体复制备份

---

## 📞 维护信息

- **开发者:** 十三香 (agent 管理者)
- **直属领导:** 张亮
- **公司:** 理财魔方
- **最后更新:** 2026-03-13

---

## 📝 更新日志

### v1.0.0 (2026-03-13)
- ✅ 初始版本发布
- ✅ 公众号 biz 查询功能
- ✅ 文章抓取功能（支持分页）
- ✅ 时间范围筛选
- ✅ JSON + Markdown 双格式输出
- ✅ 权限控制（仅限蒜蓉使用）
- ✅ 签名加密存储
