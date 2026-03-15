# 安装指南

本文档提供详细的安装步骤和配置说明。

---

## 📋 系统要求

### 必需

- **操作系统**: Linux / macOS / Windows (WSL)
- **Python**: 3.10 或更高版本
- **内存**: 至少 2GB RAM
- **磁盘空间**: 至少 1GB

### 推荐

- **操作系统**: Ubuntu 20.04+ / macOS 12+
- **Python**: 3.12
- **内存**: 4GB RAM
- **磁盘空间**: 5GB

---

## 🚀 安装步骤

### 步骤 1: 安装依赖

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install -y python3 python3-pip git curl
```

#### macOS

```bash
brew install python3 git curl
```

---

### 步骤 2: 安装 SearXNG

SearXNG 是必需的搜索引擎。

#### 方式1: Docker（推荐）

```bash
# 安装 Docker
curl -fsSL https://get.docker.com | sh

# 运行 SearXNG
docker run -d \
  --name searxng \
  -p 8080:8080 \
  -e BASE_URL=http://localhost:8080 \
  -e INSTANCE_NAME=Nero-Search \
  searxng/searxng:latest

# 测试
curl http://localhost:8080/search?q=test&format=json
```

#### 方式2: 本地安装

参见 [SearXNG 官方文档](https://github.com/searxng/searxng)

---

### 步骤 3: 安装 LibreTranslate

LibreTranslate 用于翻译英文内容。

#### 方式1: 使用公共实例（免费）

直接使用公共 API：
```
https://translate.example.com
```

#### 方式2: Docker（推荐）

```bash
docker run -d \
  --name libretranslate \
  -p 5000:5000 \
  libretranslate/libretranslate:latest

# 测试
curl -X POST http://localhost:5000/translate \
  -H "Content-Type: application/json" \
  -d '{"q":"test","source":"en","target":"zh"}'
```

---

### 步骤 4: 创建 Notion 数据库

#### 4.1 创建 Notion Integration

1. 访问 [Notion Developers](https://www.notion.so/my-integrations)
2. 点击 "New integration"
3. 填写名称：`Nero Market Research`
4. 复制 API Key（以 `ntn_` 开头）

#### 4.2 创建商机池数据库

1. 在 Notion 中创建新页面
2. 添加数据库（Table）
3. 命名为 "Opportunities"
4. 添加字段（参见 `templates/opportunities_template.json`）
5. 复制数据库 ID（从 URL）

#### 4.3 创建 Daily Report 数据库

1. 创建另一个数据库
2. 命名为 "Daily Reports"
3. 添加字段（参见 `templates/daily_report_template.json`）
4. 复制数据库 ID

#### 4.4 授权 Integration

1. 打开两个数据库
2. 点击右上角 "..." → "Add connections"
3. 选择你的 Integration

---

### 步骤 5: 安装 Nero

```bash
# 克隆仓库
git clone https://github.com/your-username/nero-market-research.git
cd nero-market-research

# 运行安装脚本
chmod +x install.sh
./install.sh
```

---

### 步骤 6: 配置

```bash
# 复制配置模板
cd ~/.nero-market-research
cp config.json.example config.json

# 编辑配置
nano config.json
```

**必需配置**：

```json
{
  "notion": {
    "api_key": "ntn_your_api_key",
    "database_id": "your_opportunities_db_id",
    "daily_report_db_id": "your_daily_report_db_id"
  },
  "search": {
    "primary_url": "http://localhost:8080"
  },
  "translation": {
    "api_url": "http://localhost:5000"
  }
}
```

---

### 步骤 7: 启动系统

```bash
# 启动
nero start

# 查看日志
nero logs

# 查看状态
nero status
```

---

## ✅ 验证安装

### 1. 检查服务状态

```bash
nero status
```

应该看到：
```
✅ Nero 系统运行中
```

### 2. 检查 Notion 连接

```bash
nero sync
```

应该看到：
```
✅ Notion 连接成功
```

### 3. 检查数据收集

等待1小时后，查看日志：

```bash
nero logs-today
```

应该看到类似：
```
[INFO] GitHub Miner: 找到 15 个痛点
[INFO] 数据质量过滤: 保留 12 个
[INFO] 需求评分: 保留 2 个高分机会
```

---

## 🔧 故障排查

### 问题 1: SearXNG 连接失败

**检查**：
```bash
curl http://localhost:8080/search?q=test&format=json
```

**解决**：
- 确认 Docker 容器运行中
- 检查端口 8080 是否被占用

---

### 问题 2: Notion API 401 错误

**检查**：
- API Key 是否正确
- Integration 是否有数据库访问权限

**解决**：
- 重新创建 Integration
- 重新授权数据库连接

---

### 问题 3: Python 依赖安装失败

**解决**：
```bash
pip3 install --upgrade pip
pip3 install -r requirements.txt --user
```

---

## 📚 下一步

- [配置说明](CONFIGURATION.md) - 详细的配置参数
- [使用手册](USAGE.md) - 详细的使用方法
- [API参考](API_REFERENCE.md) - 开发者文档

---

## 🆘 获取帮助

- **Discord**: [加入社区](https://discord.gg/xxx)
- **Email**: zcweah@gmail.com
- **GitHub Issues**: [提交问题](https://github.com/your-username/nero-market-research/issues)
