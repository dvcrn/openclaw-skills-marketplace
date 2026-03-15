# GitHub 仓库设置指南

## 创建 GitHub 仓库

### 方法1: 使用 GitHub CLI
```bash
# 登录 GitHub
gh auth login

# 创建仓库
gh repo create openclaw-skill-book-review \
  --public \
  --description "将读书心得扩展成有深度的点评 - OpenClaw Skill" \
  --source=. \
  --remote=origin \
  --push
```

### 方法2: 手动创建
1. 访问 https://github.com/new
2. 填写仓库信息:
   - **Repository name**: `openclaw-skill-book-review`
   - **Description**: 将读书心得扩展成有深度的点评 - OpenClaw Skill
   - **Visibility**: Public
   - **Initialize**: 不要勾选 (已有本地仓库)
3. 点击 "Create repository"
4. 按照页面提示推送本地代码:
```bash
git remote add origin https://github.com/yourusername/openclaw-skill-book-review.git
git branch -M main
git push -u origin main
```

## 创建 Release

### 方法1: 使用 GitHub CLI
```bash
# 创建标签
git tag -a v1.0.0 -m "Release v1.0.0 - MVP版本"
git push origin v1.0.0

# 创建 Release
gh release create v1.0.0 \
  --title "v1.0.0 - MVP版本" \
  --notes "第一个可用版本，包含核心功能"
```

### 方法2: 手动创建
1. 访问仓库页面
2. 点击 "Releases" → "Create a new release"
3. 选择或创建标签: `v1.0.0`
4. 填写 Release 信息:
   - **Title**: v1.0.0 - MVP版本
   - **Description**: 
     ```
     ## v1.0.0 - MVP版本

     ### 功能特性
     - ✅ 智能解析读书心得
     - ✅ 搜索用户笔记库
     - ✅ AI 生成深度点评
     - ✅ 多格式输出支持

     ### 使用方法
     ```bash
     npm install -g openclaw-skill-book-review
     book-review "你的读书心得"
     ```

     ### 配置
     ```bash
     export DEEPSEEK_API_KEY=your-api-key
     export BOOK_REVIEW_NOTE_PATHS=~/Notes
     ```
     ```
5. 点击 "Publish release"

## 配置 GitHub Actions Secrets

在仓库设置中添加以下 Secrets:
- `DEEPSEEK_API_KEY`: DeepSeek API 密钥
- `NPM_TOKEN`: NPM 发布令牌 (用于自动发布)

## 后续维护

### 更新代码
```bash
git add .
git commit -m "描述更新内容"
git push origin main
```

### 发布新版本
```bash
# 更新版本号
npm version patch  # 或 minor, major

# 推送标签
git push origin main --tags

# GitHub Actions 会自动构建和发布
```