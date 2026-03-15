# wx-article-fetcher Skill 安装说明

## 📦 发布信息

- **Skill 名称:** wx-article-fetcher
- **版本:** 1.0.0
- **作者:** 十三香 (agent 管理者)
- **发布时间:** 2026-03-13
- **Skill ID:** k978pa1fn0nrygwr5xmxvp31sd82vzdj

---

## 🔐 权限控制

**授权 Agent:** 蒜蓉

**其他 agent 无法使用** - 脚本内置权限检查，非授权 agent 调用会被拒绝。

---

## 🚀 安装步骤

### 方式一：通过 ClawHub 安装（推荐）

让蒜蓉在自己的环境中运行：

```bash
clawhub install wx-article-fetcher
```

### 方式二：手动安装

1. 复制 skill 目录到蒜蓉的 skills 文件夹：

```bash
cp -r /Users/edy/.openclaw/workspace/baseagent/skills/wx-article-fetcher \
      /Users/edy/.openclaw/agents/suanrong/skills/
```

2. 在蒜蓉的 AGENTS.md 或 TOOLS.md 中添加引用

---

## 🔧 配置签名

安装后需要配置签名才能使用：

### 方式一：环境变量（推荐）

```bash
export WX_QUERY_SIGN="jki213k111skb11aa"
```

永久设置（添加到 ~/.zshrc）：
```bash
echo 'export WX_QUERY_SIGN="jki213k111skb11aa"' >> ~/.zshrc
source ~/.zshrc
```

### 方式二：交互式输入

首次运行命令时会自动提示输入签名。

---

## 📖 使用命令

安装完成后，蒜蓉可以使用以下命令：

| 命令 | 说明 | 示例 |
|------|------|------|
| `wx-biz-query <名称>` | 查询公众号 biz | `wx-biz-query 理财魔方` |
| `wx-articles-fetch <biz>` | 抓取文章 | `wx-articles-fetch MzU5MDkxMTI4Nw==` |
| `wx-biz-list` | 查看缓存 | `wx-biz-list` |
| `wx-biz-clear` | 清空缓存 | `wx-biz-clear` |
| `wx-biz-export [文件]` | 导出缓存 | `wx-biz-export backup.json` |

---

## 📁 输出位置

- **公众号缓存:** `~/.wx_biz_query/cache.json`
- **文章保存:** `~/.wx_articles/<公众号名称>_<时间戳>/`

---

## ⚠️ 安全说明

1. 签名信息不要分享给其他 agent 或人员
2. 脚本有权限检查，非授权 agent 调用会被拒绝
3. 文章数据仅保存在本地，不会上传

---

## 🆘 问题反馈

如有问题请联系：
- **开发者:** 十三香 (agent 管理者)
- **直属领导:** 张亮
