---
name: prism-gen-demo
description: "English: Retrieve, filter, sort, merge, and visualize multiple CSV result files from PRISM-Gen molecular generation/screening. Provides portable query-based skills. No HPC connection required, directly analyze pre-calculated results.\n 中文: 对PRISM-Gen分子生成/筛选的多个CSV结果文件进行检索、过滤、排序、合并和可视化，提供可移植的查询型技能。无需HPC连接，直接分析预计算结果。"
---

# PRISM-Gen Demo Skill

**English**: PRISM-Gen pre-calculation result display demo: Provides retrieval, filtering, sorting, merging, and visualization of multiple CSV result files from molecular generation/screening, offering portable query-based skills.

**中文**: PRISM-Gen预计算结果展示Demo：对分子生成/筛选的多个CSV结果文件进行检索、过滤、排序、合并和可视化，提供可移植的查询型技能。

---

## English Section

### Overview
PRISM-Gen Demo is a portable skill for analyzing pre-calculated molecular screening results. It provides query-based data retrieval, filtering, sorting, merging, and visualization capabilities without requiring HPC connections or computational workflows.

### Design Goals
- **Portability**: Does not trigger HPC computation workflows, only processes existing CSV files
- **Stability**: Core functions work offline; Python dependencies optional for advanced visualization
- **Query-based**: Provides retrieval, filtering, sorting, and merging functions
- **Structured**: Returns results in a clear structured format
- **Visualization**: Provides data visualization and profile summarization (requires Python)

### Usage Scenarios
✅ **Use this skill when:**
- "Show PRISM Demo results"
- "Retrieve molecular data" / "Filter CSV results"
- "Sort molecules" / "Top N screening"
- "Merge multiple stage results" / "Profile summarization"
- "Visualization analysis" / "Chart display"
- "Export results" / "Format conversion"

### Core Function Architecture

#### 1. Data Source Management
- **List data sources**: Display all available CSV files
- **Source information**: Show file structure and statistics
- **Data preview**: Quick view of sample data

#### 2. Data Query
- **Conditional filtering**: Single or multi-column condition screening
- **Top N selection**: Sort by specified column to get best molecules
- **Range queries**: Support numerical ranges and string matching

#### 3. Data Analysis
- **Correlation analysis**: Calculate Pearson, Spearman correlation coefficients
- **Regression analysis**: Linear regression and trend lines
- **Distribution analysis**: Histograms, box plots, Q-Q plots

#### 4. Data Visualization
- **Distribution plots**: Univariate distribution visualization
- **Scatter plots**: Bivariate correlation analysis
- **Statistical charts**: Publication-quality statistical charts

#### 5. Data Export
- **CSV export**: Save filtered and sorted results
- **Chart export**: PNG, PDF, SVG formats
- **Report generation**: Structured analysis reports

### Supported CSV Files
- `step3a_optimized_molecules.csv` - Surrogate model optimized molecules
- `step3b_dft_results.csv` - xTB+DFT electronic screening results
- `step3c_dft_refined.csv` - GEM re-ranking results
- `step4a_admet_final.csv` - ADMET filtering results
- `step4b_top_molecules_pyscf.csv` - DFT validation (PySCF) results
- `step4c_master_summary.csv` - Master summary table
- `step5a_broadspectrum_docking.csv` - Broad-spectrum docking results
- `step5b_final_candidates.csv` - Final candidate molecules

### Key Molecular Properties
- **Identifiers**: smiles, molecule_id, name
- **Activity**: pIC50, reward, broad
- **Physicochemical properties**: LogP, MW, TPSA, HBD, HBA
- **Safety**: hERG_Prob, AMES, hepatotoxicity
- **Drug-likeness**: QED, SA, Lipinski
- **Electronic properties**: gap, energy, dipole
- **Docking results**: docking_score, binding_energy

### Quick Start Examples

#### Example 1: List Data Sources
```bash
bash scripts/demo_list_sources.sh
```

#### Example 2: Filter High-Activity Molecules
```bash
# Filter molecules with pIC50 > 7.0
bash scripts/demo_filter.sh step4a_admet_final.csv pIC50 '>' 7.0
```

#### Example 3: Get Top 10 Active Molecules
```bash
bash scripts/demo_top.sh step4a_admet_final.csv pIC50 10
```

#### Example 4: Generate Distribution Plot
```bash
bash scripts/demo_plot_distribution.sh step4a_admet_final.csv pIC50
```

#### Example 5: Correlation Analysis
```bash
bash scripts/demo_plot_scatter.sh step4a_admet_final.csv pIC50 QED --trendline --correlation
```

### Technical Requirements

#### Basic Functions (No Installation Required, Fully Offline)
- ✅ Bash shell environment
- ✅ Standard Unix tools (awk, sed, grep)
- ✅ File read/write permissions
- 🚫 **No network connection required**
- 🚫 **No Python installation required**

#### Advanced Functions (Requires Python, Works Offline After Installation)
- 🐍 Python 3.10+
- 📦 Core packages: pandas, numpy, matplotlib, seaborn
- 🔬 Scientific computing: scipy, scikit-learn (optional)
- ⚠️ **Network required for installation only**
- ✅ **Offline usage after installation**

#### Compatibility
- ✅ Linux / macOS / WSL2
- ✅ Local file system
- ✅ Basic functions: Fully offline
- ⚠️ Advanced functions: Network required for installation only

### Project Structure
```
prism-gen-demo/
├── README.md                    # This document
├── SKILL.md                     # OpenClaw skill definition
├── requirements.txt             # Python dependencies
├── data/                        # Pre-calculation result CSV files
├── scripts/                     # Core scripts
├── config/                      # Configuration files
├── examples/                    # Usage examples
├── docs/                        # Documentation
├── output/                      # Output directory
└── plots/                       # Chart output
```

---

## 中文部分

### 概述
PRISM-Gen Demo 是一个用于分析预计算分子筛选结果的可移植技能。它提供基于查询的数据检索、过滤、排序、合并和可视化功能，无需HPC连接或计算工作流。

### 设计目标
- **可移植性**: 不触发HPC计算流程，只处理既有CSV文件
- **稳定性**: 核心功能离线工作；Python依赖仅用于高级可视化（可选）
- **查询型**: 提供检索、过滤、排序、合并功能
- **结构化**: 以清晰的结构化方式返回结果
- **可视化**: 提供数据可视化和profile汇总（需要Python）

### 使用场景
✅ **使用此技能当：**
- "查看PRISM Demo结果" / "展示预计算结果"
- "检索分子数据" / "过滤CSV结果"
- "排序分子" / "Top N筛选"
- "合并多个阶段结果" / "Profile汇总"
- "可视化分析" / "图表展示"
- "导出结果" / "格式转换"

### 核心功能架构

#### 1. 数据源管理
- **列出数据源**: 显示所有可用CSV文件
- **数据源信息**: 显示文件结构和统计信息
- **数据预览**: 快速查看样本数据

#### 2. 数据查询
- **条件过滤**: 基于单列或多列条件筛选分子
- **Top N筛选**: 按指定列排序获取最佳分子
- **范围查询**: 支持数值范围和字符串匹配

#### 3. 数据分析
- **相关性分析**: 计算Pearson、Spearman相关系数
- **回归分析**: 线性回归和趋势线
- **分布分析**: 直方图、箱线图、Q-Q图

#### 4. 数据可视化
- **分布图**: 单变量分布可视化
- **散点图**: 双变量相关性分析
- **统计图表**: 论文质量的统计图表

#### 5. 数据导出
- **CSV导出**: 保存过滤和排序结果
- **图表导出**: PNG、PDF、SVG格式
- **报告生成**: 结构化分析报告

### 支持的CSV文件
- `step3a_optimized_molecules.csv` - 代理模型优化分子
- `step3b_dft_results.csv` - xTB+DFT电子筛选结果
- `step3c_dft_refined.csv` - GEM重排序结果
- `step4a_admet_final.csv` - ADMET过滤结果
- `step4b_top_molecules_pyscf.csv` - DFT验证(PySCF)结果
- `step4c_master_summary.csv` - 主汇总表
- `step5a_broadspectrum_docking.csv` - 广谱对接结果
- `step5b_final_candidates.csv` - 最终候选分子

### 关键分子属性
- **标识符**: smiles, molecule_id, name
- **活性**: pIC50, reward, broad
- **物化性质**: LogP, MW, TPSA, HBD, HBA
- **安全性**: hERG_Prob, AMES, hepatotoxicity
- **药物相似性**: QED, SA, Lipinski
- **电子性质**: gap, energy, dipole
- **对接结果**: docking_score, binding_energy

### 快速开始示例

#### 示例1：列出数据源
```bash
bash scripts/demo_list_sources.sh
```

#### 示例2：筛选高活性分子
```bash
# 筛选pIC50 > 7.0的分子
bash scripts/demo_filter.sh step4a_admet_final.csv pIC50 '>' 7.0
```

#### 示例3：获取Top 10活性分子
```bash
bash scripts/demo_top.sh step4a_admet_final.csv pIC50 10
```

#### 示例4：生成分布图
```bash
bash scripts/demo_plot_distribution.sh step4a_admet_final.csv pIC50
```

#### 示例5：相关性分析
```bash
bash scripts/demo_plot_scatter.sh step4a_admet_final.csv pIC50 QED --trendline --correlation
```

### 技术要求

#### 基础功能（无需安装，完全离线）
- ✅ Bash shell环境
- ✅ 标准Unix工具 (awk, sed, grep)
- ✅ 文件读写权限
- 🚫 **无需网络连接**
- 🚫 **无需Python安装**

#### 高级功能（需要Python，安装后离线工作）
- 🐍 Python 3.10+
- 📦 核心包: pandas, numpy, matplotlib, seaborn
- 🔬 科学计算包: scipy, scikit-learn (可选)
- ⚠️ **仅安装需要网络**
- ✅ **安装后可离线使用**

#### 兼容性
- ✅ Linux / macOS / WSL2
- ✅ 本地文件系统
- ✅ 基础功能：完全离线
- ⚠️ 高级功能：仅安装需要网络

### 项目结构
```
prism-gen-demo/
├── README.md                    # 本文档
├── SKILL.md                     # OpenClaw技能定义
├── requirements.txt             # Python依赖
├── data/                        # 预计算结果CSV文件
├── scripts/                     # 核心脚本
├── config/                      # 配置文件
├── examples/                    # 使用示例
├── docs/                        # 文档
├── output/                      # 输出目录
└── plots/                       # 图表输出
```

---

## License / 许可证
MIT License - See [LICENSE](LICENSE) file for details. / MIT许可证 - 详见[LICENSE](LICENSE)文件。

## Contact / 联系方式
For questions or suggestions, please refer to the documentation or contact the skill author. / 如有问题或建议，请参考文档或联系技能作者。

