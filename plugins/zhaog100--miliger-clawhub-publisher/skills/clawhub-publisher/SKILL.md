---
name: clawhub-publisher
description: "ClawHub技能发布助手。在发布新技能前自动检查ClawHub/GitHub上的现有版本，对比实现思路，智能整合差异后发布/更新。Trigger on phrases like \"发布技能\", \"publish skill\", \"ClawHub发布\", \"检查技能版本\", \"整合技能更新\"."
---

# ClawHub Publisher

自动化ClawHub技能发布流程，确保版本一致性和代码质量。

## 核心理念

**"先检查后发布，智能整合，避免覆盖"**

发布前必须：
1. 检查ClawHub/GitHub现有版本
2. 对比实现思路和代码差异
3. 智能整合重要变更
4. 更新版本号后发布

## 工作流程

### 完整发布流程（推荐）

```bash
# 1. 检查现有版本
bash scripts/check-existing.sh <skill-name>

# 2. 对比差异（如果存在）
bash scripts/compare-versions.sh <skill-name>

# 3. 智能整合（如果有差异）
# 手动审查并合并重要变更

# 4. 发布/更新
bash scripts/publish.sh <skill-name> <version>
```

### 快速发布（新技能）

```bash
# 跳过检查，直接发布（仅适用于新技能）
bash scripts/publish.sh <skill-name> 1.0.0
```

### 更新现有技能

```bash
# 1. 检查+对比+下载
bash scripts/update.sh <skill-name>

# 2. 手动整合差异
# 3. 更新版本号后发布
bash scripts/publish.sh <skill-name> x.y.z
```

## 脚本说明

### 1. check-existing.sh - 检查现有版本

**功能**：
- 检查ClawHub是否存在该技能
- 检查GitHub仓库是否存在该技能
- 返回版本信息和所有者

**用法**：
```bash
bash scripts/check-existing.sh <skill-name>
```

**输出示例**：
```
ClawHub: 已存在
  - 版本: 3.4.0
  - 所有者: zhaog100
  - Package ID: k97d4m6m5hpwd33g64j2g12zxs82ezj1

GitHub: 未找到
```

**退出码**：
- 0：不存在（可以发布）
- 1：存在且所有者是当前用户（需要更新）
- 2：存在但所有者不是当前用户（需要换slug或放弃）

### 2. compare-versions.sh - 对比版本差异

**功能**：
- 下载ClawHub最新版本到临时目录
- 对比本地版本和远程版本
- 生成差异报告（文件、行数、功能）

**用法**：
```bash
bash scripts/compare-versions.sh <skill-name>
```

**输出示例**：
```
=== 版本对比报告 ===
本地版本: 3.5.0
远程版本: 3.4.0

=== 文件差异 ===
+ scripts/new-feature.sh (新增)
~ SKILL.md (+45 -12)
~ scripts/main.sh (+120 -80)

=== 功能差异 ===
+ 新增功能A
- 移除功能B
~ 优化功能C

=== 建议 ===
需要整合：远程版本有重要的bug修复
```

### 3. publish.sh - 发布技能

**功能**：
- 验证技能结构（SKILL.md必需）
- 检查版本号格式
- 自动添加acceptLicenseTerms
- 上传到ClawHub

**用法**：
```bash
bash scripts/publish.sh <skill-path> <version>
```

**示例**：
```bash
# 发布新技能
bash scripts/publish.sh ./skills/my-skill 1.0.0

# 更新现有技能
bash scripts/publish.sh ./skills/my-skill 2.1.0
```

**注意事项**：
- 需要修改 `/usr/lib/node_modules/clawhub/dist/cli/commands/publish.js` 添加 `acceptLicenseTerms: true`
- 详细步骤见 references/clawhub-api.md

### 4. update.sh - 更新技能

**功能**：
- 一键检查+对比+下载
- 自动合并简单差异
- 标记复杂冲突

**用法**：
```bash
bash scripts/update.sh <skill-name>
```

## 版本管理规范

### 版本号格式

```
MAJOR.MINOR.PATCH
```

- **MAJOR**：重大更新（不兼容的API变更）
- **MINOR**：功能更新（向后兼容）
- **PATCH**：Bug修复（向后兼容）

### 更新规则

1. **首次发布**：1.0.0
2. **功能更新**：x.y.0 → x.(y+1).0
3. **Bug修复**：x.y.z → x.y.(z+1)
4. **重大更新**：x.0.0 → (x+1).0.0

### 命名规范

- **官方技能**：`<功能名>`（如：github、weather）
- **个人定制**：`miliger-<功能名>`（如：miliger-playwright-scraper）

## 整合策略

### 优先级判断

1. **远程优先**：远程版本有重要bug修复或安全更新
2. **本地优先**：本地版本有新功能或重大改进
3. **合并**：两者都有重要更新，需要智能合并

### 整合步骤

1. **下载远程版本**：`clawhub install <slug>`
2. **对比差异**：`bash scripts/compare-versions.sh <slug>`
3. **审查变更**：手动审查每个差异文件
4. **合并重要变更**：保留重要的bug修复和新功能
5. **更新版本号**：根据变更类型更新版本
6. **测试验证**：测试整合后的功能
7. **发布更新**：`bash scripts/publish.sh <path> <version>`

## 常见场景处理

### 场景1：发布新技能

```bash
# 1. 检查是否存在
bash scripts/check-existing.sh my-skill
# 输出：不存在

# 2. 直接发布
bash scripts/publish.sh ./skills/my-skill 1.0.0
```

### 场景2：更新自己的技能

```bash
# 1. 检查现有版本
bash scripts/check-existing.sh my-skill
# 输出：存在，所有者是zhaog100

# 2. 对比差异
bash scripts/compare-versions.sh my-skill

# 3. 整合变更
# （手动审查并合并）

# 4. 发布更新
bash scripts/publish.sh ./skills/my-skill 2.0.0
```

### 场景3：发现同名技能（非自己）

```bash
# 1. 检查现有版本
bash scripts/check-existing.sh my-skill
# 输出：存在，所有者不是zhaog100

# 2. 选择方案
# 方案A：使用不同slug
bash scripts/publish.sh ./skills/my-skill 1.0.0 --slug miliger-my-skill

# 方案B：放弃发布（避免重复）
echo "已存在同名技能，放弃发布"
```

## 参考文档

- **references/clawhub-api.md** - ClawHub CLI详细使用指南
- **references/git-workflow.md** - Git协作工作流程
- **references/best-practices.md** - 技能发布最佳实践

## 注意事项

1. **发布前必检查**：避免覆盖他人工作
2. **版本号规范**：遵循语义化版本规范
3. **测试验证**：发布前务必测试
4. **文档更新**：重要变更需更新CHANGELOG
5. **备份本地**：整合前备份本地版本

## 故障排除

### 问题1：acceptLicenseTerms错误

**原因**：ClawHub CLI v0.7.0 缺少此字段

**解决**：修改 publish.js 添加 acceptLicenseTerms: true

详细步骤见 references/clawhub-api.md

### 问题2：文件过多导致发布失败

**原因**：包含venv、node_modules等大目录

**解决**：创建 .clawhubignore 文件

```
venv/
node_modules/
__pycache__/
*.log
logs/
```

### 问题3：版本冲突无法合并

**原因**：远程和本地都有重大变更

**解决**：
1. 手动审查每个冲突文件
2. 保留重要功能
3. 测试整合后的版本
4. 发布为新的MAJOR版本

## 示例：完整发布流程

```bash
# 场景：发布 session-memory-enhanced v4.0.1

# 1. 检查现有版本
cd /root/.openclaw/workspace/skills/clawhub-publisher
bash scripts/check-existing.sh session-memory-enhanced
# 输出：存在，所有者zhaog100，版本4.0.0

# 2. 对比差异
bash scripts/compare-versions.sh session-memory-enhanced
# 输出：本地有新功能（+3个文件），远程无更新

# 3. 发布更新
bash scripts/publish.sh ../session-memory-enhanced 4.0.1
# 输出：发布成功，Package ID: k97carwxs0htme5y071ye69ykx82mmwg

# 4. 验证
clawhub inspect session-memory-enhanced
# 输出：版本4.0.1，已发布
```
