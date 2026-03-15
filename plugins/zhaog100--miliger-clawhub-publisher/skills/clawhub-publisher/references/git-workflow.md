# Git 协作工作流程

## 概述

本文档描述如何使用 Git 协作来管理技能的版本和更新。

## 核心理念

**"分支隔离，合并审查，版本标记"**

- 本地开发在独立分支
- 远程更新通过PR审查
- 重要版本打Tag标记

## 工作流程

### 场景1：本地新功能开发

```bash
# 1. 创建功能分支
cd /root/.openclaw/workspace/skills/my-skill
git checkout -b feature/new-feature

# 2. 开发新功能
vim scripts/new-feature.sh
vim SKILL.md

# 3. 提交更改
git add .
git commit -m "Add: new-feature for better performance"

# 4. 合并到主分支
git checkout main
git merge feature/new-feature

# 5. 打标签
git tag -a v2.1.0 -m "Version 2.1.0 - New feature"

# 6. 推送到远程
git push origin main --tags

# 7. 发布到ClawHub
bash ../clawhub-publisher/scripts/publish.sh . 2.1.0
```

### 场景2：整合远程更新

```bash
# 1. 拉取远程最新版本
git fetch origin

# 2. 创建合并分支
git checkout -b merge/remote-updates

# 3. 下载远程ClawHub版本
cd /tmp
clawhub install my-skill --target ./remote

# 4. 复制远程文件
cp -r ./remote/my-skill/* /root/.openclaw/workspace/skills/my-skill/

# 5. 查看差异
cd /root/.openclaw/workspace/skills/my-skill
git status
git diff

# 6. 解决冲突
# 手动编辑冲突文件

# 7. 提交合并
git add .
git commit -m "Merge: remote updates from ClawHub v2.0.0"

# 8. 合并到主分支
git checkout main
git merge merge/remote-updates

# 9. 更新版本号
# 修改 package.json 中的版本号

git add package.json
git commit -m "Bump version to 2.1.0"

# 10. 发布更新
bash ../clawhub-publisher/scripts/publish.sh . 2.1.0
```

### 场景3：冲突解决

```bash
# 1. 查看冲突文件
git status

# 2. 编辑冲突文件
vim SKILL.md

# 冲突标记：
# <<<<<<< HEAD
# 本地版本内容
# =======
# 远程版本内容
# >>>>>>> remote-branch

# 3. 手动选择保留内容
# 删除冲突标记，保留需要的内容

# 4. 标记为已解决
git add SKILL.md

# 5. 继续合并
git commit -m "Resolve conflicts in SKILL.md"
```

## 分支管理策略

### 分支类型

1. **main**：主分支，稳定版本
2. **develop**：开发分支，集成新功能
3. **feature/***：功能分支，单一功能开发
4. **bugfix/***：修复分支，Bug修复
5. **release/***：发布分支，版本准备

### 分支命名规范

```
feature/new-feature      # 新功能
bugfix/fix-login-error   # Bug修复
release/v2.1.0           # 发布准备
hotfix/critical-bug      # 紧急修复
```

## Tag 管理

### 创建Tag

```bash
# 轻量标签
git tag v1.0.0

# 附注标签（推荐）
git tag -a v1.0.0 -m "Version 1.0.0 - Initial release"
```

### 查看Tag

```bash
# 列出所有标签
git tag

# 查看标签详情
git show v1.0.0
```

### 推送Tag

```bash
# 推送单个标签
git push origin v1.0.0

# 推送所有标签
git push origin --tags
```

### 删除Tag

```bash
# 删除本地标签
git tag -d v1.0.0

# 删除远程标签
git push origin --delete v1.0.0
```

## 提交信息规范

### 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type类型

- **feat**：新功能
- **fix**：Bug修复
- **docs**：文档更新
- **style**：代码格式（不影响功能）
- **refactor**：重构
- **test**：测试
- **chore**：构建/工具

### 示例

```bash
feat(scripts): add check-existing.sh for version checking

- Add ClawHub API integration
- Add GitHub repository checking
- Add exit code for different scenarios

Closes #123
```

## 最佳实践

### 1. 提交频率

- **小步提交**：每个逻辑单元一个提交
- **频繁推送**：每天至少推送一次
- **避免大提交**：单个提交不超过500行

### 2. 分支策略

- **短期分支**：功能分支不超过1周
- **及时合并**：完成后立即合并
- **删除旧分支**：合并后删除功能分支

### 3. 冲突预防

- **频繁拉取**：每天拉取远程更新
- **提前沟通**：重大更改提前通知
- **模块化设计**：减少文件交叉

### 4. 版本同步

```bash
# 定期同步ClawHub版本
bash ../clawhub-publisher/scripts/update.sh my-skill

# 定期同步Git远程
git fetch origin
git merge origin/main
```

## 协作场景

### 多人协作

```bash
# 1. 克隆仓库
git clone https://github.com/organization/skills.git
cd skills/my-skill

# 2. 创建功能分支
git checkout -b feature/my-feature

# 3. 开发并提交
git add .
git commit -m "feat: add my-feature"

# 4. 推送到远程
git push origin feature/my-feature

# 5. 创建Pull Request
# 在GitHub上创建PR

# 6. 代码审查
# 等待其他开发者审查

# 7. 合并
# PR批准后合并
```

### 紧急修复

```bash
# 1. 从main分支创建hotfix
git checkout main
git checkout -b hotfix/critical-bug

# 2. 修复Bug
vim scripts/main.sh
git add .
git commit -m "fix: critical bug in main.sh"

# 3. 合并到main
git checkout main
git merge hotfix/critical-bug

# 4. 打标签
git tag -a v1.0.1 -m "Hotfix: critical bug fix"

# 5. 紧急发布
bash ../clawhub-publisher/scripts/publish.sh . 1.0.1
```

## 工具集成

### Git Hooks

**pre-commit**：提交前检查

```bash
#!/bin/bash
# .git/hooks/pre-commit

# 检查SKILL.md是否存在
if [ ! -f "SKILL.md" ]; then
    echo "❌ SKILL.md is required"
    exit 1
fi

# 检查版本号格式
VERSION=$(grep -oP 'version["\s:]+\K[\d.]+' package.json 2>/dev/null)
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "⚠️  Invalid version format: $VERSION"
    read -p "Continue? (y/N): " -n 1 -r
    [[ ! $REPLY =~ ^[Yy]$ ]] && exit 1
fi

echo "✅ Pre-commit check passed"
```

### 自动化脚本

```bash
#!/bin/bash
# auto-release.sh - 自动化发布流程

VERSION="$1"

# 1. 运行测试
npm test || exit 1

# 2. 更新版本号
npm version "$VERSION"

# 3. 生成CHANGELOG
git-changelog -o CHANGELOG.md

# 4. 提交更改
git add .
git commit -m "chore: release v$VERSION"

# 5. 打标签
git tag -a "v$VERSION" -m "Release v$VERSION"

# 6. 推送
git push origin main --tags

# 7. 发布到ClawHub
bash ../clawhub-publisher/scripts/publish.sh . "$VERSION"
```

## 参考资源

- Git官方文档：https://git-scm.com/doc
- GitHub Flow：https://guides.github.com/introduction/flow/
- 语义化版本：https://semver.org/
- 提交信息规范：https://www.conventionalcommits.org/
