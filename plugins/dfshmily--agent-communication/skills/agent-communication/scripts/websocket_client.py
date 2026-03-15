#!/usr/bin/env python3
"""
WebSocket Agent 客户端
Agent 连接到消息代理进行实时通信
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Callable, Optional

try:
    import websockets
except ImportError:
    print("安装依赖: pip install websockets")
    sys.exit(1)

# 默认配置
DEFAULT_SERVER = "ws://localhost:8765"

class AgentClient:
    """WebSocket Agent 客户端"""
    
    def __init__(self, agent_id: str, server_url: str = DEFAULT_SERVER):
        self.agent_id = agent_id
        self.server_url = server_url
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.connected = False
        self.message_handler: Optional[Callable] = None
        self.reconnect_interval = 5
    
    async def connect(self):
        """连接到消息代理"""
        while True:
            try:
                self.websocket = await websockets.connect(self.server_url)
                self.connected = True
                
                # 注册
                await self.websocket.send(json.dumps({
                    "type": "register",
                    "agent_id": self.agent_id
                }))
                
                # 等待注册确认
                response = await self.websocket.recv()
                data = json.loads(response)
                
                if data.get("type") == "registered":
                    print(f"[CONNECTED] Agent '{self.agent_id}' 已连接")
                    return True
                
            except Exception as e:
                print(f"[ERROR] 连接失败: {e}")
                await asyncio.sleep(self.reconnect_interval)
    
    async def disconnect(self):
        """断开连接"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
    
    async def send(self, to_agent: str, message: str, priority: str = "normal"):
        """发送消息"""
        if not self.connected or not self.websocket:
            print("[ERROR] 未连接到服务器")
            return {"success": False, "error": "Not connected"}
        
        try:
            await self.websocket.send(json.dumps({
                "type": "send",
                "from": self.agent_id,
                "to": to_agent,
                "message": message,
                "priority": priority
            }))
            
            # 等待确认
            response = await self.websocket.recv()
            return json.loads(response)
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def broadcast(self, message: str, agents: list, priority: str = "normal"):
        """广播消息"""
        if not self.connected or not self.websocket:
            print("[ERROR] 未连接到服务器")
            return {"success": False, "error": "Not connected"}
        
        try:
            await self.websocket.send(json.dumps({
                "type": "broadcast",
                "from": self.agent_id,
                "message": message,
                "agents": agents,
                "priority": priority
            }))
            
            response = await self.websocket.recv()
            return json.loads(response)
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_status(self):
        """获取状态"""
        if not self.connected or not self.websocket:
            return {"error": "Not connected"}
        
        try:
            await self.websocket.send(json.dumps({"type": "status"}))
            response = await self.websocket.recv()
            return json.loads(response)
        except Exception as e:
            return {"error": str(e)}
    
    def on_message(self, handler: Callable):
        """设置消息处理器"""
        self.message_handler = handler
    
    async def listen(self):
        """监听消息"""
        while self.connected and self.websocket:
            try:
                data = await self.websocket.recv()
                msg = json.loads(data)
                
                # 调用消息处理器
                if self.message_handler:
                    await self.message_handler(msg)
                else:
                    # 默认处理
                    if msg.get("type") == "message":
                        print(f"[MESSAGE] From {msg['from']}: {msg['message']}")
            
            except websockets.exceptions.ConnectionClosed:
                self.connected = False
                print("[DISCONNECTED] 连接已断开，尝试重连...")
                await self.connect()
            
            except Exception as e:
                print(f"[ERROR] 监听错误: {e}")
                await asyncio.sleep(1)
    
    async def run(self, message_handler: Optional[Callable] = None):
        """运行客户端"""
        if message_handler:
            self.on_message(message_handler)
        
        await self.connect()
        await self.listen()


# 命令行接口
async def cli():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="WebSocket Agent 客户端")
    parser.add_argument("--agent", required=True, help="Agent ID")
    parser.add_argument("--server", default=DEFAULT_SERVER, help="服务器地址")
    parser.add_argument("--send", help="发送消息 (格式: to:message)")
    parser.add_argument("--broadcast", help="广播消息 (格式: agents:message)")
    
    args = parser.parse_args()
    
    client = AgentClient(args.agent, args.server)
    
    if args.send:
        # 发送模式
        await client.connect()
        to, message = args.send.split(":", 1)
        result = await client.send(to, message)
        print(json.dumps(result, indent=2))
        await client.disconnect()
    
    elif args.broadcast:
        # 广播模式
        await client.connect()
        agents_str, message = args.broadcast.split(":", 1)
        agents = agents_str.split(",")
        result = await client.broadcast(message, agents)
        print(json.dumps(result, indent=2))
        await client.disconnect()
    
    else:
        # 监听模式
        async def handle_message(msg):
            if msg.get("type") == "message":
                print(f"📨 [{msg['from']}] {msg['message']}")
            elif msg.get("type") == "status":
                print(f"🟢 [{msg['agent_id']}] {msg['status']}")
        
        await client.run(handle_message)


if __name__ == "__main__":
    asyncio.run(cli())