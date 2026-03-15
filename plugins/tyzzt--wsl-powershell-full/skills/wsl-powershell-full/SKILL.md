---
name: wsl-powershell-full
description: "WSL-PowerShell Controller (Full)"
---

# WSL-PowerShell 控制技能

通过 WSL 调用 Windows PowerShell，实现从 Linux 环境控制 Windows 宿主机。

## 原理

WSL 挂载 Windows 盘符到 `/mnt/`，可以直接调用 Windows 可执行文件：
- PowerShell: `/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe`
- CMD: `/mnt/c/Windows/System32/cmd.exe`

## 使用方法

### 直接执行 PowerShell 命令

```bash
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command "命令"
```

### 执行 PowerShell 脚本

```bash
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -File "/mnt/c/path/to/script.ps1"
```

## 常用命令示例

### 系统信息
```bash
# 获取系统信息
powershell.exe -Command "Get-ComputerInfo"

# 获取进程列表
powershell.exe -Command "Get-Process | Select-Object -First 10 Name,Id,CPU"

# 获取服务状态
powershell.exe -Command "Get-Service | Where-Object {$_.Status -eq 'Running'} | Select-Object -First 10 Name,DisplayName"
```

### 文件操作
```bash
# 列出目录
powershell.exe -Command "Get-ChildItem C:\\Users"

# 复制文件
powershell.exe -Command "Copy-Item C:\\source\\file.txt C:\\dest\\file.txt"

# 创建文件
powershell.exe -Command "New-Item -Path C:\\test.txt -ItemType File -Force"
```

### 进程管理
```bash
# 启动程序
powershell.exe -Command "Start-Process notepad.exe"

# 停止进程
powershell.exe -Command "Stop-Process -Name notepad -Force"
```

### 网络操作
```bash
# 获取网络配置
powershell.exe -Command "Get-NetIPConfiguration"

# Ping 测试
powershell.exe -Command "Test-Connection -ComputerName google.com -Count 2"
```

## 路径转换

WSL 路径 ↔ Windows 路径：
- WSL: `/mnt/c/Users/Tao` ↔ Windows: `C:\Users\Tao`
- 使用 `wslpath` 命令转换：
  ```bash
  wslpath -w /mnt/c/Users  # 输出 C:\Users
  wslpath -u C:\\Users     # 输出 /mnt/c/Users
  ```

## 注意事项

1. **权限**: 某些操作可能需要管理员权限，使用 `-Verb RunAs` 启动提升的 PowerShell
2. **路径转义**: Windows 路径中的 `\` 需要转义为 `\\`
3. **编码**: PowerShell 默认输出 UTF-16，可能需要转换
4. **执行策略**: 运行脚本可能需要 `Set-ExecutionPolicy`

## 安全提示

- 谨慎执行系统级命令
- 避免删除关键系统文件
- 测试命令前先确认影响范围
