# GitHub 仓库设置指南

## 🎯 目标
将系统维护技能推送到 GitHub 作为开源版本备份。

## 📋 前提条件
1. GitHub 账号: jazzqi
2. SSH 密钥已配置（在 tmux 'git' 会话中已验证工作）

## 🚀 设置步骤

### 方法 A：通过 tmux 'git' 会话（推荐）

1. **连接到 tmux 会话**
   ```bash
   tmux attach -t git
   ```

2. **在 tmux 中执行**
   ```bash
   # 进入技能目录
   cd ~/.openclaw/skills/system-maintenance
   
   # 添加远程仓库（创建后）
   git remote add origin git@github.com:jazzqi/openclaw-system-maintenance.git
   
   # 推送代码
   git push -u origin master
   ```

### 方法 B：通过网页创建

1. **创建 GitHub 仓库**
   - 访问: https://github.com/new
   - 仓库名: `openclaw-system-maintenance`
   - 描述: `OpenClaw System Maintenance Skill - Daily cleanup and optimization automation`
   - 选择: 不初始化 README、.gitignore、license
   - 点击创建

2. **获取 SSH URL**
   ```
   git@github.com:jazzqi/openclaw-system-maintenance.git
   ```

3. **本地推送**
   ```bash
   cd ~/.openclaw/skills/system-maintenance
   git remote add origin git@github.com:jazzqi/openclaw-system-maintenance.git
   git branch -M main  # 如果需要重命名分支
   git push -u origin main
   ```

## 📁 仓库内容

### 核心文件
```
├── SKILL.md                    # 技能文档
├── entry.js                    # JavaScript 入口点
├── package.json               # npm 配置
├── scripts/
│   └── daily-maintenance-optimization.sh  # 维护脚本
├── examples/
│   └── setup-guide.md         # 设置指南
└── docs/                      # 文档目录
```

### 许可证建议
建议添加 `LICENSE` 文件，选择:
- MIT License（最宽松）
- Apache 2.0（专利保护）
- GPL-3.0（强 copyleft）

## 🔧 推送后操作

### 1. 验证推送
```bash
git log --oneline -5
git remote -v
```

### 2. 设置仓库信息
```bash
# 添加 README.md（可选）
echo "# OpenClaw System Maintenance Skill" > README.md
echo "基于 2026-03-08 实践经验创建的系统清理与优化维护技能。" >> README.md

# 添加 LICENSE（可选）
curl -o LICENSE https://opensource.org/licenses/MIT

# 提交并推送
git add README.md LICENSE
git commit -m "docs: add README and LICENSE"
git push
```

### 3. 更新 package.json 仓库信息
```json
{
  "repository": {
    "type": "git",
    "url": "git+https://github.com/jazzqi/openclaw-system-maintenance.git"
  },
  "bugs": {
    "url": "https://github.com/jazzqi/openclaw-system-maintenance/issues"
  },
  "homepage": "https://github.com/jazzqi/openclaw-system-maintenance#readme"
}
```

## 📦 与 ClawHub 集成

### 已发布到 ClawHub
- **名称**: `system-maintenance`
- **版本**: `1.0.0`
- **ID**: `k97bca5502xm85egs9gba5zkks82ekd0`
- **ClawHub 安装**: `clawhub install system-maintenance`

### 双仓库优势
1. **ClawHub**: 方便 OpenClaw 用户安装和使用
2. **GitHub**: 开源协作、版本控制、问题跟踪

## 🔄 更新流程

### 发布新版本
1. 更新代码
2. 提交到 GitHub
3. 发布到 ClawHub
4. 更新文档

```bash
# 1. 代码更新
git add .
git commit -m "feat: add new feature"
git push

# 2. ClawHub 发布新版本
clawhub publish . --version 1.1.0
```

## 🆘 故障排除

### SSH 问题
```bash
# 测试连接
ssh -T git@github.com

# 检查密钥
ssh-add -l

# 重新添加密钥
ssh-add ~/.ssh/id_rsa
```

### 推送被拒绝
```bash
# 强制推送（谨慎使用）
git push -f origin main

# 或先拉取
git pull origin main --rebase
```

### 分支名称冲突
```bash
# 重命名分支
git branch -M main

# 或使用现有分支
git push -u origin master:main
```

---

## 📝 备注

### 创建时间
- **技能开发**: 2026-03-07 深夜至 2026-03-08 凌晨
- **ClawHub 发布**: 2026-03-08 03:08
- **GitHub 推送**: 待完成

### 基于的实践经验
本技能基于 2026-03-07 的 Gateway 认证修复和财经新闻任务优化经验创建，包含完整的系统维护自动化方案。

---

**提示**: GitHub 推送可以在明天通过 tmux 'git' 会话轻松完成，该会话已配置正确的 SSH 密钥。