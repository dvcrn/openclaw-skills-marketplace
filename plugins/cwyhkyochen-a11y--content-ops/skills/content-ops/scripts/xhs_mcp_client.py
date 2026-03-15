#!/usr/bin/env python3
"""
小红书 MCP SSE 客户端
支持完整的 MCP 协议 over SSE
"""

import json
import requests
import sseclient
import uuid
import time
import threading
import queue

class MCPClient:
    def __init__(self, base_url="http://localhost:18060"):
        self.base_url = base_url
        self.message_endpoint = f"{base_url}/mcp"
        self.session = requests.Session()
        self.initialized = False
        self.pending_requests = {}
        self.response_queue = queue.Queue()
        self.sse_thread = None
        self.stop_event = threading.Event()
        
    def _sse_listener(self):
        """监听 SSE 事件"""
        try:
            # 建立 SSE 连接
            headers = {
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache"
            }
            
            response = self.session.get(
                self.message_endpoint,
                headers=headers,
                stream=True,
                timeout=60
            )
            
            client = sseclient.SSEClient(response)
            
            for event in client.events():
                if self.stop_event.is_set():
                    break
                    
                try:
                    data = json.loads(event.data)
                    if "id" in data and data["id"] in self.pending_requests:
                        req_id = data["id"]
                        self.pending_requests[req_id].put(data)
                except json.JSONDecodeError:
                    pass
                    
        except Exception as e:
            print(f"SSE 监听错误: {e}")
    
    def initialize(self):
        """初始化 MCP 会话"""
        if self.initialized:
            return True
            
        # 启动 SSE 监听线程
        self.sse_thread = threading.Thread(target=self._sse_listener)
        self.sse_thread.daemon = True
        self.sse_thread.start()
        
        time.sleep(0.5)  # 等待连接建立
        
        # 发送初始化请求
        init_request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "content-ops-client",
                    "version": "1.0.0"
                }
            }
        }
        
        response = self._send_request(init_request)
        
        if response and "result" in response:
            # 发送 initialized 通知
            initialized_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            self._send_notification(initialized_notification)
            self.initialized = True
            return True
        
        return False
    
    def _send_request(self, request):
        """发送请求并等待响应"""
        req_id = request.get("id")
        if req_id:
            self.pending_requests[req_id] = queue.Queue()
        
        try:
            response = self.session.post(
                self.message_endpoint,
                json=request,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if req_id:
                # 等待 SSE 响应
                try:
                    result = self.pending_requests[req_id].get(timeout=30)
                    del self.pending_requests[req_id]
                    return result
                except queue.Empty:
                    return None
            else:
                return response.json()
                
        except Exception as e:
            print(f"请求错误: {e}")
            return None
    
    def _send_notification(self, notification):
        """发送通知（不需要响应）"""
        try:
            self.session.post(
                self.message_endpoint,
                json=notification,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
        except Exception as e:
            print(f"通知错误: {e}")
    
    def call_tool(self, tool_name, arguments):
        """调用 MCP 工具"""
        if not self.initialized:
            if not self.initialize():
                return {"error": "初始化失败"}
        
        request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        return self._send_request(request)
    
    def close(self):
        """关闭连接"""
        self.stop_event.set()
        if self.sse_thread:
            self.sse_thread.join(timeout=2)


def main():
    print("🔌 连接小红书 MCP 服务...\n")
    
    client = MCPClient()
    
    try:
        # 初始化
        print("1. 初始化 MCP 会话...")
        if client.initialize():
            print("   ✅ 初始化成功\n")
        else:
            print("   ❌ 初始化失败\n")
            return
        
        # 检查登录状态
        print("2. 检查登录状态...")
        result = client.call_tool("check_login_status", {})
        
        if result and "result" in result:
            content = result["result"]["content"][0]["text"]
            print(f"   {content}\n")
        else:
            print(f"   错误: {result}\n")
        
        # 搜索 AI 内容
        print("3. 搜索 AI 相关内容...")
        search_result = client.call_tool("search_feeds", {
            "keyword": "AI人工智能",
            "filters": {
                "sort_by": "最多点赞",
                "publish_time": "一周内"
            }
        })
        
        if search_result and "result" in search_result:
            content_text = search_result["result"]["content"][0]["text"]
            data = json.loads(content_text)
            
            feeds = data.get("feeds", [])
            print(f"   ✅ 找到 {len(feeds)} 条内容\n")
            
            # 显示前5条
            for i, feed in enumerate(feeds[:5], 1):
                interact = feed.get("interact_info", {})
                title = feed.get("title", feed.get("desc", "无标题"))[:40]
                user = feed.get("user", {}).get("nickname", "未知")
                likes = interact.get("liked_count", 0)
                
                print(f"   {i}. {title}")
                print(f"      👤 {user} | 👍{likes}")
        else:
            print(f"   错误: {search_result}\n")
    
    finally:
        client.close()

if __name__ == "__main__":
    main()
