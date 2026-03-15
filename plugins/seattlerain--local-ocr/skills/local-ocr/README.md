# Local OCR Skill

本地离线 HLA 分型报告解析器。

## 快速开始

```bash
# 安装依赖
pip install easyocr opencv-python

# 运行解析
python3 scripts/hla_ocr.py path/to/report.jpg
```

## 输出格式

JSON 包含 `samples` 数组，每个样本有 `id`, `name`, `gender`, `age`, `relation`, `alleles`（6 个 HLA 位点）。

## 支持格式

- 8204-/8304-/8316-/8273- 格式（meta 行含角色+ID）
- 20251102xxxx 格式（姓名行 + ID行 + 性别年龄行）
- 密集表头格式（姓名 + 12 列等位基因数据）

## 特性

- 完全离线，无隐私风险
- 自动 Y 轴行排序
- OCR 错误自动修正
- 过滤噪声行（匹配标注等）

## 技术栈

- EasyOCR (chi_sim + en)
- OpenCV (行聚类)
- 自定义多格式解析器
