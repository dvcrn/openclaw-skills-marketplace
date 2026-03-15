# Code Sentinel - GitHub 部署指南

## 私有仓库创建

由于权限限制，请手动在 GitHub 创建私有仓库：

### 1. 在 GitHub 网页创建仓库

访问: https://github.com/new

- **Repository name**: `code-sentinel`
- **Owner**: `panshi-ai`
- **Private**: ✅ 勾选
- **Initialize this repository with a README**: ❌ 不勾选
- **.gitignore**: Python
- **License**: None

点击 **Create repository**

### 2. 推送本地代码

```bash
cd /Users/zhangpeng/.openclaw/workspace-panshi/skills/code-sentinel

# 添加远程仓库
git remote set-url origin https://github.com/panshi-ai/code-sentinel.git

# 推送代码
git push -u origin main
```

## 配置环境变量（安全）

在 GitHub 仓库设置中添加以下 Secrets：

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `GH_TOKEN` | `ghp_xxx` | GitHub Personal Access Token |
| `TWITTER_API_KEY` | `xxx` | 番茄小说相关 API |
| `OPENAI_API_KEY` | `sk-xxx` | OpenAI API Key |

## GitHub Actions 配置

工作流已配置在 `.github/workflows/codesentinel.yml`：

- ✅ Push to main/develop 自动触发
- ✅ Pull Request 自动审查
- ✅ Security + Performance 双流程
- ✅ 自动修复建议 PR

## OpenClaw Control Center 集成

仓库路径: `/workspace-panshi/skills/code-sentinel`

## 本地开发

```bash
cd /Users/zhangpeng/.openclaw/workspace-panshi/skills/code-sentinel

# 激活虚拟环境（可选）
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install playwright
playwright install chromium

# 运行测试
python3 scripts/sentinel.py ./test-project

# 自动修复
python3 scripts/autofix.py ./test-project
```

## 安全检查

✅ 已确认无硬编码：
- 无数据库密码
- 无 API Key
- 无私有 Token
- 仅使用环境变量 `FQXX_USER` / `FQXX_PASS`

## 下一步

1. 手动创建 GitHub 私有仓库
2. 推送代码
3. 配置 Secrets
4. 测试 GitHub Actions
5. 集成到 OpenClaw 主流程

---

**ℹ️ 注意**: 私有仓库确保敏感配置不会泄露到公网。
