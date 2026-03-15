# Skill Shield - OpenClaw 扩展安全管理系统

安全管理已安装的 OpenClaw 扩展，扫描风险、存储风险列表、提供 allowlist 策略控制。

## 功能特性

- 🔍 **自动扫描** - 扫描所有已安装的扩展
- ⚠️ **风险评估** - 识别 10 种常见安全风险
- 💾 **持久存储** - 保存风险报告到 memory
- 🔐 **Allowlist** - 配置默认信任的扩展
- 🚫 **黑名单** - 阻止危险扩展执行
- ⚡ **使用前检查** - 调用扩展前自动风险提示

## 风险类别

| 风险ID | 风险名称 | 严重程度 |
|--------|----------|----------|
| R001 | 网络访问 | 高 |
| R002 | 文件写入 | 高 |
| R003 | 文件读取 | 中 |
| R004 | 命令执行 | 严重 |
| R005 | 外部API | 中 |
| R006 | 数据外发 | 严重 |
| R007 | 凭证访问 | 严重 |
| R008 | 无签名验证 | 低 |
| R009 | 依赖未知 | 中 |
| R010 | 权限过宽 | 高 |

## 安装

```bash
# 扩展已自动安装
# 如需重新安装:
cp -r skill-shield/ ~/.openclaw/workspace/skills/
```

## 使用方法

### 扫描所有扩展

```bash
python3 ~/.openclaw/workspace/skills/skill-shield/scripts/shield.py scan
```

输出示例:
```
🔍 正在扫描 10 个扩展...

📊 扫描完成!
   🔴 严重: 2
   🟠 高危: 3
   🟡 中危: 1
   🟢 低危/安全: 4

💾 风险报告已保存到: ~/.openclaw/workspace/memory/shield-risks.json
```

### 检查单个扩展

```bash
python3 ~/.openclaw/workspace/skills/skill-shield/scripts/shield.py check <extension-name>
```

示例:
```bash
python3 ~/.openclaw/workspace/skills/skill-shield/scripts/shield.py check weather-search
```

输出:
```
⚠️ weather-search 风险等级: medium
风险项: R001(网络访问), R005(外部API)
```

### 添加到 Allowlist

```bash
python3 ~/.openclaw/workspace/skills/skill-shield/scripts/shield.py add-allowlist <extension-name>
```

添加到 allowlist 的扩展使用时不会提示风险。

### 从 Allowlist 移除

```bash
python3 ~/.openclaw/workspace/skills/skill-shield/scripts/shield.py remove-allowlist <extension-name>
```

### 添加到黑名单

```bash
python3 ~/.openclaw/workspace/skills/skill-shield/scripts/shield.py add-blocked <extension-name>
```

添加到黑名单的扩展将被阻止执行。

### 查看风险列表

```bash
python3 ~/.openclaw/workspace/skills/skill-shield/scripts/shield.py view
```

### 清除风险记录

```bash
python3 ~/.openclaw/workspace/skills/skill-shield/scripts/shield.py clear
```

## 配置文件

配置文件位置: `~/.openclaw/workspace/skills/skill-shield/config.json`

```json
{
  "allowlist": [
    "file-search",
    "weather-search"
  ],
  "autoApprove": [],
  "blocked": [],
  "scanOnInstall": true,
  "promptOnHighRisk": true
}
```

配置说明:
- `allowlist`: 默认信任的扩展，跳过风险检查
- `autoApprove`: 自动批准的扩展（不需要用户确认）
- `blocked`: 黑名单，完全阻止执行
- `scanOnInstall`: 安装时自动扫描（暂未实现）
- `promptOnHighRisk`: 高风险时提示用户

## 在 OpenClaw 中使用

### 在 TUI 中执行扫描

```bash
# 扫描所有扩展
python3 ~/.openclaw/workspace/skills/skill-shield/scripts/shield.py scan
```

### 设置定时扫描

```bash
# 每天早上 9 点扫描
openclaw cron create \
  --name "skill-shield-scan" \
  --schedule "0 9 * * *" \
  --command "python3 ~/.openclaw/workspace/skills/skill-shield/scripts/shield.py scan"
```

### 查看风险报告

```bash
# 查看当前风险状态
python3 ~/.openclaw/workspace/skills/skill-shield/scripts/shield.py view
```

## 数据存储

### 风险数据库

位置: `~/.openclaw/workspace/memory/shield-risks.json`

```json
{
  "version": "1.0.0",
  "lastScanTime": "2026-03-11T09:45:00Z",
  "extensions": {
    "a-stock-dragon-tiger": {
      "path": "/path/to/extension",
      "risks": ["R001", "R004", "R006"],
      "severity": "severe",
      "scanTime": "2026-03-11T09:45:00Z",
      "userDecision": "approved"
    }
  },
  "allowlist": ["file-search", "weather-search"],
  "history": [
    {
      "extension": "a-stock-dragon-tiger",
      "action": "blocked",
      "time": "2026-03-11T09:50:00Z"
    }
  ]
}
```

## 集成到 Agent 工作流

如果你希望在每次使用扩展前自动检查，可以创建一个 wrapper。

不过需要注意:
- 这需要修改 agent 的行为
- 目前 skill-shield 需要手动调用
- 未来可以通过 hook 实现自动检查（暂未实现）

## 故障排除

### 扫描失败
```bash
# 检查扩展目录权限
ls -la ~/.openclaw/workspace/skills/

# 手动运行扫描查看错误
python3 ~/.openclaw/workspace/skills/skill-shield/scripts/shield.py scan -v
```

### 配置文件错误
```bash
# 重置配置文件
echo '{}' > ~/.openclaw/workspace/skills/skill-shield/config.json
```

## 扩展计划

- [ ] Hook 机制：在使用扩展前自动检查
- [ ] 安装时扫描：clawhub install 时自动扫描
- [ ] 风险修复建议：提供风险缓解建议
- [ ] 定期报告：每周发送安全报告到飞书

## 贡献

欢迎提交 Issue 和 Pull Request！

---

**安全提醒**: 请定期扫描和更新风险数据库，确保及时发现新的安全风险。