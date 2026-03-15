# ClawHub API 使用指南

## 概述

ClawHub CLI 是与 ClawHub 平台交互的命令行工具，用于发布、安装和管理技能。

## 安装

```bash
npm install -g clawhub
```

## 核心命令

### 1. inspect - 查看技能信息

**用法**：
```bash
clawhub inspect <skill-name>
```

**输出示例**：
```
name: session-memory-enhanced
description: Session-Memory Enhanced v4.0.0 - 统一增强版
version: 4.0.1
owner: zhaog100
packageId: k97carwxs0htme5y071ye69ykx82mmwg
```

**退出码**：
- 0：技能存在
- 1：技能不存在

### 2. install - 安装技能

**用法**：
```bash
clawhub install <skill-name> [--target <directory>]
```

**示例**：
```bash
# 安装到默认目录
clawhub install github

# 安装到指定目录
clawhub install github --target ./my-skills
```

**注意**：
- 默认安装到 `~/.openclaw/skills/`
- 会自动创建目录结构

### 3. publish - 发布技能

**用法**：
```bash
clawhub publish <path> --slug <slug> --version <version>
```

**示例**：
```bash
clawhub publish /path/to/skill --slug my-skill --version 1.0.0
```

**⚠️ 已知问题（v0.7.0）**：

CLI 缺少 `acceptLicenseTerms` 字段，需要手动修改：

**修复步骤**：

1. **定位文件**：
   ```bash
   PUBLISH_JS="/usr/lib/node_modules/clawhub/dist/cli/commands/publish.js"
   ```

2. **备份原文件**：
   ```bash
   sudo cp "$PUBLISH_JS" "$PUBLISH_JS.bak"
   ```

3. **修改文件**：
   ```bash
   sudo sed -i "s/form\.set('payload', JSON\.stringify({/form.set('payload', JSON.stringify({\n        acceptLicenseTerms: true,/" "$PUBLISH_JS"
   ```

4. **验证修改**：
   ```bash
   grep "acceptLicenseTerms" "$PUBLISH_JS"
   ```

**输出示例**：
```
acceptLicenseTerms: true,
slug: 'my-skill',
...
```

### 4. list - 列出已安装技能

**用法**：
```bash
clawhub list [--installed]
```

**输出示例**：
```
Installed skills:
  - github (v1.2.0)
  - weather (v1.0.0)
  - session-memory-enhanced (v4.0.1)
```

### 5. update - 更新技能

**用法**：
```bash
clawhub update <skill-name>
```

**示例**：
```bash
clawhub update github
```

## 高级用法

### .clawhubignore 文件

排除不需要上传的文件，避免发布失败。

**示例**：
```
venv/
node_modules/
__pycache__/
*.log
logs/
.git/
.gitignore
*.pyc
.env
README.md
CHANGELOG.md
```

**位置**：放在技能根目录

**生效范围**：发布时自动排除

### Package ID

每次发布成功后会生成唯一的 Package ID。

**格式**：`k97carwxs0htme5y071ye69ykx82mmwg`

**用途**：
- 唯一标识一次发布
- 可以用于版本追踪
- 可在 ClawHub 网站查看详情

### 版本管理

**语义化版本**：`MAJOR.MINOR.PATCH`

- **MAJOR**：重大更新（不兼容的API变更）
- **MINOR**：功能更新（向后兼容）
- **PATCH**：Bug修复（向后兼容）

**示例**：
```
1.0.0 → 1.0.1 (Bug修复)
1.0.1 → 1.1.0 (功能更新)
1.1.0 → 2.0.0 (重大更新)
```

## 故障排除

### 问题1：acceptLicenseTerms 错误

**错误信息**：
```
Error: acceptLicenseTerms: invalid value
```

**原因**：ClawHub CLI v0.7.0 缺少此字段

**解决**：见上文"publish 命令"部分的修复步骤

### 问题2：文件过多导致发布失败

**错误信息**：
```
Error: SKILL.md required
```

**真实原因**：文件数量超过限制（误导性错误）

**解决**：创建 `.clawhubignore` 排除大目录

### 问题3：网络超时

**错误信息**：
```
Error: ETIMEDOUT
```

**原因**：网络连接问题

**解决**：
1. 检查网络连接
2. 使用代理（如需要）
3. 稍后重试

### 问题4：权限错误

**错误信息**：
```
Error: EACCES
```

**原因**：没有写权限

**解决**：
```bash
# 使用sudo
sudo clawhub publish ...

# 或修改npm全局目录权限
sudo chown -R $(whoami) /usr/lib/node_modules
```

## API 响应格式

### 成功响应
```json
{
  "success": true,
  "data": {
    "packageId": "k97carwxs0htme5y071ye69ykx82mmwg",
    "slug": "session-memory-enhanced",
    "version": "4.0.1",
    "owner": "zhaog100",
    "createdAt": "2026-03-10T22:40:00Z"
  }
}
```

### 错误响应
```json
{
  "success": false,
  "error": {
    "code": "INVALID_SLUG",
    "message": "Slug already exists with different owner"
  }
}
```

## 环境变量

### CLAWHUB_API_URL

自定义 ClawHub API 地址（默认：https://api.clawhub.com）

```bash
export CLAWHUB_API_URL="https://custom-api.clawhub.com"
```

### CLAWHUB_TOKEN

认证令牌（通常不需要手动设置）

```bash
export CLAWHUB_TOKEN="your-token-here"
```

## 调试模式

启用详细日志：

```bash
DEBUG=clawhub:* clawhub publish ...
```

## 最佳实践

1. **发布前检查**：使用 `clawhub inspect` 检查是否已存在
2. **版本管理**：遵循语义化版本规范
3. **文件清理**：使用 `.clawhubignore` 排除不必要的文件
4. **测试验证**：发布后使用 `clawhub inspect` 验证
5. **备份本地**：更新前备份本地版本

## 参考链接

- ClawHub 官网：https://clawhub.com
- ClawHub CLI GitHub：https://github.com/openclaw/clawhub
- Issue 反馈：https://github.com/openclaw/clawhub/issues
