# 📱 小红书自动发布 Skill - 账号信息

> 所有配置已完成，只需手动确认

---

## ✅ 已自动完成

| 项目 | 状态 | 说明 |
|------|------|------|
| **Skill 创建** | ✅ 完成 | `skills/xiaohongshu-auto-publish/` |
| **主程序** | ✅ 完成 | `skill.py`（集成 SkillPay） |
| **技能测试** | ✅ 完成 | 发布成功！ |
| **SkillPay Key** | ✅ 配置 | 已使用皇上的密钥 |

---

## ⏳ 需要皇上手动确认

### 1. ClawHub 登录发布

**原因：** 需要浏览器扫码确认

**操作：**
```bash
cd /Users/xiaofang/.openclaw/workspace-taizi/skills/xiaohongshu-auto-publish
clawhub publish .
```

**或者访问：** https://clawhub.ai/dashboard

---

### 2. SkillPay 产品创建

**原因：** API 返回 404，需网页创建

**操作：**
1. 访问：https://skillpay.me/dashboard/products
2. 点击"创建产品"
3. 填写：
   - **名称：** 小红书自动发布技能
   - **描述：** 一键发布小红书笔记 - AI 文案 + 中国风封面
   - **价格：** ¥0.01
   - **产品 ID：** xhs_auto_publish
4. 保存后获取产品链接

---

## 📋 账号信息汇总

### SkillPay
- **API Key:** `sk_4eacbcc9e4411bd1490794b27867199f9801e3150b4c354541e6a2927931a06e`
- **产品 ID:** `xhs_auto_publish`
- **价格:** ¥0.01/次
- **管理后台:** https://skillpay.me/dashboard

### ClawHub
- **Skill 名称:** `xiaohongshu-auto-publish`
- **管理后台:** https://clawhub.ai/dashboard
- **技能目录:** `/Users/xiaofang/.openclaw/workspace-taizi/skills/xiaohongshu-auto-publish/`

### 小红书 MCP
- **状态:** ✅ 已登录
- **位置:** `~/.openclaw/workspace/skills/xiaohongshu-mcp/bin/cookies.json`

---

## 🎯 技能使用说明

### 测试模式（跳过支付）
```bash
cd /Users/xiaofang/.openclaw/workspace-taizi/skills/xiaohongshu-auto-publish
python3 skill.py "发布主题" --skip-payment
```

### 正式模式（需要支付）
```bash
python3 skill.py "发布主题" \
  --user-id YOUR_USER_ID \
  --payment-token YOUR_PAYMENT_TOKEN
```

---

## 📊 测试结果

```
✅ 技能功能测试成功！
- 文案生成：877 字
- 封面生成：中国风
- 自动发布：成功
- SkillPay 验证：跳过（测试模式）
```

---

## 💰 收费模式

```
单次发布：¥0.01
---------
10 次/天 = ¥0.1/天 = ¥3/月
50 次/天 = ¥0.5/天 = ¥15/月
100 次/天 = ¥1/天 = ¥30/月
```

---

## 📁 文件清单

```
xiaohongshu-auto-publish/
├── skill.py                  # 主程序 ✅
├── SKILL.md                  # 描述文件 ✅
├── README.md                 # 使用说明 ✅
├── SETUP.md                  # 配置指南 ✅
├── ACCOUNTS.md               # 账号信息（本文档）✅
├── publish.sh                # 发布脚本 ✅
├── configure_skillpay.py     # SkillPay 配置工具 ✅
└── assets/
    └── cover.png             # 技能封面 ✅
```

---

## ⚠️ 注意事项

1. **ClawHub 发布** - 需要浏览器扫码登录
2. **SkillPay 产品** - 需要网页手动创建
3. **收款账户** - 确保 SkillPay 绑定了正确的收款账户
4. **测试模式** - 使用 `--skip-payment` 参数测试功能

---

*创建时间：2026-03-05 20:30*
*版本：1.0.0*
