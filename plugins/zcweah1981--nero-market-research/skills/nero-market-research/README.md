# Nero Market Research v4.0 Final

**AI 独立开发者的情报挖掘系统**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![GitHub stars](https://img.shields.io/github/stars/your-username/nero-market-research.svg?style=social&label=Star)](https://github.com/your-username/nero-market-research)

---

## 🎯 一句话介绍

从 500 条噪音中，精准找到那 1-2 个值得打开 VS Code 的神仙点子。

---

## 📸 效果展示

### Notion 商机池

![Notion Dashboard](docs/images/notion-dashboard.png)

每天自动同步高分机会到 Notion，包含：
- 英文原文（Demand Content）
- 中文翻译（Trans Content）
- PM专业解读（PM 解读）

### 每日报告

![Daily Report](docs/images/daily-report.png)

每天 21:00 北京时间自动生成报告，推送高分机会。

---

## ⚡ 快速开始

### 方式1: 一键安装（推荐）

```bash
git clone https://github.com/your-username/nero-market-research.git
cd nero-market-research
chmod +x install.sh
./install.sh
```

### 方式2: 从 ClawHub 安装

```bash
clawhub install nero-market-research
```

### 配置（3分钟）

1. **复制配置模板**
```bash
cd ~/.nero-market-research
cp config.json.example config.json
```

2. **编辑配置文件**
```bash
nano config.json
```

3. **填入必需的 API Keys**
```json
{
  "notion": {
    "api_key": "ntn_your_api_key",
    "database_id": "your_database_id",
    "daily_report_db_id": "your_daily_report_db_id"
  }
}
```

4. **启动系统**
```bash
nero start
```

**完成！系统开始24小时自动收集产品机会！** 🎉

---

## 🌟 核心功能

### 1️⃣ 自动化数据收集

- **350个数据源**：Reddit + Twitter + GitHub + ProductHunt + 其他平台
- **24小时循环**：每小时自动执行一个数据源
- **智能去重**：SimHash算法，自动过滤重复内容

### 2️⃣ 智能评分系统

**数据质量过滤器**：
- ✅ 完整性验证
- ✅ 相关性评分（TF-IDF + 关键词）
- ✅ 噪音过滤（学术/宣传/教程）
- ✅ 保留率：76%

**需求评分器 v2.0**：
- ✅ 一票否决机制（4种陷阱）
- ✅ 四维打分（痛点/技术/变现/获客）
- ✅ 标签化归类（4种商业打法）
- ✅ 最终保留率：12%

### 3️⃣ Notion 自动同步

**三字段结构**：
- **Demand Content**：英文原文
- **Trans Content**：中文翻译
- **PM 解读**：专业解读 + 建议

**智能关联**：
- 自动创建/获取 Daily Report
- 自动关联当天报告
- 自动清理重复条目

### 4️⃣ 每日报告

- **21:00 北京时间**：自动生成报告
- **Telegram 推送**：高分机会通知
- **Notion 同步**：报告自动保存

---

## 📊 预期效果

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

## 🎯 适用人群

### ✅ 适合

- 独立开发者（前端技术栈为主）
- 想在 1-3 个月内快速验证 MVP
- 关注 B2B SaaS、自动化工具、效率工具
- 资源有限，需要精准筛选机会

### ❌ 不适合

- 需要 VC 级别的市场规模分析
- 关注硬件、重度后端、AI训练项目
- 需要详细的市场调研报告
- 团队协作开发

---

## 🛠 技术栈

- **Python 3.10+**
- **SearXNG API**（搜索引擎，主备模式）
- **LibreTranslate API**（翻译服务）
- **Notion API**（数据同步）
- **systemd**（定时任务）

---

## 📁 项目结构

```
nero-market-research/
├── SKILL.md                    # 快速开始指南
├── README.md                   # 本文档
├── install.sh                  # 一键安装脚本
├── config.json.example         # 配置模板
├── scripts/                    # 核心脚本
│   ├── cycle_execution.py      # 24小时循环执行
│   ├── auto_pipeline.py        # 自动化管道
│   ├── data_quality_filter.py  # 数据质量过滤器
│   ├── demand_scorer_v2.py     # 需求评分器
│   ├── sync_to_notion.py       # Notion同步
│   └── generate_report.py      # 报告生成
├── config/                     # 配置文件
│   ├── reddit_mines.json       # Reddit矿区
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

## 📖 详细文档

- [安装指南](docs/SETUP_GUIDE.md) - 详细的安装步骤和依赖安装
- [配置说明](docs/CONFIGURATION.md) - 完整的配置参数和 Notion 设置
- [使用手册](docs/USAGE.md) - 详细的使用方法和最佳实践
- [API参考](docs/API_REFERENCE.md) - 开发者文档和接口说明
- [产品方案](../NERO_PRODUCT_SPEC.md) - 完整的产品方案文档

---

## 🔧 常用命令

```bash
# 系统控制
nero start          # 启动系统
nero stop           # 停止系统
nero restart        # 重启系统
nero status         # 查看状态

# 日志查看
nero logs           # 查看实时日志
nero logs-today     # 查看今日日志

# 手动执行
nero run            # 立即执行一次
nero sync           # 手动同步到Notion
nero report         # 生成今日报告

# 数据管理
nero cleanup        # 清理旧数据
nero stats          # 查看统计数据
```

---

## 🐛 故障排查

### Q: 系统没有数据？

**A**: 检查 SearXNG 连接状态

```bash
curl http://localhost:8080/search?q=test&format=json
```

如果失败，请检查 SearXNG 服务是否正常运行。

---

### Q: Notion 同步失败？

**A**: 检查 API Key 和 Database ID

1. 打开 [Notion Developers](https://www.notion.so/my-integrations)
2. 确认 Integration 有访问数据库的权限
3. 确认 Database ID 正确（从 URL 复制）

---

### Q: 翻译失败？

**A**: 检查 LibreTranslate 服务

```bash
curl -X POST https://translate.example.com/translate \
  -H "Content-Type: application/json" \
  -d '{"q":"test","source":"en","target":"zh"}'
```

如果失败，请检查服务地址和 Token。

---

### Q: 系统占用资源过高？

**A**: 调整执行频率

编辑 `config/execution.json`：

```json
{
  "execution_interval_hours": 2,  // 从1小时改为2小时
  "max_concurrent_miners": 1      // 限制并发数
}
```

---

## 🤝 贡献指南

欢迎贡献代码、报告问题、提出建议！

### 如何贡献

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发指南

- 使用 Python 3.10+
- 遵循 PEP 8 代码规范
- 添加单元测试
- 更新文档

---

## 📄 License

MIT License

Copyright (c) 2026 Pascal AI Team

详见 [LICENSE](LICENSE) 文件

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

## ⭐ Star History

如果这个项目对你有帮助，请给一个 ⭐ Star！

[![Star History Chart](https://api.star-history.com/svg?repos=your-username/nero-market-research&type=Date)](https://star-history.com/#your-username/nero-market-research&Date)

---

**让每一个产品灵感都来自真实痛点，而不是拍脑门。** 🚀
