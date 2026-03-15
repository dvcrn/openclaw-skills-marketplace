# 📦 ClawHub 发布包

## 🚀 发布到 ClawHub

### 方法 1：使用 clawhub CLI（推荐）

```bash
# 1. 安装 clawhub（如果未安装）
npm install -g clawhub

# 2. 登录 ClawHub
clawhub login

# 3. 发布 Skill
cd /home/ereala/.openclaw/workspace/skills/browser-toggle
clawhub publish

# 4. 验证发布
clawhub search browser-toggle
```

### 方法 2：手动上传

1. 访问：https://clawhub.com/skills/create
2. 填写信息：
   - **名称：** browser-toggle
   - **版本：** 1.0.0
   - **描述：** 一键启用/禁用 OpenClaw 内置浏览器
   - **分类：** Tools
   - **标签：** browser, automation, utility
3. 上传文件：
   - `dist/browser-toggle-v1.0.0.tar.gz`
4. 填写 `package.json` 中的信息
5. 点击 **发布**

---

## 📋 ClawHub 配置说明

### package.json 字段说明

```json
{
  "name": "browser-toggle",          // Skill 名称
  "version": "1.0.0",                 // 版本号
  "description": "描述信息",
  "author": "作者",
  "license": "MIT",                   // 许可证
  "main": "browser_toggle.py",        // 主程序
  "category": "tools",                // 分类
  "tags": ["browser", "automation"]   // 标签
}
```

---

## 📊 发布后验证

```bash
# 搜索 Skill
clawhub search browser-toggle

# 安装 Skill
clawhub install browser-toggle

# 查看信息
clawhub info browser-toggle
```

---

## 🔗 分享链接

发布成功后，分享链接：
```
https://clawhub.com/skills/browser-toggle
```

安装命令：
```bash
clawhub install browser-toggle
```

---

*ClawHub 发布指南 v1.0*
