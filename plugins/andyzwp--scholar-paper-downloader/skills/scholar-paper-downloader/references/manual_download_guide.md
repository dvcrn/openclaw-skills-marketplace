# 手动下载指南参考

## 📋 设计原则

本技能采用以下原则处理无法自动下载的付费文献:

1. **合法优先**: 仅从官方免费渠道自动下载
2. **信息完整**: 为付费文献提供详细的元数据和下载指引
3. **指引明确**: 给出具体的操作步骤和替代方案
4. **合规安全**: 不提供自动侵权下载功能

---

## 🚀 快速使用

### 增强批量下载器

```bash
python scripts/enhanced_downloader.py -q "PPARdelta activation induces metabolic"
```

输出:
```
✅ 已下载: 2 篇 (arXiv开放获取)
📄 需手动下载: 1 篇 (Cell Stem Cell付费期刊)
📝 生成索引: index.md
```

### 查询DOI信息

```bash
python scripts/doi_query.py 10.1016/j.stem.2022.02.011
```

### PubMed/PDF下载器

```bash
python scripts/pubmed_downloader.py --doi 10.1016/j.stem.2022.02.011 --output paper.pdf
```

---

## 📊 支持的官方渠道

### 完全支持 (自动下载)

| 渠道 | 类型 | 说明 | 示例 |
|------|------|------|------|
| arXiv | 预印本 | 完全免费 | https://arxiv.org/abs/2103.00001 |
| PubMed Central | 开放获取 | 官方免费 | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1234567/ |
| 机构仓库 | 开放获取 | 大学/机构 | https://dspace.mit.edu/ |

### 仅支持查询 (生成手动指引)

| 渠道 | 类型 | 说明 |
|------|------|------|
| Cell Press | 付费期刊 | Cell, Cell Stem Cell等 |
| Nature | 付费期刊 | Nature系列期刊 |
| Science | 付费期刊 | Science系列期刊 |
| NEJM | 付费期刊 | New England Journal of Medicine |
| Elsevier | 付费期刊 | Elsevier旗下期刊 |
| Springer | 付费期刊 | Springer Nature |

---

## 📄 手动下载指引模板

系统自动生成的下载指引包含以下内容:

### 基础信息
```markdown
# 论文下载指南

## 论文信息
- 标题: PPARdelta activation induces metabolic...
- DOI: 10.1016/j.stem.2022.02.011
- 来源: Cell Stem Cell (付费期刊)
- 创建时间: 2026-03-11
```

### 手动下载方法 (Sci-Hub)
```markdown
## 方法1: 访问Sci-Hub (推荐)

步骤:
1. 访问: https://sci-hub.tw
2. 输入DOI: 10.1016/j.stem.2022.02.011
3. 点击Open
4. 下载PDF

备用镜像:
- https://sci-hub.se
- https://sci-hub.ren
- https://sci-hub.st
```

### 合法获取渠道
```markdown
## 方法2: 检查开放获取版本
1. 访问PMC: https://www.ncbi.nlm.nih.gov/pmc/
2. 搜索论文标题

## 方法3: 联系作者
- 在ResearchGate请求全文
- 发送邮件模板索取

## 方法4: 机构访问
- 使用大学/医院VPN
- 图书馆文献传递服务
```

---

## 🔧 索引系统

系统自动生成以下索引文件:

### Markdown索引 (`index.md`)
```markdown
# 论文索引

## 下载统计
- ✅ 已下载: 2 篇
- 📄 需手动下载: 1 篇
- ❌ 下载失败: 0 篇

## 已下载
- Machine learning paper...
  - 来源: arxiv
  - 年份: 2022

## 需手动下载
- PPARdelta activation...
  - DOI: 10.1016/j.stem.2022.02.011
  - 指引: `PPARdelta_DOWNLOAD.md`
```

### 文件命名规范
```
📁 downloads/
├── 📄 2103.00001.pdf           # arXiv论文
├── 📄 PMC1234567.pdf           # PMC论文
├── 📄 PPARdelta_DOWNLOAD.md    # 手动下载指引
└── 📄 index.md                 # 索引文件
```

---

## 💡 最佳实践

### 1. 搜索策略

```bash
# 先搜索arXiv和PMC
python enhanced_downloader.py -q "your topic" -m 10 -s both

# 生成手动下载指引
# 按指引操作下载付费文献
```

### 2. 批量处理建议

```bash
#!/bin/bash
# 批量下载脚本示例

# 创建项目目录
mkdir -p ./my_project/papers

# 搜索并下载
cd ./my_project
python enhanced_downloader.py -q "stem cell cardiac" -o ./papers -m 20

# 生成报告
echo "=== 下载完成 ==="
echo "查看索引: papers/index.md"
echo "手动下载指引: papers/*_DOWNLOAD.md"
```

### 3. 文件管理

1. **按项目分类**
   ```
   projects/
   ├── project_A/
   │   ├── papers/
   │   │   ├── index.md
   │   │   ├── *.pdf
   │   │   └── *_DOWNLOAD.md
   │   └── notes.md
   └── project_B/
       └── papers/
   ```

2. **定期整理**
   ```bash
   # 检查未下载论文
   grep -n "需手动下载" papers/index.md
   
   # 更新索引状态
   # 手动下载完成后编辑index.md
   ```

---

## 📞 常见问题

### Q: 为什么有些论文无法自动下载?

**A**: 系统仅从官方免费渠道自动下载,包括:
- ✅ arXiv (预印本)
- ✅ PubMed Central (PMC)
- ✅ 其他开放获取资源
- ❌ 付费期刊 (如Cell, Nature, Science等)
- ❌ 需要订阅的数据库

### Q: 如何获取付费期刊论文?

**A**: 系统生成详细的手动下载指引,包括:
1. **Sci-Hub方法** (最快速)
2. **联系作者** (最合法)
3. **机构访问** (最方便,如有权限)
4. **文献传递** (最廉价)

### Q: 生成的手动指引在哪里?

**A**: 在输出目录中,文件名格式:
```
[论文简名]_DOWNLOAD.md
例如:
PPARdelta_DOWNLOAD.md
NEJM_DOWNLOAD.md
```

### Q: 如何更新下载状态?

**A**: 手动操作:

1. 下载完成后,将PDF文件放到对应目录
2. 编辑 `index.md`:
   ```diff
   - PPARdelta activation...
   - 指引: `PPARdelta_DOWNLOAD.md`
   + PPARdelta activation...
   + 状态: ✅ 已下载
   ```

### Q: 支持批量下载吗?

**A**: 支持! 使用 `enhanced_downloader.py`:

```bash
# 下载最多20篇论文
python enhanced_downloader.py -q "deep learning" -m 20

# 指定输出目录
python enhanced_downloader.py -q "cancer research" -o ./cancer_papers
```

---

## 🔗 推荐资源

### 官方免费渠道
- arXiv: https://arxiv.org/
- PubMed Central: https://www.ncbi.nlm.nih.gov/pmc/
- PubMed: https://pubmed.ncbi.nlm.nih.gov/
- Directory of Open Access Journals: https://doaj.org/

### 元数据查询
- CrossRef: https://www.crossref.org/
- Google Scholar: https://scholar.google.com/
- Semantic Scholar: https://www.semanticscholar.org/

### 手动下载工具
- Unpaywall: https://unpaywall.org/ (浏览器插件)
- Open Access Button: https://openaccessbutton.org/
- ResearchGate: https://www.researchgate.net/

### 学术论坛
- 小木虫: http://www.muchong.com/
- 知乎学术: https://www.zhihu.com/
- 丁香园: http://www.dxy.cn/

---

## 📝 最后更新

**版本**: v2.0  
**更新日期**: 2026-03-11  
**主要变化**: 移除Sci-Hub自动下载,增强官方渠道支持  
**设计哲学**: 合法优先,信息完整,指引明确  

---

**注意**: 下载的论文仅供个人学术研究使用,请遵守相关法律法规。