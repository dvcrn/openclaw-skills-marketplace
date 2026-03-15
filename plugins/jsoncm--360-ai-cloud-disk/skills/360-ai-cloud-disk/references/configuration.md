# 配置说明

## 获取 API Key

请访问 [360 AI云盘 MCP 控制台](https://www.yunpan.com/v2/mcp) 获取您的 API_KEY 和 ECS_ENV 配置。

## 环境变量

### 通用配置

| 变量名 | 必需 | 说明 | 默认值 | 获取方式 |
|--------|------|------|--------|----------|
| `API_KEY` | ✅ | 360 AI云盘 API 密钥 | - | [获取链接](https://www.yunpan.com/v2/mcp) |
| `ECS_ENV` | ❌ | 环境配置（prod/test） | `prod` | [获取链接](https://www.yunpan.com/v2/mcp) |
| `SUB_CHANNEL` | ❌ | 渠道配置 | `open` | - |

### 动态鉴权（多用户场景）

| 变量名 | 必需 | 说明 | 优先级 |
|--------|------|------|--------|
| `MCP_API_KEY` | ❌ | 动态 API 密钥（覆盖 API_KEY） | 最高 |
| `MCP_ECS_ENV` | ❌ | 动态环境配置（覆盖 ECS_ENV） | 最高 |
| `MCP_SUB_CHANNEL` | ❌ | 动态渠道配置（覆盖 SUB_CHANNEL） | 最高 |

**动态鉴权说明：**
- 优先级：`MCP_*` 环境变量 > 普通环境变量 > `.env` 文件配置
- 适用于多用户场景，每次调用前设置不同的鉴权信息
- HTTP 模式下通过 Header 传递，不暴露在 URL 中

### 连接模式

| 变量名 | 必需 | 说明 | 默认值 |
|--------|------|------|--------|
| `MCP_MODE` | ❌ | 连接模式（http/npx/local） | `http` |

### HTTP 模式

| 变量名 | 必需 | 说明 | 默认值 |
|--------|------|------|--------|
| `MCP_HTTP_URL` | ❌ | HTTP API 端点 | `https://mcp.yunpan.com/mcp` |
| `MCP_HTTP_TIMEOUT` | ❌ | HTTP 超时时间（秒） | `30` |

> **特别说明：** 即使使用 HTTP 模式，当调用 `file-upload-stdio` 工具时，因为需要访问本地文件系统，系统会自动降级切换为 npx 模式执行。

### npx 模式

| 变量名 | 必需 | 说明 | 默认值 |
|--------|------|------|--------|
| `MCP_NPX_PACKAGE` | ❌ | npm 包名 | - |

## 连接模式说明

### HTTP 模式（推荐）

通过 HTTP API 与 MCP Server 通信，无需本地安装 MCP Server。

**优势：**
- 最简单的配置方式
- 无需本地安装 Node.js
- 适合生产环境
- 支持动态鉴权（通过 HTTP Header）

### npx 模式（可选）

使用 `npx` 从 npm 下载并运行 MCP Server。

**前提条件：**
- Node.js >= 14.0.0
- 网络连接（用于下载 npm 包）

## 动态鉴权使用示例

### 单用户场景（静态配置）

在 `.env` 文件中配置：
```bash
API_KEY=your_static_api_key
ECS_ENV=prod
```

### 多用户场景（动态鉴权）

每次调用前设置环境变量：
```bash
# 用户1调用
MCP_API_KEY=user1_key python3 executor.py user-info

# 用户2调用
MCP_API_KEY=user2_key python3 executor.py file-list path=/

# 用户3调用（带环境配置）
MCP_API_KEY=user3_key MCP_ECS_ENV=test python3 executor.py file-search key=文档
```

### 服务器集成示例

在服务器端，可以根据用户会话动态设置鉴权信息：
```python
import os
import subprocess

def execute_tool_for_user(user_id, tool_name, **kwargs):
    # 从数据库获取用户的 API Key
    user_api_key = get_user_api_key(user_id)
    
    # 设置环境变量
    env = os.environ.copy()
    env['MCP_API_KEY'] = user_api_key
    env['MCP_ECS_ENV'] = 'prod'
    
    # 执行工具
    result = subprocess.run(
        ['python3', 'executor.py', tool_name] + [f'{k}={v}' for k, v in kwargs.items()],
        env=env,
        capture_output=True,
        text=True
    )
    
    return json.loads(result.stdout)
```

## 系统依赖

- Python >= 3.8
- HTTP 模式：无额外依赖
- npx 模式：Node.js >= 14.0.0, npm
