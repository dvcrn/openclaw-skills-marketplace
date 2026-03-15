# 小红书自动发布技能

> 一键发布小红书笔记 - AI 文案 + 中国风封面 + 自动发布

## 🎯 功能特点

- ✅ AI 智能文案（700-800 字）
- ✅ 中国风古典插画封面
- ✅ 自动发布到小红书
- ✅ 字数自动优化
- ✅ 排版精美
- ✅ 零 API 成本

## 💰 收费说明

- **价格：** ¥0.01/次
- **支付平台：** SkillPay
- **计费方式：** 按发布次数

## 📋 使用方法

### 1. 购买使用权限

访问：https://skillpay.me/p/xiaohongshu-auto-publish

支付 ¥0.01 获取使用 Token

### 2. 使用技能

```bash
# 基础用法
python skill.py "发布主题" --user-id YOUR_USER_ID --payment-token YOUR_TOKEN

# 测试模式（跳过支付）
python skill.py "发布主题" --skip-payment
```

### 3. 示例

```bash
# 发布 OpenClaw 教程
python skill.py "OpenClaw 安装教程" --user-id xxx --payment-token xxx

# 发布效率工具推荐
python skill.py "效率工具推荐" --user-id xxx --payment-token xxx
```

## 📦 系统要求

- Python 3.8+
- Pillow (PIL)
- requests
- xiaohongshu-mcp 已配置
- 小红书已登录

## 🔧 安装依赖

```bash
pip install pillow requests
```

## 📁 文件结构

```
xiaohongshu-auto-publish/
├── SKILL.md           # Skill 描述
├── skill.py           # 主程序
├── README.md          # 使用说明
└── assets/            # 资源文件
    └── cover.png      # 技能封面
```

## 🎨 输出内容

每次发布包含：

1. **封面图** - 中国风古典插画（720x1280）
2. **文案** - AI 生成（700-800 字）
3. **标签** - 10 个精准标签
4. **发布结果** - 成功/失败反馈

## ⚠️ 注意事项

1. 需要先登录小红书 MCP
2. 支付 Token 一次有效
3. 建议每日发布≤3 篇
4. 内容需符合平台规范

## 🆘 问题反馈

遇到问题请联系：
- Skill 作者：太子
- 邮箱：support@example.com

## 📄 许可证

MIT License

---

*版本：1.0.0*
*最后更新：2026-03-05*
