---
name: clawhub-skill-publishing-guide
description: "ClawHub Skill 发布避坑指南。让你的 Skill 发布后能被搜索到，避免安全扫描导致隐藏。适用于需要发布 Skill 到 ClawHub 的开发者。"
---

# ClawHub Skill 发布避坑指南

## 发布前检查清单

### ✅ 必须避免的内容

| 问题类型 | 风险等级 | 解决方案 |
|----------|----------|------------|
| 硬编码 API Keys | 🔴 高 | 使用环境变量 |
| HTTP 明文传输 | 🟡 中 | 添加安全警告说明 |
| 外部 URL/端点 | 🟢 低 | 正常发布 |
| 敏感信息 | 🔴 高 | 移除或环境变量 |

### ✅ 推荐做法

1. **API Key 放在环境变量**
```python
# ❌ 硬编码（会被扫描拦截）
API_KEY = "sk-xxx"

# ✅ 环境变量（安全）
API_KEY = os.environ.get("API_KEY")
```

2. **HTTP endpoint 要警告用户**
```markdown
## ⚠️ 安全警告
- HTTP 明文传输，API Key 可能有泄露风险
- 仅在可信网络使用
```

3. **SKILL.md 要声明必需的环境变量**
```markdown
## 环境变量
- API_KEY=xxx  # 必需
- BASE_URL=http://example.com  # 可选
```

## ⚠️ 开发者协议确认（新！）

**如果发布时遇到错误：`acceptLicenseTerms: invalid value`**

说明你需要先在 ClawHub 网站上同意开发者协议：

1. 访问 https://clawhub.ai
2. 登录你的账户
3. 进入 **Settings** 或 **Developer Settings**
4. 同意开发者许可协议
5. 然后再执行发布命令

## 发布命令

```bash
# 方式一：使用 clawhub CLI（需要先在网站同意开发者协议）
clawhub publish ./skills/your-skill --version 1.0.0

# 方式二：使用 curl 直接发布（支持 acceptLicenseTerms）
TOKEN=$(cat ~/.config/clawhub/config.json | jq -r '.token')
curl -X POST "https://clawhub.ai/api/v1/skills" \
  -H "Authorization: Bearer $TOKEN" \
  -F 'payload={"slug":"your-skill","displayName":"Your Skill","version":"1.0.0","changelog":"","tags":["latest"],"acceptLicenseTerms":true};type=application/json' \
  -F "files=@SKILL.md;filename=SKILL.md"
```

**注意**：`acceptLicenseTerms: true` 是必需的参数，表示同意开发者许可协议。

## 发布后验证

```bash
# 搜索 Skill
clawhub search your-skill-name

# 检查状态
clawhub inspect your-skill-name
```

## 常见问题

### Q: Skill 被隐藏怎么办？
A: 等待安全扫描通过，或移除敏感信息重新发布

### Q: 提示 hard-coded credentials 怎么办？
A: 改用环境变量，添加安全警告

### Q: 版本号冲突怎么办？
A: 升级版本号，如 1.0.0 → 1.0.1

### Q: 提示 acceptLicenseTerms: invalid value 怎么办？
A: 先在 ClawHub 网站上同意开发者协议，然后再发布
