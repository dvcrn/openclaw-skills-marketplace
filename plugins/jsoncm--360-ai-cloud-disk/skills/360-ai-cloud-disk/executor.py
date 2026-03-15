#!/usr/bin/env python3
"""
360 AI Cloud Disk - Executor
自动生成的 MCP 工具执行器

支持三种模式：
- local: 本地运行 MCP Server（开发调试）
- npx: 通过 npx 远程运行 MCP Server（需要 Node.js 环境）
- http: 通过 HTTP API 连接（最简单，推荐）
"""

import subprocess
import json
import sys
import os
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class MCPExecutor:
    """MCP 工具执行器 - 支持多模式连接"""

    def __init__(self):
        # 连接模式：local/npx/http
        self.mode = os.getenv("MCP_MODE", "http").lower()

        # 通用配置
        self.mcp_env = {
            "API_KEY": os.getenv("API_KEY", ""),
            "ECS_ENV": os.getenv("ECS_ENV", "prod"),
            "SUB_CHANNEL": os.getenv("SUB_CHANNEL", "open")
        }
        self.process = None
        self.id_counter = 1

        # 根据模式初始化配置
        if self.mode == "local":
            # 本地模式：使用本地构建的 MCP Server
            self.mcp_command = "node"
            self.mcp_args = ["./build/index.js","--stdio"]
            self.working_dir = os.getenv("MCP_SERVER_DIR", ".")
            print(f"[MCP] 使用本地模式，工作目录: {self.working_dir}")

        elif self.mode == "npx":
            # npx 模式：使用远程 npm 包
            self.mcp_command = "npx"
            npx_package = os.getenv("MCP_NPX_PACKAGE", "@aicloud360/mcp-server-disk@latest")
            self.mcp_args = ["-y", npx_package, "--stdio"]
            self.working_dir = None  # npx 不需要工作目录
            print(f"[MCP] 使用 npx 模式，包名: {npx_package}")

        elif self.mode == "http":
            # HTTP 模式：使用 HTTP API
            self.http_url = os.getenv("MCP_HTTP_URL", "https://mcp.yunpan.com/mcp")
            if not self.http_url:
                raise ValueError("HTTP 模式需要设置 MCP_HTTP_URL 环境变量")
            self.timeout = int(os.getenv("MCP_HTTP_TIMEOUT", "30"))
            print(f"[MCP] 使用 HTTP 模式，URL: {self.http_url}")

        else:
            raise ValueError(f"不支持的 MCP_MODE: {self.mode}，支持值：local/npx/http")

    def _start_process(self):
        """启动 MCP Server 进程（用于 local/npx 模式）"""
        if self.process and self.process.poll() is None:
            # 进程已经在运行
            return

        # 准备环境变量
        env = os.environ.copy()
        env.update(self.mcp_env)

        # 启动进程
        self.process = subprocess.Popen(
            [self.mcp_command] + self.mcp_args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            # 将 stderr 重定向到 sys.stderr，避免缓冲区阻塞，并允许用户看到日志
            stderr=sys.stderr,
            text=True,
            env=env,
            cwd=self.working_dir,
            bufsize=1  # 行缓冲
        )

        # 发送 initialize 请求
        init_request = {
            "jsonrpc": "2.0",
            "id": self.id_counter,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-02-02",
                "capabilities": {},
                "clientInfo": {
                    "name": "Claude Skill Executor",
                    "version": "1.0.0"
                }
            }
        }
        self.id_counter += 1

        self.process.stdin.write(json.dumps(init_request) + "\n")
        self.process.stdin.flush()

        # 读取 initialize 响应
        init_response = self._read_response()
        if not init_response.get("result"):
            raise Exception(f"初始化 MCP Server 失败: {init_response}")

    def _read_response(self, timeout=30):
        """读取 MCP 响应（用于 local/npx 模式）"""
        import select

        if hasattr(select, 'poll'):
            # Unix/Linux 系统
            poll_obj = select.poll()
            poll_obj.register(self.process.stdout, select.POLLIN)

            # 等待数据可读
            events = poll_obj.poll(timeout * 1000)  # 转换为毫秒
            if not events:
                raise Exception("读取 MCP 响应超时")

            # 读取一行
            line = self.process.stdout.readline()
        else:
            # Windows 系统
            import time
            start_time = time.time()
            line = ""

            while time.time() - start_time < timeout:
                char = self.process.stdout.read(1)
                if char == '\n':
                    break
                line += char
                time.sleep(0.01)

            if not line.endswith('\n'):
                raise Exception("读取 MCP 响应超时")

        if not line.strip():
            raise Exception("MCP Server 没有返回有效响应")

        try:
            response = json.loads(line.strip())
            return response
        except json.JSONDecodeError:
            raise Exception(f"解析 MCP 响应失败: {line}")

    def _execute_http(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """通过 HTTP 模式执行工具调用
        
        鉴权机制（优先级从高到低）：
        1. 动态环境变量: MCP_API_KEY, MCP_ECS_ENV, MCP_SUB_CHANNEL
        2. 静态环境变量: API_KEY, ECS_ENV, SUB_CHANNEL
        3. .env 文件中的配置
        
        传递方式：通过 HTTP Header 传递（更安全，不暴露在 URL 中）
        """
        try:
            # 构建请求 URL (JSON-RPC 端点)
            base_url = self.http_url.rstrip('/')
            if not base_url.endswith('/mcp'):
                 # 简单处理：如果 URL 不以 /mcp 结尾，尝试追加。
                 if not base_url.endswith('/'):
                     base_url += '/mcp'
                 else:
                     base_url += 'mcp'
            
            url = base_url
            
            # 获取鉴权信息（支持动态覆盖）
            # 优先级: MCP_* 环境变量 > 普通环境变量 > self.mcp_env（来自 .env）
            api_key = os.getenv("MCP_API_KEY") or os.getenv("API_KEY") or self.mcp_env.get("API_KEY", "")
            ecs_env = os.getenv("MCP_ECS_ENV") or os.getenv("ECS_ENV") or self.mcp_env.get("ECS_ENV", "prod")
            sub_channel = os.getenv("MCP_SUB_CHANNEL") or os.getenv("SUB_CHANNEL") or self.mcp_env.get("SUB_CHANNEL", "open")
            
            # 构建请求头（使用 Header 传递鉴权信息，比 URL 参数更安全）
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json, text/event-stream',
                'User-Agent': 'Claude Skill Executor/1.0.0'
            }
            
            # 添加鉴权 Header
            if api_key:
                headers['X-API-Key'] = api_key
            if ecs_env:
                headers['X-ECS-Env'] = ecs_env
            if sub_channel:
                headers['X-Sub-Channel'] = sub_channel
            
            # 日志输出（隐藏敏感信息）
            masked_key = f"{api_key[:8]}...{api_key[-4:]}" if api_key and len(api_key) > 12 else "***"
            print(f"[MCP] HTTP 请求: {url}")
            print(f"[MCP] 鉴权: api_key={masked_key}, ecs_env={ecs_env}, sub_channel={sub_channel}")

            # 构建 JSON-RPC 请求数据
            request_payload = {
                "jsonrpc": "2.0",
                "id": self.id_counter,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": kwargs
                }
            }
            self.id_counter += 1
            request_body = json.dumps(request_payload).encode('utf-8')

            # 构建请求
            req = urllib.request.Request(
                url,
                data=request_body,
                method='POST',
                headers=headers
            )

            # 发送请求
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                data = response.read().decode('utf-8')
                json_response = json.loads(data)
                
                if "error" in json_response:
                    return {
                        "success": False,
                        "error": json_response["error"]
                    }
                
                return {
                    "success": True,
                    "result": json_response.get("result", {})
                }

        except urllib.error.HTTPError as e:
            error_detail = ""
            if e.fp:
                try:
                    error_detail = e.fp.read().decode('utf-8')
                except:
                    pass
            return {
                "success": False,
                "error": f"HTTP 错误 {e.code}: {error_detail or e.reason}"
            }

        except urllib.error.URLError as e:
            return {
                "success": False,
                "error": f"连接错误: {e.reason}"
            }

        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"解析响应失败: {str(e)}"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"HTTP 请求失败: {str(e)}"
            }

    def execute(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """执行 MCP 工具调用"""
        try:
            # 针对本地文件处理工具，若当前为 HTTP 模式则自动降级到 npx 模式
            if tool_name in ["file-upload-stdio"] and self.mode == "http":
                print(f"[MCP] 工具 {tool_name} 需要访问本地文件系统，自动切换为 npx 模式执行")
                self.mode = "npx"
                self.mcp_command = "npx"
                npx_package = os.getenv("MCP_NPX_PACKAGE", "@aicloud360/mcp-server-disk@latest")
                self.mcp_args = ["-y", npx_package, "--stdio"]
                self.working_dir = None

            if self.mode == "http":
                # HTTP 模式：使用 HTTP API
                return self._execute_http(tool_name, **kwargs)
            else:
                # local/npx 模式：使用 subprocess + JSON-RPC stdio
                # 启动进程（如果尚未启动）
                self._start_process()

                # 构建 MCP 请求
                request = {
                    "jsonrpc": "2.0",
                    "id": self.id_counter,
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": kwargs
                    }
                }
                self.id_counter += 1

                # 发送请求
                self.process.stdin.write(json.dumps(request) + "\n")
                self.process.stdin.flush()

                # 读取响应
                response = self._read_response()

                if "error" in response:
                    return {
                        "success": False,
                        "error": response["error"]
                    }

                return {
                    "success": True,
                    "result": response.get("result", {})
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"执行 MCP 工具失败: {str(e)}"
            }

    def close(self):
        """关闭 MCP Server 进程（用于 local/npx 模式）"""
        if self.mode == "http":
            # HTTP 模式不需要关闭连接
            return

        if self.process and self.process.poll() is None:
            # 发送 shutdown 请求
            try:
                shutdown_request = {
                    "jsonrpc": "2.0",
                    "id": self.id_counter,
                    "method": "shutdown"
                }
                self.id_counter += 1

                self.process.stdin.write(json.dumps(shutdown_request) + "\n")
                self.process.stdin.flush()

                # 读取 shutdown 响应
                self._read_response()

                # 发送 exit 通知
                exit_notification = {
                    "jsonrpc": "2.0",
                    "method": "exit"
                }
                self.process.stdin.write(json.dumps(exit_notification) + "\n")
                self.process.stdin.flush()
            except:
                pass  # 忽略关闭时的错误

            # 等待进程结束
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()

            self.process = None

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: python executor.py <tool_name> [args...]")
        print("\n支持的连接模式（通过 MCP_MODE 环境变量设置）:")
        print("  local  : 本地 MCP Server（开发场景）")
        print("  npx    : 远程 npm 包（需要 Node.js）")
        print("  http   : HTTP API（最简单，默认）")
        print("\n示例:")
        print("  MCP_MODE=local python executor.py user-info")
        print("  MCP_MODE=npx python executor.py file-list path=/")
        print("  MCP_MODE=http MCP_HTTP_URL=https://mcp.yunpan.com/mcp python executor.py user-info")
        sys.exit(1)

    tool_name = sys.argv[1]
    args = {}

    # 解析参数
    for arg in sys.argv[2:]:
        if "=" in arg:
            key, value = arg.split("=", 1)
            try:
                parsed_value = json.loads(value)
                if not isinstance(parsed_value, str) or (value.startswith('"') and value.endswith('"')):
                    value = parsed_value
            except Exception:
                pass
            args[key] = value

    # 执行工具
    executor = MCPExecutor()
    try:
        result = executor.execute(tool_name, **args)
        # 输出结果
        print(json.dumps(result, indent=2, ensure_ascii=False))
    finally:
        executor.close()

if __name__ == "__main__":
    main()