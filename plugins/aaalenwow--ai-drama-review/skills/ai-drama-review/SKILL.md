---
name: ai-drama-review
description: "AI短剧规范识别技能包。检测AI短剧中的文本/小说版权侵权、年龄分级合规性（18+/12+）、小说魔改程度，并生成结构化合规报告。支持本地关键词快速扫描 + AI深度分析两层架构。Beta 阶段 - 仅供参考，不作为法律依据。"
---

This skill identifies compliance risks in AI-generated short dramas, including copyright infringement, age rating violations, and unauthorized novel adaptations. It uses a two-layer architecture: local keyword scanning for fast baseline detection, plus AI-powered deep analysis for context-aware accuracy.

**Warning: BETA** — 本技能包正在测试中，检测结果仅供参考，不作为法律依据。请结合专业法律意见使用。

用户提供剧本文本、字幕文件或视频描述，本技能将执行合规审查并生成结构化风险报告。

---

## Phase 1: 环境检测与初始化

当用户请求对短剧内容进行合规审查时，先执行环境检测：

```bash
python3 scripts/env_detect.py
```

检测内容：
1. **Python 版本**: >= 3.8
2. **可用 API 密钥**: OPENAI_API_KEY / ANTHROPIC_API_KEY（用于深度分析）
3. **可选 Python 包**: jieba（中文分词，提升版权检测精度）
4. **网络连通性**: API 端点可达性

确定运行模式：
- **仅本地模式 (local_only)**: 无 API 密钥时的降级模式，仅执行关键词匹配和文本算法分析
- **混合模式 (hybrid)**（推荐）: 本地快速扫描 + AI 深度上下文分析，精度更高

向用户展示环境状态和可用功能。

---

## Phase 2: 版权侵权检测

接收用户提供的剧本/台词文本，执行版权侵权检测：

```bash
python3 scripts/text_similarity.py --input <script_file> --reference-dir <reference_texts_dir>
```

### 2.1 文本预处理

1. 统一编码（Unicode 归一化）
2. 去除标点符号和多余空白
3. 按段落分割，过滤过短段落（< 20 字）
4. 中文分词（优先使用 jieba，降级为字符级分词）

### 2.2 三重相似度检测

对每个段落与参考文本库逐段比对，计算三种互补指标：

| 算法 | 检测能力 | 权重 |
|------|----------|------|
| n-gram Jaccard 系数 | 局部词汇重复 | 0.3 |
| 归一化编辑距离 | 整体文本差异 | 0.3 |
| TF-IDF 余弦相似度 | 语义主题相似 | 0.4 |

综合得分超过阈值（默认 0.7）的段落标记为疑似侵权。

### 2.3 AI 语义确认（混合模式）

将高疑似段落发送 AI 进行语义级分析：
- 排除通用表达和公共领域内容
- 评估独创性和实质性相似
- 识别改写和同义替换

向用户展示：可疑段落列表、相似度分数、疑似来源、AI 分析意见。

---

## Phase 3: 年龄分级合规检测

扫描剧本内容的年龄分级合规性：

```bash
python3 scripts/age_rating_scanner.py --input <script_file> --target-rating <all_ages|12+|18+>
```

### 3.1 Layer 1: 本地关键词快速扫描

加载分类关键词库（暴力/色情/恐怖/脏话/烟酒毒品），逐段扫描：
- 记录命中的关键词、类别、严重度（mild/moderate/severe）
- 保留命中位置和上下文（前后 30 字）
- 根据命中密度和严重程度计算初步分级建议

### 3.2 Layer 2: AI 上下文深度分析（混合模式）

将关键词命中的上下文段落发送 AI 模型：
- 判断是否为真正的不当内容（排除否定语境、文学修辞、历史引用等误报）
- 评估上下文中的内容倾向
- 给出分级建议及具体理由

### 3.3 辅助内容分析

- **视频关键帧描述**: 如果用户提供了视频帧描述，分析画面内容风险
- **音频转录文本**: 如果用户提供了音频转录，扫描脏话和不当音效描述

### 3.4 分级输出

| 分级 | 说明 |
|------|------|
| 全年龄 (all_ages) | 内容适合所有年龄段 |
| 12+ | 含轻度暴力/冲突，需家长指导 |
| 18+ | 含较强暴力/恐怖/成人主题 |
| 不合规 (non_compliant) | 超出可接受范围，建议修改 |

---

## Phase 4: 小说魔改检测

比对原著与改编版本，评估改编偏离程度：

```bash
python3 scripts/adaptation_detector.py --original <original_file> --adapted <adapted_file>
```

### 4.1 结构对齐

使用动态规划算法（Needleman-Wunsch 变体）将原著章节与改编版段落对齐，识别：
- 保留的原始情节
- 新增的情节段
- 被删除的原著内容
- 被修改的段落

### 4.2 角色偏离检测

提取角色列表和设定，比对变化：
- 性格特征改动
- 角色关系改动
- 角色命运改动

### 4.3 关键情节比对

通过 AI 提取核心情节点，评估改编对原著核心的改动程度。

### 4.4 偏离度评分

综合输出偏离度评分（0-100）：

| 评分范围 | 分类 | 说明 |
|----------|------|------|
| 0 - 30 | 忠实改编 | 保留原著核心，合理调整 |
| 30 - 60 | 合理改编 | 有较大改动但未偏离核心 |
| 60 - 100 | 严重魔改 | 大幅偏离原著，可能引发争议 |

---

## Phase 5: 合规报告生成

汇总所有检测结果，生成结构化报告：

```bash
python3 scripts/report_generator.py --results <detection_results.json> --format <json|markdown>
```

报告内容：
- **总体风险等级**: 低 / 中 / 高 / 严重
- **版权侵权风险**: 疑似来源、相似段落、相似度分数
- **年龄分级合规**: 分级建议、各类别命中详情
- **小说魔改详情**: 偏离度评分、核心改动列表
- **违规位置标注**: 段落编号、时间戳、场景编号
- **整改建议清单**: 针对每项风险的具体修改建议

---

## Phase 6: 编排与完整审查

一键执行完整审查流程：

```bash
python3 scripts/review_orchestrator.py --input <script_file> [--reference-dir <dir>] [--original <file>] [--target-rating 12+] [--checks copyright rating adaptation]
```

流程：
1. 环境检测，确定运行模式
2. 加载输入文本（支持 .txt / .srt / .json 格式）
3. 执行选定的检测模块
4. AI 综合风险评估（混合模式）
5. 生成合规报告
6. 格式化风险提示文本，标注并告知用户违规风险

**风险提示格式**: 当检测到违规时，生成结构化的风险提示，供模型向用户展示具体的违规类型、位置和整改建议。

---

## 凭证安全

### 环境变量配置

**AI 分析（至少配置一个以启用混合模式）：**
- `OPENAI_API_KEY` — OpenAI API（用于深度内容分析）
- `ANTHROPIC_API_KEY` — Anthropic Claude API（备选）

**安全原则：**
- 所有凭证仅通过环境变量读取，零持久化
- 不记录、不打印、不缓存任何密钥值
- 无 API 密钥时自动降级为本地模式

---

## 免责声明

本技能包提供的合规检测结果仅供参考，不构成法律意见。使用者应结合专业法律顾问的意见做出最终判断。检测结果可能存在误报或漏报，建议对高风险内容进行人工复核。
