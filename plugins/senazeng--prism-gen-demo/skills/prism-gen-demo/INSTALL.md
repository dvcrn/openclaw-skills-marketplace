# 安装说明

## 快速安装
```bash
bash setup.sh
```

## 手动安装
1. 确保Python 3.10+已安装
2. 安装依赖包:
   ```bash
   pip install -r requirements.txt
   ```
3. 设置脚本权限:
   ```bash
   chmod +x scripts/*.sh scripts/*.py
   ```
4. 创建必要目录:
   ```bash
   mkdir -p output/filtered output/top plots logs
   ```

## 验证安装
```bash
# 测试Python环境
python3 -c "import pandas; print('Pandas版本:', pandas.__version__)"

# 测试脚本
bash scripts/demo_list_sources.sh
```

## 添加到OpenClaw
```bash
ln -s $(pwd) ~/projects/openclaw/skills/prism-gen-demo
```
