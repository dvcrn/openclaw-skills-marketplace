---
name: xhs-kit-publisher
description: "使用xhs-kit Python库高效发布小红书内容，无需浏览器，支持多账号和定时发布"
---

# xhs-kit 小红书发布技能

使用 `xhs-kit` Python库实现高效、稳定的小红书内容发布，无需打开浏览器，支持多账号管理和定时发布。

## 🎯 核心优势

| 特性 | 传统浏览器方式 | xhs-kit方式 |
|------|---------------|------------|
| **效率** | 低（3-5分钟） | ✅ **高（~60秒）** |
| **稳定性** | 低（浏览器崩溃） | ✅ **高** |
| **多账号** | ❌ 不支持 | ✅ **支持** |
| **资源占用** | 高（开浏览器） | ✅ **低** |
| **定时发布** | 需要外部调度 | ✅ **内置支持** |

## 📦 安装

```bash
# 1. 创建虚拟环境
python3 -m venv xhs-env
source xhs-env/bin/activate

# 2. 安装xhs-kit
pip install -U xhs-kit

# 3. 安装Playwright浏览器
playwright install chromium

# 4. 安装其他依赖
pip install pillow requests markdown pyyaml
```

## 🔑 快速开始

### 1. 登录小红书账号
```bash
# 终端二维码登录（推荐）
xhs-kit login-qrcode --terminal

# 或保存二维码图片
xhs-kit login-qrcode --save qrcode.png
```

### 2. 检查登录状态
```bash
xhs-kit status
```

### 3. 发布内容
```bash
# 基本发布
xhs-kit publish \
  --title "标题（不超过20字）" \
  --content "正文内容..." \
  --image /path/to/image.jpg \
  --tag "标签1" \
  --tag "标签2"

# 定时发布
xhs-kit publish \
  --title "标题" \
  --content "内容" \
  --schedule-at "2026-03-08T11:00:00+08:00"
```

## 📁 项目结构

```
xhs-kit-publisher/
├── SKILL.md                    # 本文档
├── publish_xhs.sh              # 发布脚本示例
├── xhs_kit_guide.md            # 完整使用指南
├── config/
│   ├── account1_cookies.json   # 账号1 cookies
│   └── account2_cookies.json   # 账号2 cookies
├── scripts/
│   ├── multi_account_publish.sh # 多账号发布脚本
│   └── schedule_publish.py     # 定时发布脚本
└── examples/
    ├── simple_publish.md       # 简单发布示例
    └── advanced_features.md    # 高级功能示例
```

## 🚀 核心功能

### 1. 多账号管理
```bash
# 登录不同账号
xhs-kit login-qrcode --terminal --cookies-file config/account1.json
xhs-kit login-qrcode --terminal --cookies-file config/account2.json

# 使用指定账号发布
xhs-kit publish --title "..." --cookies-file config/account1.json
```

### 2. 发布前验证
```bash
# debug模式验证（不实际发布）
xhs-kit debug-publish \
  --title "标题" \
  --content "内容" \
  --image image.jpg \
  --verbose
```

### 3. 批量发布
```bash
#!/bin/bash
# multi_publish.sh

CONTENT_FILE="content.txt"
IMAGES=("image1.jpg" "image2.jpg" "image3.jpg")

while IFS= read -r line; do
    title=$(echo "$line" | cut -d'|' -f1)
    content=$(echo "$line" | cut -d'|' -f2)
    tags=$(echo "$line" | cut -d'|' -f3)
    
    xhs-kit publish \
      --title "$title" \
      --content "$content" \
      --image "${IMAGES[RANDOM % ${#IMAGES[@]}]}" \
      --tag "$tags"
    
    sleep 60  # 避免频繁发布
done < "$CONTENT_FILE"
```

## ⚙️ 配置说明

### 环境变量
```bash
# 设置默认cookies文件
export XHS_COOKIES_FILE="~/.config/xhs-kit/cookies.json"

# 设置默认图片目录
export XHS_IMAGE_DIR="~/images/xiaohongshu"

# 设置发布间隔（秒）
export XHS_PUBLISH_INTERVAL=300
```

### 配置文件示例
```json
{
  "accounts": [
    {
      "name": "艺术分享账号",
      "cookies_file": "config/art_account.json",
      "tags": ["#艺术", "#创作", "#手工"],
      "publish_schedule": "0 10,15,20 * * *"
    },
    {
      "name": "生活分享账号", 
      "cookies_file": "config/life_account.json",
      "tags": ["#生活", "#日常", "#分享"],
      "publish_schedule": "0 12,18 * * *"
    }
  ],
  "default_image_size": "1242x1660",
  "quality": 95,
  "max_tags": 5
}
```

## 🔧 故障排除

### 常见问题
1. **登录失败**
   ```bash
   # 清除旧cookies重新登录
   rm -rf ~/.config/xhs-kit/
   xhs-kit login-qrcode --terminal
   ```

2. **发布失败**
   ```bash
   # 先测试debug模式
   xhs-kit debug-publish --title "测试" --image test.jpg --verbose
   
   # 检查图片格式和大小
   file test.jpg
   ls -lh test.jpg
   ```

3. **Cookies过期**
   ```bash
   # 检查登录状态
   xhs-kit status --verify
   
   # 重新登录
   xhs-kit logout
   xhs-kit login-qrcode --terminal
   ```

### 错误代码
- `ERR_NO_LOGIN`: 未登录，需要重新扫码
- `ERR_IMAGE_INVALID`: 图片格式或尺寸无效
- `ERR_TITLE_TOO_LONG`: 标题超过20字
- `ERR_NETWORK`: 网络问题，检查连接

## 📊 监控和日志

### 日志配置
```bash
# 发布时记录详细日志
xhs-kit publish --title "..." 2>&1 | tee -a publish.log

# 查看发布历史
grep -E "✅|❌|发布" publish.log | tail -20
```

### 状态监控
```bash
#!/bin/bash
# monitor_xhs.sh

# 检查登录状态
if xhs-kit status; then
    echo "✅ 登录状态正常"
else
    echo "❌ 需要重新登录"
    # 发送通知...
fi

# 检查今日发布次数
TODAY=$(date +%Y-%m-%d)
PUBLISH_COUNT=$(grep -c "$TODAY.*发布成功" publish.log 2>/dev/null || echo 0)
echo "今日已发布: $PUBLISH_COUNT 次"
```

## 🎯 最佳实践

### 1. 内容策略
- **标题**：不超过20字，吸引眼球
- **正文**：80-1000字，段落清晰
- **图片**：1242x1660像素，JPG/PNG格式
- **标签**：3-5个相关标签

### 2. 发布频率
- 新账号：每天1-2篇
- 成熟账号：每天2-3篇
- 多账号：错开发布时间

### 3. 安全策略
- 避免相同内容重复发布
- 使用不同图片和标题
- 保持自然发布间隔
- 定期更换cookies

## 📞 支持

### 常用命令速查
```bash
# 登录相关
xhs-kit login-qrcode --terminal      # 终端二维码登录
xhs-kit login-qrcode --save qr.png   # 保存二维码
xhs-kit status                       # 检查登录状态
xhs-kit logout                       # 退出登录

# 发布相关  
xhs-kit debug-publish --verbose      # 测试发布
xhs-kit publish                      # 实际发布
xhs-kit publish --schedule-at ...    # 定时发布

# 内容管理
xhs-kit search --keyword "关键词"    # 搜索内容
```

### 资源链接
- [xhs-kit GitHub](https://github.com/xxx/xhs-kit)
- [小红书发布规范](https://creator.xiaohongshu.com)
- [Pexels免费图片](https://www.pexels.com)

---

**使用此技能，你可以实现高效、稳定、可扩展的小红书内容发布，告别浏览器自动化的低效和不稳定问题！** 🚀