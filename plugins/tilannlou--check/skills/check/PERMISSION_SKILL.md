# Permission Manager Skill

## 描述
一个用于处理系统权限问题的OpenClaw技能。该技能专门解决在Windows和WSL环境下执行系统命令（特别是pip、Ollama、Docker等服务）时遇到的权限问题。

## 功能
- 检查当前权限状态（是否为管理员、是否在WSL环境等）
- 诊断pip、Ollama、Docker命令执行权限问题
- 提供针对性的权限修复建议
- 安全运行pip命令（自动添加--user标志避免权限问题）
- 安全运行Ollama命令（检查服务状态和权限）
- 安全运行Docker命令（处理WSL集成和用户组问题）
- 尝试以提升权限运行系统命令
- 识别WSL环境并提供相应解决方案

## 使用方法

### 检查权限状态
```
检查当前权限状态
检查权限
权限诊断
```

### 获取权限修复建议
```
权限修复建议
如何解决权限问题
权限建议
```

### 安全运行pip命令
```
pip安装 requests
pip安装 --user numpy
pip卸载 old-package
```

### 安全运行Ollama命令
```
ollama list
ollama pull llama2
ollama run mistral
```

### 安全运行Docker命令
```
docker ps
docker images
docker run hello-world
```

### 运行系统命令
```
运行命令 dir
运行命令 ls -la
运行命令 netstat -an
```

## 输入参数
- 查询字符串包含操作类型和参数（如权限检查、pip命令、ollama命令、docker命令等）

## 输出格式
返回JSON格式的结果，包括：
- 操作状态
- 详细信息（权限状态、命令输出等）
- 时间戳
- 错误信息（如有）

## 适用场景
- OpenClaw在Windows/WSL环境下遇到权限问题
- pip命令执行失败
- Ollama服务无法访问或权限不足
- Docker命令因权限问题无法执行
- 系统命令无权限执行
- 需要安全安装Python包
- 诊断WSL环境配置问题

## 依赖
- Python 3.7+
- 系统命令行工具（pip, ollama, docker）

## 注意事项
- 在Windows上，某些操作可能需要用户交互（如UAC提示）
- 建议在WSL中使用--user标志安装Python包
- 确保Ollama服务正在运行
- 在WSL中确保Docker Desktop已启动并启用了WSL集成
- 对于敏感操作，系统可能会要求确认