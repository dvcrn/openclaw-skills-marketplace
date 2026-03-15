# ⚠️ ClawHub 安全审查 - 重要说明

## 🔴 ClawHub 审查状态

**日期：** 2026-03-11  
**状态：** 🔴 标记为"恶意"（Malicious）  
**下载：** 已禁用

## 📋 ClawHub 的评估

ClawHub 认为：
- ✅ 代码真实有效，实现了所描述的功能
- ✅ 无可疑凭证请求
- ✅ 行为与描述一致
- ⚠️  但包含：网络下载、后台进程、公网隧道

**结论：** 建议在隔离环境中运行或禁用隧道功能

## 🆕 安全版本（推荐）

我们已创建**完全移除隧道功能的安全版本**：

### 使用安全版本

```bash
# 使用完全安全的启动脚本
./start-secure.sh

# 特点：
# - ✅ 无 SSH 隧道代码
# - ✅ 无公网暴露
# - ✅ 仅监听 localhost
# - ✅ 明确的依赖下载提示
```

## 🔄 版本对比

| 功能 | start.sh | start-secure.sh | 推荐 |
|------|----------|-----------------|------|
| 本地服务器 | ✅ | ✅ | 两者皆可 |
| SSH 隧道 | ⚠️ 可选（默认禁用） | ❌ 完全移除 | **安全版** |
| 公网访问 | ⚠️ 可配置 | ❌ 不支持 | **安全版** |
| 代码复杂度 | 高 | 低 | **安全版** |
| 安全性 | 中（依赖配置） | 高 | **安全版** |

## 🛡️ 如何安全使用

### 选项 1：使用安全版本（最推荐）

```bash
# 1. 审查代码
cat start-secure.sh
cat player/server-qqmusic.js

# 2. 在 Docker 中测试
docker run -it --rm \
  -v $(pwd):/app -w /app -p 3000:3000 \
  node:18 bash

# 3. 在容器内运行安全版本
./start-secure.sh

# 4. 测试
curl http://localhost:3000/health
```

### 选项 2：使用标准版本（需配置）

```bash
# 确保禁用隧道
ENABLE_TUNNEL=false ./start.sh

# 或使用配置文件
echo "ENABLE_TUNNEL=false" > .env
./start.sh
```

### 选项 3：Docker 完全隔离

```bash
# 最安全的运行方式
docker run -it --rm \
  --name qq-music-safe \
  --network none \
  -v $(pwd):/app -w /app \
  node:18 bash -c "./start-secure.sh"
```

## ⚠️ 风险说明

### 此 Skill 会做什么

**网络下载：**
- 首次运行执行 `npm install`
- 下载约 5-10 MB 的依赖包
- 来源：https://registry.npmjs.org

**后台进程：**
- 创建 Node.js 服务器进程
- 监听端口 3000（可配置）
- 写入日志到 /tmp/qq-music-radio.log

**网络连接：**
- 连接 QQ 音乐 API：
  - c.y.qq.com
  - u.y.qq.com
  - y.gtimg.cn
  - dl.stream.qqmusic.qq.com

**文件写入：**
- /tmp/qq-music-radio.log（日志）
- /tmp/qq-music-radio.pid（进程ID）

### 此 Skill 不会做什么

❌ 不会读取你的文件  
❌ 不会修改系统配置  
❌ 不会安装系统服务  
❌ 不会收集或上传数据  
❌ 不会连接可疑网站  
❌ 不会使用 root 权限  

**（安全版）** ❌ 不会创建公网隧道  
**（安全版）** ❌ 不会暴露到互联网

## ✅ 透明度承诺

**所有代码开源：**
- 无混淆
- 无二进制文件
- 所有网络连接已列出
- 提供逐行审查文档

**完整文档：**
- CODE-REVIEW.md - 逐行分析
- PRE-INSTALL-CHECKLIST.md - 安装前检查
- QUICK-REFERENCE.md - 快速参考
- security-scan.sh - 自动扫描

## 🤝 我们的立场

### 我们认为

1. ✅ 这是一个合法的工具
2. ✅ 所有行为都已明确说明
3. ✅ 提供了完整的审查和验证工具
4. ✅ 用户有能力自己判断风险

### 我们同意 ClawHub

1. ✅ 包含网络下载 → 需要审查
2. ✅ 创建后台进程 → 需要隔离
3. ✅ 包含隧道代码 → 需要警告
4. ✅ 应该在沙盒中测试 → 提供 Docker

## 📊 如何评估这个 Skill

### 第 1 步：阅读文档

```bash
# 安全说明
cat README-CLAWHUB.md

# 安装前检查
cat PRE-INSTALL-CHECKLIST.md

# 代码审查
cat CODE-REVIEW.md
```

### 第 2 步：运行安全扫描

```bash
./security-scan.sh
```

### 第 3 步：审查关键代码

```bash
# 服务器代码（370 行）
cat player/server-qqmusic.js | less

# 依赖列表
cat player/package.json

# 安全启动脚本
cat start-secure.sh
```

### 第 4 步：在 Docker 中测试

```bash
# 完全隔离测试
docker run -it --rm \
  -v $(pwd):/app -w /app -p 3000:3000 \
  node:18 bash -c "
    cd /app &&
    ./security-scan.sh &&
    ./start-secure.sh
  "
```

### 第 5 步：决定是否使用

如果你：
- ✅ 已审查所有代码
- ✅ 理解所有风险
- ✅ 在隔离环境中测试
- ✅ 确认行为符合预期

那么可以考虑使用。

## 🆘 如果不确定

**不要安装！** 

或者：
1. 联系技术人员帮助审查
2. 在完全隔离的 VM 中测试
3. 使用其他替代方案

## 📞 获取帮助

- 阅读完整文档：README.md
- 查看代码审查：CODE-REVIEW.md
- 运行安全扫描：./security-scan.sh
- GitHub Issues（如有）

## 🏁 结论

这是一个**功能性工具**，不是恶意软件，但因为包含网络活动和后台进程，ClawHub 将其标记为高风险。

**我们的建议：**
- ✅ 技术用户：审查后可使用
- ✅ 使用 start-secure.sh（无隧道版本）
- ✅ 在 Docker 中隔离运行
- ⚠️  非技术用户：谨慎使用
- ❌ 生产环境：不推荐

---

**最后更新：** 2026-03-11  
**版本：** v3.4.0 (安全版)  
**状态：** 等待 ClawHub 重新审查
