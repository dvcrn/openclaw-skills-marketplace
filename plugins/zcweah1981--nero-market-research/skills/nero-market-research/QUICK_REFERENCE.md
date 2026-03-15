# 🚀 Nero Market Research - 快速参考卡

**仓库地址**: https://github.com/zcweah1981/nero-market-research

---

## 📋 常用命令

### Git 同步

```bash
cd /root/.openclaw/workspace-work/nero-market-research

# 修改文件后同步
./auto-sync.sh "提交信息"

# 查看状态
git status

# 查看历史
git log --oneline -5
```

---

### 系统控制

```bash
# 查看系统状态
ps aux | grep cycle_execution

# 查看实时日志
tail -f /root/.openclaw/workspace-work/logs/cycle_execution.log

# 查看今日数据
ls -lh /root/.openclaw/workspace-work/memory/research/daily/*$(date +%Y%m%d)*
```

---

### Notion 同步

```bash
# 手动同步
cd /root/.openclaw/workspace-work
python3 skills/research/scripts/sync_opportunities_to_notion_v5.py

# 生成报告
python3 skills/research/scripts/generate_daily_report_v3.py
```

---

## 📅 定时任务

| 时间 | 任务 | 状态 |
|------|------|------|
| 每小时 | Miner执行 | ✅ 自动 |
| 21:00 | 每日报告 | ✅ 自动 |
| 周一02:00 | 每周MVP | ✅ 自动 |

---

## 🐛 故障排查

### Git 推送失败

```bash
# 检查SSH连接
ssh -i /root/.ssh/id_ed25519_github -T git@github.com

# 重新配置远程
git remote remove origin
git remote add origin git@github.com:zcweah1981/nero-market-research.git
```

---

### 系统无数据

```bash
# 检查进程
ps aux | grep cycle_execution

# 检查日志
tail -50 /root/.openclaw/workspace-work/logs/cycle_execution.log
```

---

## 📚 文档位置

- **快速开始**: SKILL.md
- **详细说明**: README.md
- **安装指南**: docs/SETUP_GUIDE.md
- **配置说明**: docs/CONFIGURATION.md
- **使用手册**: docs/USAGE.md
- **Git同步**: GIT_SYNC_GUIDE.md

---

**最后更新**: 2026-03-10 18:02 北京时间
