#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
convert.py - 一键 Word → 清华 MBA thuthesis PDF 转换器
用法: python3 convert.py <input.docx> [output_dir]
"""

import sys
import os
import re
import subprocess
from pathlib import Path


def _auto_cite_missing(latex_dir: Path):
    """
    检测 refs.bib 中未被正文引用的文献，用关键词匹配在章节 .tex 中自动插入 \\cite{key}。
    策略：从文献 title/author 提取关键词 → 在正文段落中搜索 → 在匹配句末插入。
    """
    bib_file = latex_dir / 'ref' / 'refs.bib'
    if not bib_file.exists():
        return

    bib_text = bib_file.read_text(encoding='utf-8')

    # 解析所有 BibTeX 条目：key → {title, author, year}
    entries = {}
    for m in re.finditer(r'@\w+\{(\w+),(.*?)^\}', bib_text, re.MULTILINE | re.DOTALL):
        key = m.group(1)
        block = m.group(2)
        title_m = re.search(r'title\s*=\s*\{(.+?)\}', block, re.DOTALL)
        author_m = re.search(r'author\s*=\s*\{(.+?)\}', block, re.DOTALL)
        year_m = re.search(r'year\s*=\s*\{(\d+)\}', block)
        entries[key] = {
            'title': title_m.group(1).replace('\n', ' ').strip() if title_m else '',
            'author': author_m.group(1).replace('\n', ' ').strip() if author_m else '',
            'year': year_m.group(1) if year_m else '',
        }

    if not entries:
        return

    # 收集正文中已有的 \cite{} 引用
    chap_files = sorted(latex_dir.glob('data/chap*.tex'))
    cited_keys = set()
    for cf in chap_files:
        for m in re.finditer(r'\\cite\{([^}]+)\}', cf.read_text(encoding='utf-8')):
            for k in m.group(1).split(','):
                cited_keys.add(k.strip())

    missing = [k for k in entries if k not in cited_keys]
    if not missing:
        print(f'   ✅ 所有 {len(entries)} 条文献均已被引用')
        return

    print(f'   发现 {len(missing)} 条未引用文献，进行关键词匹配...')

    def _extract_keywords(key: str) -> list:
        """从文献 title/author 提取中英文关键词（3字以上）"""
        e = entries[key]
        text = e['title'] + ' ' + e['author']
        # 中文：提取连续3个以上汉字的片段
        zh_words = re.findall(r'[\u4e00-\u9fff]{3,}', text)
        # 英文：提取4字母以上的单词（排除常见虚词）
        stopwords = {'with', 'from', 'that', 'this', 'their', 'have', 'been', 'into',
                     'drug', 'price', 'pricing', 'china', 'market', 'company', 'strategy'}
        en_words = [w.lower() for w in re.findall(r'[a-zA-Z]{4,}', text)
                    if w.lower() not in stopwords]
        return zh_words[:3] + en_words[:3]

    # 对每条缺失文献，在章节中找匹配句子
    inserted = {}  # key → (file, old_text, new_text)
    used_sentences = set()  # 避免同一句子被多个文献重复匹配

    for key in missing:
        keywords = _extract_keywords(key)
        if not keywords:
            continue
        best_match = None
        best_score = 0

        for cf in chap_files:
            content = cf.read_text(encoding='utf-8')
            # 找所有中文句子（以。结尾）或段落
            # 匹配正文段落行（非注释、非命令行）
            for line_m in re.finditer(r'^([^%\\][^\n]{10,}[。！？])', content, re.MULTILINE):
                line = line_m.group(1)
                if line in used_sentences:
                    continue
                # 计算关键词命中分
                score = sum(1 for kw in keywords if kw.lower() in line.lower())
                if score > best_score:
                    best_score = score
                    best_match = (cf, line)

        if best_match and best_score > 0:
            cf, matched_line = best_match
            # 在句末最后一个句号前插入 \cite{key}
            # 处理该句子可能已经有其他 \cite{} 的情况
            last_punct = max(matched_line.rfind('。'), matched_line.rfind('！'), matched_line.rfind('？'))
            if last_punct < 0:
                continue
            # 检查是否已有 \cite{} 紧邻这个句号
            prefix = matched_line[:last_punct]
            suffix = matched_line[last_punct:]
            existing_cite_m = re.search(r'\\cite\{([^}]+)\}$', prefix)
            if existing_cite_m:
                # 合并到已有 \cite{} 中
                old_cite = existing_cite_m.group(0)
                new_cite = old_cite.replace('}', f',{key}}}')
                new_line = prefix[:existing_cite_m.start()] + new_cite + suffix
            else:
                new_line = prefix + f'\\cite{{{key}}}' + suffix

            inserted[key] = (cf, matched_line, new_line)
            used_sentences.add(matched_line)

    # 执行替换
    success = 0
    for key, (cf, old_text, new_text) in inserted.items():
        content = cf.read_text(encoding='utf-8')
        if old_text in content:
            cf.write_text(content.replace(old_text, new_text, 1), encoding='utf-8')
            e = entries[key]
            print(f'   ✓ {key}: 插入 → {cf.name} (匹配: {old_text[:40]}...)')
            success += 1
        else:
            print(f'   ⚠️  {key}: 匹配句子在文件中找不到，跳过')

    # 仍未处理的（关键词无匹配）→ 用 \nocite{key} 追加到 thesis.tex
    # \nocite{} 是 LaTeX 标准命令：强制 bibtex 输出该条目，不需要正文 \cite{}
    still_missing = [k for k in missing if k not in inserted]
    if still_missing:
        print(f'   {len(still_missing)} 条无关键词匹配，用 \\nocite 强制输出...')
        thesis_tex = latex_dir / 'thesis.tex'
        if thesis_tex.exists():
            content = thesis_tex.read_text(encoding='utf-8')
            nocite_lines = '\n'.join(f'\\nocite{{{k}}}' for k in still_missing)
            # 插入到 \bibliographystyle 命令之前
            marker = '\\bibliographystyle{'
            if marker in content:
                content = content.replace(marker, nocite_lines + '\n' + marker, 1)
                thesis_tex.write_text(content, encoding='utf-8')
                for k in still_missing:
                    print(f'      → \\nocite{{{k}}} 已写入 thesis.tex')

    print(f'   完成：{success + len(still_missing)}/{len(missing)} 条文献已补全引用')


def run(cmd, cwd=None, check=True):
    print(f'▶ {cmd}')
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    if check and result.returncode != 0:
        print(f'❌ 命令失败 (exit {result.returncode})')
        sys.exit(result.returncode)
    return result.returncode

def main():
    if len(sys.argv) < 2:
        print('用法: python3 convert.py <input.docx> [output_dir]')
        print('示例: python3 convert.py 我的论文.docx ./output')
        sys.exit(1)

    docx_path = Path(sys.argv[1]).resolve()
    if not docx_path.exists():
        print(f'❌ 找不到文件: {docx_path}')
        sys.exit(1)

    # 输出目录默认为 ./output/<论文名>
    if len(sys.argv) >= 3:
        base_out = Path(sys.argv[2]).resolve()
    else:
        base_out = Path('output') / docx_path.stem

    scripts_dir = Path(__file__).parent
    project_root = scripts_dir.parent

    json_dir = project_root / 'output'
    latex_dir = base_out

    print(f'\n{"="*60}')
    print(f'📄 输入: {docx_path.name}')
    print(f'📁 输出: {latex_dir}')
    print(f'{"="*60}\n')

    # ── Step 1: 解析 Word ───────────────────────────────────────
    print('【Step 1/3】解析 Word 文档...')
    run(f'python3 "{scripts_dir}/parse_docx.py" "{docx_path}" "{json_dir}"')

    # 找到生成的 JSON 文件
    json_files = sorted(json_dir.glob('parsed_*.json'), key=lambda f: f.stat().st_mtime, reverse=True)
    if not json_files:
        print('❌ 未找到解析输出的 JSON 文件')
        sys.exit(1)
    json_path = json_files[0]
    print(f'   → JSON: {json_path.name}')

    # ── Step 2: 渲染 LaTeX 项目 ─────────────────────────────────
    print('\n【Step 2/3】渲染 LaTeX 项目...')
    run(f'python3 "{scripts_dir}/render.py" "{json_path}" "{latex_dir}"')

    # ── Step 2.5: 自动补全未引用文献的 \cite{} ─────────────────────
    # BibTeX 只输出被 \cite{} 引用过的条目。
    # 如果 refs.bib 里有文献但正文没有 \cite{}，PDF 参考文献列表会缺条目。
    # 自动检测并在正文中语义匹配插入。
    print('\n【Step 2.5/3】检测未引用文献并自动补全 \\cite{}...')
    _auto_cite_missing(latex_dir)

    # ── Step 3: 编译 PDF ─────────────────────────────────────────
    print('\n【Step 3/3】编译 PDF...')
    # xelatex 查找顺序：
    #   1. 环境变量 XELATEX_PATH（指定完整路径）
    #   2. 常见 macOS TeX Live 路径 /Library/TeX/texbin
    #   3. PATH 中的 xelatex（Linux/其他）
    _tex_bin = os.environ.get('XELATEX_PATH', '')
    if _tex_bin:
        extra_path = str(Path(_tex_bin).parent)
    elif Path('/Library/TeX/texbin/xelatex').exists():
        extra_path = '/Library/TeX/texbin'
    else:
        extra_path = ''
    export_path = (extra_path + ':' + os.environ.get('PATH', '')) if extra_path else os.environ.get('PATH', '')
    env = os.environ.copy()
    env['PATH'] = export_path

    def xelatex(cwd, label=''):
        result = subprocess.run(
            'xelatex -interaction=nonstopmode thesis.tex',
            shell=True, cwd=cwd, env=env,
            capture_output=True, text=True
        )
        for line in result.stdout.split('\n'):
            if any(k in line for k in ['Error', 'error', 'Fatal', '!']):
                if 'Font Warning' not in line and 'microtype' not in line:
                    print(f'   {line}')
        return result.returncode

    def toc_hash(cwd):
        """读取 .toc 文件内容的 hash，用于检测目录是否稳定"""
        import hashlib
        toc = Path(cwd) / 'thesis.toc'
        return hashlib.md5(toc.read_bytes()).hexdigest() if toc.exists() else ''

    # BibTeX 编译流程: xelatex → bibtex → xelatex → xelatex → (xelatex)
    # 第1次：生成 .aux 文件（含 \citation 记录）
    print('   第 1 次编译（生成 .aux）...')
    xelatex(latex_dir)
    h1 = toc_hash(latex_dir)

    # 运行 bibtex 生成 .bbl 文件
    bibtex_bin = str(Path(env['PATH'].split(':')[0]) / 'bibtex') if extra_path else 'bibtex'
    if not Path(bibtex_bin).exists():
        bibtex_bin = 'bibtex'
    print('   运行 bibtex...')
    result = subprocess.run(
        f'bibtex thesis',
        shell=True, cwd=latex_dir, env=env,
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f'   ⚠️  bibtex 警告（可能是部分引用未找到）:')
        for line in result.stdout.splitlines()[-5:]:
            print(f'      {line}')

    # 第2次：把参考文献 .bbl 写入
    print('   第 2 次编译（写入参考文献）...')
    xelatex(latex_dir)
    h2 = toc_hash(latex_dir)

    # 第3次：修正目录/交叉引用
    print('   第 3 次编译（稳定目录）...')
    xelatex(latex_dir)
    h3 = toc_hash(latex_dir)

    # 若 toc 还不稳定，补第4次
    if h3 != h2:
        print('   第 4 次编译（目录稳定中）...')
        xelatex(latex_dir)

    pdf_path = latex_dir / 'thesis.pdf'
    if pdf_path.exists():
        size_kb = pdf_path.stat().st_size // 1024
        print(f'\n{"="*60}')
        print(f'✅ 完成！PDF 已生成:')
        print(f'   {pdf_path}  ({size_kb} KB)')

        # 同时把 PDF 复制到 Word 原文件同目录，文件名与 Word 相同
        import shutil
        word_pdf = docx_path.with_suffix('.pdf')
        shutil.copy2(pdf_path, word_pdf)
        print(f'   → 已复制到: {word_pdf}')
        print(f'{"="*60}\n')

        # ── Step 4: 评测 ──────────────────────────────────────────
        print('\n【Step 4/4】运行 Rubric 评测...')
        evaluate_script = Path(__file__).parent / 'evaluate.py'
        if evaluate_script.exists():
            # 直接传入本次转换生成的 json_path（避免并行时用错文件）
            subprocess.run(
                [sys.executable, str(evaluate_script), str(json_path), str(latex_dir)],
                capture_output=False, text=True
            )
        else:
            print('   ⚠️  evaluate.py 不存在，跳过评测')

        # 打开 PDF（macOS open；Linux/Windows 跳过）
        import platform
        if platform.system() == 'Darwin':
            subprocess.run(['open', str(word_pdf)], check=False)
    else:
        print(f'\n❌ PDF 未生成，请检查 {latex_dir}/thesis.log')
        sys.exit(1)

if __name__ == '__main__':
    main()
