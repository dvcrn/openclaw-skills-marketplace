# WSL-PowerShell 控制器

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![WSL](https://img.shields.io/badge/WSL-2-blue)](https://docs.microsoft.com/en-us/windows/wsl/)
[![PowerShell](https://img.shields.io/badge/PowerShell-5.1%2B-blue)](https://github.com/PowerShell/PowerShell)
[![GitHub stars](https://img.shields.io/github/stars/TYzzt/wsl-powershell)](https://github.com/TYzzt/wsl-powershell)

从 WSL (Windows Subsystem for Linux) 环境调用 Windows PowerShell，实现 Linux 到 Windows 的跨系统控制。

## 🎯 功能特性

- ✅ 支持 Windows PowerShell 和 PowerShell Core
- ✅ 自动路径转换 (WSL ↔ Windows)
- ✅ 错误处理和调试模式
- ✅ 支持命令和脚本文件两种模式
- ✅ 详细的帮助和版本信息
- ✅ 彩色日志输出

## 📦 安装

### 方式 1：手动安装（推荐智能体使用）

```bash
# 克隆到 OpenClaw 工作区的 skills 目录
cd ~/.openclaw/workspace/skills
git clone https://github.com/TYzzt/wsl-powershell.git

# 添加执行权限
chmod +x wsl-powershell/scripts/psctl.sh
```

**智能体说明**：克隆后重启 OpenClaw 会话，技能会自动加载。

### 方式 2：使用 ClawHub CLI

```bash
# 安装 ClawHub CLI
npm install -g clawhub

# 登录
clawhub login

# 安装技能
clawhub install wsl-powershell
```

### 方式 3：直接下载

```bash
# 下载 ZIP
wget https://github.com/TYzzt/wsl-powershell/archive/refs/heads/main.zip
unzip main.zip -d ~/.openclaw/workspace/skills/
mv ~/.openclaw/workspace/skills/wsl-powershell-main ~/.openclaw/workspace/skills/wsl-powershell

# 添加执行权限
chmod +x ~/.openclaw/workspace/skills/wsl-powershell/scripts/psctl.sh
```

### 基本用法

```bash
# 执行 PowerShell 命令
./scripts/psctl.sh "Get-Process | Select-Object -First 5 Name,Id"

# 执行 PowerShell 脚本文件
./scripts/psctl.sh -f /mnt/c/scripts/myscript.ps1

# 检查 PowerShell 是否可用
./scripts/psctl.sh --check
```

## 📖 使用示例

### 系统信息

```bash
# 获取系统信息
./scripts/psctl.sh "Get-ComputerInfo | Select-Object WindowsProductName,WindowsVersion"

# 获取进程列表
./scripts/psctl.sh "Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Name,Id,CPU"

# 获取服务状态
./scripts/psctl.sh "Get-Service | Where-Object {\$_.Status -eq 'Running'} | Select-Object -First 10 Name,DisplayName"
```

### 文件操作

```bash
# 列出目录
./scripts/psctl.sh "Get-ChildItem C:\\Users"

# 复制文件
./scripts/psctl.sh "Copy-Item C:\\source\\file.txt C:\\dest\\file.txt -Force"

# 创建文件
./scripts/psctl.sh "New-Item -Path C:\\test.txt -ItemType File -Force"
```

### 进程管理

```bash
# 启动程序
./scripts/psctl.sh "Start-Process notepad.exe"

# 停止进程
./scripts/psctl.sh "Stop-Process -Name notepad -Force"
```

### 网络操作

```bash
# 获取网络配置
./scripts/psctl.sh "Get-NetIPConfiguration | Select-Object InterfaceAlias,IPv4Address"

# Ping 测试
./scripts/psctl.sh "Test-Connection -ComputerName google.com -Count 2"
```

### 路径转换

```bash
# 自动转换 WSL 路径到 Windows 路径
./scripts/psctl.sh -w "Get-ChildItem /mnt/c/Users"
```

## 🔧 高级选项

```bash
# 显示帮助
./scripts/psctl.sh --help

# 显示版本
./scripts/psctl.sh --version

# 调试模式
DEBUG=1 ./scripts/psctl.sh "Get-Process"

# 详细输出
./scripts/psctl.sh -v "Get-Service"

# 使用 PowerShell Core
./scripts/psctl.sh -p "Get-Module -ListAvailable"

# 检查 PowerShell 可用性
./scripts/psctl.sh --check
```

## 📁 项目结构

```
wsl-powershell/
├── README.md           # 项目说明
├── LICENSE             # Apache-2.0 许可证
├── CHANGELOG.md        # 变更日志
├── scripts/
│   ├── psctl.sh        # 主控制脚本
│   └── examples/       # 示例脚本
└── examples/           # 示例 PowerShell 脚本
```

## ⚙️ 配置

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DEBUG` | 启用调试模式 | `0` |
| `VERBOSE` | 启用详细输出 | `0` |
| `PWSH_PATH` | 自定义 PowerShell 路径 | 自动检测 |

### 路径说明

WSL 和 Windows 路径对照：

| WSL 路径 | Windows 路径 |
|----------|--------------|
| `/mnt/c/Users/Tao` | `C:\Users\Tao` |
| `/mnt/d/Projects` | `D:\Projects` |

使用 `wslpath` 命令转换：

```bash
wslpath -w /mnt/c/Users  # 输出：C:\Users
wslpath -u C:\\Users     # 输出：/mnt/c/Users
```

## ⚠️ 注意事项

1. **权限**: 某些操作可能需要管理员权限
   ```bash
   # 启动提升的 PowerShell
   ./scripts/psctl.sh "Start-Process powershell -Verb RunAs"
   ```

2. **路径转义**: Windows 路径中的 `\` 需要转义为 `\\`

3. **执行策略**: 运行脚本可能需要设置执行策略
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

4. **编码**: PowerShell 默认输出 UTF-16，可能需要转换

## 🔒 安全提示

- ⚠️ 谨慎执行系统级命令
- ⚠️ 避免删除关键系统文件
- ⚠️ 测试命令前先确认影响范围
- ⚠️ 不要执行来源不明的脚本

## 🤖 智能体集成

### 技能加载机制

OpenClaw 会自动扫描以下目录的技能：

1. `~/.openclaw/workspace/skills/` - 主工作区技能
2. `./skills/` - 当前工作目录下的技能

### 技能激活

安装后**重启 OpenClaw 会话**，技能会自动加载。智能体可以：

1. **直接调用脚本**：
   ```bash
   ~/.openclaw/workspace/skills/wsl-powershell/scripts/psctl.sh "PowerShell 命令"
   ```

2. **通过技能描述自动学习**：
   - 智能体会读取 `SKILL.md` 了解技能功能
   - 根据用户请求自动选择使用此技能

3. **示例场景**：
   - "查询 Windows 更新策略"
   - "查看 Windows 进程列表"
   - "获取系统信息"

### 技能依赖

- **WSL2** - Windows Subsystem for Linux 2
- **Windows PowerShell** - 位于 `/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe`
- **bash** - WSL 环境中的 shell

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 Apache-2.0 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [WSL](https://docs.microsoft.com/en-us/windows/wsl/) - Windows Subsystem for Linux
- [PowerShell](https://github.com/PowerShell/PowerShell) - PowerShell Core

## 📮 项目链接

- **Repository**: [github.com/TYzzt/wsl-powershell](https://github.com/TYzzt/wsl-powershell)
- **Clone**: `git clone https://github.com/TYzzt/wsl-powershell.git`
- **ClawHub**: `clawhub install wsl-powershell` (即将上线)
