# ⚠️ 安装前必读 - ClawHub 安全审查

## 🔒 重要安全提示

ClawHub 安全审查发现了一些需要注意的风险点，我们已经根据反馈进行了改进。

### ✅ 已修复的问题

**1. 默认公网暴露** - ✅ 已修复
- ~~原问题：`start.sh` 默认启用 SSH 隧道~~
- **✅ 新默认值：`ENABLE_TUNNEL=false`（本地模式）**
- 现在默认仅本地访问，更安全！

### 🆕 新增的安全文档

**1. 运行时依赖清单** - `REQUIREMENTS.md`
- 列出所有需要的系统工具
- 提供检查脚本
- 不同系统的安装方法

**2. 代码审查报告** - `CODE-REVIEW.md`
- 逐行分析关键文件
- 列出具体行号和代码
- 网络端点、文件操作、风险评估

**3. Docker 隔离环境** - 在 `REQUIREMENTS.md` 中
- 提供 Docker 使用命令
- Dockerfile 示例代码

### ⚠️ 仍需注意的风险

**1. 运行时依赖**
需要以下系统工具：
- `node` (>= 14.0.0)
- `npm` (>= 6.0.0)
- `curl`
- `pgrep` 或 `lsof`

**检查工具：**
```bash
# 快速检查
node --version && npm --version && curl --version

# 或使用完整检查脚本（见 REQUIREMENTS.md）
```

**2. 自动下载依赖**
首次运行会执行 `npm install`，下载约 5-10 MB：
- express@^4.18.2
- axios@^1.6.0
- cors@^2.8.5
- dotenv@^16.3.1

**审查依赖：**
```bash
cat player/package.json
cat player/package-lock.json | grep "resolved" | head -10
```

### ✅ 安全检查通过

我们已经扫描了所有代码：
- ✅ 无 `eval()` 或动态执行
- ✅ 无进程执行（exec/spawn）
- ✅ 网络请求仅限 QQ 音乐官方 API
- ✅ 无文件系统破坏性操作
- ✅ 无 XSS 或注入风险

**运行安全扫描：**
```bash
./security-scan.sh
```

### 📖 详细说明

- **完整清单：** `SECURITY-CHECKLIST.md`
- **安全文档：** `SECURITY.md`

### 🛡️ 推荐安装方式

```bash
# 1. 运行安全扫描
./security-scan.sh

# 2. 审查关键文件
cat player/server-qqmusic.js | less
cat player/public/app-auto.js | less

# 3. 首次使用本地模式
ENABLE_TUNNEL=false ./start.sh

# 4. 访问测试
curl http://localhost:3000/health
```

### 🆘 需要帮助？

如果你不确定，可以：
1. 在隔离环境（容器/VM）中测试
2. 阅读 `SECURITY-CHECKLIST.md` 详细指南
3. 联系作者或 ClawHub 支持

---

**继续安装表示你已理解并接受上述风险。**
