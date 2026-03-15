# 安全性与数据隐私说明

## 概述

Baidu Yijian Vision 是一个**客户端工具**，用于与百度一见视觉分析平台交互。本文档说明数据流、安全考虑事项和最佳实践。

## 数据流

```
用户图像/视频
     ↓
[本地脚本处理]
     ↓
[转换为 Base64]
     ↓
[通过 HTTPS 发送]
     ↓
https://yijian-next.cloud.baidu.com
     ↓
[远程处理和分析]
     ↓
[返回检测结果 JSON]
     ↓
[本地保存/可视化]
```

## 远程端点

### 主 API 服务

**端点：** `https://yijian-next.cloud.baidu.com`

**协议：** HTTPS（加密传输）

**认证：** Bearer Token（YIJIAN_API_KEY）

**调用场景：**
- 获取技能元数据：`GET /ep-{skill-id}/metadata`
- 执行技能：`POST /ep-{skill-id}/run`
- 注册新技能：`POST /skills/register`

### 数据传输

**发送的数据：**
1. **图像：** Base64 编码的图像数据
2. **元数据：** 源 ID、时间戳、帧标识符（用于视频处理）
3. **ROI/绊线：** 用户定义的几何数据（多边形点、检测线）

**返回的数据：**
1. **检测结果：** 边框、置信度、分类、跟踪 ID
2. **属性：** 年龄、性别、表情等推理结果
3. **OCR：** 识别的文本内容

## API Key 管理

### 安全最佳实践

✅ **正确做法：**
```bash
# 设置为环境变量（不写入代码）
export YIJIAN_API_KEY="your-api-key"

# 或在 ~/.bashrc / ~/.zshrc 中设置（本地开发）
echo 'export YIJIAN_API_KEY="your-api-key"' >> ~/.bashrc

# 在生产环境中，使用密钥管理服务（如 Kubernetes secrets）
```

❌ **错误做法：**
```bash
# 不要硬编码到代码中
YIJIAN_API_KEY="xxx" node scripts/invoke.mjs

# 不要提交到版本控制
git add .env  # ❌ 会暴露 API Key
```

### API Key 轮换

定期轮换 API Key：
1. 在一见平台生成新 Key
2. 更新环境变量
3. 删除旧 Key

## 脚本审计

所有脚本调用**仅**指向 `https://yijian-next.cloud.baidu.com`，不向其他服务发送数据。

### 关键脚本

**invoke.mjs** - 执行技能
- ✅ 调用：`yijian-next.cloud.baidu.com/api/skills/v1/{epId}/run`
- ✅ 发送：图像 + ROI/绊线（可选）
- ✅ 返回：检测结果

**register.mjs** - 注册技能
- ✅ 调用：`yijian-next.cloud.baidu.com/api/skills/register`
- ✅ 发送：技能 ID + 认证信息
- ✅ 返回：注册状态

**list.mjs** - 列出技能
- ✅ 调用：`yijian-next.cloud.baidu.com/api/skills/list`
- ✅ 返回：已注册和预设技能列表

**visualize.mjs** - 可视化结果
- ✅ **仅本地操作**，不发送网络请求
- ✅ 读取本地图像文件
- ✅ 绘制检测结果到本地文件

**show-grid.mjs** - 生成网格参考
- ✅ **仅本地操作**，不发送网络请求
- ✅ 读取本地图像文件
- ✅ 生成网格叠加层到本地文件

## 数据隐私考虑

### 图像数据

- **存储：** 用户图像不保存在本工具中，仅在内存中处理后发送
- **传输：** 通过 HTTPS 加密发送到一见平台
- **保留：** 一见平台的数据保留政策由百度管理，详见官方服务条款

### 敏感信息

**避免以下内容：**
- 个人身份证件照片
- 医疗记录
- 财务信息
- 密码或凭证

### 企业部署

在企业环境中部署时：
1. **审查服务条款** - 确认数据处理符合要求
2. **网络隔离** - 如需要，可配置代理或防火墙规则
3. **日志审计** - 监控哪些图像被处理过
4. **API Key 隔离** - 为不同的业务部分使用不同的 API Key

## 已知限制

1. **图像大小** - 大型图像（>50MB）发送可能超时，建议预处理
2. **批处理** - 大量连续请求可能触发速率限制
3. **本地存储** - 生成的可视化图像存储在本地磁盘，建议定期清理

## 安全建议

### 日常使用

- ✅ 定期更新 npm 依赖：`npm update`
- ✅ 审查脚本日志和错误
- ✅ 验证输出图像的准确性
- ✅ 定期轮换 API Key

### 生产部署

- ✅ 使用密钥管理服务（Vault、K8s Secrets）
- ✅ 启用 HTTPS 代理和防火墙规则
- ✅ 监控和记录所有 API 调用
- ✅ 实现请求速率限制
- ✅ 定期进行安全审计

### 开发环境

- ✅ 使用测试 API Key（如果可用）
- ✅ 避免提交 `.env` 文件
- ✅ 使用 `git-secrets` 防止凭证泄露
- ✅ 定期轮换开发用 API Key

## 漏洞报告

发现安全问题请：
1. **勿公开披露** - 不要在 GitHub issues 中发布安全问题
2. **联系百度安全团队** - 提交给 https://security.baidu.com
3. **包含详情** - 问题描述、复现步骤、影响范围

## 第三方依赖

### 关键依赖

- **sharp** ^0.33.0 - 图像处理
- **archiver** ^7.0.1 - 打包工具

所有依赖通过 npm 获取，可通过 `npm audit` 检查已知漏洞：

```bash
npm audit
npm audit fix  # 自动修复已知漏洞
```

## 合规性

- **HTTPS：** 所有网络通信使用 TLS 1.2+
- **数据加密：** 传输中加密，遵循行业标准
- **API 认证：** Bearer Token 认证
- **无本地日志：** 脚本不记录敏感数据

## 相关文档

- [安装指南](./INSTALL.md) - 系统要求和安装步骤
- [SKILL.md](./SKILL.md) - 使用指南
- [类型定义](./types-guide.md) - 数据结构
