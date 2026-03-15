#!/bin/bash

# 读书心得点评 Skill 发布脚本
# 使用方法: ./publish.sh YOUR_GITHUB_TOKEN

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查参数
if [ -z "$1" ]; then
    echo -e "${RED}错误: 请提供 GitHub 个人访问令牌${NC}"
    echo "使用方法: ./publish.sh YOUR_GITHUB_TOKEN"
    echo ""
    echo "如何获取令牌:"
    echo "1. 访问 https://github.com/settings/tokens"
    echo "2. 点击 'Generate new token (classic)'"
    echo "3. 选择 'repo' 权限"
    echo "4. 生成并复制令牌"
    exit 1
fi

GITHUB_TOKEN=$1
REPO_NAME="openclaw-skill-book-review"
GITHUB_USER="jianghaidong"

echo -e "${YELLOW}🚀 开始发布读书心得点评 Skill...${NC}"
echo ""

# 步骤1: 验证 Git 仓库
echo -e "${YELLOW}步骤 1/5: 验证 Git 仓库...${NC}"
if [ ! -d ".git" ]; then
    echo -e "${RED}错误: 当前目录不是 Git 仓库${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Git 仓库验证通过${NC}"
echo ""

# 步骤2: 设置远程仓库
echo -e "${YELLOW}步骤 2/5: 设置远程仓库...${NC}"
git remote remove origin 2>/dev/null || true
git remote add origin "https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${REPO_NAME}.git"
echo -e "${GREEN}✓ 远程仓库设置完成${NC}"
echo ""

# 步骤3: 推送代码
echo -e "${YELLOW}步骤 3/5: 推送代码到 GitHub...${NC}"
git push -u origin main --force
echo -e "${GREEN}✓ 代码推送成功${NC}"
echo ""

# 步骤4: 创建标签
echo -e "${YELLOW}步骤 4/5: 创建版本标签...${NC}"
git tag -a "v1.0.0" -m "Release v1.0.0 - MVP版本" 2>/dev/null || echo "标签已存在"
git push origin "v1.0.0" --force
echo -e "${GREEN}✓ 标签创建成功${NC}"
echo ""

# 步骤5: 创建 Release
echo -e "${YELLOW}步骤 5/5: 创建 GitHub Release...${NC}"

RELEASE_DATA=$(cat <<EOF
{
  "tag_name": "v1.0.0",
  "name": "v1.0.0 - MVP版本发布 🎉",
  "body": "## 🎉 v1.0.0 - MVP版本发布\\n\\n读书心得点评 Skill 的第一个可用版本！\\n\\n### ✨ 功能特性\\n\\n- **智能解析**: 自动分析读书心得的主题、情感和关键词\\n- **笔记搜索**: 在你的笔记库中智能搜索相关内容\\n- **AI 生成**: 基于 DeepSeek API 生成有深度的扩展点评\\n- **个性化引用**: 引用你的笔记内容，提供个性化反馈\\n- **多格式输出**: 支持 Markdown、纯文本、HTML 格式\\n\\n### 🚀 快速开始\\n\\n\`\`\`bash\\n# 安装\\nnpm install -g openclaw-skill-book-review\\n\\n# 配置环境变量\\nexport DEEPSEEK_API_KEY=your-api-key\\nexport BOOK_REVIEW_NOTE_PATHS=~/Notes\\n\\n# 使用\\nbook-review \"《活着》让我明白了生命的坚韧\"\\n\`\`\`\\n\\n### 📄 许可证\\n\\nMIT License\\n\\n---\\n\\n**发布时间:** 2026-03-07\\n**作者:** Digital Partners Team (珍珠, 贝尔, 哈利, 喜羊羊)\\n**版本:** v1.0.0",
  "draft": false,
  "prerelease": false
}
EOF
)

curl -s -X POST \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Content-Type: application/json" \
  -d "${RELEASE_DATA}" \
  "https://api.github.com/repos/${GITHUB_USER}/${REPO_NAME}/releases" > /dev/null

echo -e "${GREEN}✓ Release 创建成功${NC}"
echo ""

# 完成
echo -e "${GREEN}🎉 发布完成！${NC}"
echo ""
echo "项目地址: https://github.com/${GITHUB_USER}/${REPO_NAME}"
echo "Release: https://github.com/${GITHUB_USER}/${REPO_NAME}/releases/tag/v1.0.0"
echo ""
echo "你可以:"
echo "1. 访问项目页面查看代码"
echo "2. 分享项目链接给朋友"
echo "3. 在社交媒体上宣传"
echo ""
echo -e "${YELLOW}感谢使用！${NC}"