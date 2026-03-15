# Classics Text Cache

为提升检索速度，三本经典使用预抽取的 UTF-8 文本文件作为主读取源：

- `A_滴天髓.txt`
- `B_渊海子平.txt`
- `C_穷通宝鉴.txt`

## Regenerate

在项目根目录执行：

```bash
/Users/qinghuiren/Documents/skill_bazi/.venv/bin/python \
  bazi-daily/scripts/extract_classics_text.py
```

如需同时生成 markdown 文件：

```bash
/Users/qinghuiren/Documents/skill_bazi/.venv/bin/python \
  bazi-daily/scripts/extract_classics_text.py --md
```

## Source PDFs

- `/Users/qinghuiren/Downloads/滴天髓.pdf`
- `/Users/qinghuiren/Downloads/渊海子平.pdf`
- `/Users/qinghuiren/Downloads/穷通宝鉴.pdf`
