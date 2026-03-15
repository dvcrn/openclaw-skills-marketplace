# PRISM-Gen Demo - Drug Discovery Data Analysis Skill

![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-green)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

## 🎯 One-Sentence Introduction

**Analyze PRISM-Gen drug discovery pre-calculation results without HPC connection** - Provides a complete toolchain for retrieval, filtering, sorting, and visualization.

## 📊 Core Features

### 🔍 **Data Exploration**
- List all PRISM calculation result files
- View data structure and statistical information
- Quick preview of molecular data

### 🎯 **Intelligent Filtering**
- Conditional filtering (e.g., pIC50 > 7.0)
- Top N sorting (e.g., top 10 most active molecules)
- Multi-condition combined queries

### 📈 **Professional Visualization**
- Distribution plots (histogram + density curve)
- Scatter plots (with trend lines and statistical tests)
- Publication-quality chart output (300 DPI PNG)

### 📁 **Data Management**
- Automatically save filtered results
- Structured output directories
- Timestamp-marked file versions

## 🚀 5-Minute Quick Start

### 1. Install the Skill
```bash
# After installing from ClawHub, the skill will automatically appear in OpenClaw interface
# Or run in the skill directory:
cd ~/.openclaw/workspace/skills/prism-gen-demo
```

### 2. View Available Data
```bash
# List all PRISM calculation results
bash scripts/demo_list_sources.sh

# View example data information
bash scripts/demo_source_info_simple.sh example_step4a.csv
```

### 3. Basic Analysis
```bash
# Filter high-activity molecules (pIC50 > 7.6)
bash scripts/demo_filter.sh example_step4a.csv pIC50 '>' 7.6

# Get Top 5 active molecules
bash scripts/demo_top.sh example_step4a.csv pIC50 5
```

### 4. Advanced Analysis (Requires Python)
```bash
# Install dependencies (once)
pip install pandas numpy matplotlib seaborn scipy scikit-learn

# Generate distribution plot
bash scripts/demo_plot_distribution.sh example_step4a.csv pIC50

# Generate correlation scatter plot
bash scripts/demo_plot_scatter.sh example_step4a.csv pIC50 QED --trendline
```

## 🧪 Usage Scenarios

### 1. **Research Data Exploration**
```bash
# Quickly understand data overview
bash scripts/demo_list_sources.sh
bash scripts/demo_simple_preview.sh step4a_admet_final.csv
```

### 2. **Candidate Molecule Screening**
```bash
# Multi-round screening workflow
bash scripts/demo_filter.sh data.csv pIC50 '>' 7.0
bash scripts/demo_filter.sh filtered.csv hERG_Prob '<' 0.1
bash scripts/demo_top.sh filtered.csv QED 10
```

### 3. **Paper Chart Preparation**
```bash
# Generate publication-quality charts
bash scripts/demo_plot_distribution.sh data.csv pIC50 \
  --title "Activity Distribution" \
  --output "figure1.png" --dpi 300
```

### 4. **Teaching Demonstrations**
- Drug discovery data analysis process demonstration
- Practical examples of statistical methods
- Scientific data visualization teaching

## 📁 Output Structure

```
prism-gen-demo/
├── output/
│   ├── filtered/          # Filtered results (CSV)
│   └── top/              # Top N sorted results
├── plots/                # Generated charts (PNG)
└── logs/                 # Run logs (optional)
```

**All output files automatically include timestamps** for easy version management.

## ⚙️ Technical Requirements

### Basic Functions (No Installation Required, Fully Offline)
- ✅ Bash shell environment
- ✅ Standard Unix tools (awk, sed, grep)
- ✅ File read/write permissions
- 🚫 **No network connection required**
- 🚫 **No Python installation required**

### Advanced Functions (Requires Python, Works Offline After Installation)
- 🐍 Python 3.10+
- 📦 Core packages: pandas, numpy, matplotlib, seaborn
- 🔬 Scientific computing: scipy, scikit-learn (optional)
- ⚠️ **Network required for installation only**
- ✅ **Offline usage after installation**

### Compatibility
- ✅ Linux / macOS / WSL2
- ✅ Local file system
- ✅ Basic functions: Fully offline
- ⚠️ Advanced functions: Network required for installation only

## ❓ Frequently Asked Questions

### Q: Do I need to connect to HPC?
**A: No.** This skill only analyzes local CSV files and does not trigger any computation.

### Q: Is the data safe?
**A: Completely safe.** Read-only operations, original data is not modified, all outputs are saved in separate directories.

### Q: Do I need network connection?
**A: Basic functions don't need it.** Basic data query and analysis functions use Bash scripts and don't require network. Advanced visualization functions require Python packages (pandas, matplotlib, etc.), which need network connection for installation, but can work offline after one-time installation.

### Q: How to verify skill security?
**A: Provides verification mode**:
```bash
# Verify skill without installing dependencies
bash scripts/verify_skill.sh --dry-run
# View function descriptions of all scripts
bash scripts/list_scripts_info.sh
```

### Q: Does it support custom data?
**A: Yes.** Put CSV files in the `data/` directory and they will be automatically recognized.

### Q: Do I need programming experience?
**A: Basic functions don't require it.** Advanced visualization requires basic Python environment configuration.

### Q: How to get help?
**A: Check detailed tutorial**:
```bash
# View complete tutorial
cat TUTORIAL.md

# Run test to verify installation
bash scripts/test_fixed.sh
```

## 📚 Learning Resources

### Built-in Documentation
- `TUTORIAL.md` - Complete usage tutorial
- `SKILL.md` - OpenClaw skill definition
- `RELEASE_NOTES.md` - Version update notes
- `docs/DETAILED_README.md` - Detailed technical documentation (development version)

### Example Workflow
1. **Data Exploration** → `demo_list_sources.sh`
2. **Preliminary Screening** → `demo_filter.sh`
3. **Fine Sorting** → `demo_top.sh`
4. **Visualization** → `demo_plot_*.sh`
5. **Result Export** → Check `output/` and `plots/` directories

## 🆕 Changelog

### v1.0.0 (2026-03-06)
- ✅ Initial release: 6 core function modules
- ✅ Example data and real PRISM datasets
- ✅ Basic + advanced analysis modes
- ✅ Publication-quality chart output
- ✅ Complete documentation and examples

## 🤝 Support & Feedback

### Skill Issues
- Check troubleshooting section in `TUTORIAL.md`
- Check Python dependencies: `pip list | grep -E "(pandas|matplotlib)"`

### Feature Suggestions
This skill is open source and extensible, welcome to customize based on actual needs.

### Academic Collaboration
For customized data analysis workflows, please contact the skill author.

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

---

**Start your drug discovery data analysis journey now!** 🧬

*"Transform complex computational data into clear scientific insights"*

---

# PRISM-Gen Demo - 药物发现数据分析技能

## 🎯 一句话介绍

**无需HPC连接，直接分析PRISM-Gen药物发现预计算结果** - 提供检索、过滤、排序、可视化的完整工具链。

## 📊 核心功能

### 🔍 **数据探索**
- 列出所有PRISM计算结果文件
- 查看数据结构和统计信息
- 快速预览分子数据

### 🎯 **智能筛选**
- 条件过滤（如：pIC50 > 7.0）
- Top N排序（如：活性最高的10个分子）
- 多条件组合查询

### 📈 **专业可视化**
- 分布图（直方图 + 密度曲线）
- 散点图（含趋势线和统计检验）
- 论文级图表输出（300 DPI PNG）

### 📁 **数据管理**
- 自动保存筛选结果
- 结构化输出目录
- 时间戳标记文件版本

## 🚀 5分钟快速开始

### 1. 安装技能
```bash
# 从ClawHub安装后，技能会自动出现在OpenClaw界面
# 或在技能目录中运行：
cd ~/.openclaw/workspace/skills/prism-gen-demo
```

### 2. 查看可用数据
```bash
# 列出所有PRISM计算结果
bash scripts/demo_list_sources.sh

# 查看示例数据信息
bash scripts/demo_source_info_simple.sh example_step4a.csv
```

### 3. 基础分析
```bash
# 筛选高活性分子 (pIC50 > 7.6)
bash scripts/demo_filter.sh example_step4a.csv pIC50 '>' 7.6

# 获取Top 5活性分子
bash scripts/demo_top.sh example_step4a.csv pIC50 5
```

### 4. 高级分析（需要Python）
```bash
# 安装依赖（一次）
pip install pandas numpy matplotlib seaborn scipy scikit-learn

# 生成分布图
bash scripts/demo_plot_distribution.sh example_step4a.csv pIC50

# 生成相关性散点图
bash scripts/demo_plot_scatter.sh example_step4a.csv pIC50 QED --trendline
```

## 🧪 使用场景

### 1. **研究数据探索**
```bash
# 快速了解数据概况
bash scripts/demo_list_sources.sh
bash scripts/demo_simple_preview.sh step4a_admet_final.csv
```

### 2. **候选分子筛选**
```bash
# 多轮筛选工作流
bash scripts/demo_filter.sh data.csv pIC50 '>' 7.0
bash scripts/demo_filter.sh filtered.csv hERG_Prob '<' 0.1
bash scripts/demo_top.sh filtered.csv QED 10
```

### 3. **论文图表准备**
```bash
# 生成发表级图表
bash scripts/demo_plot_distribution.sh data.csv pIC50 \
  --title "Activity Distribution" \
  --output "figure1.png" --dpi 300
```

### 4. **教学演示**
- 药物发现数据分析流程展示
- 统计方法实际应用示例
- 科研数据可视化教学

## 📁 输出结构

```
prism-gen-demo/
├── output/
│   ├── filtered/          # 筛选结果（CSV）
│   └── top/              # Top N排序结果
├── plots/                # 生成的图表（PNG）
└── logs/                 # 运行日志（可选）
```

**所有输出文件自动包含时间戳**，便于版本管理。

## ⚙️ 技术要求

### 基础功能（无需安装，完全离线）
- ✅ Bash shell环境
- ✅ 标准Unix工具（awk, sed, grep）
- ✅ 文件读写权限
- 🚫 **无需网络连接**
- 🚫 **无需Python安装**

### 高级功能（需要Python，安装后离线）
- 🐍 Python 3.10+
- 📦 核心包：pandas, numpy, matplotlib, seaborn
- 🔬 科学计算包：scipy, scikit-learn（可选）
- ⚠️ **仅安装需要网络**
- ✅ **安装后可离线使用**

### 兼容性
- ✅ Linux / macOS / WSL2
- ✅ 本地文件系统
- ✅ 基础功能：完全离线
- ⚠️ 高级功能：仅安装需要网络

## ❓ 常见问题

### Q: 需要连接HPC吗？
**A: 不需要**。本技能只分析本地CSV文件，不触发任何计算。

### Q: 数据安全吗？
**A: 完全安全**。只读操作，不修改原始数据，所有输出保存在独立目录。

### Q: 需要网络连接吗？
**A: 基础功能不需要**。基础数据查询和分析功能使用Bash脚本，无需网络。高级可视化功能需要Python包（pandas, matplotlib等），这些包安装需要网络连接，但使用一次后即可离线工作。

### Q: 如何验证技能安全性？
**A: 提供验证模式**：
```bash
# 在不安装依赖的情况下验证技能
bash scripts/verify_skill.sh --dry-run
# 查看所有脚本的功能说明
bash scripts/list_scripts_info.sh
```

### Q: 支持自定义数据吗？
**A: 支持**。将CSV文件放入`data/`目录即可自动识别。

### Q: 需要编程经验吗？
**A: 基础功能不需要**。高级可视化需要基本的Python环境配置。

### Q: 如何获取帮助？
**A: 查看详细教程**：
```bash
# 查看完整教程
cat TUTORIAL.md

# 运行测试验证安装
bash scripts/test_fixed.sh
```

## 📚 学习资源

### 内置文档
- `TUTORIAL.md` - 完整使用教程
- `SKILL.md` - OpenClaw技能定义
- `RELEASE_NOTES.md` - 版本更新说明
- `docs/DETAILED_README.md` - 详细技术文档（开发版）

### 示例工作流
1. **数据探索** → `demo_list_sources.sh`
2. **初步筛选** → `demo_filter.sh`
3. **精细排序** → `demo_top.sh`
4. **可视化** → `demo_plot_*.sh`
5. **结果导出** → 查看`output/`和`plots/`目录

## 🆕 更新日志

### v1.0.0 (2026-03-06)
- ✅ 初始发布：6个核心功能模块
- ✅ 示例数据和真实PRISM数据集
- ✅ 基础+高级分析模式
- ✅ 论文级图表输出
- ✅ 完整文档和示例

## 🤝 支持与反馈

### 技能问题
- 查看`TUTORIAL.md`中的故障排除章节
- 检查Python依赖：`pip list | grep -E "(pandas|matplotlib)"`

### 功能建议
本技能开源可扩展，欢迎基于实际需求定制。

### 学术合作
如需定制化数据分析流程，请联系技能作者。

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件。

---

**立即开始你的药物发现数据分析之旅！** 🧬

*"将复杂的计算数据转化为清晰的科学洞察"*