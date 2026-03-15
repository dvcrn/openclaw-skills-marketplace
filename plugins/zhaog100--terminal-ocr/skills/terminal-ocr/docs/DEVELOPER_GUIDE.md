# 终端OCR技能开发者指南

## 📁 项目结构

```
terminal-ocr/
├── SKILL.md                    # 技能元数据
├── README.md                   # 技能简介
├── install.sh                  # 安装脚本
├── config/
│   └── ocr-config.json         # 配置文件
├── scripts/
│   ├── enhanced-terminal-ocr.py # 主脚本（增强版）
│   ├── preprocess-image.py     # 图像预处理（基础版）
│   └── fallback-ai-analysis.py # AI视觉分析（备用）
├── docs/
│   ├── USER_GUIDE.md          # 用户指南
│   └── DEVELOPER_GUIDE.md     # 开发者指南
├── tests/                     # 测试目录
└── venv/                      # Python虚拟环境
```

## 🔧 开发环境

### 依赖安装
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install opencv-python pillow numpy
```

### 开发流程
1. **修改代码**：在`scripts/`目录下开发
2. **测试功能**：使用`tests/`目录进行测试
3. **更新文档**：同步更新`docs/`目录
4. **配置调整**：修改`config/ocr-config.json`
5. **版本发布**：更新`SKILL.md`和`README.md`

## 🧪 测试方案

### 单元测试
```python
# tests/test_preprocessing.py
def test_image_preprocessing():
    # 测试图像预处理功能
    pass

# tests/test_ocr_engines.py  
def test_ocr_engine_selection():
    # 测试OCR引擎选择逻辑
    pass
```

### 集成测试
```bash
# 测试完整流程
python scripts/enhanced-terminal-ocr.py tests/sample-terminal.png -o tests/output/
```

### 性能测试
```python
# tests/test_performance.py
def test_large_image_processing():
    # 测试大图片处理性能
    pass
```

## 🚀 功能扩展

### 添加新OCR引擎
1. 在`config/ocr-config.json`中添加引擎配置
2. 在`scripts/enhanced-terminal-ocr.py`中实现引擎逻辑
3. 更新用户指南和开发者指南

### 添加新预处理功能
1. 在`_process_single_block()`函数中添加处理步骤
2. 在配置文件中添加相关参数
3. 更新文档说明

### 添加新输出格式
1. 在`output`配置中添加格式选项
2. 实现相应的输出处理逻辑
3. 更新用户指南

## 📦 发布流程

### 本地测试
```bash
# 安装技能
bash install.sh

# 测试功能
python scripts/enhanced-terminal-ocr.py -i
```

### 发布到ClawHub
1. 更新`SKILL.md`版本号
2. 更新`package.json`（如果需要）
3. 打包技能：`tar -czf terminal-ocr-v0.2.0.tar.gz *`
4. 发布：`clawhub publish terminal-ocr-v0.2.0.tar.gz`

## 🔍 调试技巧

### 日志调试
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 性能分析
```python
import cProfile
cProfile.run('main()', 'profile.stats')
```

### 内存监控
```python
import psutil
process = psutil.Process()
print(f"内存使用: {process.memory_info().rss / 1024 / 1024:.2f} MB")
```

## 📈 版本规划

### v0.1.0 - 基础功能
- ✅ 图像分块处理
- ✅ 图像增强
- ✅ AI视觉分析

### v0.2.0 - 增强功能  
- ✅ 配置文件支持
- ✅ 交互式模式
- ✅ 多引擎支持
- ✅ 错误处理

### v0.3.0 - 完整OCR
- [ ] Tesseract集成
- [ ] 命令行语法高亮
- [ ] 日志格式识别

### v1.0.0 - 稳定版本
- [ ] 批量处理
- [ ] Web界面
- [ ] 完整测试套件

---
*版本：0.2.0*
*最后更新：2026-03-05*