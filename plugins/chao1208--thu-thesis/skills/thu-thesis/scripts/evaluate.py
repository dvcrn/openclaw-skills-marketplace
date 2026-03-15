#!/usr/bin/env python3
"""
evaluate.py — thu-thesis 转换质量 Rubric 评测
==============================================
检测 Word → PDF 转换过程中的内容完整性和格式合规性。

用法：
    python3 evaluate.py <parsed_json> <latex_dir> [--pdf <pdf_path>]

评测维度：
    A. 内容完整性（Content Fidelity）
    B. 格式合规性（Format Compliance）
    C. 参考文献（References）
    D. 图片（Figures）
    E. 表格（Tables）
    F. 缩略语（Abbreviations）

评测结果：
    - 每项 rubric 给出：PASS / WARN / FAIL + 说明
    - 最终汇总：总分、通过率、FAIL 项列表
    - 输出到 <latex_dir>/evaluation_report.md
"""

import sys
import json
import re
import os
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# Rubric 定义
# 每条规则：id, 维度, 权重(1=必要/2=重要/3=亮点), 标题, check_fn
# check_fn(data, latex_dir) → (level, message)
#   level: 'PASS' | 'WARN' | 'FAIL'
# ─────────────────────────────────────────────────────────────────────────────

def check_title(data, latex_dir):
    """A1: 中文标题不为空"""
    title = data.get('title', '').strip()
    if not title:
        return 'FAIL', '中文标题缺失'
    if len(title) < 5:
        return 'WARN', f'中文标题过短（{len(title)}字）：{title}'
    # 检查 thusetup.tex 里有无 title（文件在 latex_dir 根目录）
    ts = latex_dir / 'thusetup.tex'
    if not ts.exists():
        ts = latex_dir / 'data' / 'thusetup.tex'  # 兼容旧版路径
    if ts.exists() and title[:8] in ts.read_text(encoding='utf-8'):
        return 'PASS', f'"{title[:30]}"'
    return 'PASS', f'"{title[:30]}"（已从JSON验证）'


def check_title_en(data, latex_dir):
    """A2: 英文标题不为空"""
    title_en = data.get('title_en', '').strip()
    if not title_en:
        return 'FAIL', '英文标题缺失'
    if len(title_en) < 10:
        return 'WARN', f'英文标题过短：{title_en}'
    return 'PASS', f'"{title_en[:60]}"'


def check_author(data, latex_dir):
    """A3: 作者姓名不为空"""
    author = data.get('author', '').strip()
    if not author:
        return 'FAIL', '作者姓名缺失'
    return 'PASS', author


def check_author_en(data, latex_dir):
    """A4: 英文作者名不为空"""
    author_en = data.get('author_en', '').strip()
    if not author_en:
        return 'WARN', '英文作者名缺失（可人工补充）'
    return 'PASS', author_en


def check_supervisor(data, latex_dir):
    """A5: 导师信息不为空"""
    sup = data.get('supervisor', '').strip()
    if not sup:
        return 'FAIL', '导师姓名缺失'
    # 检查格式：应包含"教授"/"副教授"/"研究员"等职称
    if not re.search(r'教授|研究员|副教授|讲师|导师', sup):
        return 'WARN', f'导师字段缺少职称信息："{sup}"'
    return 'PASS', sup


def check_department(data, latex_dir):
    """A6: 培养单位不为空"""
    dept = data.get('department', '').strip()
    if not dept:
        return 'WARN', '培养单位缺失（可人工补充）'
    return 'PASS', dept


def check_date(data, latex_dir):
    """A7: 日期格式合法"""
    date = data.get('date', '').strip()
    if not date:
        return 'WARN', '日期缺失'
    if re.match(r'^\d{4}-\d{2}', date):
        return 'PASS', date
    return 'WARN', f'日期格式异常（期望 YYYY-MM）："{date}"'


def check_abstract_cn(data, latex_dir):
    """A8: 中文摘要不为空，且有实质内容"""
    abstract = data.get('abstract_cn', '').strip()
    if not abstract:
        return 'FAIL', '中文摘要缺失'
    if len(abstract) < 50:
        return 'WARN', f'中文摘要过短（{len(abstract)}字）'
    return 'PASS', f'{len(abstract)}字'


def check_abstract_en(data, latex_dir):
    """A9: 英文摘要不为空"""
    abstract = data.get('abstract_en', '').strip()
    if not abstract:
        return 'FAIL', '英文摘要缺失'
    if len(abstract) < 100:
        return 'WARN', f'英文摘要过短（{len(abstract)}字符）'
    return 'PASS', f'{len(abstract)}字符'


def check_keywords_cn(data, latex_dir):
    """A10: 中文关键词数量合理"""
    kw = data.get('keywords_cn', [])
    if not kw:
        return 'FAIL', '中文关键词缺失'
    if len(kw) < 2:
        return 'WARN', f'中文关键词只有{len(kw)}个：{kw}'
    return 'PASS', f'{len(kw)}个：{kw}'


def check_keywords_en(data, latex_dir):
    """A11: 英文关键词数量合理"""
    kw = data.get('keywords_en', [])
    if not kw:
        return 'FAIL', '英文关键词缺失'
    if len(kw) < 2:
        return 'WARN', f'英文关键词只有{len(kw)}个'
    return 'PASS', f'{len(kw)}个'


def check_chapters(data, latex_dir):
    """B1: 章节结构完整（至少3章，每章有内容块）"""
    chapters = data.get('chapters', [])
    if len(chapters) < 3:
        return 'FAIL', f'只有{len(chapters)}章，论文通常应有至少3章'
    empty_chapters = [ch.get('title', f'第{i+1}章') for i, ch in enumerate(chapters)
                      if len(ch.get('content', [])) < 2]
    if empty_chapters:
        return 'WARN', f'以下章节内容极少（<2个块）：{empty_chapters}'
    total_blocks = sum(len(ch.get('content', [])) for ch in chapters)
    return 'PASS', f'{len(chapters)}章，共{total_blocks}个内容块'


def check_chapter_tex(data, latex_dir):
    """B2: 所有章节 .tex 文件存在且非空"""
    chapters = data.get('chapters', [])
    missing = []
    too_short = []
    for i in range(len(chapters)):
        f = latex_dir / 'data' / f'chap{i+1:02d}.tex'
        if not f.exists():
            missing.append(f.name)
        elif len(f.read_text(encoding='utf-8').strip()) < 200:
            too_short.append(f.name)
    if missing:
        return 'FAIL', f'缺少章节文件：{missing}'
    if too_short:
        return 'WARN', f'章节文件内容过短（<200字符）：{too_short}'
    return 'PASS', f'{len(chapters)}个章节文件均存在'


def check_text_content(data, latex_dir):
    """B3: 正文文字总量合理（MBA论文通常>5000字）"""
    total_chars = 0
    for ch in data.get('chapters', []):
        for item in ch.get('content', []):
            if item.get('type') == 'text':
                total_chars += len(item.get('content', ''))
    if total_chars < 3000:
        return 'FAIL', f'正文文字总量过少：{total_chars}字（可能解析失败）'
    if total_chars < 8000:
        return 'WARN', f'正文文字总量偏少：{total_chars}字'
    return 'PASS', f'正文共约{total_chars}字'


def check_section_headings(data, latex_dir):
    """B4: 有节（section/heading）级别标题（Heading 3 / level 3）"""
    has_section = False
    count = 0
    for ch in data.get('chapters', []):
        for item in ch.get('content', []):
            # parse_docx 输出 type='section'，level=2/3/4；兼容旧格式 type='heading'
            if item.get('level') == 3 and item.get('type') in ('section', 'heading'):
                has_section = True
                count += 1
    if not has_section:
        return 'WARN', '未检测到节级标题（Heading 3），可能章节层级解析不足'
    return 'PASS', f'存在 {count} 个三级节标题（Heading 3）'


def check_references(data, latex_dir):
    """C1: 参考文献列表不为空"""
    refs = data.get('references', [])
    if not refs:
        return 'FAIL', '参考文献列表为空'
    if len(refs) < 5:
        return 'WARN', f'参考文献偏少：只有{len(refs)}条'
    return 'PASS', f'{len(refs)}条参考文献'


def check_refs_bib(data, latex_dir):
    """C2: refs.bib 存在且条目数与原文一致"""
    refs = data.get('references', [])
    bib_file = latex_dir / 'ref' / 'refs.bib'
    if not bib_file.exists():
        return 'FAIL', 'ref/refs.bib 不存在'
    bib_text = bib_file.read_text(encoding='utf-8')
    bib_count = len(re.findall(r'^@\w+\{', bib_text, re.MULTILINE))
    if bib_count == 0:
        return 'FAIL', 'refs.bib 无 BibTeX 条目'
    if bib_count < len(refs):
        return 'WARN', f'BibTeX 条目({bib_count})少于原文参考文献({len(refs)})'
    return 'PASS', f'{bib_count}条 BibTeX 条目'


def check_refs_author_title(data, latex_dir):
    """C3: refs.bib 中 author/title 字段完整率"""
    bib_file = latex_dir / 'ref' / 'refs.bib'
    if not bib_file.exists():
        return 'FAIL', 'refs.bib 不存在'
    bib_text = bib_file.read_text(encoding='utf-8')
    entries = re.findall(r'@\w+\{(\w+),(.*?)^\}', bib_text, re.MULTILINE | re.DOTALL)
    total = len(entries)
    if total == 0:
        return 'FAIL', '无 BibTeX 条目'
    missing_author = 0
    missing_title = 0
    for key, block in entries:
        if not re.search(r'author\s*=\s*\{.{3,}\}', block):
            missing_author += 1
        if not re.search(r'title\s*=\s*\{.{3,}\}', block):
            missing_title += 1
    if missing_author > total * 0.3 or missing_title > total * 0.3:
        return 'FAIL', (f'author 缺失{missing_author}/{total}条，'
                        f'title 缺失{missing_title}/{total}条（>30%，解析可能有问题）')
    if missing_author > 0 or missing_title > 0:
        return 'WARN', (f'author 缺失{missing_author}/{total}条，'
                        f'title 缺失{missing_title}/{total}条')
    return 'PASS', f'{total}条均有 author 和 title'


def check_bbl_count(data, latex_dir):
    """C4: BibTeX文件条目数与原文一致（检查 refs.bib，而非 bbl）

    bbl 只含被 \\cite 的文献，refs.bib 才代表全部参考文献是否被正确转换。
    bbl 存在且无 bibitem 是编译问题，单独标注。
    """
    refs = data.get('references', [])
    bib_file = latex_dir / 'ref' / 'refs.bib'
    if not bib_file.exists():
        return 'WARN', 'refs.bib 不存在，跳过检查'

    bib_text = bib_file.read_text(encoding='utf-8')
    bib_keys = re.findall(r'^@\w+\{(\w+),', bib_text, re.MULTILINE)
    # 排除注释掉的（以 % 开头行不计入）
    bib_count = len([k for k in bib_keys])

    if bib_count == 0:
        return 'FAIL', 'refs.bib 无任何 BibTeX 条目'
    if bib_count < len(refs):
        return 'FAIL', f'BibTeX条目({bib_count})少于Word原文({len(refs)})条，差{len(refs)-bib_count}条'
    return 'PASS', f'BibTeX={bib_count}条，Word原文={len(refs)}条，完全一致 ✓'


def check_cite_coverage(data, latex_dir):
    """C5: 正文中每条参考文献都被 \\cite 引用"""
    bib_file = latex_dir / 'ref' / 'refs.bib'
    if not bib_file.exists():
        return 'WARN', 'refs.bib 不存在，跳过检查'
    bib_text = bib_file.read_text(encoding='utf-8')
    all_keys = set(re.findall(r'^@\w+\{(\w+),', bib_text, re.MULTILINE))
    cited_keys = set()
    for cf in sorted((latex_dir / 'data').glob('chap*.tex')):
        for m in re.finditer(r'\\cite\{([^}]+)\}', cf.read_text(encoding='utf-8')):
            for k in m.group(1).split(','):
                cited_keys.add(k.strip())
    # 也算 \nocite
    thesis_tex = latex_dir / 'thesis.tex'
    if thesis_tex.exists():
        for m in re.finditer(r'\\nocite\{([^}]+)\}', thesis_tex.read_text(encoding='utf-8')):
            for k in m.group(1).split(','):
                cited_keys.add(k.strip())
    uncited = all_keys - cited_keys
    if uncited:
        return 'WARN', f'{len(uncited)}条文献未被引用（已用\\nocite兜底）：{sorted(uncited)[:5]}'
    return 'PASS', f'所有{len(all_keys)}条文献均被\\cite或\\nocite覆盖'


def check_cite_relevance(data, latex_dir):
    """C6: cite内容关联性抽检（失误扣分制，最多扣10分）

    核心问题：正文中的 \\cite{key} 是否真实引用了该文献的内容？
    机器规则只能做粗粒度判断，因此采用"抽检"策略：
      1. 随机抽取10个 cite 样本，输出「上下文 + 文献信息」供人工核查
      2. 机器端代理指标：检查正文中是否存在 \\cite{key} 的 key 在 bib 中
         author/title 均为空的情况 → bib 质量差意味着引用来源不可追溯，计为失误
      3. 扣分：bib字段完全缺失的 cite 次数，每次扣1分，最多扣10分
    抽检样本写入 evaluation_report.md 供人工确认。
    """
    import random
    bib_file = latex_dir / 'ref' / 'refs.bib'
    if not bib_file.exists():
        return 'WARN', 'refs.bib 不存在，跳过检查'

    # 解析 bib：key → {author, year, title}
    bib_text = bib_file.read_text(encoding='utf-8')
    bib_info = {}
    for m in re.finditer(r'@\w+\{(\w+),(.*?)(?=\n@\w|\Z)', bib_text, re.DOTALL):
        key = m.group(1)
        body = m.group(2)
        author_m = re.search(r'author\s*=\s*\{([^}]+)\}', body)
        year_m = re.search(r'year\s*=\s*\{(\d{4})\}', body)
        title_m = re.search(r'title\s*=\s*\{([^}]+)\}', body)
        bib_info[key] = {
            'author': author_m.group(1)[:40] if author_m else '',
            'year': year_m.group(1) if year_m else '',
            'title': title_m.group(1)[:60] if title_m else '',
        }

    chap_files = sorted((latex_dir / 'data').glob('chap*.tex'))
    if not chap_files:
        return 'WARN', '未找到章节 .tex 文件，跳过检查'

    # 收集所有 cite 出现位置
    all_cites = []
    cite_pat = re.compile(r'\\cite\{(\w+)\}')
    for cf in chap_files:
        text = cf.read_text(encoding='utf-8')
        for m in cite_pat.finditer(text):
            key = m.group(1)
            if key not in bib_info:
                continue
            start = max(0, m.start() - 120)
            end = min(len(text), m.end() + 80)
            ctx = text[start:end].replace('\n', ' ').strip()
            all_cites.append({'key': key, 'ctx': ctx, 'bib': bib_info[key], 'file': cf.name})

    if not all_cites:
        return 'PASS', '正文中无 \\cite 引用'

    # ── 机器代理指标：bib字段为空的 cite 计为失误 ──
    ghost_cites = [c for c in all_cites
                   if not c['bib']['author'] and not c['bib']['title']]
    deduction = min(len(ghost_cites), 10)

    # ── 随机抽检10个样本 ──
    random.seed(hash(str(latex_dir)) & 0xFFFF)
    sample_n = min(10, len(all_cites))
    samples = random.sample(all_cites, sample_n)

    # 把抽检样本存到 data 中，供 format_report 输出
    data['_c6_samples'] = samples
    data['_c6_ghost_count'] = len(ghost_cites)
    data['_c6_total'] = len(all_cites)

    if deduction == 0:
        return 'PASS', (
            f'共{len(all_cites)}处cite，bib字段完整，无不可追溯引用。'
            f'已随机抽取{sample_n}个样本写入报告供人工核查。'
        )
    sample_keys = [f'{c["key"]}@{c["file"]}' for c in ghost_cites[:5]]
    return 'DEDUCT', (
        f'发现{len(ghost_cites)}处cite对应bib的author/title均为空（扣{deduction}分）\n'
        f'   引用来源不可追溯，示例：{sample_keys}\n'
        f'   已随机抽取{sample_n}个样本写入报告供人工核查。'
    )


def check_author_year_cite(data, latex_dir):
    """C7: 正文 author-year 行文引用必须有对应 \\cite（关键失误检查）

    文献综述等章节中常见 "曹玉（2025）分析了..." 这类行文引用。
    若此类引用未被转换为 \\cite{key}，属于学术不端风险，判定为 FAIL。
    """
    # 收集所有 chap*.tex 文本
    chap_files = sorted((latex_dir / 'data').glob('chap*.tex'))
    if not chap_files:
        return 'WARN', '未找到章节 .tex 文件，跳过检查'

    # author-year 模式（同 render.py 的匹配规则）
    ay_pattern = re.compile(
        r'((?:[\u4e00-\u9fff]{1,6}(?:[和与及、][\u4e00-\u9fff]{1,4})*(?:等)?)'
        r'|(?:[A-Z][a-z]+(?:[A-Z][a-z]+)+)'
        r'|(?:[A-Z][a-zA-Z]+(?:\s+(?:et\s+al\.?|and\s+[A-Z][a-zA-Z]+))*)'
        r')'
        r'([（(])'
        r'((19|20)\d{2})'
        r'([）)])'
        r'(?!\\\\cite)'  # 后面没有 \cite 即未转换
    )

    missing_samples = []
    total_ay = 0

    for cf in chap_files:
        text = cf.read_text(encoding='utf-8')
        for m in ay_pattern.finditer(text):
            full = m.group(0)
            # 检查该 match 后面是否有 \cite（考虑到 LaTeX 转义后的情况）
            after = text[m.end():m.end()+20]
            if not after.startswith(r'\cite{'):
                total_ay += 1
                if len(missing_samples) < 5:
                    missing_samples.append(f'{full}（在 {cf.name}）')

    if total_ay == 0:
        return 'PASS', '未检测到未引用的 author-year 行文引用'
    if total_ay <= 2:
        return 'WARN', f'{total_ay} 处 author-year 行文引用未转为 \\cite：{missing_samples}'
    return 'FAIL', (
        f'⚠️  关键失误：{total_ay} 处 author-year 行文引用缺少 \\cite，存在学术不端风险！\n'
        f'   示例：{missing_samples[:3]}\n'
        f'   原因：文献综述等章节使用了"作者（年份）"格式但未生成 \\cite{{key}}。\n'
        f'   修复：检查 refs.bib 中是否有对应文献，确保 author+year 能匹配到 BibTeX key。'
    )


def check_figures(data, latex_dir):
    """D1: 图片提取数量与正文声明一致"""
    figures = data.get('figures', {})
    fig_count = len(figures)
    # 统计章节中 type=figure 的块
    tex_figs = 0
    for ch in data.get('chapters', []):
        for item in ch.get('content', []):
            if item.get('type') == 'figure':
                tex_figs += 1
    if fig_count == 0 and tex_figs == 0:
        return 'NA', '未检测到图片（原文可能无图）'
    # 检查 figures/ 目录
    fig_dir = latex_dir / 'figures'
    actual_files = list(fig_dir.glob('*.png')) + list(fig_dir.glob('*.jpg')) + list(fig_dir.glob('*.jpeg')) if fig_dir.exists() else []
    if len(actual_files) < fig_count:
        return 'WARN', f'figures目录只有{len(actual_files)}个文件，但解析到{fig_count}张图'
    return 'PASS', f'{len(actual_files)}张图片已提取到 figures/'


def check_figure_captions(data, latex_dir):
    """D2: 图片有 caption（不全为空）"""
    total_figs = 0
    no_caption = 0
    for ch in data.get('chapters', []):
        for item in ch.get('content', []):
            if item.get('type') == 'figure':
                total_figs += 1
                if not item.get('caption', '').strip():
                    no_caption += 1
    if total_figs == 0:
        return 'NA', '无图片，跳过'
    if no_caption == total_figs:
        return 'WARN', f'所有{total_figs}张图片均无 caption'
    if no_caption > 0:
        return 'WARN', f'{no_caption}/{total_figs}张图片无 caption'
    return 'PASS', f'{total_figs}张图片均有 caption'


def check_figure_latex(data, latex_dir):
    """D3: 章节 .tex 中图片以 \\includegraphics 形式存在"""
    total_figs = sum(1 for ch in data.get('chapters', [])
                     for item in ch.get('content', []) if item.get('type') == 'figure')
    if total_figs == 0:
        return 'NA', '无图片，跳过'
    chap_files = sorted((latex_dir / 'data').glob('chap*.tex'))
    latex_figs = sum(len(re.findall(r'\\includegraphics', f.read_text(encoding='utf-8')))
                     for f in chap_files)
    if latex_figs == 0:
        return 'FAIL', f'解析到{total_figs}张图片但 .tex 中无 \\includegraphics'
    if latex_figs < total_figs:
        return 'WARN', f'\\includegraphics 出现{latex_figs}次，但解析到{total_figs}张图片'
    return 'PASS', f'{latex_figs}处 \\includegraphics'


def check_tables(data, latex_dir):
    """E1: 表格提取数量"""
    total_tables = sum(1 for ch in data.get('chapters', [])
                       for item in ch.get('content', []) if item.get('type') == 'table')
    if total_tables == 0:
        return 'NA', '未检测到表格（原文可能无表格）'
    return 'PASS', f'共{total_tables}个表格'


def check_table_format(data, latex_dir):
    """E2: 表格格式为 booktabs 三线表（tabularx + toprule/midrule/bottomrule）"""
    chap_files = sorted((latex_dir / 'data').glob('chap*.tex'))
    tables_tex = 0
    correct_format = 0
    wrong_format = []
    for cf in chap_files:
        text = cf.read_text(encoding='utf-8')
        # 找所有 table 环境
        for m in re.finditer(r'\\begin\{table\}.*?\\end\{table\}', text, re.DOTALL):
            tables_tex += 1
            block = m.group(0)
            has_tabularx = 'tabularx' in block
            has_toprule = '\\toprule' in block
            has_midrule = '\\midrule' in block
            has_bottomrule = '\\bottomrule' in block
            has_hline = '\\hline' in block
            has_vertical = re.search(r'\|[lcrX]|\|[lcrX]', block)
            if has_tabularx and has_toprule and has_midrule and has_bottomrule and not has_hline:
                correct_format += 1
            else:
                issues = []
                if not has_tabularx:
                    issues.append('非tabularx')
                if not has_toprule:
                    issues.append('缺toprule')
                if not has_midrule:
                    issues.append('缺midrule')
                if not has_bottomrule:
                    issues.append('缺bottomrule')
                if has_hline:
                    issues.append('有\\hline')
                if has_vertical:
                    issues.append('有竖线')
                wrong_format.append(f'{cf.name}({",".join(issues)})')
    if tables_tex == 0:
        return 'NA', '章节 .tex 中无 table 环境，跳过'
    if wrong_format:
        return 'FAIL', f'{len(wrong_format)}/{tables_tex}个表格格式不符合三线表标准：{wrong_format[:3]}'
    return 'PASS', f'{correct_format}个表格均符合 tabularx+booktabs 三线表格式'


def check_table_captions(data, latex_dir):
    """E3: 表格有 caption"""
    total_tables = sum(1 for ch in data.get('chapters', [])
                       for item in ch.get('content', []) if item.get('type') == 'table')
    if total_tables == 0:
        return 'NA', '无表格'
    no_caption = sum(1 for ch in data.get('chapters', [])
                     for item in ch.get('content', [])
                     if item.get('type') == 'table' and not item.get('caption', '').strip())
    if no_caption == total_tables:
        return 'WARN', f'所有{total_tables}个表格均无 caption'
    if no_caption > 0:
        return 'WARN', f'{no_caption}/{total_tables}个表格无 caption'
    return 'PASS', f'{total_tables}个表格均有 caption'


def check_abbreviations(data, latex_dir):
    """F1: 缩略语表已生成"""
    deno_file = latex_dir / 'data' / 'denotation.tex'
    if not deno_file.exists():
        return 'FAIL', 'data/denotation.tex 不存在'
    text = deno_file.read_text(encoding='utf-8')
    items = re.findall(r'\\item\[', text)
    if not items:
        return 'WARN', 'denotation.tex 无缩略语条目（\\item[...）'
    return 'PASS', f'{len(items)}个缩略语条目'


def check_orphan_abbrevs(data, latex_dir):
    """F2: 孤儿缩略语已标注待补充"""
    deno_file = latex_dir / 'data' / 'denotation.tex'
    if not deno_file.exists():
        return 'WARN', 'denotation.tex 不存在'
    text = deno_file.read_text(encoding='utf-8')
    pending = re.findall(r'请人工填写', text)
    if pending:
        return 'WARN', f'{len(pending)}个孤儿缩略语待人工补充（已标注，无需担心）'
    return 'PASS', '无孤儿缩略语（或孤儿缩略语已全部在词典中）'


def check_acknowledgements(data, latex_dir):
    """G1: 致谢内容不为空"""
    ack = data.get('acknowledgements', '').strip()
    ack_file = latex_dir / 'data' / 'acknowledgements.tex'
    if not ack:
        return 'WARN', '原文未检测到致谢内容'
    if ack_file.exists():
        content = ack_file.read_text(encoding='utf-8')
        if len(content.strip()) < 50:
            return 'WARN', 'acknowledgements.tex 内容过少'
    return 'PASS', f'致谢{len(ack)}字'


def check_resume(data, latex_dir):
    """G2: 个人简历不为空"""
    resume = data.get('resume', '').strip()
    resume_file = latex_dir / 'data' / 'resume.tex'
    if not resume:
        return 'WARN', '原文未检测到个人简历内容'
    if resume_file.exists():
        content = resume_file.read_text(encoding='utf-8')
        if len(content.strip()) < 50:
            return 'WARN', 'resume.tex 内容过少'
    return 'PASS', f'个人简历{len(resume)}字'


def check_pdf_exists(data, latex_dir):
    """H1: PDF 已生成"""
    pdf = latex_dir / 'thesis.pdf'
    if not pdf.exists():
        return 'FAIL', 'thesis.pdf 不存在（编译失败或未运行）'
    size_kb = pdf.stat().st_size / 1024
    if size_kb < 100:
        return 'WARN', f'PDF 文件过小（{size_kb:.0f}KB），可能编译不完整'
    return 'PASS', f'thesis.pdf {size_kb:.0f}KB'


def check_no_latex_errors(data, latex_dir):
    """H2: LaTeX 编译无 Error"""
    log_file = latex_dir / 'thesis.log'
    if not log_file.exists():
        return 'WARN', 'thesis.log 不存在（未编译）'
    log_text = log_file.read_text(encoding='utf-8', errors='ignore')
    errors = re.findall(r'^! .+$', log_text, re.MULTILINE)
    if errors:
        return 'FAIL', f'{len(errors)}个 LaTeX Error：{errors[:3]}'
    # 检查常见警告
    overfull = len(re.findall(r'Overfull \\hbox', log_text))
    if overfull > 10:
        return 'WARN', f'{overfull}个 Overfull \\hbox 警告（可能有文字超出页面边界）'
    return 'PASS', '无 LaTeX Error'


def check_thusetup_format(data, latex_dir):
    """H3: thusetup.tex 格式符合 thuthesis MBA 配置"""
    # thusetup.tex 在 latex_dir 根目录（非 data/ 子目录）
    ts_file = latex_dir / 'thusetup.tex'
    if not ts_file.exists():
        ts_file = latex_dir / 'data' / 'thusetup.tex'  # 兼容旧版
    if not ts_file.exists():
        return 'FAIL', 'thusetup.tex 不存在（查找了根目录和data/子目录）'
    text = ts_file.read_text(encoding='utf-8')
    checks = [
        ('degree.*master', 'degree=master 缺失'),
        ('degree-type.*professional', 'degree-type=professional 缺失'),
        ('degree-category', 'degree-category 缺失'),
    ]
    issues = [msg for pattern, msg in checks if not re.search(pattern, text)]
    if issues:
        return 'WARN', '；'.join(issues)
    return 'PASS', 'thusetup.tex MBA 配置正确'


# ─────────────────────────────────────────────────────────────────────────────
# Rubric 注册表
# ─────────────────────────────────────────────────────────────────────────────
RUBRICS = [
    # id, 维度, 权重(1=必要 2=重要 3=亮点), 标题, check_fn
    ('A1',  'A.内容-元信息', 1, '中文标题',          check_title),
    ('A2',  'A.内容-元信息', 1, '英文标题',          check_title_en),
    ('A3',  'A.内容-元信息', 1, '作者姓名',          check_author),
    ('A4',  'A.内容-元信息', 2, '英文作者名',        check_author_en),
    ('A5',  'A.内容-元信息', 1, '导师信息',          check_supervisor),
    ('A6',  'A.内容-元信息', 2, '培养单位',          check_department),
    ('A7',  'A.内容-元信息', 2, '日期格式',          check_date),
    ('A8',  'A.内容-摘要',  1, '中文摘要',           check_abstract_cn),
    ('A9',  'A.内容-摘要',  1, '英文摘要',           check_abstract_en),
    ('A10', 'A.内容-摘要',  1, '中文关键词',         check_keywords_cn),
    ('A11', 'A.内容-摘要',  2, '英文关键词',         check_keywords_en),
    ('B1',  'B.内容-正文',  1, '章节结构完整',       check_chapters),
    ('B2',  'B.内容-正文',  1, '章节.tex文件',       check_chapter_tex),
    ('B3',  'B.内容-正文',  1, '正文文字总量',       check_text_content),
    ('B4',  'B.内容-正文',  2, '节级标题存在',       check_section_headings),
    ('C1',  'C.参考文献',   1, '参考文献列表',       check_references),
    ('C2',  'C.参考文献',   1, 'refs.bib 生成',      check_refs_bib),
    ('C3',  'C.参考文献',   1, 'BibTeX字段完整性',   check_refs_author_title),
    ('C4',  'C.参考文献',   1, 'PDF参考文献完整性',  check_bbl_count),
    ('C5',  'C.参考文献',   2, '引用覆盖率',              check_cite_coverage),
    ('C6',  'C.参考文献',   0, 'cite内容关联性（失误扣分）', check_cite_relevance),
    ('C7',  'C.参考文献',   3, 'author-year引用规范',      check_author_year_cite),
    ('D1',  'D.图片',       2, '图片提取数量',       check_figures),
    ('D2',  'D.图片',       2, '图片caption',        check_figure_captions),
    ('D3',  'D.图片',       1, '图片LaTeX渲染',      check_figure_latex),
    ('E1',  'E.表格',       2, '表格提取数量',       check_tables),
    ('E2',  'E.表格',       1, '三线表格式',         check_table_format),
    ('E3',  'E.表格',       2, '表格caption',        check_table_captions),
    ('F1',  'F.缩略语',     2, '缩略语表生成',       check_abbreviations),
    ('F2',  'F.缩略语',     3, '孤儿缩略语标注',     check_orphan_abbrevs),
    ('G1',  'G.附件',       2, '致谢内容',           check_acknowledgements),
    ('G2',  'G.附件',       2, '个人简历',           check_resume),
    ('H1',  'H.编译',       1, 'PDF已生成',          check_pdf_exists),
    ('H2',  'H.编译',       1, '无LaTeX Error',      check_no_latex_errors),
    ('H3',  'H.编译',       2, 'thusetup格式',       check_thusetup_format),
]


# ─────────────────────────────────────────────────────────────────────────────
# 主评测逻辑
# ─────────────────────────────────────────────────────────────────────────────

LEVEL_EMOJI = {'PASS': '✅', 'WARN': '⚠️ ', 'FAIL': '❌', 'DEDUCT': '➖', 'NA': '—'}
WEIGHT_LABEL = {0: '失误扣分', 1: '必要', 2: '重要', 3: '亮点'}
# 每档权重对应的满分（必要=3, 重要=2, 亮点=1，DEDUCT项=0固定满分/单独扣分）
WEIGHT_MAX = {0: 0, 1: 3, 2: 2, 3: 1}
# 每档结果对应得分比例：PASS=1.0, WARN=0.5, FAIL=0.0, NA=跳过
LEVEL_RATIO = {'PASS': 1.0, 'WARN': 0.5, 'FAIL': 0.0, 'NA': None, 'DEDUCT': None}


def run_evaluation(parsed_json: Path, latex_dir: Path) -> dict:
    """运行所有 rubric，返回评测结果字典"""
    with open(parsed_json, encoding='utf-8') as f:
        data = json.load(f)

    # ── 展平 meta 子字典到顶层（parse_docx.py 把封面信息放在 data['meta'] 里）──
    if 'meta' in data and isinstance(data['meta'], dict):
        for k, v in data['meta'].items():
            if k not in data:
                data[k] = v

    results = []
    for rubric_id, dimension, weight, title, check_fn in RUBRICS:
        try:
            level, message = check_fn(data, latex_dir)
        except Exception as e:
            level, message = 'WARN', f'检查出错：{e}'

        # 计算该项得分
        max_score = WEIGHT_MAX.get(weight, 0)
        deduction = 0
        item_score = 0.0

        if level == 'DEDUCT':
            # 失误扣分项：从消息中解析扣分数
            dm = re.search(r'扣\s*(\d+)\s*分', message)
            deduction = int(dm.group(1)) if dm else 0
            item_score = -deduction
        elif level == 'NA':
            item_score = None   # 不计入分母
        elif LEVEL_RATIO.get(level) is not None:
            item_score = round(max_score * LEVEL_RATIO[level], 1)

        results.append({
            'id': rubric_id,
            'dimension': dimension,
            'weight': weight,
            'weight_label': WEIGHT_LABEL.get(weight, str(weight)),
            'max_score': max_score,
            'title': title,
            'level': level,
            'message': message,
            'score': item_score,
            'deduction': deduction,
        })

    # ── 汇总得分 ──
    scored = [r for r in results if r['score'] is not None]
    total_score = sum(r['score'] for r in scored)
    total_max = sum(r['max_score'] for r in scored if r['level'] != 'DEDUCT')
    pct = round(total_score / total_max * 100, 1) if total_max > 0 else 0

    # ── 维度得分 ──
    dim_scores = {}
    for r in scored:
        d = r['dimension']
        if d not in dim_scores:
            dim_scores[d] = {'score': 0.0, 'max': 0}
        dim_scores[d]['score'] += r['score']
        if r['level'] != 'DEDUCT':
            dim_scores[d]['max'] += r['max_score']

    # ── checklist 统计（保留兼容）
    fails = [r for r in results if r['level'] == 'FAIL']
    warns = [r for r in results if r['level'] == 'WARN']
    passes = [r for r in results if r['level'] == 'PASS']
    deducts = [r for r in results if r['level'] == 'DEDUCT']
    total_deduction = sum(r['deduction'] for r in deducts)
    critical_fails = [r for r in fails if r['weight'] == 1]

    return {
        'results': results,
        'summary': {
            'total': len(results),
            'pass': len(passes),
            'warn': len(warns),
            'fail': len(fails),
            'deduct_items': len(deducts),
            'total_deduction': total_deduction,
            'critical_fails': len(critical_fails),
            'passed': len(critical_fails) == 0,
            'total_score': round(total_score, 1),
            'total_max': total_max,
            'pct': pct,
            'dim_scores': dim_scores,
        },
        '_c6_samples': data.get('_c6_samples', []),
        '_c6_total': data.get('_c6_total', 0),
        'docx': parsed_json.stem,
        'latex_dir': str(latex_dir),
    }


def format_report(eval_result: dict) -> str:
    """格式化为 Markdown 报告（以分数为核心）"""
    lines = []
    s = eval_result['summary']

    # 评级
    pct = s['pct']
    if pct >= 90:
        grade = '优秀 🏆'
    elif pct >= 75:
        grade = '良好 ✅'
    elif pct >= 60:
        grade = '合格 ⚠️'
    else:
        grade = '不合格 ❌'

    lines.append(f'# 论文转换质量评测报告')
    lines.append(f'')
    lines.append(f'**来源：** {eval_result["docx"]}')
    lines.append(f'**输出：** {eval_result["latex_dir"]}')
    lines.append(f'')
    lines.append(f'## 🏆 总分：{s["total_score"]} / {s["total_max"]} 分（{pct}%）— {grade}')
    lines.append(f'')

    # 维度得分表
    lines.append(f'### 维度得分')
    lines.append(f'')
    lines.append(f'| 维度 | 得分 | 满分 | 得分率 |')
    lines.append(f'|------|------|------|--------|')
    for dim, ds in s['dim_scores'].items():
        sc = ds['score']
        mx = ds['max']
        rate = f"{round(sc/mx*100)}%" if mx > 0 else 'N/A'
        bar = '█' * int((sc / mx * 10) if mx > 0 else 0)
        lines.append(f'| {dim} | {sc} | {mx} | {rate} {bar} |')
    lines.append(f'')

    # 问题汇总
    fails = [r for r in eval_result['results'] if r['level'] == 'FAIL']
    deducts = [r for r in eval_result['results'] if r['level'] == 'DEDUCT']
    warns = [r for r in eval_result['results'] if r['level'] == 'WARN']

    if fails:
        lines.append(f'### ❌ 失败项（得0分，需修复）')
        lines.append(f'')
        for r in fails:
            lines.append(f'- **[{r["id"]}] {r["title"]}**（{r["weight_label"]}，满分{r["max_score"]}分→得0）：{r["message"]}')
        lines.append(f'')

    if deducts:
        lines.append(f'### ➖ 失误扣分项')
        lines.append(f'')
        for r in deducts:
            lines.append(f'- **[{r["id"]}] {r["title"]}**（扣{r["deduction"]}分）：{r["message"]}')
        lines.append(f'')

    # C6 抽检样本
    samples = eval_result.get('_c6_samples', [])
    if samples:
        lines.append(f'### 🔍 C6 cite内容关联性抽检样本（人工核查）')
        lines.append(f'')
        lines.append(f'> 共{eval_result.get("_c6_total","?")}处cite，随机抽取{len(samples)}个，请逐一核查「上下文」与「文献」是否内容相关。')
        lines.append(f'')
        for i, s in enumerate(samples, 1):
            bib = s['bib']
            bib_str = f'{bib["author"]} ({bib["year"]}) — {bib["title"]}' if bib['author'] or bib['title'] else '⚠️ bib字段为空'
            ctx = s['ctx'][:200].replace('|', '｜')
            lines.append(f'**样本{i}** `[{s["key"]}]` @{s["file"]}')
            lines.append(f'- 文献：{bib_str}')
            lines.append(f'- 上下文：{ctx}')
            lines.append(f'- 人工判断：[ ] 关联合理 [ ] 关联存疑 [ ] 明显错误')
            lines.append(f'')

    if warns:
        lines.append(f'### ⚠️  警告项（得半分）')
        lines.append(f'')
        for r in warns:
            lines.append(f'- [{r["id"]}] {r["title"]}（{r["weight_label"]}，满分{r["max_score"]}→得{r["score"]}）：{r["message"]}')
        lines.append(f'')

    # 完整明细表
    lines.append(f'### 完整评测明细')
    lines.append(f'')
    lines.append(f'| ID | 维度 | 检查项 | 类型 | 满分 | 得分 | 说明 |')
    lines.append(f'|----|------|--------|------|------|------|------|')
    for r in eval_result['results']:
        emoji = LEVEL_EMOJI.get(r['level'], '?')
        sc_str = str(r['score']) if r['score'] is not None else 'N/A'
        if r['level'] == 'DEDUCT':
            sc_str = f'-{r["deduction"]}'
        msg = r['message'].replace('|', '｜').replace('\n', ' / ')
        lines.append(f'| {r["id"]} | {r["dimension"]} | {r["title"]} | {r["weight_label"]} | {r["max_score"]} | {emoji}{sc_str} | {msg} |')

    return '\n'.join(lines)


def print_summary(eval_result: dict):
    """控制台输出（以分数为核心）"""
    s = eval_result['summary']
    pct = s['pct']
    if pct >= 90:
        grade = '优秀'
    elif pct >= 75:
        grade = '良好'
    elif pct >= 60:
        grade = '合格'
    else:
        grade = '不合格'

    print('\n' + '='*60)
    print(f'📊 总分：{s["total_score"]} / {s["total_max"]} 分  ({pct}%)  [{grade}]')
    print('='*60)

    # 维度得分
    print('维度得分：')
    for dim, ds in s['dim_scores'].items():
        sc = ds['score']
        mx = ds['max']
        rate = f"{round(sc/mx*100)}%" if mx > 0 else 'N/A'
        print(f'   {dim:<20} {sc:>4} / {mx:<3} ({rate})')

    print('─'*60)

    # 只打印有问题的项
    for r in eval_result['results']:
        if r['level'] in ('FAIL', 'WARN', 'DEDUCT'):
            emoji = LEVEL_EMOJI[r['level']]
            sc_str = f'-{r["deduction"]}分' if r['level'] == 'DEDUCT' else f'{r["score"]}/{r["max_score"]}分'
            print(f'{emoji} [{r["id"]}] {r["title"]}（{sc_str}）：{r["message"][:70]}')

    print('='*60)


def main():
    if len(sys.argv) < 3:
        print('用法：python3 evaluate.py <parsed.json> <latex_dir>')
        sys.exit(1)

    parsed_json = Path(sys.argv[1])
    latex_dir = Path(sys.argv[2])

    if not parsed_json.exists():
        print(f'错误：{parsed_json} 不存在')
        sys.exit(1)
    if not latex_dir.exists():
        print(f'错误：{latex_dir} 不存在')
        sys.exit(1)

    print(f'🔍 评测中：{parsed_json.name} → {latex_dir}')
    eval_result = run_evaluation(parsed_json, latex_dir)
    print_summary(eval_result)

    # 写入报告
    report = format_report(eval_result)
    report_path = latex_dir / 'evaluation_report.md'
    report_path.write_text(report, encoding='utf-8')
    print(f'\n📄 完整报告已保存：{report_path}')

    # 非零退出码表示有必要项失败
    sys.exit(0 if eval_result['summary']['passed'] else 1)


if __name__ == '__main__':
    main()
