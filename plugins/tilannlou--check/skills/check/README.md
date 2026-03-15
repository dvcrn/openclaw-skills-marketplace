# OpenClaw Development Skills Bundle

这是一个为 OpenClaw 框架设计的开发工具包，包含五个重要的开发相关技能：

1. **环境检查器** - 检查系统环境是否满足AI/ML开发需求
2. **代码生成和测试运行器** - 生成代码、保存文件并运行测试
3. **RAG管理器** - 管理多个RAG系统，按类别组织并支持动态创建新分类
4. **权限管理器** - 处理系统权限问题，特别是PIP和系统命令执行权限
5. **通用权限管理器** - 通用权限管理器，可处理各种系统命令的权限问题

## 功能特性

### 环境检查器
- ✅ 检查系统中安装的工具（Python、pip、Git、Docker、Node.js等）
- ✅ 检查Python包安装状态（AI/ML相关、RAG相关、工具类等）
- ✅ 检查工作区目录结构（model、utils、scripts等）
- ✅ 检查RAG环境配置（API密钥等）
- ✅ 自动安装缺失的Python包

### 代码生成和测试运行器
- ✅ 根据自然语言需求生成代码
- ✅ 支持多种编程语言（Python、JavaScript、Java等）
- ✅ 运行生成的代码并捕获输出
- ✅ 运行用户提供的测试代码
- ✅ 将代码保存到指定文件路径
- ✅ 返回详细的执行结果

### RAG管理器
- ✅ 按层级结构组织RAG系统（大类 -> 子类 -> 项目）
- ✅ 预设分类结构：程式類（Python、JavaScript、Java、各種程式指令用法）和文章類（新聞、文章、技術文檔）
- ✅ 创建新的分类和子分类
- ✅ 添加项目到指定分类
- ✅ 搜索和获取特定项目
- ✅ 列出所有分类、子分类和项目
- ✅ 支持项目元数据存储

### 权限管理器
- ✅ 检查当前权限状态（是否为管理员、是否在WSL环境等）
- ✅ 诊断pip命令执行权限问题
- ✅ 提供针对性的权限修复建议
- ✅ 安全运行pip命令（自动添加--user标志避免权限问题）
- ✅ 尝试以提升权限运行系统命令
- ✅ 识别WSL环境并提供相应解决方案

### 通用权限管理器
- ✅ 检查常用命令（pip、docker、ollama、git等）的可访问性
- ✅ 提供通用的权限修复建议
- ✅ 智能运行任何系统命令（自动尝试多种权限策略）
- ✅ 根据系统环境自动选择最佳执行策略
- ✅ 支持多种权限提升和降权执行策略
- ✅ 自动重试机制（当一个策略失败时自动尝试其他策略）

## 安装到OpenClaw

### 方法一：通过命令行安装

```bash
# 在OpenClaw根目录下运行
clawdbot skill install e:/CHECK/
```

或者如果你将此工具上传到了GitHub：

```bash
clawdbot skill install username/openclaw-dev-skills
```

### 方法二：手动安装

1. 将此目录的全部文件复制到OpenClaw的skills目录下
2. 重启OpenClaw服务

```bash
# 找到OpenClaw的skills目录，通常是
# ~/.openclaw/skills/ 或类似的路径
cp -r e:/CHECK/* ~/.openclaw/skills/dev_skills/
```

### 方法三：通过Git安装

如果你想使用Git管理的方式：

```bash
# 首先你需要将此项目推送到一个Git仓库
# 然后在OpenClaw中安装
clawdbot skill install https://github.com/yourusername/openclaw-dev-skills
```

## 使用方法

### 环境检查器

安装完成后，你可以通过以下方式使用环境检查技能：

#### 检查环境
```
"检查我的开发环境"
"验证Python包是否齐全"
"检查系统环境是否满足AI开发要求"
```

#### 安装缺失的包
```
"安装缺失的Python包"
"帮我安装所有缺失的依赖"
```

#### 安装特定包
```
"安装numpy"
"安装langchain和openai"
```

### 代码生成和测试运行器

使用代码生成和测试运行技能：

#### 生成并运行代码
```
"生成一个计算阶乘的Python函数"
"写一个JavaScript程序来反转字符串"
"创建一个Java类来表示学生信息"
```

#### 运行测试
```
"运行以下测试代码..."
"对这个函数运行单元测试"
"执行测试验证功能"
```

#### 保存代码
```
"生成一个排序算法并保存到 sort.py"
"将计算器程序保存到 calc.js"
```

### RAG管理器

使用RAG管理技能：

#### 列出分类
```
"列出所有分类"
"显示分类列表"
"查看有哪些大类"
```

#### 列出子分类
```
"列出程式類的子分类"
"显示文章類下有哪些子类"
"查看程式類的子分类"
```

#### 列出项目
```
"列出程式類/Python下的项目"
"显示文章類/新聞中的内容"
"查看JavaScript子分类的项目"
```

#### 创建分类
```
"创建分类 新的大类名称"
"新建分类 学习资料"
```

#### 创建子分类
```
"创建子分类 程式類 新的编程语言"
"新建子分类 文章類 博客文章"
```

#### 搜索项目
```
"搜索 Python装饰器"
"查找 关键词"
"搜索 JavaScript异步编程"
```

### 权限管理器

使用权限管理技能：

#### 检查权限状态
```
"检查当前权限状态"
"检查权限"
"权限诊断"
```

#### 获取权限修复建议
```
"权限修复建议"
"如何解决权限问题"
"权限建议"
```

#### 安全运行pip命令
```
"pip安装 requests"
"pip安装 --user numpy"
"pip卸载 old-package"
```

#### 运行系统命令
```
"运行命令 dir"
"运行命令 ls -la"
"运行命令 netstat -an"
```

### 通用权限管理器

使用通用权限管理技能处理各种系统命令：

#### 检查权限状态
```
"检查当前权限状态"
"检查权限"
"权限诊断"
```

#### 获取权限修复建议
```
"权限修复建议"
"如何解决权限问题"
"权限建议"
```

#### 运行任何系统命令
```
"运行命令 pip install requests"
"运行命令 docker ps"
"运行命令 ollama list"
"运行命令 git clone https://repo.git"
"运行命令 npm install"
"运行命令 python script.py"
```

#### 直接执行命令
```
"pip install requests"
"docker ps"
"ollama run llama2"
"git status"
"npm install"
"python manage.py migrate"
```

## 输出示例

### 环境检查器输出
```json
{
  "timestamp": "2026-03-01T13:24:21.123456",
  "system": "Windows",
  "python_version": "3.11.5",
  "summary": {
    "total_checks": 30,
    "passed_checks": 12,
    "failed_checks": 18,
    "success_rate": 40.0,
    "environment_ready": false
  },
  "details": {
    "system_tools": {...},
    "python_packages": {...},
    "workspace": {...},
    "rag_environment": {...}
  }
}
```

### 代码生成和测试运行器输出
```json
{
  "status": "success",
  "generated_code": "...",
  "run_result": {
    "exit_code": 0,
    "stdout": "Hello World!",
    "stderr": ""
  },
  "test_result": null,
  "temp_file": "/tmp/tmpxyz123.py",
  "timestamp": "2026-03-01T13:24:21.123456"
}
```

### RAG管理器输出
```json
{
  "status": "success",
  "message": "分类 '学习资料' 创建成功",
  "category": "学习资料",
  "timestamp": "2026-03-01T13:24:21.123456"
}
```

### 权限管理器输出
```json
{
  "status": "success",
  "is_admin": false,
  "is_wsl": true,
  "pip_issue": true,
  "suggestions": [
    {
      "issue": "PIP执行失败",
      "solution": "在WSL中使用用户安装: pip install --user <package_name>",
      "alternative": "确保Python安装在WSL环境中而不是Windows中"
    }
  ],
  "timestamp": "2026-03-01T13:24:21.123456"
}
```

### 通用权限管理器输出
```json
{
  "status": "success",
  "command": "pip install requests",
  "return_code": 0,
  "stdout": "Collecting requests...",
  "stderr": "",
  "strategy_used": "user_flag",
  "timestamp": "2026-03-01T13:24:21.123456"
}
```

## 配置要求

- Python 3.7 或更高版本
- OpenClaw 框架
- 对应编程语言的运行环境
- 管理员权限（用于安装Python包）

## 支持的编程语言

- Python
- JavaScript
- Java
- C++
- C
- Go
- Rust
- Bash/Shell
- PHP
- Ruby
- TypeScript

## 权限说明

这些技能需要以下权限：

- `execute_commands`: 执行系统命令以运行代码
- `read_system_info`: 读取系统信息
- `install_packages`: 安装Python包
- `write_files`: 创建和修改文件
- `read_files`: 读取文件内容
- `delete_files`: 删除文件

## 故障排除

### 权限问题
如果遇到权限问题，请确保OpenClaw有足够的权限执行系统命令和安装Python包。

### 网络问题
安装Python包时需要网络连接，如果遇到网络问题，请检查网络设置。

### 代码执行超时
代码执行有30秒的超时限制，长时间运行的代码可能会被终止。

### 语言环境问题
确保目标编程语言的运行环境已正确安装。

### WSL环境问题
- 确认使用WSL2并正确配置网络
- 在WSL中使用--user标志安装Python包
- 确保Python安装在WSL环境中而非Windows中

## 贡献

欢迎提交Issue和Pull Request来改进这些技能！

## 许可证

MIT License