---
name: merge-dev-to-pre-or-beta
description: "执行「开发分支 → pre 或 beta」的合并与推送流程。包含：在当前开发分支拉取最新、切换到目标分支并拉取、合并并推送、切回开发分支、拉取并推送开发分支到远端。用户说「合并到 pre」或「合并到 beta」时使用，根据用户说的分支名选择目标。"
---

# 合并开发分支到 pre 或 beta 并推送

## 使用时如何区分 pre 和 beta

根据用户**明确说出的分支名**确定目标，不要猜测：

| 用户说法示例 | 目标分支 TARGET |
|-------------|-----------------|
| 合并到 **pre**、发布到 pre、同步 pre、合并到预发 | `pre` |
| 合并到 **beta**、发布到 beta、同步 beta、合并到测试 | `beta` |

- 用户只说「合并到 pre」→ 本次只对 **pre** 执行流程。
- 用户只说「合并到 beta」→ 本次只对 **beta** 执行流程。
- 用户同时说「先 pre 再 beta」或「pre 和 beta 都要」→ 按顺序执行两次（先 pre，再 beta），或询问用户本次先做哪一个。
- 用户未指明 pre 或 beta（例如只说「合并到预发分支」）→ 若项目里「预发」对应 pre，则用 `pre`；若有歧义则**询问用户**：合并到 pre 还是 beta？

## 适用场景

- 用户要求「把当前开发分支合并到 pre」「合并到 beta」「发布到 pre/beta」「同步 pre/beta」
- 需要将当前开发分支的代码合并进 **pre** 或 **beta** 并推送到远端

## 前置条件

- 当前仓库已关联远端，且当前在要合并的**开发分支**上
- 工作区无未提交更改（建议先 `git status` 检查），避免拉取/切换冲突

## 操作流程

按顺序执行以下步骤，每步失败时先解决再继续。下文中 `TARGET` 为 `pre` 或 `beta`（由用户说法确定，见上表）。

### 步骤 1：在当前开发分支拉取最新

- 记录当前分支名（即「开发分支」），后续合并与最后切回时要用：
  - 执行 `git branch --show-current` 得到分支名，记为 `DEV_BRANCH`
- 拉取当前分支远端最新：
  - `git pull origin $DEV_BRANCH`（或 `git pull`，若当前分支已跟踪远端）

### 步骤 2：切换到目标分支并拉取最新

- 切换分支：`git checkout $TARGET`
- 拉取目标分支最新：`git pull origin $TARGET`

### 步骤 3：合并开发分支到目标分支并推送

- 将步骤 1 的开发分支合并进当前分支（TARGET）：
  - `git merge $DEV_BRANCH`
- 若有冲突：解决冲突后 `git add`、`git commit`，再继续
- 推送到远端：`git push origin $TARGET`

### 步骤 4：切回开发分支

- 切换回原来的开发分支：`git checkout $DEV_BRANCH`

### 步骤 5：同步开发分支到远端

- 当前已在开发分支，先拉取远端最新（若有更新）：`git pull origin $DEV_BRANCH`
- 再推送本地分支到远端：`git push origin $DEV_BRANCH`

## 命令汇总（供复制执行）

- `DEV_BRANCH`：步骤 1 得到的当前分支名（如 `f/skill`）
- `TARGET`：本次目标分支，取 `pre` 或 `beta`（按用户说法，见上表）

```bash
# 1) 记录开发分支并拉取
DEV_BRANCH=$(git branch --show-current)
git pull origin "$DEV_BRANCH"

# 2) 切换到目标分支并拉取
git checkout "$TARGET"
git pull origin "$TARGET"

# 3) 合并并推送
git merge "$DEV_BRANCH"
git push origin "$TARGET"

# 4) 切回开发分支
git checkout "$DEV_BRANCH"

# 5) 同步开发分支到远端（先拉取再推送）
git pull origin "$DEV_BRANCH"
git push origin "$DEV_BRANCH"
```

## 注意事项

- 若 pre/beta 在远端被保护或需 MR/PR，则推送可能被拒绝，应改为在 Git 托管平台创建「开发分支 → 目标分支」的合并请求。
- 合并前可先执行 `git status` 和 `git stash` 处理本地未提交更改，避免拉取或切换失败。
