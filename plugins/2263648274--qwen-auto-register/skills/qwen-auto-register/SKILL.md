---
name: qwen-auto-register
description: "自动注册 Qwen 账号并获取 token。支持预测性自动切换，避免 API 额度超限。需要安装 auto-register 包。"
---

# Qwen 自动注册

自动完成 Qwen 账号注册、邮箱验证、token 获取、网关重启全流程。

## 安装

首次使用需要安装依赖：

```bash
# 从 GitHub 安装
pip install git+https://github.com/2263648274/qwen-auto-register.git

# 安装浏览器
playwright install chromium
```

## 网络要求

**中国大陆用户需要配置代理：**

### 方式一：临时设置（当前会话有效）

```bash
# PowerShell
$env:HTTP_PROXY="http://127.0.0.1:7890"
$env:HTTPS_PROXY="http://127.0.0.1:7890"
```

### 方式二：永久设置（系统环境变量）

1. 搜索"环境变量"
2. 用户变量 → 新建
3. 变量名：`HTTP_PROXY`，值：`http://127.0.0.1:你的代理端口`
4. 变量名：`HTTPS_PROXY`，值：`http://127.0.0.1:你的代理端口`
5. 重启终端/IDE

### 方式三：在 .env 文件中配置

在 `auto_register` 项目目录下创建 `.env` 文件：

```
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

## 用法

```
# 手动注册新账号
帮我注册一个新的 Qwen 账号

# 检查当前账号状态
检查 Qwen token 状态

# 预测性切换（推荐）
检查并切换 Qwen 账号
```

## 流程

1. 生成临时邮箱
2. 自动填写注册表单
3. 等待并点击激活邮件
4. 提取 access + refresh token
5. 写入 auth-profiles.json（覆盖旧 token）
6. 重置使用统计
7. 自动重启 Gateway

## 预测性切换

技能会监控：
- **请求计数**：接近每日限制时自动注册新号
- **Token 过期时间**：提前 1 小时刷新
- **错误率**：连续失败自动切换

## 输出

✅ 新账号已就绪，立即可用！（旧账号已覆盖）

## 注意事项

- 需要安装 Python 包：`pip install auto-register`
- 首次运行需要安装浏览器：`playwright install chromium`
- 整个过程约 2-3 分钟
- 旧账号直接覆盖，不保留备份
