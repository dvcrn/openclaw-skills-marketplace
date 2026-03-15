---
name: file-manager-service
description: "文件管理服务（含启动/关闭/打开页面/移动文件）。Use when: 启动/停止/重启服务、打开 Web 页面、浏览/管理文件、查看文件内容、搜索文件、创建/删除/移动目录或文件、添加目录备注。服务运行在 http://127.0.0.1:8888，管理/root/.openclaw/workspace/projects 目录。"
---

# File Manager Service Skill

操作运行在 `http://127.0.0.1:8888` 的文件管理服务，管理 `/root/.openclaw/workspace/projects` 目录。

## 快速开始

### 服务管理

```bash
# 启动服务
python scripts/file_manager.py start

# 停止服务
python scripts/file_manager.py stop

# 重启服务
python scripts/file_manager.py restart

# 查看状态
python scripts/file_manager.py status

# 打开 Web 页面
python scripts/file_manager.py open
```

### 文件管理

```bash
# 列出文件
python scripts/file_manager.py list

# 列出指定目录
python scripts/file_manager.py list ai-agent-enterprise-design

# 查看文件内容
python scripts/file_manager.py cat path/to/file.md

# 搜索文件
python scripts/file_manager.py search 关键词

# 统计信息
python scripts/file_manager.py stats

# 创建目录
python scripts/file_manager.py mkdir parent/path NewDirName

# 删除文件/目录
python scripts/file_manager.py delete path/to/item

# 移动文件/目录
python scripts/file_manager.py move source/path dest/path

# 获取/设置目录备注
python scripts/file_manager.py note directory-name
python scripts/file_manager.py note directory-name 备注内容
```

### 直接调用 API

| 操作 | 端点 | 方法 |
|------|------|------|
| 列出文件 | `/api/files?path=xxx` | GET |
| 获取文件内容 | `/api/file/content?path=xxx` | GET |
| 保存文件 | `/api/file/save` | POST |
| 下载文件 | `/api/file/download?path=xxx` | GET |
| 删除 | `/api/delete` | POST |
| 移动 | `/api/move` | POST |
| 创建目录 | `/api/create/dir` | POST |
| 创建文件 | `/api/create/file` | POST |
| 搜索 | `/api/search?q=xxx` | GET |
| 统计 | `/api/stats` | GET |
| 获取备注 | `/api/notes/get?path=xxx` | GET |
| 保存备注 | `/api/notes/save` | POST |

## 使用示例

### 启动服务并打开页面

```bash
python scripts/file_manager.py start
python scripts/file_manager.py open
```

### 查看服务状态

```bash
python scripts/file_manager.py status
```

输出：
```json
{
  "running": true,
  "pid": 12345,
  "url": "http://127.0.0.1:8888",
  "service_dir": "/path/to/file-manager-service"
}
```

## 支持的文件类型

可编辑/查看的文件扩展名：
`.txt`, `.md`, `.html`, `.py`, `.js`, `.json`, `.yaml`, `.yml`, `.css`, `.xml`, `.log`, `.sh`, `.bash`, `.sql`, `.java`, `.go`, `.rs`, `.ts`, `.jsx`, `.tsx`, `.htm`, `.svg`

## 安全限制

- 所有路径必须在 `/root/.openclaw/workspace/projects` 内
- 不能删除根目录
- 隐藏文件（以`.`开头）不显示
- 目录备注仅支持第一级子目录

## 故障排除

**服务启动失败**：检查 `scripts/.service.log` 日志文件

**端口被占用**：`lsof -ti :8888 | xargs kill -9` 然后重新启动

**路径非法**：确保路径在允许的根目录内

**文件类型不支持**：检查文件扩展名是否在允许列表中
