# 技能发布最佳实践

## 概述

本文档总结了在 ClawHub 发布和管理技能的最佳实践，帮助避免常见问题，提高发布效率。

## 核心原则

### 1. 先检查后发布

**永远不要**直接发布新技能，**必须先检查**是否已存在。

```bash
# 正确流程
bash scripts/check-existing.sh my-skill
# 输出：不存在 → 可以发布
# 输出：存在（自己的） → 需要更新
# 输出：存在（他人的） → 换slug或放弃

bash scripts/publish.sh ./skills/my-skill 1.0.0
```

### 2. 版本号语义化

遵循 [语义化版本 2.0.0](https://semver.org/) 规范。

```
MAJOR.MINOR.PATCH

MAJOR - 重大更新（不兼容的API变更）
MINOR - 功能更新（向后兼容）
PATCH - Bug修复（向后兼容）
```

**示例**：
```
1.0.0 → 1.0.1  # Bug修复
1.0.1 → 1.1.0  # 新功能
1.1.0 → 2.0.0  # 重大更新
```

### 3. 文件最小化

**只包含必需的文件**，排除不必要的依赖。

**使用 .clawhubignore**：

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

**原因**：
- 减少上传时间
- 避免发布失败（文件过多）
- 提高下载速度

## 发布前检查清单

### 1. 文件结构

```bash
my-skill/
├── SKILL.md          # ✅ 必需
├── package.json      # ✅ 推荐（版本管理）
├── scripts/          # ⚡ 脚本
├── references/       # 📚 参考文档
├── assets/           # 🎨 资源文件
└── .clawhubignore    # ✅ 必需（排除文件）
```

### 2. SKILL.md 验证

```bash
# 检查必需字段
grep -E "^name:|^description:" SKILL.md
```

**必需字段**：
- `name`：技能名称
- `description`：技能描述

**建议字段**：
- 清晰的功能说明
- 使用示例
- 触发条件

### 3. 版本号检查

```bash
# 检查版本号格式
VERSION=$(grep -oP 'version["\s:]+\K[\d.]+' package.json 2>/dev/null)
if [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "✅ 版本号格式正确: $VERSION"
else
    echo "❌ 版本号格式错误: $VERSION"
fi
```

### 4. 功能测试

```bash
# 测试核心脚本
bash scripts/main.sh --test

# 测试SKILL.md示例
# 手动验证SKILL.md中的示例命令是否有效
```

## 发布流程

### 标准流程（推荐）

```bash
# 1. 检查现有版本
bash scripts/check-existing.sh my-skill

# 2. 测试功能
bash scripts/main.sh --test

# 3. 更新版本号
# 修改 package.json 中的版本号

# 4. 提交Git
git add .
git commit -m "chore: bump version to x.y.z"
git tag -a vx.y.z -m "Version x.y.z"
git push origin main --tags

# 5. 发布到ClawHub
bash scripts/publish.sh . x.y.z

# 6. 验证发布
clawhub inspect my-skill
```

### 快速流程（仅适用于新技能）

```bash
# 1. 检查是否存在
bash scripts/check-existing.sh my-skill
# 输出：不存在

# 2. 直接发布
bash scripts/publish.sh . 1.0.0
```

## 更新流程

### 整合远程更新

```bash
# 1. 下载远程版本
bash scripts/update.sh my-skill

# 2. 查看差异
git diff

# 3. 合并重要变更
# 手动审查并合并

# 4. 测试
bash scripts/main.sh --test

# 5. 更新版本号
# 修改 package.json

# 6. 发布
bash scripts/publish.sh . x.y.z
```

## 常见问题

### 问题1：发布失败 - acceptLicenseTerms

**症状**：
```
Error: acceptLicenseTerms: invalid value
```

**原因**：ClawHub CLI v0.7.0 缺少此字段

**解决**：
```bash
# 修改 publish.js
sudo sed -i "s/form\.set('payload', JSON\.stringify({/form.set('payload', JSON.stringify({\n        acceptLicenseTerms: true,/" /usr/lib/node_modules/clawhub/dist/cli/commands/publish.js
```

### 问题2：发布失败 - 文件过多

**症状**：
```
Error: SKILL.md required
```

**真实原因**：文件数量超过限制（误导性错误）

**解决**：
```bash
# 创建 .clawhubignore
cat > .clawhubignore << 'EOF'
venv/
node_modules/
__pycache__/
*.log
EOF
```

### 问题3：版本冲突

**症状**：远程和本地都有重大更新

**解决**：
```bash
# 1. 下载远程版本
bash scripts/update.sh my-skill

# 2. 手动合并冲突
# 审查每个冲突文件，保留重要功能

# 3. 充分测试
bash scripts/main.sh --test

# 4. 发布为新的MAJOR版本
bash scripts/publish.sh . 2.0.0
```

### 问题4：同名技能已存在

**症状**：
```
检查结果：存在，所有者不是zhaog100
```

**解决方案A**：使用不同slug
```bash
bash scripts/publish.sh . 1.0.0 --slug miliger-my-skill
```

**解决方案B**：放弃发布
```bash
echo "已存在同名技能，放弃发布"
```

## 命名规范

### 技能名称

**格式**：`[namespace-]feature-name`

**示例**：
```
github                  # 官方技能
weather                 # 官方技能
miliger-playwright      # 个人定制
session-memory-enhanced # 功能增强版
```

**规则**：
- 小写字母、数字、连字符
- 长度 < 64字符
- 避免特殊字符

### 版本标签

**格式**：`vMAJOR.MINOR.PATCH`

**示例**：
```
v1.0.0  # 首次发布
v1.1.0  # 功能更新
v2.0.0  # 重大更新
```

## 质量保证

### 代码质量

1. **Shell脚本**：
   - 使用 `shellcheck` 检查
   - 添加错误处理 `set -e`
   - 提供帮助信息

2. **Python脚本**：
   - 遵循 PEP 8 规范
   - 添加文档字符串
   - 编写单元测试

3. **SKILL.md**：
   - 清晰的描述
   - 完整的示例
   - 触发条件

### 测试覆盖

```bash
# 功能测试
bash scripts/main.sh --test

# 集成测试
bash scripts/main.sh --integration-test

# 回归测试
bash scripts/main.sh --regression-test
```

### 文档完整性

- ✅ SKILL.md（必需）
- ❌ README.md（不需要）
- ❌ CHANGELOG.md（不需要）
- ✅ 代码注释（推荐）

## 性能优化

### 文件压缩

```bash
# 压缩大型资源
gzip -9 assets/large-file.txt

# 优化图片
optipng assets/icon.png
```

### 依赖最小化

```bash
# 只安装必需依赖
pip install --no-deps package-name

# 使用虚拟环境
python -m venv venv
source venv/bin/activate
pip install package-name
```

## 安全考虑

### 敏感信息

**永远不要**包含：
- API密钥
- 密码
- 私钥
- 个人信息

**使用环境变量**：
```bash
# .env 文件（已排除）
API_KEY=your-api-key

# 脚本中读取
API_KEY=${API_KEY:-default-value}
```

### 权限控制

```bash
# 脚本不应要求root权限
# 如果必需，明确说明

# 文件权限
chmod +x scripts/main.sh
chmod 644 SKILL.md
```

## 发布后维护

### 监控反馈

```bash
# 检查下载量
clawhub stats my-skill

# 查看Issue
gh issue list --repo openclaw/clawhub

# 回复评论
gh issue comment <issue-number> --body "已修复，将在下个版本发布"
```

### 定期更新

```bash
# 每月检查依赖更新
pip list --outdated
npm outdated

# 每季度检查ClawHub更新
bash scripts/update.sh my-skill
```

### 版本退役

```bash
# 标记为deprecated
# 在SKILL.md中添加：
# > ⚠️ 此技能已弃用，请使用 new-skill-name

# 发布最后版本
bash scripts/publish.sh . 99.99.99
```

## 示例：完整发布流程

```bash
#!/bin/bash
# complete-release.sh - 完整发布流程

SKILL_NAME="my-skill"
NEW_VERSION="2.1.0"

# 1. 检查现有版本
echo "【1/7】检查现有版本..."
bash scripts/check-existing.sh "$SKILL_NAME"

# 2. 运行测试
echo "【2/7】运行测试..."
bash scripts/main.sh --test || exit 1

# 3. 更新版本号
echo "【3/7】更新版本号..."
sed -i "s/version.*:.*/version\": \"$NEW_VERSION\",/" package.json

# 4. 提交Git
echo "【4/7】提交Git..."
git add .
git commit -m "chore: release v$NEW_VERSION"
git tag -a "v$NEW_VERSION" -m "Release v$NEW_VERSION"

# 5. 推送到远程
echo "【5/7】推送到远程..."
git push origin main --tags

# 6. 发布到ClawHub
echo "【6/7】发布到ClawHub..."
bash scripts/publish.sh . "$NEW_VERSION"

# 7. 验证发布
echo "【7/7】验证发布..."
clawhub inspect "$SKILL_NAME"

echo "✅ 发布完成！"
```

## 参考资源

- ClawHub 官网：https://clawhub.com
- 语义化版本：https://semver.org/
- 提交信息规范：https://www.conventionalcommits.org/
- ShellCheck：https://www.shellcheck.net/
- PEP 8：https://pep8.org/
