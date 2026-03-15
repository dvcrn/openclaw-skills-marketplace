---
name: grafana-inspector
description: "Grafana 自动化巡检技能。使用 Grafana API 进行系统服务自动化巡检，包括：(1) 检查主机和中间件状态 (2) 捕获监控面板截图 (3) 计算健康评分 (4) 生成巡检报告 (5) 发送报告到飞书文档。使用场景：定期系统健康检查、运维自动化巡检、监控报告生成。"
---

# Grafana 自动化巡检技能

## 快速开始

```bash
# 1. 配置 Grafana 连接信息
cp scripts/config.example.json scripts/config.json
# 编辑 scripts/config.json 填入你的配置

# 2. 执行巡检
cd scripts
python auto_inspect.py config.json
```

## 配置说明

### Grafana 配置

| 参数 | 说明 | 示例 |
|------|------|------|
| `grafana_url` | Grafana 服务地址 | `http://localhost:3000` |
| `api_key` | Grafana API Key | `eyJrIjoi...` |
| `dashboard_uid` | 要巡检的仪表盘 UID | `system-monitor` |
| `panel_ids` | 要截图的面板 ID 列表（可选） | `[1, 2, 3]` |

### 飞书配置（可选）

| 参数 | 说明 | 获取方式 |
|------|------|------|
| `feishu_app_id` | 飞书应用 App ID | 飞书开放平台 |
| `feishu_app_secret` | 飞书应用 App Secret | 飞书开放平台 |
| `feishu_folder_token` | 飞书云文档文件夹 Token | 从云文档 URL 获取 |

## 输出内容

巡检完成后生成：

- **服务状态** - 主机、中间件健康状态
- **健康评分** - 0-100 分综合评分
- **异常信息** - 检测到的问题和告警
- **监控截图** - Grafana 面板截图
- **巡检报告** - Markdown 格式报告 + 飞书文档链接

## 使用方式

### 方式 1：直接运行脚本

```bash
cd C:\Users\huama\.openclaw\workspace\skills\grafana-inspector\scripts
python auto_inspect.py config.json
```

### 方式 2：在 OpenClaw 中调用

当用户提到以下关键词时触发此技能：

- "执行系统巡检"
- "生成监控报告"
- "检查服务状态"
- "Grafana 巡检"
- "自动化巡检"

### 方式 3：配置定时任务

使用 OpenClaw 的 cron 功能设置定期巡检：

```json
{
  "name": "每日系统巡检",
  "schedule": {"kind": "cron", "expr": "0 9 * * *"},
  "payload": {
    "kind": "systemEvent",
    "text": "执行 Grafana 自动化巡检"
  }
}
```

## 脚本说明

### auto_inspect.py
主巡检脚本，整合所有功能：
- 执行健康检查
- 捕获监控截图
- 生成报告
- 发送到飞书

### grafana_check.py
Grafana 健康检查模块：
- 检查数据源状态
- 检查主机指标（CPU、内存、磁盘）
- 检查中间件状态（MySQL、Redis 等）
- 检查告警状态
- 计算健康评分

### capture_dashboard.py
监控面板截图模块：
- 使用 Grafana 渲染 API
- 支持单面板或整个仪表盘
- 支持批量截图

### feishu_report.py
飞书报告生成模块：
- 创建飞书云文档
- 上传巡检报告
- 返回文档链接

## 健康评分规则

| 评分 | 状态 | 说明 |
|------|------|------|
| 90-100 | excellent | 系统运行优秀 |
| 70-89 | good | 系统运行良好 |
| 50-69 | warning | 存在警告 |
| 0-49 | critical | 严重问题 |

扣分项：
- 每个活跃告警：-10 分
- 每个检查异常：-5 分

## 前置要求

### Grafana 配置

1. **启用 API 访问**
   ```ini
   # grafana.ini
   [auth.api_keys]
   enabled = true
   ```

2. **创建 API Key**
   - 进入 Grafana → Configuration → API keys
   - 创建具有 Viewer 或 Editor 权限的 Key

3. **安装 Image Renderer（截图必需）**
   ```bash
   # 使用 grafana-cli 安装
   grafana-cli plugins install grafana-image-renderer
   
   # 或使用 Docker
   docker run -d --name=grafana-renderer \
     -e RENDERING_MODE=clustered \
     grafana/grafana-image-renderer
   ```

### 飞书配置

1. 创建飞书自建应用
2. 申请以下权限：
   - 云文档读写权限
   - 文档管理权限
3. 获取 App ID 和 App Secret

## 示例输出

```
============================================================
🚀 Grafana 自动化巡检系统
============================================================

📋 步骤 1: 检查主机和中间件状态...
✅ 主机监控检查：healthy
✅ MySQL: healthy
✅ Redis: healthy

📸 步骤 2: 捕获监控面板截图...
截图已保存：./screenshots/panel_1_20260313_161200.png

📝 步骤 3: 生成巡检报告...
报告生成完成

📤 步骤 4: 发送报告到飞书文档...
文档创建成功：docx123456

============================================================
✅ 巡检完成!
============================================================

📊 巡检摘要:
   状态：EXCELLENT
   健康评分：95/100
   检查项：3
   告警数：0
   异常数：0
   截图数：1

🔗 飞书报告：https://your-company.feishu.cn/docx/docx123456
```

## 故障排查

### 截图失败
- 检查 Grafana Image Renderer 插件是否安装
- 确认 `rendering` 配置正确
- 检查防火墙是否允许渲染服务访问

### 飞书发送失败
- 验证 App ID 和 App Secret 是否正确
- 检查应用权限是否足够
- 确认 folder_token 有效

### API 连接失败
- 验证 grafana_url 是否可访问
- 检查 API Key 是否过期
- 确认网络连接正常

## 相关文件

- `scripts/auto_inspect.py` - 主巡检脚本
- `scripts/grafana_check.py` - 健康检查模块
- `scripts/capture_dashboard.py` - 截图模块
- `scripts/feishu_report.py` - 飞书报告模块
- `scripts/config.example.json` - 配置模板
- `references/api_docs.md` - Grafana API 文档参考
