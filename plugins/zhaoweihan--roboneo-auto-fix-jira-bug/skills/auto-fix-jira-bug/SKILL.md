---
name: auto-fix-jira-bug
description: "自动修复 Jira Bug 的端到端流程。根据 Jira 链接获取 bug 详情与附件，分析是否属于本项目前端代码问题，修复代码并提交，合并到 pre 环境，最后更新 Jira 状态为已解决并打上 AI解决 标签。用户提供 Jira bug 链接时使用。"
---

# 自动修复 Jira Bug 并部署

## 适用场景

用户提供一个 Jira issue 链接（如 `https://jira.meitu.com/browse/ROB-2681`），要求自动修复该 bug、部署到 pre 环境并更新 Jira 状态。

## 前置条件

- 当前工作区为目标前端项目仓库，且在开发分支上
- 工作区无未提交更改（先 `git status` 检查）
- Omnibus MCP Server 已启用（提供 Jira 工具）
- `merge-dev-to-pre-or-beta` skill 可用

## 操作流程

按顺序执行以下 6 个步骤，每步完成后再进入下一步。

---

### 步骤 1：解析 Jira 链接并获取 Bug 详情

从用户提供的链接中提取 issue key（如 `ROB-2681`）。

1. 调用 `jira_get_issue` 获取 issue 详情（expand 设为 `editmeta,transitions`）：

```
CallMcpTool: server=user-Omnibus, toolName=jira_get_issue
arguments: { "issueKey": "<ISSUE_KEY>", "expand": "editmeta,transitions" }
```

2. 调用 `jira_get_attachments` 获取附件列表（截图、视频等）：

```
CallMcpTool: server=user-Omnibus, toolName=jira_get_attachments
arguments: { "issueKey": "<ISSUE_KEY>" }
```

3. 从返回结果中提取以下关键信息：
   - **标题**（summary）
   - **描述**（description）— bug 的文字描述
   - **重现步骤**（通常在 description 或自定义字段中）
   - **期望结果**与**实际结果**
   - **附件**（截图/视频 URL）— 尝试通过 WebFetch 或 Read 工具查看图片内容
   - **editmeta** — 记录可编辑字段及其 allowedValues，后续更新状态时需要
   - **transitions** — 记录可用的状态流转及其 ID，找到「已解决」对应的 transitionId

---

### 步骤 2：分析 Bug 是否属于本项目代码问题

根据步骤 1 获取的信息，结合项目代码进行分析：

1. **理解 bug 描述**：仔细阅读标题、描述、重现步骤、期望/实际结果
2. **查看附件**：如有截图或视频，通过工具查看以理解 bug 现象
3. **通过关键词定位代码**：先根据下方「关键词 → 代码位置映射」缩小搜索范围，再用 SemanticSearch / Grep / Glob 精确定位
4. **判断归属**：

| 判断结果 | 后续动作 |
|---------|---------|
| **是本项目前端代码 bug** | 继续步骤 3 |
| **非本项目 bug**（后端/其他项目/配置/环境问题） | **停止流程**，通知用户原因，并建议转给对应负责方 |
| **信息不足无法判断** | **暂停流程**，向用户说明需要补充的信息 |

---

### 关键词 → 代码位置映射

根据 bug 描述中的关键词，快速定位到对应的代码区域：

#### 业务模块

| 关键词 | 代码位置 | 说明 |
|--------|---------|------|
| 工作流、流程、flow、SOP | `packages/roboneo-sdk/src/pages/RoboneoFlow` 及子组件 | 工作流相关页面与逻辑 |
| 画布、canvas、无限画布、拖拽 | `packages/roboneo-sdk/src/pages/RoboneoCanvas` 及子组件 | 画布相关页面与逻辑 |
| Agent、智能体、对话 | `packages/roboneo-sdk/src/pages/RoboneoAgent` 及子组件 | Agent 相关页面与逻辑 |
| Agent 分享封面、分享封面页、share cover | `packages/roboneo-sdk/src/pages/RoboneoShareCover` 及子组件 | Agent 分享封面页 |
| Agent 分享、分享页、share | `packages/roboneo-sdk/src/pages/RoboneoShare` 及子组件 | Agent 分享页 |
| 工作流分享、流程分享、flow share | `packages/roboneo-sdk/src/pages/RoboneoFlowShare` 及子组件 | 工作流分享页 |

#### SDK / npm 包

| 关键词 | npm 包 | 说明 |
|--------|--------|------|
| 登录、注册、账号、鉴权、token | `@meitu/account` 相关包 | 账号 SDK |
| 订阅、会员、付费、套餐、权益 | `@meitu/subscribe` 相关包 | 订阅 SDK |
| 客服、反馈、工单、帮助 | `@meitu/feedback` 相关包 | 客服 SDK |
| JSBridge、端能力、Native、app 交互 | `@meitu/hogger` 相关包 | App 交互 SDK |
| 画布引擎、infinite-canvas、缩放、平移 | `@meitu/whee-infinite-canvas` 相关包 | 画布 SDK |
| 上传、文件上传、图片上传、upload | `@meitu/upload` 相关包 | 上传 SDK |

定位策略：
1. 先匹配关键词确定模块/SDK 范围
2. 若命中业务模块 → 在对应目录下搜索
3. 若命中 SDK 包 → 先在 `node_modules/<包名>` 中查看接口定义，再在项目代码中搜索该包的调用处
4. 若 bug 涉及 SDK 包内部逻辑（非调用方式问题）→ 该 bug 可能不属于本项目，**停止流程**并通知用户

---

### 步骤 3：修复 Bug

确认是本项目前端代码 bug 后，进行修复：

1. **定位根因**：根据步骤 2 的分析结果，精确定位出问题的代码位置
2. **制定修复方案**：在修改前先向用户简要说明修复思路
3. **实施修复**：使用编辑工具修改代码
4. **检查质量**：
   - 使用 ReadLints 检查修改后的文件是否有 linter 错误
   - 确认修复不会引入新问题
5. **记录修复信息**（供后续填写 Jira 使用）：
   - `BUG_CAUSE`：bug 产生原因（简明扼要）
   - `BUG_SOLUTION`：bug 解决方案（简明扼要）
   - `BUG_IMPACT`：bug 影响范围（如：影响哪些页面/功能/用户群）

完成修复后，**等待用户确认代码无误**（用户 keep 所有改动）后再进入步骤 4。

---

### 步骤 4：生成 Commit 并提交

用户确认全部代码改动后：

1. 执行 `git status` 和 `git diff` 查看变更
2. 生成 commit message，格式：

```
fix(<模块>): <简短描述>

<ISSUE_KEY>: <bug 标题>
- 原因: <BUG_CAUSE>
- 方案: <BUG_SOLUTION>
```

3. 提交 commit：

```bash
git add <changed_files>
git commit -m "<commit_message>"
```

---

### 步骤 5：合并到 pre 环境

调用 `merge-dev-to-pre-or-beta` skill，目标分支为 **pre**。

执行该 skill 的完整流程：
1. 记录当前开发分支并拉取最新
2. 切换到 pre 分支并拉取最新
3. 合并开发分支到 pre 并推送
4. 切回开发分支
5. 同步开发分支到远端

---

### 步骤 6：更新 Jira Bug 状态

合并成功后，更新 Jira issue：

#### 6.1 流转状态为「已解决」

先从步骤 1 获取的 transitions 中找到「已解决」/「Resolved」对应的 `transitionId`。

调用 `jira_transition_issue`：

```
CallMcpTool: server=user-Omnibus, toolName=jira_transition_issue
arguments: {
  "issueKey": "<ISSUE_KEY>",
  "transitionId": "<RESOLVED_TRANSITION_ID>",
  "fields": { ... },  // 根据 editmeta 填写必填字段
  "comment": "AI 自动修复并已部署到 pre 环境。\n原因: <BUG_CAUSE>\n方案: <BUG_SOLUTION>\n影响范围: <BUG_IMPACT>"
}
```

transition 时的 `fields` 需要根据步骤 1 获取的 editmeta 来构建，常见必填字段：
- **bug 产生原因**（对应 customfield，从 editmeta 中查找字段名包含「原因」的字段）
- **bug 解决方案**（对应 customfield，从 editmeta 中查找字段名包含「方案」或「解决」的字段）
- **bug 影响范围**（对应 customfield，从 editmeta 中查找字段名包含「影响」或「范围」的字段）

如果这些字段是 `option` 类型，从 `allowedValues` 中选择最匹配的值。
如果是 `string` 类型，直接填入文本。

#### 6.2 更新 issue 标签

调用 `jira_update_issue` 为 issue 添加标签 `AI解决`：

```
CallMcpTool: server=user-Omnibus, toolName=jira_update_issue
arguments: {
  "issueKey": "<ISSUE_KEY>",
  "fields": {
    "labels": ["AI解决", ...原有labels]
  }
}
```

注意：labels 是数组，需要保留原有标签并追加 `AI解决`，不要覆盖。

---

## 流程中断处理

| 中断情况 | 处理方式 |
|---------|---------|
| bug 不属于本项目 | 停止流程，通知用户并说明原因 |
| 信息不足无法分析 | 暂停流程，向用户说明需要补充的信息 |
| 修复方案不确定 | 向用户说明多种方案，由用户选择后继续 |
| 用户未 keep 代码改动 | 等待用户确认后再提交 commit |
| 合并冲突 | 尝试解决冲突，如无法自动解决则通知用户手动处理 |
| Jira 状态流转失败 | 通知用户手动操作，提供需要填写的信息 |

## 注意事项

- 修复代码时以前端代码为主，项目技术栈请根据实际仓库判断（React / React Native / Vue 等）
- commit message 使用 Conventional Commits 风格
- 操作 Jira 前务必先通过 `jira_get_issue`（expand=editmeta,transitions）获取元数据
- 更新 labels 时保留原有标签，追加 `AI解决`
- 整个流程中保持向用户汇报进度
