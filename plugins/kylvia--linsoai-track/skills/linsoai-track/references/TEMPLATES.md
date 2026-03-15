# 任务模板库

预置的常用定时任务模板。使用时根据实际需求调整参数。

---

## 1. 每日价格/汇率监控

追踪加密货币、股票或汇率的每日变化。

```bash
openclaw cron add \
  --name "每日BTC价格追踪" \
  --cron "0 9 * * *" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "查看当前 BTC/USDT 价格，与昨天的价格对比，计算涨跌幅。生成简短报告，包含：当前价格、24h涨跌幅、7日趋势。如果涨跌幅超过5%，用 openclaw message send 通知我。"
```

**变体：** 将 BTC 替换为 ETH、美元汇率、黄金价格等。

---

## 2. 每日新闻/资讯摘要

自动汇总特定领域的当日新闻。

```bash
openclaw cron add \
  --name "AI领域每日简报" \
  --cron "0 8 * * *" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "汇总今天 AI 领域的重要新闻和动态，包括：大模型发布、融资事件、政策变化、开源项目。按重要程度排序，每条新闻一句话摘要。完成后用 openclaw message send 发送给我。"
```

**变体：** 区块链新闻、科技新闻、行业新闻等。

---

## 3. 服务器/服务状态检查

定期检查服务的可用性和健康状态。

```bash
openclaw cron add \
  --name "服务状态检查" \
  --every 3h \
  --session isolated \
  --message "检查以下服务的状态：
1. https://api.example.com/health — 期望返回 200
2. https://app.example.com — 期望页面正常加载
对每个服务记录响应时间。如果任何服务异常或响应超过 5 秒，立即用 openclaw message send 通知我，包含异常详情。"
```

---

## 4. 竞品网站变化监控

监控竞品网站的内容变化。

```bash
openclaw cron add \
  --name "竞品官网监控" \
  --cron "0 10 * * *" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "访问竞品网站 https://competitor.com 的首页和定价页面，与之前的内容对比。关注：产品功能更新、定价变化、新的营销活动。如果发现重要变化，用 openclaw message send 通知我，包含变化摘要。"
```

---

## 5. 每周报告生成

每周自动生成汇总报告。

```bash
openclaw cron add \
  --name "每周AI简报" \
  --cron "0 10 * * 1" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "生成本周 AI 领域周报，包含：
1. 本周最重要的 5 条新闻
2. 值得关注的新开源项目
3. 重要论文摘要
4. 下周值得关注的事件
格式化为 Markdown，完成后用 openclaw message send 发送给我。"
```

---

## 6. 一次性到期提醒

在指定时间提醒一次，然后自动停止。

```bash
openclaw cron add \
  --name "域名到期提醒" \
  --at "2026-06-01T09:00" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "提醒：域名 example.com 将在 7 天后（6月8日）到期，请及时续费。用 openclaw message send 通知我。"
```

**变体：** 证书到期、合同到期、会员续费等。

---

## 7. 定时数据备份

定期执行数据备份命令。

```bash
openclaw cron add \
  --name "每日数据库备份" \
  --cron "0 3 * * *" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "执行以下备份步骤：
1. 运行 pg_dump 导出数据库到 /backups/db-$(date +%Y%m%d).sql
2. 压缩备份文件
3. 删除 7 天前的旧备份
4. 检查备份文件大小是否合理
如果备份失败，立即用 openclaw message send 通知我。"
```

---

## 8. 社交媒体/内容监控

追踪特定话题或账号的动态。

```bash
openclaw cron add \
  --name "GitHub趋势追踪" \
  --cron "0 18 * * *" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "查看今天 GitHub Trending 上的热门项目，重点关注 AI/ML 和 DevTools 类别。列出 Top 5 项目，包含：项目名、星标数、一句话描述。如果有特别值得关注的项目（星标增长极快或与我的技术栈相关），用 openclaw message send 通知我。"
```
