# 环境配置指南

## 核心思路
使用虚拟环境隔离依赖，确保环境一致性。

## 基础安装

### 创建虚拟环境
```bash
# 创建环境
python -m venv yolo-env

# 激活环境
source yolo-env/bin/activate  # Linux/Mac
# yolo-env\Scripts\activate   # Windows
```

### 安装核心依赖
```bash
# 基础安装
pip install ultralytics opencv-python

### 验证安装
```python
from ultralytics import YOLO
print("✅ 环境配置成功")
```

## 可选依赖
```bash
# 开发工具
pip install matplotlib pandas

# GPU加速
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 环境检查
```python
import torch
print(f"CUDA可用: {torch.cuda.is_available()}")
print(f"GPU数量: {torch.cuda.device_count()}")
```

## 配置建议

### 项目结构
```
yolo-project/
├── yolo-env/          # 虚拟环境
├── data/              # 数据目录
├── models/            # 模型文件
└── scripts/           # 脚本文件
```

### requirements.txt
```
ultralytics>=8.4.0
opencv-python>=4.5.0
```

## 常见问题
```bash
# 安装失败
python -m pip install --upgrade pip
pip install ultralytics --no-cache-dir

# 依赖冲突
python -m venv new-env
source new-env/bin/activate
pip install ultralytics
```

## 维护建议
1. 定期更新：`pip install -U ultralytics`
2. 环境备份：导出`requirements.txt`
3. 测试验证：新环境先运行简单测试