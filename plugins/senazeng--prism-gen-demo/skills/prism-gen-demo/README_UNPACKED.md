# PRISM-Gen Demo Skill - Unpacked Version

This is an unpacked PRISM-Gen Demo skill folder containing all necessary files.

## Folder Structure

```
prism-gen-demo-unpacked/
├── README.md                    # Main documentation
├── SKILL.md                     # OpenClaw skill definition
├── CHANGELOG.md                 # Change log
├── TUTORIAL.md                  # Tutorial document
├── LICENSE                      # License file
├── requirements.txt             # Python dependencies
├── setup.sh                     # Installation script
├── assets/                      # Resource files
├── config/                      # Configuration files
├── data/                        # Pre-calculation result CSV files
├── docs/                        # Documentation
├── examples/                    # Usage examples
├── output/                      # Output directory (empty)
├── plots/                       # Chart output directory (empty)
└── scripts/                     # Core scripts
```

## Included Data Files

1. **step3a_optimized_molecules.csv** - Surrogate model optimized molecules
2. **step3b_dft_results.csv** - xTB+DFT electronic screening results
3. **step3c_dft_refined.csv** - GEM re-ranking results
4. **step4a_admet_final.csv** - ADMET filtering results
5. **step4b_top_molecules_pyscf.csv** - DFT validation (PySCF) results
6. **step4c_master_summary.csv** - Master summary table
7. **step5a_broadspectrum_docking.csv** - Broad-spectrum docking results
8. **step5b_final_candidates.csv** - Final candidate molecules
9. **example_step4a.csv** - Example file
10. **step3a_optimized_molecules_raw.csv** - Raw optimized molecule data
11. **step3a_top200.csv** - Top 200 molecules

## Quick Start

### Basic Functions (No Installation Required)
```bash
# List data sources
bash scripts/demo_list_sources.sh

# Filter high-activity molecules (pIC50 > 7.0)
bash scripts/demo_filter.sh step4a_admet_final.csv pIC50 '>' 7.0

# Get Top 10 active molecules
bash scripts/demo_top.sh step4a_admet_final.csv pIC50 10
```

### Advanced Functions (Requires Python)
```bash
# Install dependencies
bash setup.sh

# Generate distribution plot
bash scripts/demo_plot_distribution.sh step4a_admet_final.csv pIC50

# Correlation analysis
bash scripts/demo_plot_scatter.sh step4a_admet_final.csv pIC50 QED --trendline --correlation
```

## Skill Information
- Version: 1.0.2
- Author: May
- Creation Date: 2026-03-09
- License: MIT

## Location
`/home/may/.openclaw/workspace/prism-gen-demo-unpacked/`

---

# PRISM-Gen Demo 技能 - 未打包版本

这是一个未打包的 PRISM-Gen Demo 技能文件夹，包含所有必要的文件。

## 文件夹结构

```
prism-gen-demo-unpacked/
├── README.md                    # 主说明文档
├── SKILL.md                     # OpenClaw 技能定义
├── CHANGELOG.md                 # 变更日志
├── TUTORIAL.md                  # 教程文档
├── LICENSE                      # 许可证文件
├── requirements.txt             # Python 依赖
├── setup.sh                     # 安装脚本
├── assets/                      # 资源文件
├── config/                      # 配置文件
├── data/                        # 预计算结果 CSV 文件
├── docs/                        # 文档
├── examples/                    # 使用示例
├── output/                      # 输出目录（空）
├── plots/                       # 图表输出目录（空）
└── scripts/                     # 核心脚本
```

## 包含的数据文件

1. **step3a_optimized_molecules.csv** - 代理模型优化分子
2. **step3b_dft_results.csv** - xTB+DFT 电子筛选结果
3. **step3c_dft_refined.csv** - GEM 重排序结果
4. **step4a_admet_final.csv** - ADMET 过滤结果
5. **step4b_top_molecules_pyscf.csv** - DFT 验证 (PySCF) 结果
6. **step4c_master_summary.csv** - 主汇总表
7. **step5a_broadspectrum_docking.csv** - 广谱对接结果
8. **step5b_final_candidates.csv** - 最终候选分子
9. **example_step4a.csv** - 示例文件
10. **step3a_optimized_molecules_raw.csv** - 原始优化分子数据
11. **step3a_top200.csv** - Top 200 分子

## 快速开始

### 基础功能（无需安装）
```bash
# 列出数据源
bash scripts/demo_list_sources.sh

# 筛选高活性分子 (pIC50 > 7.0)
bash scripts/demo_filter.sh step4a_admet_final.csv pIC50 '>' 7.0

# 获取 Top 10 活性分子
bash scripts/demo_top.sh step4a_admet_final.csv pIC50 10
```

### 高级功能（需要 Python）
```bash
# 安装依赖
bash setup.sh

# 生成分布图
bash scripts/demo_plot_distribution.sh step4a_admet_final.csv pIC50

# 相关性分析
bash scripts/demo_plot_scatter.sh step4a_admet_final.csv pIC50 QED --trendline --correlation
```

## 技能信息
- 版本: 1.0.2
- 作者: May
- 创建时间: 2026-03-09
- 许可证: MIT

## 位置
`/home/may/.openclaw/workspace/prism-gen-demo-unpacked/`