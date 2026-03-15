#!/usr/bin/env bash
# Cover Letter Generator — cover-letter skill
# Powered by BytesAgain | bytesagain.com | hello@bytesagain.com

CMD="$1"
shift 2>/dev/null
INPUT="$*"

case "$CMD" in
  write)
    cat << 'PROMPT'
你是资深HR顾问和求职信专家。为用户生成一封中文求职信。

结构：
1. 📌 称呼（尊敬的[公司]招聘负责人）
2. 🎯 开头Hook（1-2句话抓住注意力，与职位相关的亮点）
3. 💼 核心段落（2-3段）
   - 关键经历与职位匹配
   - 具体成就（用数字量化）
   - 对公司的了解和热情
4. 🤝 结尾（表达面试意愿+联系方式提示）
5. 此致敬礼

风格：专业但不死板，有温度。长度500-800字。

目标职位和公司：
PROMPT
    echo "$INPUT"
    ;;

  write-en)
    cat << 'PROMPT'
You are a senior career coach. Generate a professional English cover letter.

Structure:
1. Header (contact info placeholder)
2. Opening Hook (1-2 compelling sentences)
3. Body (2-3 paragraphs):
   - Key experience matching the role
   - Quantified achievements
   - Company knowledge and enthusiasm
4. Closing (interview request + availability)

Tone: Professional, confident, not generic. Length: 300-500 words.

Position and company:
PROMPT
    echo "$INPUT"
    ;;

  match)
    cat << 'PROMPT'
你是JD分析专家。分析这份JD（职位描述），提取：

1. 🔑 硬性要求（必须具备的技能/经验/学历）
2. 💎 加分项（优先考虑的条件）
3. 🎯 核心关键词（应该在求职信中出现的词）
4. 📊 匹配度评估表
   | 要求 | 重要程度 | 建议策略 |
5. ✍️ 求职信应该重点突出的3个方面
6. ⚠️ 需要规避/弱化的方面

用中文分析。

JD内容：
PROMPT
    echo "$INPUT"
    ;;

  review)
    cat << 'PROMPT'
你是资深HR，评审过10000+求职信。对这封求职信打分并给出修改建议。

评分维度（满分100）：
1. 开头吸引力 (20分) — 前两句是否让人想继续读
2. 经历匹配度 (25分) — 经历与职位的关联性
3. 量化成果 (20分) — 是否用数字证明能力
4. 真诚度 (15分) — 是否有个人特色，不是模板感
5. 格式规范 (10分) — 长度、结构、称呼
6. 行动号召 (10分) — 结尾是否有力

输出：
- 总分 + 等级 (S/A/B/C/D)
- 每个维度的得分和评语
- 3个具体修改建议（标注原文→修改后）
- 1个亮点表扬

用中文。

求职信内容：
PROMPT
    echo "$INPUT"
    ;;

  template)
    cat << 'PROMPT'
你是求职信模板专家。根据类型生成Markdown格式的求职信模板，可以直接保存为.md文件使用。

模板类型：
- 应届生 — 突出学习能力、实习、项目经历
- 社招 — 突出工作成就、行业经验
- 内推 — 提到推荐人、更亲切的语气
- 转行 — 强调可迁移技能、转行动机
- 外企 — 中英双语版本、国际化表达

输出完整Markdown模板，用 [方括号] 标注需要替换的部分。
在模板后附加使用说明。

请求的模板类型：
PROMPT
    echo "$INPUT"
    ;;

  batch)
    cat << 'PROMPT'
你是求职信创意总监。为同一个职位生成3封不同风格的求职信：

## 风格1: 正式专业版
- 传统结构，稳重可靠
- 适合：国企、银行、政府机构

## 风格2: 创意个性版
- 用故事开头，展现个性
- 适合：互联网、创意行业、初创公司

## 风格3: 简洁高效版
- 精炼到300字以内，直击要点
- 适合：投递量大时、简历已经很强时

每封都要：
- 完整可用（不是大纲）
- 有具体的示例内容
- 标注适用场景

用中文。

目标职位：
PROMPT
    echo "$INPUT"
    ;;

  *)
    cat << 'EOF'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📝 Cover Letter Generator — 使用指南
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  write [职位] [公司]     生成中文求职信
  write-en [pos] [co]    Generate English cover letter
  match [JD内容]         JD关键词分析+匹配建议
  review [求职信]         求职信评分(1-100)+修改建议
  template [类型]        模板库(应届/社招/内推/转行/外企)
  batch [职位]           批量生成3种风格求职信

  示例:
    write 产品经理 字节跳动
    write-en Software Engineer Google
    match 招聘Java开发工程师，3年经验...
    review 尊敬的HR，我对贵公司...
    template 应届生
    batch 前端开发工程师

  Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
EOF
    ;;
esac
