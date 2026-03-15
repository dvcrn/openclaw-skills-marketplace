---
name: skill-shield
description: "OpenClaw扩展安全管理系统。扫描已安装扩展的安全风险，提供allowlist策略控制，在使用高风险扩展前进行风险提示。适用于安全管理、风险评估、权限控制场景。"
---

# Skill Shield - OpenClaw扩展安全管理系统

## 概述

安全管理已安装的OpenClaw扩展，扫描风险、存储风险列表、提供allowlist策略控制，确保在使用高风险扩展前进行风险提示和用户确认。

## 核心功能

1. **自动扫描**：扫描所有已安装的扩展，识别安全风险
2. **风险评估**：基于代码分析识别10种常见安全风险
3. **Allowlist管理**：配置默认信任的扩展，跳过风险检查
4. **黑名单管理**：阻止危险扩展执行
5. **风险提示**：使用高风险扩展前提示用户确认
6. **持久存储**：保存风险报告到memory，支持历史查询

## 风险类别

| 风险ID | 风险名称 | 严重程度 | 检测关键词 |
|--------|----------|----------|-----------|
| R001 | 网络访问 | 高 | requests, curl, fetch, urllib, http, socket |
| R002 | 文件写入 | 高 | write, create, save, mkdir, rmdir, unlink |
| R003 | 文件读取 | 中 | read, open, cat, glob, listdir |
| R004 | 命令执行 | 严重 | exec, subprocess, shell, spawn, Popen, system |
| R005 | 外部API | 中 | api, webhook, endpoint, send, notify, post, get |
| R006 | 数据外发 | 严重 | upload, send, transfer, export, forward |
| R007 | 凭证访问 | 严重 | apiKey, password, token, secret, credential, auth |
| R008 | 无签名验证 | 低 | 无_meta.json文件 |
| R009 | 依赖未知 | 中 | requirements.txt, package.json, dependencies |
| R010 | 权限过宽 | 高 | chmod 777, allowlist, full |

## 使用方法

### 扫描所有扩展
```
执行skill-shield扫描所有已安装的扩展
```

### 检查特定扩展
```
执行skill-shield检查<extension-name>的风险
```

### 添加到Allowlist
```
执行skill-shield添加<extension-name>到allowlist
```

### 从Allowlist移除
```
执行skill-shield移除<extension-name>从allowlist
```

### 添加到黑名单
```
执行skill-shield添加<extension-name>到黑名单
```

### 查看风险报告
```
执行skill-shield查看风险列表
```

### 清除风险记录
```
执行skill-shield清除风险记录
```

## 配置说明

配置文件位置：`~/.openclaw/workspace/skills/skill-shield/config.json`

```json
{
  "allowlist": ["file-search", "weather-search"],
  "autoApprove": [],
  "blocked": [],
  "scanOnInstall": true,
  "promptOnHighRisk": true
}
```

- **allowlist**: 默认信任的扩展，跳过风险检查
- **autoApprove**: 自动批准的扩展（不需要用户确认）
- **blocked**: 黑名单，完全阻止执行
- **scanOnInstall**: 安装时自动扫描
- **promptOnHighRisk**: 高风险时提示用户

## 数据存储

风险数据库位置：`~/.openclaw/workspace/memory/shield-risks.json`

```json
{
  "version": "1.0.0",
  "lastScanTime": "2026-03-11T09:45:00Z",
  "skills": {
    "extension-name": {
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
      "extension": "extension-name",
      "action": "blocked",
      "time": "2026-03-11T09:50:00Z"
    }
  ]
}
```

## 使用示例

### 场景1：首次扫描
```
用户：扫描所有扩展
Agent：🔍 正在扫描9个扩展...
      
      📊 扫描完成!
      🔴 严重: 6
      🟠 高危: 1
      🟡 中危: 0
      🟢 低危/安全: 2
      
      💾 风险报告已保存
```

### 场景2：使用高风险扩展
```
用户：执行a-stock-dragon-tiger
Agent：⚠️ 安全警告
      扩展: a-stock-dragon-tiger
      风险等级: severe
      风险项:
        - R001: 网络访问
        - R004: 命令执行
        - R006: 数据外发
      是否继续? (yes/no):
用户：yes
Agent：✅ 继续执行
```

### 场景3：添加到Allowlist
```
用户：将weather-search添加到allowlist
Agent：✅ 已将weather-search添加到allowlist
      后续使用将不再提示风险
```

## 风险等级映射

| 严重程度 | 包含风险 | 用户确认要求 |
|----------|----------|-------------|
| 严重 | R004, R006, R007 | 强制确认 |
| 高 | R001, R002, R010 | 强制确认 |
| 中 | R003, R005, R009 | 建议确认 |
| 低 | R008 | 可选确认 |

## 技术实现

### 扫描流程
1. 遍历`~/.openclaw/workspace/skills/`目录
2. 读取每个扩展的SKILL.md、scripts/、references/
3. 基于关键词匹配识别风险
4. 计算严重程度等级
5. 生成风险报告并存储

### 检查流程
1. 检查扩展是否在allowlist → 跳过检查
2. 检查扩展是否在blocked → 阻止执行
3. 查询风险数据库 → 获取风险信息
4. 根据严重程度决定是否提示用户
5. 记录用户决策到历史

## 安全原则

- ✅ 所有高风险操作需要用户明确确认
- ✅ Allowlist中的扩展默认信任
- ✅ 风险记录持久化存储
- ✅ 支持审计历史查询
- ✅ 黑名单完全阻止执行

## 扩展计划

- [ ] Hook机制：在使用扩展前自动检查
- [ ] 安装时扫描：clawhub install时自动扫描
- [ ] 风险修复建议：提供风险缓解建议
- [ ] 定期报告：每周发送安全报告到飞书

## 故障排除

### 扫描失败
```bash
# 检查扩展目录权限
ls -la ~/.openclaw/workspace/skills/

# 手动运行扫描
python3 ~/.openclaw/workspace/skills/skill-shield/scripts/shield.py scan
```

### 配置文件错误
```bash
# 重置配置文件
echo '{}' > ~/.openclaw/workspace/skills/skill-shield/config.json
```

## 依赖要求

- Python 3.6+
- 无需额外依赖包
- 标准库：os, re, json, glob, hashlib, pathlib, datetime, argparse, typing