---
name: ncbi-search
description: "Search NCBI databases using E-Utilities API (official, free). Supports multiple databases: PubMed (literature), Gene, Protein, Nucleotide, dbSNP, ClinVar, Taxonomy, etc. Automatically detects search intent and routes to appropriate database. Returns formatted results with key information. Use for biomedical literature, gene information, protein sequences, genetic variants, and more."
---

# NCBI Search

NCBI 多数据库智能检索工具，使用官方 E-Utilities API。免费、可靠、无外部依赖。

## 支持的数据库

| 数据库 | 用途 | 触发关键词 |
|--------|------|-----------|
| **pubmed** | 文献检索 | paper, article, review, 研究, 论文, 文献, 发表 |
| **gene** | 基因信息 | gene, 基因, symbol, 编码 |
| **protein** | 蛋白质序列 | protein, 蛋白, amino acid, 序列 |
| **nucleotide** | 核酸序列 | sequence, DNA, RNA, 序列, 基因组 |
| **snp** | SNP变异 | SNP, variant, 变异, 多态性 |
| **clinvar** | 临床变异 | clinvar, clinical variant, 致病突变 |
| **taxonomy** | 物种分类 | species, 物种, taxonomy, 分类 |
| **biosample** | 生物样本 | biosample, 样本 |
| **assembly** | 基因组组装 | genome assembly, 基因组组装 |
| **sra** | 测序数据 | SRA, sequencing, 测序数据 |

## 智能意图识别

技能会自动判断用户搜索意图：

### 论文检索（PubMed）
触发条件：查询包含论文相关关键词，或没有明确数据库指向

```
"Alzheimer disease mechanisms" → PubMed
"recent review on diabetes" → PubMed
"Smith author cancer paper" → PubMed
```

### 基因检索
触发条件：基因符号、基因相关关键词

```
"APOE gene" → Gene
"BRCA1 function" → Gene
"TP53 human" → Gene
```

### 蛋白质检索
触发条件：蛋白质相关关键词

```
"insulin protein sequence" → Protein
"p53 protein" → Protein
```

### 变异检索
触发条件：变异相关关键词

```
"rs12345 SNP" → dbSNP
"BRCA1 pathogenic variant" → ClinVar
```

## 使用方式

### 自动模式（推荐）

```bash
# 自动判断搜索意图
python ~/.agents/skills/ncbi-search/scripts/ncbi_search.py "APOE gene"
python ~/.agents/skills/ncbi-search/scripts/ncbi_search.py "Alzheimer disease review"
python ~/.agents/skills/ncbi-search/scripts/ncbi_search.py "insulin protein"
```

### 指定数据库

```bash
# 明确指定数据库
python ~/.agents/skills/ncbi-search/scripts/ncbi_search.py "APOE" --db gene
python ~/.agents/skill/ncbi-search/scripts/ncbi_search.py "diabetes" --db pubmed
python ~/.agents/skills/ncbi-search/scripts/ncbi_search.py "rs429358" --db snp
```

### 高级选项

```bash
# PubMed 限定年份
python ~/.agents/skills/ncbi-search/scripts/ncbi_search.py "Alzheimer" --years 5

# 限定文章类型
python ~/.agents/skills/ncbi-search/scripts/ncbi_search.py "diabetes" --type review

# 限定物种（基因检索）
python ~/.agents/skills/ncbi-search/scripts/ncbi_search.py "APOE" --db gene --organism human
```

## 输出示例

### PubMed 检索

```
======================================================================
PubMed Search Results
======================================================================
Query: APOE[Title/Abstract] AND "Alzheimer Disease"[MeSH]
Total: 400 articles | Returned: 10 articles
======================================================================

[1] PMID: 33597265
Title: APOE immunotherapy reduces cerebral amyloid angiopathy...
Authors: Xiong M, Jiang H, Serrano J et al.
Journal: Science translational medicine (2021)
DOI: 10.1126/scitranslmed.abd7522
URL: https://pubmed.ncbi.nlm.nih.gov/33597265/
----------------------------------------------------------------------
```

### Gene 检索

```
======================================================================
Gene Search Results
======================================================================
Query: APOE[Gene Name] AND human[Organism]
Total: 1 gene | Returned: 1 gene
======================================================================

[1] Gene ID: 348
Symbol: APOE
Name: apolipoprotein E
Organism: Homo sapiens (human)
Chromosome: 19q13.32
Summary: Apolipoprotein E (APOE) is a protein involved in the...
URL: https://www.ncbi.nlm.nih.gov/gene/348
----------------------------------------------------------------------
```

### dbSNP 检索

```
======================================================================
dbSNP Search Results
======================================================================
Query: rs429358
Total: 1 variant | Returned: 1 variant
======================================================================

[1] rsID: rs429358
Gene: APOE
Alleles: C/T
Clinical: Pathogenic (Alzheimer disease)
Frequency: T=0.14 (EUR)
URL: https://www.ncbi.nlm.nih.gov/snp/rs429358
----------------------------------------------------------------------
```

## API Key 配置

```powershell
# 设置环境变量
[Environment]::SetEnvironmentVariable("NCBI_API_KEY", "your-api-key", "User")
```

| 方式 | 速率 |
|------|------|
| 无 API Key | 3 次/秒 |
| 有 API Key | 10 次/秒 |

## 与其他技能配合

| 任务 | 技能 |
|------|------|
| 基因详细信息 | `gene-database` |
| 蛋白质结构 | AlphaFold |
| 文献综述 | `literature-review` |
| 引用管理 | `citation-verifier` |

## 文件结构

```
ncbi-search/
├── SKILL.md
├── scripts/
│   ├── ncbi_search.py      # 主脚本（多数据库）
│   ├── pubmed_search.py    # PubMed专用
│   └── ncbi_utils.py       # 工具函数
└── references/
    └── query_syntax.md
```

## 参考

- E-Utilities 文档: https://www.ncbi.nlm.nih.gov/books/NBK25501/
- 数据库列表: https://www.ncbi.nlm.nih.gov/books/NBK25500/table/chapter.T5/

---

**技能状态**: 就绪
**API 要求**: NCBI API Key (免费)
**费用**: 免费