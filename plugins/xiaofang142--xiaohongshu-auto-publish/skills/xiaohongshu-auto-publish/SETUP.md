# 📱 小红书自动发布 Skill - 配置指南

> 技能已创建完成，需要完成以下配置步骤

---

## ✅ 已完成的配置

| 项目 | 状态 | 位置 |
|------|------|------|
| **Skill 目录** | ✅ 已创建 | `skills/xiaohongshu-auto-publish/` |
| **SKILL.md** | ✅ 已创建 | 描述文件 |
| **skill.py** | ✅ 已创建 | 主程序 |
| **README.md** | ✅ 已创建 | 使用说明 |
| **publish.sh** | ✅ 已创建 | 发布脚本 |
| **技能封面** | ✅ 已生成 | `assets/cover.png` |

---

## 🔧 需要完成的配置

### 1. 登录 ClawHub

```bash
clawhub login
```

### 2. 发布到 ClawHub

```bash
cd /Users/xiaofang/.openclaw/workspace-taizi/skills/xiaohongshu-auto-publish
clawhub publish .
```

### 3. 设置 SkillPay 产品

访问：https://skillpay.me/dashboard/products

创建新产品：
- **名称：** 小红书自动发布技能
- **描述：** 一键发布小红书笔记 - AI 文案 + 中国风封面
- **价格：** ¥0.01
- **产品 ID：** xhs_auto_publish

### 4. 更新 SkillPay API 配置

编辑 `skill.py`，确认 API Key 正确：

```python
SKILLPAY_API_KEY = "sk_4eacbcc9e4411bd1490794b27867199f9801e3150b4c354541e6a2927931a06e"
```

### 5. 设置收费

```bash
clawhub set-price xiaohongshu-auto-publish --price 0.01
```

---

## 📋 使用流程

### 用户购买流程

1. 访问 SkillPay 产品页面
2. 支付 ¥0.01
3. 获取支付 Token
4. 运行技能

### 用户使用方法

```bash
# 付费使用
python skill.py "发布主题" --user-id YOUR_ID --payment-token YOUR_TOKEN

# 测试模式（跳过支付）
python skill.py "发布主题" --skip-payment
```

---

## 💰 收费模式

| 项目 | 设置 |
|------|------|
| **单次价格** | ¥0.01 |
| **计费方式** | 按次计费 |
| **支付平台** | SkillPay |
| **收款账户** | 皇上绑定的账户 |

---

## 📊 收入预估

| 每日发布 | 月收入 | 年收入 |
|---------|--------|--------|
| 10 次 | ¥3 | ¥1095 |
| 50 次 | ¥15 | ¥5475 |
| 100 次 | ¥30 | ¥10950 |

---

## ⚠️ 注意事项

1. **SkillPay 配置** - 需要确认 API 路径和认证方式
2. **ClawHub 登录** - 发布前需要登录
3. **测试模式** - 使用 `--skip-payment` 测试功能
4. **收款账户** - 确保 SkillPay 绑定了正确的收款账户

---

## 🆘 问题排查

### SkillPay API 404

可能 API 路径不正确，检查：
- API 文档：https://skillpay.me/api/docs
- 尝试不同路径：`/api/v1/products` 或 `/products`

### ClawHub 发布失败

```bash
# 确认登录
clawhub login

# 确认路径
cd skills/xiaohongshu-auto-publish
clawhub publish .
```

### 技能运行失败

```bash
# 检查依赖
pip install pillow requests

# 检查 MCP 登录
cd ~/.openclaw/workspace/skills/xiaohongshu-mcp/bin
./xiaohongshu-login-darwin-arm64
```

---

*配置时间：2026-03-05*
*版本：1.0.0*
