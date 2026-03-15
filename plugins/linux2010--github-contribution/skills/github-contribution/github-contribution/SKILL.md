---
name: github-contribution
description: GitHub 开源项目代码贡献完整工作流程。使用场景：当需要为开源项目解决 issue 或 bug 时，提供从 fork、同步、开发到提交 PR 的完整指导。包含自动化 PR 创建支持。
---

# GitHub 开源项目代码贡献技能

## 工作流程概述

为开源项目贡献代码的标准流程：
1. **Fork 项目** - 创建官方仓库的个人副本
2. **同步 Fork** - 确保与官方 main/master 分支保持一致  
3. **创建特性分支** - 基于最新代码创建专门的开发分支
4. **开发和测试** - 在特性分支上实现解决方案（高质量代码）
5. **自动化 PR 创建** - 使用 GitHub CLI 自动提交 PR

## 高质量 PR 标准（经验总结）

### ✅ 代码质量要求

1. **三层防御设计** - 不要依赖单一修复，提供多层保护
2. **完整测试覆盖** - 至少 3-4 个测试用例覆盖边界情况
3. **零警告零错误** - oxlint/eslint 必须 0 warnings, 0 errors
4. **无副作用** - 只修改必要的文件，不引入无关变更
5. **防御性编程** - 考虑 edge cases 和回归预防

### ✅ Commit Message 规范

```bash
# 格式：<type>(<scope>): <description>
# 示例：
fix(ui): prevent empty state overlay from blocking chat input (#45707)

# Body 包含：
# - 问题描述和影响
# - 解决方案（多层防御）
# - 测试覆盖
# - 质量验证
```

### ✅ PR 描述模板

```markdown
## Problem
清晰描述问题、影响范围、发生频率

## Solution (Three-Layer Defense)
1. Layer 1: 根本原因修复
2. Layer 2: 防御性措施
3. Layer 3: 额外保护

## Testing
- 测试用例数量
- 代码质量验证（oxlint 0 errors）

Fixes #<issue-number>
```

---

## 详细步骤指南

### 1. Fork 项目并克隆

```bash
# 如果还没有 fork，先在 GitHub 网页上 fork 项目
# 然后克隆你的 fork 到本地
git clone https://github.com/your-username/repository-name.git
cd repository-name
```

### 2. 设置上游远程并同步

```bash
# 添加官方仓库作为上游远程
git remote add upstream https://github.com/original-owner/repository-name.git

# 验证远程配置
git remote -v

# 切换到 main 分支（或 master）
git checkout main

# 从上游获取最新更改
git fetch upstream

# 将上游更改合并到本地 main
git merge upstream/main

# 推送到你的 fork
git push origin main
```

### 3. 创建特性分支

```bash
# 基于最新的 main 创建新分支
# 分支命名建议：fix/issue-number-brief-description 或 feature/brief-description
git checkout -b fix/123-bug-description

# 验证当前分支
git branch
```

### 4. 开发和测试解决方案

- 在特性分支上编写代码修复 issue
- 运行项目的测试套件确保没有破坏现有功能
- 遵循项目的代码风格和贡献指南
- 提交有意义的 commit 信息

```bash
# 添加更改的文件
git add .

# 提交更改（使用描述性提交信息）
git commit -m "Fix: brief description of what was fixed"

# 推送到你的 fork 的特性分支
git push origin fix/123-bug-description
```

### 5. 自动化 PR 创建（使用 GitHub CLI）

#### 前置条件：配置 GitHub CLI 和 Workflow 权限

```bash
# 检查 gh 认证状态
gh auth status

# 如果缺少 workflow 权限，刷新 token
gh auth refresh -s workflow -h github.com
# 按提示在浏览器中授权 workflow 权限
```

#### 步骤 5.1: Rebase 到最新 upstream/main

```bash
# 切换到 PR 分支
git checkout fix/issue-number

# Rebase 到最新 upstream/main
git fetch upstream
git rebase upstream/main

# 解决冲突（如果有）
git checkout --theirs <conflicted-files>
git add <files>
GIT_EDITOR=true git rebase --continue

# 强制推送到 fork（rebase 后必须）
git push --force-with-lease origin fix/issue-number
```

#### 步骤 5.2: 使用 gh API 创建 PR

```bash
# 方法 1: 使用 gh pr create（需要正确配置 base）
gh pr create \
  --base openclaw/openclaw:main \
  --head Linux2010:fix/issue-number \
  --title "fix(scope): description (#issue)" \
  --body "PR description here"

# 方法 2: 使用 gh API（更可靠）
gh api --method POST /repos/openclaw/openclaw/pulls \
  -f title="fix(scope): description (#issue)" \
  -f head="username:fix/issue-number" \
  -f base="main" \
  -f body="PR description"
```

#### PR 描述最佳实践

```markdown
## Problem
WebChat empty state covers input box for tool-only sessions (heartbeat/cron), 
causing complete session lockout.

**Impact**: High | **Frequency**: Every 30min

## Solution (Three-Layer Defense)

1. **Fix emptiness logic** - Check total messages (history + tools)
2. **Force input z-index: 100** - Always above overlay
3. **Disable overlay pointer-events** - Allow click-through

## Testing
- Added `test.ts` with 4 test cases
- Code Quality: oxlint 0 warnings, 0 errors

Fixes #45707
```

---

## 常见问题处理

### 同步冲突解决

如果在同步过程中遇到冲突：

```bash
# 在 main 分支上
git fetch upstream
git merge upstream/main

# 如果有冲突，手动解决后
git add .
git commit
git push origin main
```

### 特性分支更新

如果官方仓库有新提交，需要更新你的特性分支：

```bash
# 切换到 main 并同步
git checkout main
git fetch upstream
git merge upstream/main
git push origin main

# 切换回特性分支并 rebase
git checkout your-feature-branch
git rebase main

# 如果有冲突，解决后继续
git add .
git rebase --continue

# 强制推送到你的 fork（因为 rebase 改变了历史）
git push --force-with-lease origin your-feature-branch
```

### OAuth Workflow 权限问题

如果推送时遇到 `refusing to allow an OAuth App to create or update workflow` 错误：

```bash
# 检查当前 token 权限
gh auth status

# 刷新 token 添加 workflow 权限
gh auth refresh -s workflow -h github.com

# 按提示在浏览器中授权
# 1. 访问 https://github.com/login/device
# 2. 输入显示的一次性代码
# 3. 勾选 "Allow GitHub Actions workflow permissions"
# 4. 点击 "Authorize"

# 验证权限已添加
gh auth status | grep workflow

# 切换回 HTTPS 远程（如果是 SSH）
git remote set-url origin https://github.com/username/repo.git

# 重新推送
git push --force-with-lease origin branch-name
```

---

## 贡献检查清单

在提交 PR 前，请确保：

- [ ] **代码质量**
  - [ ] oxlint/eslint 0 warnings, 0 errors
  - [ ] 遵循项目代码风格指南
  - [ ] 无无关文件变更
- [ ] **测试覆盖**
  - [ ] 添加了必要的测试用例（至少 3-4 个）
  - [ ] 覆盖边界情况和 edge cases
  - [ ] 本地测试验证通过
- [ ] **防御性设计**
  - [ ] 三层防御（根本修复 + 保护措施 + 额外预防）
  - [ ] 考虑回归预防
  - [ ] 代码注释清晰
- [ ] **PR 质量**
  - [ ] Commit message 符合 Conventional Commits
  - [ ] PR 描述清晰完整（问题 + 方案 + 测试）
  - [ ] 关联了相关 issue（Fixes #123）
  - [ ] Rebase 到最新 upstream/main
- [ ] **权限配置**
  - [ ] gh auth 已配置
  - [ ] workflow 权限已授权
  - [ ] 远程 URL 配置正确（HTTPS）

---

## 实战经验（2026-03-14 #45707）

### 问题背景
修复 WebChat 空状态遮罩覆盖输入框的 bug（#45707）

### 执行流程

1. **代码修复** - 三层防御设计
   - Layer 1: 修复空状态检查逻辑
   - Layer 2: z-index: 100 强制输入框在上层
   - Layer 3: pointer-events: none 允许点击穿透

2. **质量验证**
   ```bash
   pnpm lint ui/src/ui/views/chat.ts  # 0 warnings, 0 errors
   ```

3. **测试用例**
   ```bash
   # 4 个测试覆盖：
   - tool-only sessions (heartbeat/cron)
   - truly empty sessions
   - history-only sessions
   - mixed messages
   ```

4. **Rebase 同步**
   ```bash
   git fetch upstream
   git rebase upstream/main
   GIT_EDITOR=true git rebase --continue
   ```

5. **Token 授权**
   ```bash
   gh auth refresh -s workflow
   # 浏览器授权 workflow 权限
   ```

6. **推送分支**
   ```bash
   git remote set-url origin https://github.com/Linux2010/openclaw.git
   git push --force-with-lease origin fix/45707-webchat-input-lockout
   ```

7. **创建 PR**
   ```bash
   gh api --method POST /repos/openclaw/openclaw/pulls \
     -f title="fix(ui): prevent empty state overlay from blocking chat input (#45707)" \
     -f head="Linux2010:fix/45707-webchat-input-lockout" \
     -f base="main" \
     -f body="PR description"
   ```

### 结果
✅ PR #45813 创建成功
✅ 代码质量：oxlint 0 warnings, 0 errors
✅ 测试覆盖：4 个测试用例
✅ 三层防御设计

---

## 参考资源

- **GitHub 官方贡献指南**：每个项目通常在 CONTRIBUTING.md 中有详细说明
- **项目特定要求**：检查项目的 README、文档和已有 PR 的模式
- **社区规范**：了解项目的沟通方式和期望
- **GitHub CLI 文档**：https://cli.github.com/manual/

使用此技能时，请根据具体项目的实际情况调整工作流程。
