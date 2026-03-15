# File Manager Service Skill - 完整包

将文件管理服务 + Skill 一起打包，方便共享给他人使用。

## 包含内容

```
file-manager-skill/
├── SKILL.md                  # Skill 定义
├── README.md                 # 使用说明
├── scripts/
│   └── file_manager.py       # 客户端脚本（含服务管理）
└── file-manager-service/     # 服务端（需从原位置复制）
    ├── app.py
    └── templates/
```

## 完整打包步骤

### 1. 准备完整目录

```bash
cd /root/.openclaw/workspace/projects

# 复制服务代码到 Skill 目录
cp -r file-manager-service file-manager-skill/
```

### 2. 打包

```bash
# 方法 A: tar.gz 压缩包
tar -czf file-manager-complete.tar.gz file-manager-skill/

# 方法 B: zip 压缩包
zip -r file-manager-complete.zip file-manager-skill/
```

### 3. 分发给他人

发送压缩包给对方，对方解压到任意位置。

## 使用方式（对方）

### 安装依赖

```bash
pip install requests flask
```

### 启动服务

```bash
cd file-manager-skill
python scripts/file_manager.py start
```

### 打开页面

```bash
python scripts/file_manager.py open
```

或直接访问：http://127.0.0.1:8888

### 停止服务

```bash
python scripts/file_manager.py stop
```

### 查看状态

```bash
python scripts/file_manager.py status
```

## 命令行用法

```bash
# 服务管理
python scripts/file_manager.py start      # 启动
python scripts/file_manager.py stop       # 停止
python scripts/file_manager.py restart    # 重启
python scripts/file_manager.py status     # 状态
python scripts/file_manager.py open       # 打开页面

# 文件管理
python scripts/file_manager.py list       # 列出文件
python scripts/file_manager.py cat <path> # 查看内容
python scripts/file_manager.py search <q> # 搜索
python scripts/file_manager.py stats      # 统计
python scripts/file_manager.py delete <p> # 删除
python scripts/file_manager.py mkdir <p> <n>  # 创建目录
python scripts/file_manager.py note <p> [n]   # 备注
```

## 作为 OpenClaw Skill 使用

如果对方也使用 OpenClaw，可以将 `file-manager-skill` 目录复制到：

```bash
cp -r file-manager-skill ~/.openclaw/skills/
```

然后在 OpenClaw 中直接说：
- "启动文件管理服务"
- "打开文件管理页面"
- "列出 projects 目录"
- "搜索 README 文件"

## 自定义配置

如需修改端口，编辑 `file-manager-service/app.py`：

```python
app.run(host='0.0.0.0', port=9999, debug=False)  # 修改端口
```

并修改 `scripts/file_manager.py`：

```python
BASE_URL = "http://127.0.0.1:9999"  # 同步修改
```
