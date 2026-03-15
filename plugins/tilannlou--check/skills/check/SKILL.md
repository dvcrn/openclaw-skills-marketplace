---
name: check
description: "CHECK"
---

# Environment Checker Skill

## 描述
检查系统环境是否满足AI/ML开发需求的工具，包括Python包、系统工具、工作区结构和RAG环境配置的检查。

## 功能
- 检查系统中安装的工具（Python、pip、Git、Docker、Node.js等）
- 检查Python包安装状态（AI/ML相关、RAG相关、工具类等）
- 检查工作区目录结构（model、utils、scripts等）
- 检查RAG环境配置（API密钥等）
- 自动安装缺失的Python包

## 使用方法

### 检查环境
```
检查我的开发环境
检查系统环境是否满足AI开发要求
验证Python包是否齐全
```

### 安装缺失的包
```
安装缺失的Python包
帮我安装所有缺失的依赖
```

### 安装特定包
```
安装numpy
安装langchain和openai
```

## 输入参数
- 无特殊参数，根据用户请求的意图自动执行相应功能

## 输出格式
返回JSON格式的环境检查结果，包括：
- 时间戳
- 系统信息
- Python版本
- 检查摘要（总数、通过数、失败数、成功率）
- 详细的检查结果（系统工具、Python包、工作区、RAG环境）

## 适用场景
- 新环境搭建时的环境检查
- AI/ML项目初始化前的依赖验证
- RAG应用部署前的环境验证
- 定期环境维护和依赖更新

## 依赖
- Python 3.7+
- pip
- 系统需支持subprocess调用（大多数现代操作系统均支持）

## 注意事项
- 部分Python包可能需要较长的安装时间
- 安装包时可能需要网络连接
- 某些系统工具检查可能需要管理员权限