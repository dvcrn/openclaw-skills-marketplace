---
name: weekly-digest
description: "自动生成周报（GitHub + Notion + 新闻），支持飞书/邮件发送。"
---

# Weekly Digest - AI 周报生成器

自动生成技术周报，整合 GitHub 动态、Notion 会议记录、行业新闻。

## 使用场景

- 每周五自动生成个人/团队周报
- 项目进度汇报
- 技术动态追踪

## 功能

1. **GitHub 动态** - 自动抓取 commits/PRs/issues
2. **Notion 会议记录** - 提取会议待办和决策
3. **行业新闻** - 实时搜索相关技术新闻
4. **飞书发送** - 自动发送周报到飞书群/个人

## 使用方法

```bash
# 生成周报
clawhub run weekly-digest --since "7 days ago" --to "today"

# 发送到飞书
clawhub run weekly-digest --send-to-feishu --channel "技术周报"
```

## 配置

在 `~/.openclaw/openclaw.json` 配置：

```json5
{
  skills: {
    entries: {
      "weekly-digest": {
        enabled: true,
        env: {
          FEISHU_APP_ID: "your_app_id",
          FEISHU_APP_SECRET: "your_app_secret"
        }
      }
    }
  }
}
```

## 输出格式

```markdown
# 周报 (2026-02-27 ~ 2026-03-05)

## GitHub 动态
- ✅ 完成 5 个 commits
- 🔀 合并 3 个 PRs
- 🐛 修复 2 个 issues

## 会议记录
- 周一：产品评审会（待办：XXX）
- 周三：技术方案讨论（决策：XXX）

## 行业新闻
- OpenClaw 发布新版本...
- AI 领域新突破...

## 下周计划
- [ ] XXX
- [ ] XXX
```

## 定制开发 Custom Development

**收费模式 Pricing Tiers：**

| 版本 | 价格 | 功能 |
|------|------|------|
| **标准版 Standard** | 免费 Free | 基础功能，个人使用 |
| **专业版 Pro** | $30/month (¥199/月) | 全部功能 + 优先支持 |
| **定制版 Custom** | $700-3000 (¥5000-20000) | 私有化部署 + 功能定制 |

**联系方式 Contact：**
- 📧 邮箱 Email：1776480440@qq.com
- 💬 微信 WeChat：私信获取 DM for details

**支持支付 Payment：**
- 国内 Domestic：私信获取
- 国际 International：私信获取（PayPal/Wise）

**售后支持 After-Sales：**
- 首年免费维护 Free for 1st year
- 次年 $100/年 (¥700/年) optional

---

**技能来源 Source：** https://clawhub.ai/sukimgit/weekly-digest
**作者 Author：** Monet + 老高
**版本 Version：** 1.0.6
**联系 Contact：** 私信获取
