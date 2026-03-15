---
name: huo15-doc-template / 火一五文档模板
description: "【版权：青岛火一五信息科技有限公司 账号：huo15】火一五文档技能（别名）。文档模板生成工具。用于生成公司正式文档（合同、报价单、功能说明书、发货单、PDA 单据、会议纪要等），包含公司信息、字体规范、页面设置等模板规则/PDF 文档时。**生成 Word 默认使用此技能**。触发场景：(1) 生成合同或报价单 (2) 创建 Word 文档模板 (3) 按公司规范排版文档 (4) 使用公文格式生成文档 (5) 用户说\"写个文档\"、\"生成文档\"、\"创建文档\"、\"生成会议纪要\"等"
---

# 文档模板技能

## 快速开始

1. **字体设置**：默认使用仿宋，小四（12pt）
2. **页面边距**：上下 3.7/3.5cm，左右 2.8/2.6cm
3. **页眉**：LOGO + 公司名称 + 底线
4. **页脚**：页码居中，格式"第 X 页 共 Y 页"，仿宋小四

---

## 配置规则

### 字体规范
- **默认正文**：仿宋，小四（12pt）
- **一级标题**：黑体，小三（15pt），加粗
- **二级标题**：楷体，小四（12pt），加粗
- **三级标题**：仿宋，小四（12pt），加粗

**WPS 字体兼容**：
- 汉字字体：使用 `仿宋`
- 每个 run 都要设置字体域 `w:eastAsia`

---

## ⚠️ 重要：Markdown 语法转换规则

### 禁止直接在 Word 中使用 Markdown 语法

**严禁将 Markdown 语法直接写入 Word 文档**，例如：
- ❌ 错误：`**加粗文本**` → Word 中会显示星号
- ❌ 错误：`| 列1 | 列2 |` → Word 中会显示管道符
- ❌ 错误：`# 一级标题` → Word 中会显示井号

### 正确转换方法

#### 1. 加粗转换
- Markdown：`**这是加粗**`
- Word：设置 `run.bold = True`

```python
# 错误示例（不要这样写！）
p = doc.add_paragraph("**这是加粗**")  # ❌ 会显示星号

# 正确示例
p = doc.add_paragraph("这是加粗")
p.runs[0].bold = True  # ✅ 真正加粗
```

#### 2. 表格转换
- Markdown：
```
| 列1 | 列2 | 列3 |
|------|------|------|
| 内容 | 内容 | 内容 |
```
- Word：使用 `doc.add_table()` 创建表格

```python
# 正确示例
table = doc.add_table(rows=2, cols=3)
table.style = 'Table Grid'

# 设置表头
header_cells = table.rows[0].cells
header_cells[0].text = "列1"
header_cells[1].text = "列2"
header_cells[2].text = "列3"

# 设置表头样式
for cell in header_cells:
    for paragraph in cell.paragraphs:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in paragraph.runs:
            run.bold = True
            run.font.name = '黑体'
            run.font.size = Pt(12)
```

#### 3. 标题转换
- Markdown：`# 一级标题`
- Word：添加段落并设置样式

```python
# 正确示例
p = doc.add_paragraph("一级标题")
p.runs[0].bold = True
p.runs[0].font.name = '黑体'
p.runs[0].font.size = Pt(15)
```

### 自检清单（生成文档前必查）

生成文档后，检查以下内容：
- [ ] 文档中是否有 `**`、`__`、`#` 等 Markdown 符号？
- [ ] 表格是否使用了 `|` 管道符？
- [ ] 链接是否显示了 `[文字](URL)` 格式？
- [ ] 列表是否显示了 `-` 或 `*` 前缀？

**如果有任何一项为"是"，则文档不合格，需要重新生成**

### ⚠️ 字体问题根本原因

**问题**：WPS 和 Word 对字体的渲染方式不同，WPS 需要显式设置字体域才能正确识别中文字体。

**解决方案**：每个 run 都必须设置以下三个属性：
1. `run.font.name = font_name` - 设置字体名称
2. `run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)` - 设置字体域（WPS兼容）
3. `run.font.size = Pt(font_size)` - 设置字号

### 字体设置正确示范

```python
from docx.oxml.ns import qn

def set_chinese_font(run, font_name='仿宋', font_size=12, bold=False):
    """
    设置中文字体，确保WPS和Word兼容
    必须对每个run都调用此函数！
    """
    # 1. 设置西文字体名称
    run.font.name = font_name
    # 2. 设置字体域（WPS兼容关键）
    run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)
    # 3. 设置字号
    run.font.size = Pt(font_size)
    # 4. 设置加粗
    run.bold = bold
    return run
```

### ❌ 常见错误

| 错误做法 | 后果 |
|---------|------|
| 只设置 `run.font.name` | Word显示正确，WPS显示为宋体 |
| 不设置 `w:eastAsia` 字体域 | WPS无法识别中文字体 |
| 只在第一个run设置字体 | 后续文字字体丢失 |
| 使用 `set_font()` 但没有设置字体域 | WPS显示不正确 |

### ✅ 正确做法

```python
# 正确：每个run都设置字体
p = doc.add_paragraph()
run = p.add_run('这是正文')
set_chinese_font(run, '仿宋', 12)  # ✅ 每个run都调用

# 错误：只设置一次
p = doc.add_paragraph()
run = p.add_run('这是正文')
run.font.name = '仿宋'  # ❌ 缺少字体域
```

---

### 完整函数模板（必须复制使用）

```python
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

def set_chinese_font(run, font_name='仿宋', font_size=12, bold=False):
    """
    设置中文字体，确保WPS和Word兼容
    必须对每个run都调用此函数！
    """
    run.font.name = font_name
    run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)
    run.font.size = Pt(font_size)
    run.bold = bold
    return run
```

### 页面设置（GB/T 9704-2012 公文格式）
- 上边距：3.7cm
- 下边距：3.5cm
- 左边距：2.8cm
- 右边距：2.6cm
- 纸张：A4

### 页眉（必须包含 LOGO）
- LOGO 路径：`/Users/jobzhao/.openclaw/workspace/assets/logo.png`
- 内容：LOGO 图片 + 公司名称（紧挨着）
- 字体：仿宋，小四（12pt）
- **必须添加页眉底线**（细线）

**页眉代码示例（必须包含 LOGO 图片）**：

```python
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

def add_header_with_logo(doc, logo_path='/Users/jobzhao/.openclaw/workspace/assets/logo.png'):
    """添加页眉，包含 LOGO 图片 + 公司名称 + 底线"""
    section = doc.sections[0]
    header = section.header
    header.paragraphs.clear()
    
    # 设置页眉高度
    section.header_distance = Cm(1.5)
    
    # 添加段落（左对齐）
    paragraph = header.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    # 1. 添加 LOGO 图片（如果存在）
    if os.path.exists(logo_path):
        try:
            # 添加图片，高度 1cm，宽度自动
            run = paragraph.add_run()
            run.add_picture(logo_path, height=Cm(1.0))
        except Exception as e:
            # 如果图片加载失败，继续添加文字
            pass
    
    # 2. 添加公司名称（紧挨着 LOGO）
    run = paragraph.add_run(' 青岛火一五信息科技有限公司')
    set_font(run, '黑体', 10)
    
    # 3. 添加页眉底线
    pPr = OxmlElement('w:pPr')
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), '000000')
    pBdr.append(bottom)
    pPr.append(pBdr)
    paragraph._element.insert(0, pPr)
    
    return header
```

**重要提醒（强制执行）**：
- 生成文档时**必须调用** `add_header_with_logo(doc)` 函数
- LOGO 图片路径：`/Users/jobzhao/.openclaw/workspace/assets/logo.png`
- 如果图片不存在，**必须报错并停止生成**，不能跳过 LOGO 继续生成文档
- 公司名称与 LOGO 之间保留一个空格，紧挨着显示

**LOGO 添加检查清单（每次生成文档前必须自检）**：
- [ ] LOGO 图片文件是否存在于 `/Users/jobzhao/.openclaw/workspace/assets/logo.png`
- [ ] 代码中是否调用了 `add_picture()` 方法添加 LOGO
- [ ] 页眉中是否包含 LOGO + 公司名称 + 底线 三个元素
- [ ] 是否设置了页眉底线（`w:bottom` 边框）

**常见错误及解决方案**：

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 文档没有 LOGO | 代码中缺少 `add_picture()` 调用 | 必须调用 `run.add_picture(logo_path, height=Cm(1.0))` |
| LOGO 路径错误 | 图片路径写错或文件不存在 | 使用绝对路径，生成前检查 `os.path.exists(logo_path)` |
| LOGO 太大/太小 | 高度设置不合理 | 使用 `height=Cm(1.0)` 标准高度 |
| LOGO 和文字分开 | 没有在同一 paragraph 中添加 | LOGO 和公司名称必须在同一个 paragraph 中 |

**完整调用示例**：

```python
from docx import Document
from docx.shared import Cm
import os

# 创建文档
doc = Document()

# 1. 设置页面格式
for section in doc.sections:
    section.top_margin = Cm(3.7)
    section.bottom_margin = Cm(3.5)
    section.left_margin = Cm(2.8)
    section.right_margin = Cm(2.6)

# 2. 添加页眉（必须包含 LOGO）
logo_path = '/Users/jobzhao/.openclaw/workspace/assets/logo.png'

# 检查 LOGO 是否存在
if not os.path.exists(logo_path):
    raise FileNotFoundError(f"LOGO 图片不存在：{logo_path}")

section = doc.sections[0]
header = section.header
header.paragraphs.clear()
section.header_distance = Cm(1.5)

paragraph = header.add_paragraph()
paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT

# 添加 LOGO
run = paragraph.add_run()
run.add_picture(logo_path, height=Cm(1.0))

# 添加公司名称
run = paragraph.add_run(' 青岛火一五信息科技有限公司')
set_font(run, '黑体', 10)

# 添加底线
# ...（参考上方完整代码）

# 3. 继续添加文档内容
# ...
```

### 页脚（GB/T 9704-2012 公文格式）
- **内容**：页码（如"第 1 页 共 3 页"）
- **位置**：页面下边缘居中
- **字体**：仿宋，小四（12pt）
- **WPS 兼容格式**：
  - 使用 `w:eastAsia` 字体域确保 WPS 识别
  - 数字同样使用仿宋字体
- **示例**：`第 1 页 共 3 页`

### 页脚代码示例（WPS 兼容）

```python
from docx.shared import Pt, Cm
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.enum.text import WD_ALIGN_PARAGRAPH

def add_footer_with_page_numbers(doc):
    """添加页脚，包含当前页和总页数，WPS 兼容"""
    section = doc.sections[0]
    
    # 设置页脚距离页面底部边距
    section.footer_distance = Cm(1.5)
    
    # 获取或创建页脚
    footer = section.footer
    
    # 添加段落（居中）
    paragraph = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 添加"第"字
    run1 = paragraph.add_run("第")
    run1.font.name = '仿宋'
    run1._element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')
    run1.font.size = Pt(12)
    
    # 插入当前页码域（PAGE）
    run2 = paragraph.add_run()
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    instrText1 = OxmlElement('w:instrText')
    instrText1.text = 'PAGE'
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'end')
    run2._element.append(fldChar1)
    run2._element.append(instrText1)
    run2._element.append(fldChar2)
    run2.font.name = '仿宋'
    run2._element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')
    run2.font.size = Pt(12)
    
    # 添加"页 共"文字
    run3 = paragraph.add_run("页 共")
    run3.font.name = '仿宋'
    run3._element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')
    run3.font.size = Pt(12)
    
    # 插入总页数域（NUMPAGES）
    run4 = paragraph.add_run()
    fldChar3 = OxmlElement('w:fldChar')
    fldChar3.set(qn('w:fldCharType'), 'begin')
    instrText2 = OxmlElement('w:instrText')
    instrText2.text = 'NUMPAGES'
    fldChar4 = OxmlElement('w:fldChar')
    fldChar4.set(qn('w:fldCharType'), 'end')
    run4._element.append(fldChar3)
    run4._element.append(instrText2)
    run4._element.append(fldChar4)
    run4.font.name = '仿宋'
    run4._element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')
    run4.font.size = Pt(12)
    
    # 添加"页"字
    run5 = paragraph.add_run("页")
    run5.font.name = '仿宋'
    run5._element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')
    run5.font.size = Pt(12)
```

---

## 公司信息
- 公司名称：青岛火一五信息科技有限公司
- 社会信用代码：91370203MA3CKR364A
- 地址：青岛市市南区南京路 8 号创联工场 6 楼 615
- 电话：18554898815
- 邮箱：postmaster@huo15.com

## 文档结构

1. 合同标题 - 居中，黑体二号加粗
2. 合同编号 - 居中，仿宋三号
3. 签订日期 - 居中，仿宋三号
4. 一，二，三...章 - 楷体三号加粗
5. 签署栏 - 盖章、法定代表人、日期

## 表格样式
- 表头：加粗，仿宋小四
- 正文：仿宋，小四（12pt）
- 边框：Table Grid

---

## 实践经验总结（2026-03-14）

### WPS页码兼容问题解决方案

**问题**：之前生成的文档在WPS中页码显示不正确

**根因**：页码域代码实现方式不正确

**最终解决方案（2026-03-14验证通过）**：

```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# 关键：正确添加域代码的方式
run2 = paragraph.add_run()
fldChar1 = OxmlElement('w:fldChar')
fldChar1.set(qn('w:fldCharType'), 'begin')
instrText1 = OxmlElement('w:instrText')
instrText1.text = 'PAGE'
fldChar2 = OxmlElement('w:fldChar')
fldChar2.set(qn('w:fldCharType'), 'end')
run2._element.append(fldChar1)  # 注意：用append不是set
run2._element.append(instrText1)
run2._element.append(fldChar2)
run2.font.name = '仿宋'
run2._element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')
run2.font.size = Pt(12)
```

**关键要点**：
1. 必须使用 `run._element.append()` 添加域元素，而不是其他方式
2. 每个run都要设置字体域：`run._element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')`
3. 同时设置 `run.font.name = '仿宋'`
4. PAGE域显示当前页，NUMPAGES域显示总页数

**验证结果**：WPS和Word均正确显示页码

### WPS字体兼容性问题解决方案

**问题**：生成的文档在WPS中字体显示不正确（显示为宋体而非仿宋/黑体等）

**根因**：
1. 只设置了 `run.font.name`，没有设置 `w:eastAsia` 字体域
2. WPS 和 Word 对字体的渲染机制不同

**实践经验（2026-03-14验证通过）**：

```python
# 正确：每个run都要设置字体域
run.font.name = '仿宋'
run._element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')  # 关键！
run.font.size = Pt(12)
```

**关键要点**：
1. **每个run都要设置字体域**：不能只设置一次，必须对每个run调用
2. **同时设置两个属性**：`run.font.name` + `run._element.rPr.rFonts.set()`
3. **正文样式也要设置**：
```python
style = doc.styles['Normal']
style.font.name = "仿宋"
style.font.size = Pt(12)
style._element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')
```
4. **字体域必须用正确的命名空间**：`qn('w:eastAsia')`

**验证结果**：WPS和Word均正确显示字体
