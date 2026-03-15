# Universal Permission Manager Skill

## 描述
一个用于处理各种系统命令权限问题的通用OpenClaw技能。该技能可以处理Windows和WSL环境下几乎任何系统命令的权限问题，包括但不限于pip、Ollama、Docker以及其他开发工具。

## 功能
- 检查当前权限状态（是否为管理员、是否在WSL环境等）
- 诊断常用命令（pip、docker、ollama、git等）的可访问性
- 提供通用的权限修复建议
- 智能运行任何系统命令（自动尝试多种权限策略）
- 根据系统环境自动选择最佳执行策略
- 识别WSL环境并提供相应解决方案
- 支持多种权限提升和降权执行策略

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

### 运行任何系统命令
```
运行命令 pip install requests
运行命令 docker ps
运行命令 ollama list
运行命令 git clone https://repo.git
运行命令 npm install
运行命令 python script.py
```

### 直接执行命令
```
pip install requests
docker ps
ollama run llama2
git status
npm install
python manage.py migrate
```

## 智能执行策略

当运行命令时，技能会自动尝试以下策略直到成功：

1. **直接执行** - 首先尝试直接运行命令
2. **用户标志** - 对于pip等命令，自动添加--user标志
3. **Sudo执行** - 在Linux/WSL上尝试使用sudo
4. **RunAs提示** - 在Windows上提示用户以管理员身份运行

## 输入参数
- 查询字符串包含要执行的命令

## 输出格式
返回JSON格式的结果，包括：
- 操作状态
- 详细信息（命令输出等）
- 使用的策略
- 时间戳
- 错误信息（如有）

## 适用场景
- OpenClaw在Windows/WSL环境下遇到权限问题
- 任何系统命令执行失败
- 需要安全运行系统命令
- 诊断WSL环境配置问题
- 开发工具权限问题

## 依赖
- Python 3.7+
- 系统命令行工具

## 注意事项
- 在Windows上，某些操作可能需要用户交互（如UAC提示）
- 某些命令可能需要较长时间执行
- 对于敏感操作，系统可能会要求确认