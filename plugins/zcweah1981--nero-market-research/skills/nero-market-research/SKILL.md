---
name: nero-market-research
description: "Nero Market Research"
---

# Nero Market Research Skill

**一键安装 AI 独立开发者的情报挖掘系统**

## 🎯 这是什么？

Nero 是一个全自动化的市场研究系统，每天从 500+ 数据源自动收集、评分、筛选产品机会，最终只推送 1-2 个真正值得开发的神仙点子。

**核心理念**：
```
从 500 条噪音中，精准找到那 1-2 个值得打开 VS Code 的神仙点子
```

---

## ⚡ 快速开始（3步）

### 1. 安装

```bash
# 方式1: 从 ClawHub 安装（推荐）
clawhub install nero-market-research

# 方式2: 从 GitHub 安装
git clone https://github.com/your-username/nero-market-research.git
cd nero-market-research
./install.sh
```

### 2. 配置

```bash
# 复制配置模板
cp config.json.example config.json

# 编辑配置（填入你的 API keys）
nano config.json
```

**必需的 API Keys**：
- ✅ Notion API Key（免费）
- ✅ Notion Database ID（需要创建两个数据库）
- ✅ LibreTranslate URL（提供免费实例）

### 3. 启动

```bash
# 启动系统
nero-start

# 查看日志
nero-logs

# 查看状态
nero-status
```

**恭喜！系统现在开始24小时自动收集产品机会！** 🎉

---

## 📊 系统功能

### ✅ 自动化数据收集

- **350个数据源**：Reddit(100) + Twitter(50) + GitHub(30) + ProductHunt(20) + Other(50)
- **24小时循环**：每小时自动执行一个数据源
- **智能去重**：SimHash算法，自动过滤重复内容

### ✅ 智能评分系统

- **数据质量过滤**：完整性验证 + 相关性评分 + 噪音过滤（保留率76%）
- **需求评分器 v2.0**：四维打分（痛点/技术/变现/获客）+ 一票否决机制
- **标签化归类**：自动识别4种商业打法（Micro-SaaS/生态插件/竞品平替/自动化胶水）

### ✅ Notion 自动同步

- **三字段结构**：
  - `Demand Content`：英文原文
  - `Trans Content`：中文翻译
  - `PM 解读`：专业解读 + 建议
- **Daily Report 关联**：自动关联当天报告
- **智能去重**：自动清理重复条目

### ✅ 每日报告

- **21:00 北京时间**：自动生成每日报告
- **Telegram 推送**：高分机会自动通知
- **Notion 同步**：报告自动保存到 Notion

---

## 🎯 核心价值

### 独立开发者视角

| 对比维度 | VC 模式 | Nero 模式 |
|---------|---------|----------|
| **关注点** | 市场规模有多大 | 我能不能1个月做出来收钱 |
| **筛选标准** | 增长潜力 | 可行性 + 变现速度 |
| **决策速度** | 数周到数月 | 10秒决策 |

### 灵感公式

```
灵感 = (旧的行业痛点) + (新的AI能力) + (极简的交互体验)
```

---

## 📈 预期效果

| 时间 | 原始数据 | 最终保留 | 保留率 |
|------|---------|---------|--------|
| **每天** | ~500条 | ~60条 | 12% |
| **每周** | ~3,500条 | ~420条 | 12% |
| **每月** | ~15,000条 | ~1,800条 | 12% |

**高优先级机会**：5-10个/天  
**商业打法分布**：
- 🏷️ Micro-SaaS：50%
- 🏷️ API/自动化胶水：25%
- 🏷️ 生态插件：15%
- 🏷️ 高价竞品平替：10%

---

## 🛠 技术栈

- **Python 3.10+**
- **SearXNG API**（搜索引擎，主备模式）
- **LibreTranslate API**（翻译服务）
- **Notion API**（数据同步）
- **systemd**（定时任务）

---

## 📁 目录结构

```
nero-market-research/
├── SKILL.md                    # 本文档
├── README.md                   # 详细说明
├── install.sh                  # 一键安装脚本
├── uninstall.sh                # 卸载脚本
├── config.json.example         # 配置模板
├── scripts/                    # 核心脚本
│   ├── cycle_execution.py      # 24小时循环执行
│   ├── auto_pipeline.py        # 自动化管道
│   ├── data_quality_filter.py  # 数据质量过滤器
│   ├── demand_scorer_v2.py     # 需求评分器
│   ├── sync_to_notion.py       # Notion同步
│   └── generate_report.py      # 报告生成
├── config/                     # 配置文件
│   ├── reddit_mines.json       # Reddit矿区配置
│   ├── keywords.json           # 关键词库
│   └── notion_databases.json   # Notion数据库配置
├── docs/                       # 详细文档
│   ├── SETUP_GUIDE.md          # 安装指南
│   ├── CONFIGURATION.md        # 配置说明
│   ├── USAGE.md                # 使用手册
│   └── API_REFERENCE.md        # API参考
└── templates/                  # Notion模板
    ├── opportunities_template.json
    └── daily_report_template.json
```

---

## 🔧 常用命令

```bash
# 系统控制
nero-start          # 启动系统
nero-stop           # 停止系统
nero-restart        # 重启系统
nero-status         # 查看状态

# 日志查看
nero-logs           # 查看实时日志
nero-logs-today     # 查看今日日志

# 手动执行
nero-run-now        # 立即执行一次
nero-sync           # 手动同步到Notion
nero-report         # 生成今日报告

# 数据管理
nero-cleanup        # 清理旧数据
nero-duplicates     # 查看重复数据
nero-stats          # 查看统计数据
```

---

## ⚙️ 配置说明

### 必需配置

```json
{
  "notion": {
    "api_key": "ntn_xxx...",           // Notion API Key
    "database_id": "xxx-xxx-xxx",      // 商机池数据库ID
    "daily_report_db_id": "xxx-xxx-xxx" // 每日报告数据库ID
  },
  "translation": {
    "api_url": "https://translate.xxx.com",
    "api_token": "xxx"                  // 可选
  },
  "search": {
    "primary_url": "http://localhost:8080",
    "fallback_url": "https://search.xxx.com"
  }
}
```

### Notion 数据库设置

需要创建两个 Notion 数据库：

1. **商机池数据库（Opportunities）**
   - 14个字段（详见 `docs/CONFIGURATION.md`）
   - 使用模板：`templates/opportunities_template.json`

2. **每日报告数据库（Daily Reports）**
   - 7个字段
   - 使用模板：`templates/daily_report_template.json`

---

## 🐛 故障排查

### 常见问题

**Q: 系统没有数据？**  
A: 检查 SearXNG 连接状态：`nero-status`

**Q: Notion 同步失败？**  
A: 检查 API Key 和 Database ID 是否正确

**Q: 翻译失败？**  
A: 检查 LibreTranslate 服务是否正常运行

**Q: 系统占用资源过高？**  
A: 调整执行频率（编辑 `config/execution.json`）

---

## 🔄 Git自动同步

### 初始化仓库（仅第一次）

```bash
chmod +x init-git.sh
./init-git.sh <你的GitHub用户名> <你的GitHub Token>
```

### 日常同步

```bash
# 手动同步（推荐）
./auto-sync.sh "更新文档"

# 自动监控（后台运行）
./watch-sync.sh
```

---

## 📚 详细文档

- [安装指南](docs/SETUP_GUIDE.md) - 详细的安装步骤
- [配置说明](docs/CONFIGURATION.md) - 完整的配置参数
- [使用手册](docs/USAGE.md) - 详细的使用方法
- [API参考](docs/API_REFERENCE.md) - 开发者文档
- [Git同步指南](GIT_SYNC_GUIDE.md) - Git自动同步说明 ⭐

---

## 🤝 贡献

欢迎贡献代码、报告问题、提出建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 License

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- [SearXNG](https://github.com/searxng/searxng) - 开源搜索引擎
- [LibreTranslate](https://github.com/LibreTranslate/LibreTranslate) - 免费翻译API
- [Notion API](https://developers.notion.com/) - 强大的数据库功能

---

## 📮 联系方式

- **作者**: Pascal AI Team
- **Email**: zcweah@gmail.com
- **Twitter**: [@zhngchng231034](https://twitter.com/zhngchng231034)

---

**让每一个产品灵感都来自真实痛点，而不是拍脑门。** 🚀
