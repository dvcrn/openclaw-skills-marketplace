---
name: serine-protease-fragment-analysis
description: "物种蛋白关键序列片段预测分析。对给定物种/类群的蛋白质FASTA序列执行完整分析流程，提取共识序列并识别其中的关键功能片段及其预期作用。适用于：（1）用户提到\"提取蛋白关键序列/片段\"、\"分析蛋白保守区\"、\"预测蛋白功能片段\"时，（2）对新物种/类群运行完整分析流程，（3）从已有FASTA序列提取共识序列并识别关键片段，（4）跨物种横向对比关键片段差异，（5）生成结构化分析报告。不限于丝氨酸蛋白酶，适用于任何蛋白质家族。"
---

# 蛋白质关键序列片段预测分析

## 核心文件

- **主分析脚本**：`scripts/serine_protease_analysis.py`（完整分析流程，可复用于任意蛋白家族）
- **批量运行入口**：`scripts/run_full_analysis.py`（多物种批量 + 大样本采样）
- **方法细节**：`references/method.md`
- **功能域参考**：`references/functional_domains.md`（含 S1 丝氨酸蛋白酶示例；分析其他蛋白家族时需补充对应功能域）

---

## 适用蛋白家族

本流程适用于**任何蛋白质家族**，不限于丝氨酸蛋白酶。分析其他蛋白时：
- **Step 1-3**（序列读取、MSA、共识序列提取）：完全通用，无需修改
- **Step 4 功能块匹配**：需在 `KNOWN_MOTIFS` 和 `CONSERVED_BLOCKS` 中补充目标蛋白家族的已知特征序列
- 推荐来源：Pfam / InterPro / UniProt 对应蛋白家族的保守域注释

---

## 快速运行

```bash
# 单物种分析
cd <工作目录>
python3 serine_protease_analysis.py <物种名> <fasta路径>

# 多物种批量分析（推荐）
# 1. 将各物种 .fasta 文件放入 input_clean/ 目录
# 2. 运行批量脚本
python3 run_full_analysis.py
```

---

## 分析流程

### Step 1：序列读取
- 解析标准 FASTA 格式
- 统计序列数量和长度分布
- **大样本处理**：序列数超过阈值时随机采样（见 `references/method.md`）

### Step 2：多序列比对（MSA）
- 工具：**ClustalOmega**（需预安装：`apt install clustalo` 或 `conda install clustalo`）
- 输出对齐后的 FASTA 文件
- 单序列物种跳过 MSA，直接使用原始序列

### Step 3：共识序列提取
- 各位点最高频氨基酸占比 ≥ 阈值（默认 0.5）则写入，否则标 X
- 去除 gap（`-`）后得到连续共识序列

### Step 4：关键片段识别（三维度并行）
1. **已知功能块匹配**：在共识序列中搜索 Pfam S1 家族特征序列（GDSG、GDSGGP 等）
2. **高保守连续区检测**：保守率 ≥ 90%、长度 ≥ 6aa 的连续区段
3. **保守 Cys 检测**：统计共识序列中 Cys 数量（潜在二硫键网络）

### Step 5：生成报告
- 每物种：`_分析报告.md`（可读报告）+ `_key_fragments.json`（结构化数据）
- 全物种：`汇总分析报告.md`

---

## 输出文件结构

```
<工作目录>/
├── 汇总分析报告.md
└── results/
    └── <物种名>/
        ├── <物种名>_input.fasta        # 参与 MSA 的序列
        ├── <物种名>_aligned.fasta      # MSA 结果
        ├── <物种名>_consensus.fasta    # 共识序列
        ├── <物种名>_key_fragments.json # 关键片段数据
        └── <物种名>_分析报告.md        # 可读报告
```

---

## 关键参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `THRESHOLD` | 0.5 | 共识序列保守性阈值（可在脚本顶部修改） |
| `MAX_SEQ` | 50 | 超过此数量时触发随机采样 |
| `SAMPLE_SIZE` | 50 | 采样序列数 |
| `MIN_LEN` | 6 | 高保守区最小长度（aa） |
| `HIGH_CONSERVATION` | 0.90 | 高保守区保守率阈值 |

---

## 命名规范

- 工作目录命名：`关键片段预测_YYYYMMDD`
- 物种文件名建议：`NN_<学名>_<中文名>.fasta`（NN 为两位编号，便于排序）
- 已完成物种自动跳过（检测到 `_分析报告.md` + `_key_fragments.json` 则跳过）

---

## 依赖环境

- Python 3.8+
- ClustalOmega（`clustalo --version` 验证）
- 无需额外 Python 包（仅使用标准库）

---

## 注意事项

- 详细方法说明见 `references/method.md`
- 已知功能域及保守块列表见 `references/functional_domains.md`
- 脚本修改参数时，同步更新 `serine_protease_analysis.py` 和 `run_full_analysis.py` 中的对应变量
