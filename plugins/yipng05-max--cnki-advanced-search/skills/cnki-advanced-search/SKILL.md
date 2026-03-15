---
name: cnki-advanced-search
description: "知网（CNKI）高级检索论文自动化工具。当用户提供研究关键词（一组或多组）时，自动在知网 高级检索页面模拟人类检索行为：选择学术期刊类别、勾选CSSCI来源、输入主题关键词（含同义词 和同位词，用 + 连接）、多组关键词用OR关系连接，检索后按被引量排序、切换50条/页、 打开摘要视图，最终提取前100篇（不足100篇则全部）论文的题录和摘要信息并保存为Excel文件。 触发条件：用户提到需要在知网/CNKI检索论文、高级检索、按关键词搜索CSSCI/C刊论文、 下载题录信息、获取论文摘要、按被引排序检索；或说\"帮我在知网检索XX相关论文\"、 \"用知网高级检索搜索XX主题的C刊论文\"、\"帮我检索XX关键词的CSSCI论文\"。"
---

# 知网高级检索论文工具

使用Chrome DevTools MCP工具在知网高级检索页面自动执行检索操作，提取CSSCI来源期刊论文的题录和摘要信息。

## Step 0: 解析用户关键词

从用户输入中提取检索关键词，组织为检索表达式：

- **单组关键词**：关键词及其同义词/同位词用 ` + ` 连接（+前后各一个空格），填入同一个主题检索框
  - 例：用户说"数字化转型"→ 检索词为 `数字化转型 + 数字化变革 + 数字化`
- **多组关键词**：每组填入独立的主题检索框，组间关系选OR
  - 例：用户说"数字化转型与企业绩效"→ 第一组 `数字化转型 + 数字化变革`，第二组 `企业绩效 + 企业业绩 + 组织绩效`

向用户确认关键词分组和同义词扩展后再执行检索。

## Step 1: 打开知网高级检索页面

```
navigate_page → https://kns.cnki.net/kns8s/AdvSearch
```

**验证码处理**：若snapshot中出现"拖动下方拼图完成验证"或"安全验证"文本，提示用户：
> "知网需要安全验证，请在浏览器中完成滑块验证，完成后告诉我。"

等用户确认后继续。

## Step 2: 选择"学术期刊"类别

take_snapshot查看页面，找到底部类别选项卡，点击"学术期刊"链接。

页面会刷新检索表单，出现来源类别选项（CSSCI、SCI、北大核心等）。

## Step 3: 勾选CSSCI来源类别

take_snapshot确认来源类别区域已显示，找到"CSSCI"对应的checkbox元素并点击勾选。

先取消"全部期刊"的勾选（如已勾选），再勾选"CSSCI"。

## Step 4: 输入主题检索词

### 4.1 第一组关键词

找到第一个"主题"检索框（默认已存在），用fill工具输入第一组关键词表达式。

示例：`数字化转型 + 数字化变革 + 数字化`

### 4.2 多组关键词（如有）

若有多组关键词：

1. **点击"+"按钮**添加新检索行
2. take_snapshot查看新增行
3. **修改新增行的检索字段类型**：新增行默认可能不是"主题"，需点击字段类型下拉框，选择"主题"
4. **修改逻辑运算符**：点击两行之间的运算符下拉框（默认"AND"），改选"OR"
5. **填入第二组关键词**：在新增行的检索框中fill第二组关键词表达式

重复以上步骤添加更多组。

### 运算符说明

知网高级检索框内的运算符：
- `+`（或）：前后各留一个空格，如 `关键词A + 关键词B`
- `*`（与）：前后各留一个空格
- `-`（非）：前后各留一个空格

## Step 5: 执行检索

点击"检索"按钮，等待结果页加载。

```
wait_for → "检索结果" 或等待结果列表出现
```

若出现验证码，提示用户完成后重试。

## Step 6: 按被引量排序

在检索结果页take_snapshot，找到排序选项区域，点击"被引"排序按钮使结果按被引数量从高到低排列。

可能需要点击两次（第一次升序，第二次降序），确认排序方向为降序（被引最多的在前）。

## Step 7: 切换每页显示50条

take_snapshot查看分页区域，找到每页显示数量的下拉选项或链接（默认20条），切换为50条。

通常页面底部有 `20 | 50` 的选项，点击"50"。

## Step 8: 切换摘要视图

找到50旁边的视图切换图标（通常是列表视图/摘要视图的切换按钮），点击打开"摘要视图"（或称"详细视图"），使页面显示每篇论文的完整摘要。

take_snapshot确认摘要内容已展示。

## Step 9: 提取题录和摘要信息

从第一页开始，逐页提取论文信息，直到收集满100篇或所有论文提取完毕。

### 9.1 每页数据提取

使用evaluate_script提取当前页所有论文信息：

```javascript
() => {
  const articles = [];
  // 摘要视图下，每篇论文是一个独立的结果块
  document.querySelectorAll('.result-table-list tbody tr, .briefDl_D').forEach(item => {
    const titleEl = item.querySelector('.fz14, a.fz14');
    const authorEl = item.querySelector('.author, .authorSpan');
    const sourceEl = item.querySelector('.source, .journalSpan');
    const dateEl = item.querySelector('.date, .yearSpan');
    const citeEl = item.querySelector('.quote, .citeSpan');
    const downloadEl = item.querySelector('.download, .downloadSpan');
    const absEl = item.querySelector('.abstract, .absSpan');
    if (titleEl) {
      articles.push({
        title: titleEl.textContent.trim(),
        authors: authorEl?.textContent?.trim() || '',
        source: sourceEl?.textContent?.trim() || '',
        date: dateEl?.textContent?.trim() || '',
        citations: citeEl?.textContent?.trim() || '',
        downloads: downloadEl?.textContent?.trim() || '',
        abstract: absEl?.textContent?.trim() || ''
      });
    }
  });
  return articles;
}
```

**注意**：知网页面DOM结构可能更新，上述选择器为参考。实际操作时先take_snapshot查看结果页的元素结构，根据实际uid和DOM结构调整提取逻辑。优先使用snapshot中可见的文本内容直接读取。

### 9.2 逐页提取

- 每页提取50篇，第1页提取后点击"下一页"继续
- 总计提取前100篇（即前2页）；若总结果不足100篇，提取全部
- 每次翻页后等待页面加载完成再提取

### 9.3 数据结构

每篇论文提取以下字段：
| 字段 | 说明 |
|------|------|
| 序号 | 1-100 |
| 标题 | 论文标题 |
| 作者 | 所有作者，分号分隔 |
| 来源期刊 | 期刊名称 |
| 发表时间 | 年份/期次 |
| 被引次数 | 被引用数量 |
| 下载次数 | 下载数量 |
| 摘要 | 完整摘要文本 |

## Step 10: 保存为Excel

使用Python脚本将提取的数据保存为Excel文件：

```python
import json
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

wb = Workbook()
ws = wb.active
ws.title = "检索结果"

# 表头
headers = ["序号", "标题", "作者", "来源期刊", "发表时间", "被引次数", "下载次数", "摘要"]
header_font = Font(bold=True, size=11)
header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
header_font_white = Font(bold=True, size=11, color="FFFFFF")

for col, h in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col, value=h)
    cell.font = header_font_white
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal='center', vertical='center')

# 数据行
for i, article in enumerate(articles, 1):
    ws.cell(row=i+1, column=1, value=i)
    ws.cell(row=i+1, column=2, value=article['title'])
    ws.cell(row=i+1, column=3, value=article['authors'])
    ws.cell(row=i+1, column=4, value=article['source'])
    ws.cell(row=i+1, column=5, value=article['date'])
    ws.cell(row=i+1, column=6, value=article.get('citations', ''))
    ws.cell(row=i+1, column=7, value=article.get('downloads', ''))
    cell = ws.cell(row=i+1, column=8, value=article.get('abstract', ''))
    cell.alignment = Alignment(wrap_text=True, vertical='top')

# 列宽
ws.column_dimensions['A'].width = 6
ws.column_dimensions['B'].width = 50
ws.column_dimensions['C'].width = 20
ws.column_dimensions['D'].width = 20
ws.column_dimensions['E'].width = 12
ws.column_dimensions['F'].width = 10
ws.column_dimensions['G'].width = 10
ws.column_dimensions['H'].width = 80

ws.auto_filter.ref = ws.dimensions
ws.freeze_panes = 'A2'

wb.save(output_path)
```

文件保存至 `~/Downloads/知网检索结果_{关键词摘要}_{日期}.xlsx`。

安装依赖：`pip3 install openpyxl`

## 注意事项

- 知网有反爬机制，每步操作间隔1-2秒，避免频繁请求
- 验证码出现时必须请用户手动完成
- 检索前向用户确认关键词分组和同义词扩展
- 全程向用户报告进度
- 若evaluate_script提取数据不完整，改用snapshot逐条读取
- 若总结果不足100篇，告知用户实际数量并全部提取
