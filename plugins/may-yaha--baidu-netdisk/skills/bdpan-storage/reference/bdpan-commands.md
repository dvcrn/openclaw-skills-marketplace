# bdpan CLI 命令快速参考

## 认证命令

### login - 登录授权

```bash
bdpan login
```

桌面环境下（macOS）将自动弹出 WebView 授权窗口，完成登录后自动关闭。无 GUI 环境（如 SSH 远程登录）会自动切换到手动输入模式。

### logout - 注销登录

```bash
bdpan logout
```

清除本地存储的认证信息（`~/.config/bdpan/config.json`）。

### whoami - 查看认证状态

```bash
bdpan whoami
```

显示当前登录状态、用户名和 Token 有效期信息。

**已登录时输出：**
```
认证状态: 已登录
用户名: your_username
Token 有效期至: 2026-04-04 10:30:00
```

**选项：**
- `--json` - JSON 格式输出

---

## 文件操作命令

### upload - 上传文件

```bash
bdpan upload <local> <remote>
```

| 参数 | 说明 |
|------|------|
| `local` | 本地文件或文件夹路径 |
| `remote` | 网盘目标路径（相对于 `/apps/bdpan/`） |

**示例：**
```bash
# 单文件上传
bdpan upload ./report.pdf report.pdf

# 文件夹上传
bdpan upload ./project/ project/

# 上传到子目录
bdpan upload ./data.tar.gz backup/data.tar.gz
```

**选项：**
- `--json` - JSON 格式输出上传结果

### download - 下载文件

```bash
bdpan download <remote> <local> [选项]
```

| 参数 | 说明 |
|------|------|
| `remote` | 网盘文件/文件夹路径（相对于 `/apps/bdpan/`）**或**百度网盘分享链接 |
| `local` | 本地保存路径 |

**选项：**
| 选项 | 说明 |
|------|------|
| `-p` | 提取码（用于分享链接，如果链接中未包含） |
| `-t` | 自定义转存目录（相对路径自动拼接 `/apps/bdpan`，绝对路径直接使用） |
| `--json` | JSON 格式输出下载结果 |

**示例：**
```bash
# 单文件下载
bdpan download report.pdf ./downloaded-report.pdf

# 文件夹下载
bdpan download project/ ./project-restore/

# 从分享链接下载（链接中包含提取码）
bdpan download "https://pan.baidu.com/s/1xxxxx?pwd=abcd" ./downloaded/

# 使用 -p 参数单独传入提取码
bdpan download "https://pan.baidu.com/s/1xxxxx" ./downloaded/ -p abcd

# 使用 -t 参数自定义转存目录
bdpan download "https://pan.baidu.com/s/1xxxxx?pwd=abcd" ./downloaded/ -t my-folder
```

**分享链接下载说明：**
- 自动识别分享链接格式 `https://pan.baidu.com/s/1{surl}?pwd={pwd}`
- 分享文件会先转存到 `/apps/bdpan/{日期}/` 目录（或使用 `-t` 指定的目录）
- 然后下载到指定的本地路径

### transfer - 转存分享文件到网盘（不下载到本地）

```bash
bdpan transfer <分享链接> [选项]
```

| 参数 | 说明 |
|------|------|
| `分享链接` | 百度网盘分享链接 |

**选项：**
| 选项 | 说明 |
|------|------|
| `-p` | 提取码（如果链接中未包含） |
| `-d` | 目标目录（相对路径自动拼接 `/apps/bdpan`，默认为应用根目录） |
| `--json` | JSON 格式输出转存结果 |

**示例：**
```bash
# 基本用法 - 转存到应用根目录 /apps/bdpan/
bdpan transfer "https://pan.baidu.com/s/1xxxxx" -p abcd

# 提取码在链接中
bdpan transfer "https://pan.baidu.com/s/1xxxxx?pwd=abcd"

# 指定目标目录
bdpan transfer "https://pan.baidu.com/s/1xxxxx" -p abcd -d my-folder/

# JSON 输出
bdpan transfer "https://pan.baidu.com/s/1xxxxx" -p abcd --json
```

**与 download 的区别：**
- `transfer` 仅将分享文件转存到自己的网盘，不下载到本地
- `download` 会先转存再下载到本地路径
- 适用于只需要保存到网盘、不需要本地副本的场景

### ls - 查看文件列表

```bash
bdpan ls [path]
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `path` | 要查看的目录路径 | 根目录 |

**选项：**
- `--json` - JSON 格式输出

**示例：**
```bash
# 查看根目录
bdpan ls

# 查看子目录
bdpan ls backup

# JSON 输出
bdpan ls --json
```

**输出格式：**
```
类型    大小          修改时间              文件名
------  ------------  --------------------  --------
目录     -            2026-02-20 10:30:00  documents
文件    1.5 MB        2026-02-25 15:20:00  readme.txt
文件    256 KB        2026-02-24 09:15:00  config.yaml

共 3 项
```

### share - 创建分享链接

```bash
bdpan share <path>
```

| 参数 | 说明 |
|------|------|
| `path` | 要分享的文件或文件夹路径 |

**示例：**
```bash
# 分享文件
bdpan share report.pdf

# 分享文件夹
bdpan share project

# JSON 输出
bdpan share --json report.pdf
```

**输出格式：**
```
分享链接创建成功!
链接: https://pan.baidu.com/s/1xxxxxxx
提取码: abcd
有效期: 7 天
```

---

## 版本管理命令

### update - 检查/更新版本

```bash
# 手动检查更新
bdpan update check

# 自动更新到最新版本
bdpan update
```

**说明：**
- CLI 启动时会自动检查更新
- 发现新版本会显示提示

### version - 查看版本信息

```bash
# 查看当前版本
bdpan version

# 检查是否有更新
bdpan version --check
```

---

## init - 查看安装信息（v3.4.0+）

```bash
bdpan init
```

显示安装路径、配置文件路径和 PATH 配置建议。

**输出示例：**
```
bdpan 安装信息
────────────────────────────
安装路径: /home/user/.local/bin/bdpan
配置路径: /home/user/.config/bdpan/config.json

PATH 配置建议:
  export PATH="$HOME/.local/bin:$PATH"
```

---

## 全局选项

| 选项 | 说明 |
|------|------|
| `--config-path <path>` | 指定配置文件完整路径（适用于 AI Agent 集成） |
| `--json` | JSON 格式输出 |
| `--no-check-update` | 禁用版本更新检查 |
| `--help` | 显示帮助 |
| `--version` | 显示版本 |

---

## JSON 输出格式

### ls 命令输出

```json
[
  {
    "Name": "report.pdf",
    "IsDir": false,
    "Size": 1536000,
    "Modified": "2026-02-25T15:20:00Z"
  },
  {
    "Name": "documents",
    "IsDir": true,
    "Size": 0,
    "Modified": "2026-02-20T10:30:00Z"
  }
]
```

### share 命令输出

```json
{
  "link": "https://pan.baidu.com/s/1xxxxxxx",
  "pwd": "abcd",
  "period": 604800,
  "short_url": "https://pan.baidu.com/s/1xxxxxxx",
  "share_id": "xxxxxxx",
  "path": "/apps/bdpan/report.pdf"
}
```

### upload/download 命令输出

```json
{
  "status": "success",
  "local_path": "./report.pdf",
  "remote_path": "report.pdf"
}
```

### transfer 命令输出

```json
{
  "status": "success",
  "remote_path": "my-folder/shared-file.pdf",
  "share_link": "https://pan.baidu.com/s/1xxxxx",
  "file_count": 1
}
```

---

## 路径规则

- 所有路径相对于应用根目录 `/apps/bdpan/`
- 支持相对路径: `backup/data.tar.gz`
- 支持绝对路径: `/apps/bdpan/backup/data.tar.gz`
- 路径穿越 `..` 会被自动阻止

> **⛔ 双向路径映射规则：** 调用 bdpan 命令时，"我的应用数据" 必须转换为 `/apps`；向用户展示路径时，`/apps` 必须转换为 "我的应用数据"。详见 [路径规则](../SKILL.md) 章节。

---

## 配置文件位置

```
~/.config/bdpan/config.json
```

**环境变量：**

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `BDPAN_CONFIG_PATH` | 配置文件完整路径（优先级最高） | 无 |
| `BDPAN_CONFIG_DIR` | 配置文件目录 | `~/.config/bdpan` |
| `BDPAN_INSTALL_DIR` | 二进制安装目录 | `~/.local/bin` |

**配置路径优先级（v3.4.0+）：**
1. `--config-path` 命令行参数（最高优先级）
2. `BDPAN_CONFIG_PATH` 环境变量
3. `BDPAN_CONFIG_DIR` 环境变量 + `config.json`
4. `~/.config/bdpan/config.json`（默认路径）

**使用示例：**
```bash
# 使用命令行参数指定配置
bdpan --config-path /custom/path/config.json ls

# 使用环境变量指定配置
export BDPAN_CONFIG_PATH=/custom/path/config.json
bdpan ls
```

### AI Agent 集成

当 AI Agent 无法通过默认路径读取配置时，可以通过以下方式指定：

```python
import subprocess
import os

env = os.environ.copy()
env["BDPAN_CONFIG_PATH"] = "/home/user/.config/bdpan/config.json"

result = subprocess.run(
    ["bdpan", "ls", "--json"],
    env=env,
    capture_output=True,
    text=True
)
```

---

## 常见错误码

| 错误 | 说明 | 解决方案 |
|------|------|---------|
| Token expired | Token 过期 | 重新登录 |
| Path not allowed | 路径不在允许范围 | 使用 /apps/bdpan/ 下的路径 |
| File not found | 文件不存在 | 检查路径是否正确 |

---

## 平台支持

| 功能 | macOS | Linux | Windows |
|------|-------|-------|---------|
| 基础功能 | ✅ | ✅ | ✅ |
| WebView 登录 | ✅ | - | ✅ |
