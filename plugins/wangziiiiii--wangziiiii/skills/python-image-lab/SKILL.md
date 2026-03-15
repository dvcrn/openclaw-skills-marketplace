---
name: python-image-lab
description: "Python 图片处理工具箱（Pillow + img2pdf）。用于图片格式转换、压缩优化、尺寸调整、批量处理、图片转 PDF。"
---

# Python Image Lab

使用 Python（`Pillow` + `img2pdf`）完成常见图片处理任务。

## 适用场景

- 将图片互转格式（JPG/PNG/WEBP/BMP/TIFF/GIF）
- 压缩图片体积
- 批量处理整个文件夹
- 调整图片尺寸（等比/裁剪/精确）
- 将单张或多张图片合并为 PDF

## 安装依赖（跨平台推荐）

> 原则：优先隔离环境（uv 或 .venv），不要默认往系统 Python 里直接 pip。

### 方案 A（推荐）：uv

```bash
cd skills/python-image-lab
uv venv .venv
uv pip install -r requirements.txt
```

### 方案 B（通用）：Python venv

```bash
cd skills/python-image-lab
python -m venv .venv
```

激活虚拟环境：

- Windows (PowerShell)

```powershell
.venv\Scripts\Activate.ps1
```

- Linux/macOS (bash/zsh)

```bash
source .venv/bin/activate
```

安装依赖：

```bash
python -m pip install -U pip
python -m pip install -r requirements.txt
```

## 运行方式（统一）

建议始终使用虚拟环境里的 Python 来执行脚本。

- Windows

```powershell
.venv\Scripts\python scripts\convert.py --help
```

- Linux/macOS

```bash
.venv/bin/python scripts/convert.py --help
```

## 命令速查

### 1) 格式转换

```bash
# Linux/macOS
.venv/bin/python scripts/convert.py --input /path/a.png --format webp
.venv/bin/python scripts/convert.py --input /path/images --format jpg --recursive

# Windows
.venv\Scripts\python scripts\convert.py --input C:\path\a.png --format webp
```

### 2) 压缩

```bash
.venv/bin/python scripts/compress.py --input /path/a.jpg --quality 80
.venv/bin/python scripts/compress.py --input /path/images --format webp --quality 78
```

### 3) 图片转 PDF

```bash
.venv/bin/python scripts/to_pdf.py --input /path/a.png
.venv/bin/python scripts/to_pdf.py --input /path/images --output /path/images.pdf
```

### 4) 调整尺寸

```bash
.venv/bin/python scripts/resize.py --input /path/a.jpg --width 1280
.venv/bin/python scripts/resize.py --input /path/images --width 1080 --height 1080 --mode cover
```

### 5) 批量流水线

```bash
.venv/bin/python scripts/batch.py --input /path/images --format webp --quality 80 --width 1600
```

## 新增参数（增强）

- `--dry-run`：仅预览，不落盘
- `--include-ext`：仅处理指定扩展名（逗号分隔）
- `--exclude-ext`：排除指定扩展名
- `--exclude-suffixes`：排除已处理后缀（默认会跳过 `_converted/_compressed/_resized/_batch`）

示例：

```bash
.venv/bin/python scripts/batch.py \
  --input /path/images \
  --format jpg \
  --exclude-suffixes _batch,_converted,_compressed,_resized \
  --dry-run
```

## 输出策略

- 默认输出到**同目录新文件**（不会覆盖原图）
- 默认文件名增加后缀：`_converted` / `_compressed` / `_resized` / `_batch`
- 如需覆盖，传 `--overwrite`

## 错误处理

- 缺少依赖时，会给出可执行安装提示（不是 traceback）
- 不支持的目标格式会提前提示
- 批处理结束会输出 `success/fail/total`，并列出失败文件

## 注意事项

- JPG 不支持透明通道，带透明图片转 JPG 时会自动铺白底。
- GIF/多帧图默认处理首帧。
- 若输入是目录，默认按文件名排序处理。
- 若系统启用了 PEP 668（如 Debian/Ubuntu），请使用 `.venv`，不要直接系统 pip。
