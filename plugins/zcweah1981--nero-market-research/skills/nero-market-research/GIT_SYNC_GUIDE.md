# Git 自动同步说明

## 🚀 快速开始

### 1. 初始化仓库（仅第一次）

```bash
cd /root/.openclaw/workspace-work/nero-market-research
chmod +x init-git.sh
./init-git.sh <你的GitHub用户名> <你的GitHub Token>
```

**示例**：
```bash
./init-git.sh zhangcheng ncm_xxxxxxxxxxxxx
```

**执行后会自动**：
- ✅ 配置git用户信息
- ✅ 创建GitHub仓库
- ✅ 上传所有文件
- ✅ 返回仓库地址

---

### 2. 日常同步（三种方式）

#### 方式1: 手动同步 ⭐ 推荐

每次修改文件后，执行：

```bash
./auto-sync.sh "你的提交信息"
```

**示例**：
```bash
./auto-sync.sh "更新README文档"
```

---

#### 方式2: 自动监控

启动后台监控（每30秒自动检查）：

```bash
./watch-sync.sh
```

**停止监控**：按 `Ctrl+C`

---

#### 方式3: 后台运行

```bash
# 启动后台监控
nohup ./watch-sync.sh > sync.log 2>&1 &

# 查看日志
tail -f sync.log

# 停止
pkill -f watch-sync.sh
```

---

## 📝 提交规范

建议的提交信息格式：

```
✨ feat: 添加新功能
🐛 fix: 修复bug
📝 docs: 更新文档
🎨 style: 代码格式调整
♻️ refactor: 重构代码
🚀 deploy: 部署相关
```

**示例**：
```bash
./auto-sync.sh "✨ feat: 添加Telegram通知功能"
./auto-sync.sh "📝 docs: 更新安装指南"
./auto-sync.sh "🐛 fix: 修复Notion同步失败问题"
```

---

## 🔄 工作流程

### 修改文件 → 自动同步

```
1. 修改文件（vim/nano/编辑器）
   ↓
2. 保存文件
   ↓
3. 执行 ./auto-sync.sh "提交信息"
   ↓
4. 自动提交并推送到GitHub
   ↓
5. 完成！
```

---

## 📊 同步脚本说明

| 脚本 | 用途 | 频率 |
|------|------|------|
| **init-git.sh** | 初始化仓库 | 仅一次 |
| **auto-sync.sh** | 手动同步 | 每次修改后 |
| **watch-sync.sh** | 自动监控 | 后台运行 |

---

## 🛠 高级配置

### 配置自动同步别名

编辑 `~/.bashrc`：

```bash
alias nero-sync='cd /root/.openclaw/workspace-work/nero-market-research && ./auto-sync.sh'
alias nero-watch='cd /root/.openclaw/workspace-work/nero-market-research && ./watch-sync.sh'
```

**使用**：
```bash
nero-sync "更新文档"
nero-watch
```

---

### 配置Git Hook（自动同步）

创建 `.git/hooks/post-commit`：

```bash
#!/bin/bash
git push origin main
```

**效果**：每次commit后自动push

---

## 🐛 故障排查

### Q: 推送失败？

**检查**：
```bash
# 检查远程仓库
git remote -v

# 检查Token是否有效
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
```

---

### Q: 如何撤销提交？

```bash
# 撤销最后一次commit（保留修改）
git reset --soft HEAD~1

# 撤销最后一次commit（丢弃修改）
git reset --hard HEAD~1
```

---

### Q: 如何查看提交历史？

```bash
# 查看历史
git log --oneline

# 查看详细历史
git log

# 查看文件变更
git log --stat
```

---

## 📚 相关文档

- [GitHub Token创建](https://github.com/settings/tokens)
- [Git文档](https://git-scm.com/doc)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
