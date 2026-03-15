# 提交前检查清单 (Pre-Commit Checklist)

每次提交代码到 Git 仓库前，请按此清单逐项检查，确保代码质量和安全性。

## 📋 基础检查 (必做)

### 1. ✅ Git 状态检查
```bash
# 检查当前状态
git status --short

# 预期结果:
# - 只有预期的文件被修改
# - 没有意外的大文件
# - 没有临时/测试文件
```

### 2. ✅ 敏感信息检查
```bash
# 检查是否包含敏感信息
grep -r "password\|token\|secret\|key\|api_key\|private" . --include="*.json" --include="*.js" --include="*.sh" --include="*.md" 2>/dev/null | grep -v "test\|example\|dummy"

# 预期结果:
# - 无真实的 API 密钥、密码等
# - 配置文件中的占位符正确 (如 "YOUR_API_KEY_HERE")
```

### 3. ✅ .gitignore 检查
```bash
# 检查 .gitignore 是否包含必要规则
cat .gitignore | grep -E "backup|node_modules|.env|log|tmp|test" || echo "警告: .gitignore 可能不完整"

# 预期包含:
# - backup-*/ (备份目录)
# - node_modules/ (依赖包)
# - *.log (日志文件)
# - *.tmp (临时文件)
# - .env (环境变量)
# - 其他项目特定忽略规则
```

## 🛡️ 安全审查 (必做)

### 4. ✅ 密钥和凭证
- [ ] **无硬编码密钥**: 配置文件使用环境变量或占位符
- [ ] **无个人访问令牌**: GitHub、API 等 token 已移除
- [ ] **无数据库密码**: 连接字符串中的密码已移除
- [ ] **无服务账户密钥**: 云服务密钥已移除

### 5. ✅ 配置文件审查
```bash
# 检查配置文件中是否有敏感信息
find . -name "*.json" -o -name "*.yaml" -o -name "*.yml" -o -name "*.config" -o -name "*.conf" 2>/dev/null | xargs grep -l "password\|secret\|token" 2>/dev/null || echo "✅ 配置文件检查通过"
```

### 6. ✅ 脚本安全审查
- [ ] **无硬编码路径**: 使用变量或相对路径
- [ ] **权限检查**: 脚本有适当的执行权限 (`chmod +x`)
- [ ] **输入验证**: 脚本有基本的输入验证
- [ ] **错误处理**: 脚本有适当的错误处理

## 📦 版本管理 (必做)

### 7. ✅ 版本号更新
```bash
# 检查 package.json 版本号
grep '"version"' package.json

# 预期结果:
# - 版本号已根据需要更新 (语义化版本)
# - 如果是功能更新，增加 minor 版本 (1.x.0 → 1.x+1.0)
# - 如果是 bug 修复，增加 patch 版本 (1.0.x → 1.0.x+1)
# - 如果是重大变更，增加 major 版本 (x.0.0 → x+1.0.0)
```

### 8. ✅ 变更日志更新
```bash
# 检查是否有 CHANGELOG.md 或类似文件
if [ -f "CHANGELOG.md" ]; then
    echo "请更新 CHANGELOG.md"
    # 检查最近更改是否已记录
    git diff HEAD~1 --name-only | head -5
fi
```

## 📚 文档更新 (推荐)

### 9. ✅ README 更新
- [ ] **功能描述**: 新增功能是否在 README 中描述
- [ ] **安装步骤**: 安装步骤是否仍然正确
- [ ] **使用示例**: 是否有适当的使用示例
- [ ] **配置说明**: 配置选项是否文档化

### 10. ✅ SKILL.md 更新
- [ ] **技能描述**: 技能描述是否准确
- [ ] **功能列表**: 所有功能是否列出
- [ ] **使用场景**: 使用场景是否清晰
- [ ] **示例代码**: 是否有足够的示例

## 🔧 代码质量 (推荐)

### 11. ✅ 脚本可执行性
```bash
# 检查脚本是否有执行权限
find scripts -name "*.sh" -type f -exec test ! -x {} \; -print 2>/dev/null | while read file; do
    echo "警告: $file 不可执行"
done
```

### 12. ✅ 文件结构
- [ ] **目录结构**: 文件组织是否合理
- [ ] **命名规范**: 文件名是否符合约定
- [ ] **冗余文件**: 无重复或无用文件
- [ ] **备份清理**: 备份文件已从 Git 中移除

### 13. ✅ 测试文件
- [ ] **测试文件**: 测试文件已从提交中排除 (在 .gitignore)
- [ ] **临时文件**: 无临时文件被提交
- [ ] **开发文件**: 开发环境文件已排除

## 🚀 提交前最后检查

### 14. ✅ 最终 Git 检查
```bash
# 查看要提交的文件
git diff --cached --name-only

# 预期:
# - 只有必要的文件
# - 文件数量合理
# - 无意外的大文件 (>10MB)

# 查看更改内容摘要
git diff --cached --stat
```

### 15. ✅ 提交信息规范
- [ ] **信息格式**: 符合约定 (类型: 描述)
- [ ] **类型正确**: feat/fix/docs/style/refactor/test/chore
- [ ] **描述清晰**: 简明描述更改内容
- [ ] **详细说明**: 重要更改有详细说明

## 📝 提交信息模板

推荐使用以下格式：
```
类型: 简短描述

详细描述（可选）：
- 更改了哪些内容
- 为什么进行这些更改
- 可能的影响

修复的问题（如适用）：
- #123: 具体问题描述

BREAKING CHANGE（如有重大变更）：
- 描述重大变更内容
```

**类型说明**:
- `feat`: 新功能
- `fix`: bug 修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 维护任务

## 🔄 自动化检查脚本

创建 `check-before-commit.sh` 脚本自动检查：

```bash
#!/bin/bash
# 提交前自动检查脚本

echo "🔍 开始提交前检查..."
echo

# 1. Git 状态
echo "1. Git 状态:"
git status --short
echo

# 2. 敏感信息检查
echo "2. 敏感信息检查:"
grep -r "password=\|token=\|secret=\|key=" . --include="*.json" --include="*.js" --include="*.sh" 2>/dev/null | grep -v "test\|example" || echo "✅ 未发现敏感信息"
echo

# 3. 版本号检查
echo "3. 版本号检查:"
grep '"version"' package.json 2>/dev/null || echo "⚠️  无 package.json 或版本信息"
echo

# 4. .gitignore 检查
echo "4. .gitignore 检查:"
if [ -f ".gitignore" ]; then
    echo "✅ .gitignore 文件存在"
    grep -q "backup" .gitignore && echo "✅ 包含备份规则" || echo "⚠️  缺少备份规则"
else
    echo "❌ 无 .gitignore 文件"
fi
echo

echo "📋 检查完成，请根据以上结果决定是否提交。"
```

## 🎯 快速检查命令

将以下命令保存为 `quick-check.sh`：

```bash
#!/bin/bash
echo "🚀 快速提交前检查"

# 运行检查
./check-before-commit.sh

# 询问是否继续
read -p "是否继续提交? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "请输入提交信息:"
    read commit_msg
    git commit -m "$commit_msg"
else
    echo "提交取消"
fi
```

## 📌 重要提醒

### 永远不要提交：
1. **真实密钥和密码**
2. **个人访问令牌**
3. **服务账户文件**
4. **大型二进制文件** (>10MB)
5. **临时和测试文件**
6. **IDE 配置文件** (如 .vscode/, .idea/)
7. **操作系统特定文件** (如 .DS_Store, thumbs.db)

### 提交前必问：
1. **这些更改安全吗？** (无敏感信息泄露风险)
2. **这些更改必要吗？** (每个文件都有提交理由)
3. **文档更新了吗？** (README, SKILL.md 等)
4. **版本号更新了吗？** (package.json)
5. **测试通过了吗？** (如果有测试)

## 🆘 紧急情况处理

如果意外提交了敏感信息：
1. **立即撤销提交**: `git reset --soft HEAD~1`
2. **从历史中删除**: 使用 `git filter-branch` 或 BFG Repo-Cleaner
3. **轮换密钥**: 立即轮换所有泄露的密钥
4. **通知相关人员**: 如果涉及团队，立即通知

---

**使用此清单，确保每次提交都是安全、高质量的！** 🛡️

*最后更新: 2026-03-08*