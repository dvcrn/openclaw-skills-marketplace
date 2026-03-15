"""
PDF 导出器
将 Markdown/Word 转换为 PDF
"""

import os
from pathlib import Path
from datetime import datetime

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import pdfkit
    PDFKIT_AVAILABLE = True
except ImportError:
    PDFKIT_AVAILABLE = False
    print("[WARN] pdfkit 未安装，PDF 导出功能不可用")
    print("安装：pip install pdfkit")
    print("还需要安装 wkhtmltopdf: https://wkhtmltopdf.org/downloads.html")


def markdown_to_html(md_content: str) -> str:
    """
    简单的 Markdown 转 HTML
    
    :param md_content: Markdown 内容
    :return: HTML 内容
    """
    html = md_content
    
    # 标题
    html = html.replace('# ', '<h1>')
    html = html.replace('## ', '<h2>')
    html = html.replace('### ', '<h3>')
    
    # 换行
    lines = html.split('\n')
    processed_lines = []
    for line in lines:
        if line.startswith('<h'):
            # 标题行
            processed_lines.append(line + '</h1>' if '<h1>' in line else line)
        elif line.strip():
            # 普通段落
            if not line.startswith('-') and not line.startswith('1.'):
                processed_lines.append(f'<p>{line}</p>')
            else:
                processed_lines.append(f'<li>{line}</li>')
        else:
            processed_lines.append('')
    
    html = '\n'.join(processed_lines)
    
    # 包装完整 HTML
    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: "Microsoft YaHei", sans-serif; margin: 40px; }}
        h1 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        p {{ line-height: 1.8; }}
        li {{ margin: 5px 0; }}
    </style>
</head>
<body>
{html}
</body>
</html>"""
    
    return full_html


def export_pdf_from_markdown(
    md_path: str,
    output_path: str = None
) -> dict:
    """
    从 Markdown 导出 PDF
    
    :param md_path: Markdown 文件路径
    :param output_path: 输出 PDF 路径（默认同名.pdf）
    :return: 导出结果
    """
    if not PDFKIT_AVAILABLE:
        return {
            "success": False,
            "error": "pdfkit 未安装"
        }
    
    md_path = Path(md_path)
    if not md_path.exists():
        return {"success": False, "error": "源文件不存在"}
    
    # 读取 Markdown
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # 转换为 HTML
    html_content = markdown_to_html(md_content)
    
    # 生成 PDF
    if output_path is None:
        output_path = str(md_path.with_suffix('.pdf'))
    
    try:
        pdfkit.from_string(html_content, output_path)
        return {
            "success": True,
            "source": str(md_path),
            "target": output_path
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def export_pdf_from_docx(
    docx_path: str,
    output_path: str = None
) -> dict:
    """
    从 Word 导出 PDF（需要 LibreOffice 或在线转换）
    
    :param docx_path: Word 文件路径
    :param output_path: 输出 PDF 路径
    :return: 导出结果
    """
    docx_path = Path(docx_path)
    if not docx_path.exists():
        return {"success": False, "error": "源文件不存在"}
    
    # 简单方案：提示用户使用 Word 另存为
    # 复杂方案：集成 LibreOffice（需要安装）
    
    return {
        "success": False,
        "error": "需要安装 LibreOffice 或使用 Word 另存为",
        "suggestion": f"用 Word 打开 {docx_path}，然后另存为 PDF"
    }


def export_pdf_simple(
    content: str,
    filename: str,
    category: str = "temp"
) -> dict:
    """
    简单 PDF 导出（纯文本）
    
    :param content: 文档内容
    :param filename: 文件名
    :param category: 类别
    :return: 导出结果
    """
    base_path = Path(f"D:\\OpenClawDocs\\{category}")
    base_path.mkdir(parents=True, exist_ok=True)
    
    # 生成简单的文本 PDF（使用 reportlab 或其他库）
    # 这里先实现基础版本
    
    pdf_path = base_path / filename.replace('.md', '.pdf')
    
    # 临时方案：保存为 TXT，提示用户转换
    txt_path = base_path / filename.replace('.md', '.txt')
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return {
        "success": True,
        "message": "已保存为 TXT，可用 Word 打开并另存为 PDF",
        "txt_path": str(txt_path),
        "suggested_pdf": str(pdf_path)
    }


# 测试
if __name__ == "__main__":
    print("PDF 导出模块就绪")
    print(f"DOCX 支持：{DOCX_AVAILABLE}")
    print(f"PDFKit 支持：{PDFKIT_AVAILABLE}")
