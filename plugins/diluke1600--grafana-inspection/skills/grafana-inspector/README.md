# 📊 Grafana 自动化巡检技能

## 技能已创建完成！

**技能位置**: `C:\Users\huama\.openclaw\workspace\skills\grafana-inspector`

**打包文件**: `C:\Users\huama\.openclaw\workspace\grafana-inspector.skill`

---

## 🚀 快速使用

### 1. 配置 Grafana 连接

编辑 `scripts/config.json`（复制 `config.example.json`）：

```json
{
  "grafana_url": "http://your-grafana-server:3000",
  "api_key": "your_api_key_here",
  "dashboard_uid": "your_dashboard_uid",
  "panel_ids": [1, 2, 3],
  "feishu_app_id": "your_feishu_app_id",
  "feishu_app_secret": "your_feishu_app_secret"
}
```

### 2. 获取 Grafana API Key

1. 登录 Grafana
2. 进入 **Configuration** → **API keys**
3. 点击 **Add API key**
4. 选择角色（建议 Viewer）
5. 复制生成的 Key

### 3. 执行巡检

```bash
cd C:\Users\huama\.openclaw\workspace\skills\grafana-inspector\scripts
python auto_inspect.py config.json
```

---

## 📋 功能特性

| 功能 | 说明 |
|------|------|
| ✅ 主机监控检查 | CPU、内存、磁盘使用率 |
| ✅ 中间件检查 | MySQL、Redis 等状态 |
| ✅ 告警检查 | 获取当前活跃告警 |
| ✅ 监控截图 | 自动捕获 Grafana 面板 |
| ✅ 健康评分 | 0-100 综合评分 |
| ✅ 巡检报告 | Markdown 格式报告 |
| ✅ 飞书集成 | 自动发送到飞书文档 |

---

## 📁 文件结构

```
grafana-inspector/
├── SKILL.md                          # 技能说明文档
├── scripts/
│   ├── auto_inspect.py              # 主巡检脚本
│   ├── grafana_check.py             # 健康检查模块
│   ├── capture_dashboard.py         # 截图模块
│   ├── feishu_report.py             # 飞书报告模块
│   └── config.example.json          # 配置模板
└── references/
    └── api_docs.md                  # API 参考文档
```

---

## 🔧 前置要求

### Grafana Image Renderer（截图必需）

```bash
# 方法 1: 使用 grafana-cli 安装
grafana-cli plugins install grafana-image-renderer

# 方法 2: Docker 部署
docker run -d --name=grafana-renderer \
  -e RENDERING_MODE=clustered \
  grafana/grafana-image-renderer
```

### 飞书应用配置

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 创建自建应用
3. 申请权限：云文档读写
4. 获取 App ID 和 App Secret

---

## 📊 输出示例

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

---

## ⏰ 设置定时巡检

使用 OpenClaw 的 cron 功能：

```bash
# 每天早上 9 点自动巡检
openclaw cron add --schedule "0 9 * * *" --message "执行 Grafana 自动化巡检"
```

---

## 🐛 常见问题

### 截图失败
- 确保安装了 Grafana Image Renderer 插件
- 检查 `grafana.ini` 中的 rendering 配置

### 飞书发送失败
- 验证 App ID/Secret 是否正确
- 检查应用权限配置

### API 连接失败
- 确认 Grafana 服务可访问
- 检查 API Key 是否有效

---

## 📖 更多信息

- 技能文档：`SKILL.md`
- API 参考：`references/api_docs.md`
- 配置示例：`scripts/config.example.json`

---

**创建时间**: 2026-03-13
**技能版本**: 1.0.0
