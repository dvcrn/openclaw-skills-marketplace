"""PollyReach WebSocket 接收模块 - 通过 Socket.IO 实时接收消息"""

import asyncio
import json
import re
import websockets
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from login import signin_device

DEFAULT_WS_URL = "wss://www.visuai.me/ws/socket.io/?EIO=4&transport=websocket"


def parse_message(msg: str):
    """
    解析 Socket.IO 消息，提取结构化数据。
    支持以下标签类型：
      - contact_search：搜索商家结果
      - booking_plan：预订方案确认
      - booking_summary：通话结果

    Returns:
        dict | None
    """
    if not msg.startswith("42"):
        return None
    try:
        payload = json.loads(msg[2:])
        event_data = payload[1]
        data = event_data.get("data", {}).get("data", {})
        content = data.get("content", "")
        
        Done = data.get("done", "")
    
        if event_data.get("data", {}).get("type", {}) == "chat:completion:error":
            if data.get("done", ""):
                mess = data.get("content", "")
                url =  data.get("url", "")
                return {"status": "message: " + mess + " Url: " + url}

        if not content:
                    return None
                
        # 按优先级依次尝试匹配各类型标签
        for tag in ("contact_search", "booking_plan", "booking_summary"):
            match = re.search(
                r'<details\s+type="' + tag + r'"[^>]*>(.*?)</details>',
                content,
                re.DOTALL,
            )
            if match:
                # contact_search 需要等 done=True 才取值
                if  not Done:
                    continue
                try:
                    # print(f"[匹配标签] {content}", flush=True)
                    result = json.loads(match.group(1).strip())
                    result["_tag"] = tag  # 标记来源标签
                    return result
                except json.JSONDecodeError:
                    continue

        return None
    except (json.JSONDecodeError, IndexError, AttributeError, KeyError):
        return None


async def listen(
    token: str = None,
    ws_url: str = DEFAULT_WS_URL,
    on_message=None,
    stop_event: asyncio.Event = None,
    ready_event: asyncio.Event = None,
):
    """
    连接 WebSocket 并持续监听消息。

    Args:
        token: 认证 token
        ws_url: WebSocket 地址
        on_message: 回调函数 callback(parsed_dict)，收到结构化消息时调用
        stop_event: asyncio.Event，set() 后停止监听
        ready_event: asyncio.Event，连接建立完成后 set()，通知调用方可以安全发送消息
    """
    if stop_event is None:
        stop_event = asyncio.Event()
    if token is None:
        token = signin_device().get("token", "")

    async with websockets.connect(ws_url) as ws:
        # 1) EIO open
        raw = await ws.recv()
        open_data = json.loads(raw[1:])
        ping_interval = open_data.get("pingInterval", 25000) / 1000

        # 2) Socket.IO CONNECT
        await ws.send("40" + json.dumps({"token": token}))
        await ws.recv()  # CONNECT ACK

        # 3) Emit chatV1
        await ws.send("42" + json.dumps(["chatV1", {"token": token}]))

        # 通知调用方：连接已建立，可以安全发送消息
        if ready_event:
            ready_event.set()

        # 4) Ping task
        async def send_pings():
            while not stop_event.is_set():
                await asyncio.sleep(ping_interval)
                await ws.send("2")

        ping_task = asyncio.create_task(send_pings())

        # 5) Listen
        try:
            async for msg in ws:
                if stop_event.is_set():
                    break
                if msg == "3" or msg == "2":
                    if msg == "2":
                        await ws.send("3")
                    continue

                parsed = parse_message(msg)
                if parsed and on_message:
                    on_message(parsed)
        except websockets.ConnectionClosed:
            pass
        finally:
            ping_task.cancel()


class Connection:
    """WebSocket 长连接管理器，三步解耦：连接、发送、监听完全独立。"""

    def __init__(self, token: str = None, ws_url: str = DEFAULT_WS_URL):
        self.token = token if token is not None else signin_device().get("token", "")
        self.ws_url = ws_url
        self._ready = asyncio.Event()
        self._stop = asyncio.Event()
        self._callbacks = []
        self._ping_task = None

    def on_message(self, callback):
        """注册消息回调（可随时注册，支持多个回调）"""
        self._callbacks.append(callback)

    def stop(self):
        """停止监听并断开连接"""
        self._stop.set()

    @property
    def is_ready(self) -> bool:
        """连接是否已就绪"""
        return self._ready.is_set()

    async def wait_ready(self, timeout: float = 10):
        """等待连接就绪"""
        await asyncio.wait_for(self._ready.wait(), timeout=timeout)

    async def connect(self):
        """启动长连接并持续监听，收到消息时触发已注册的回调。"""
        async with websockets.connect(self.ws_url) as ws:
            # EIO open
            raw = await ws.recv()
            open_data = json.loads(raw[1:])
            ping_interval = open_data.get("pingInterval", 25000) / 1000

            # Socket.IO CONNECT
            await ws.send("40" + json.dumps({"token": self.token}))
            await ws.recv()

            # Emit chatV1
            await ws.send("42" + json.dumps(["chatV1", {"token": self.token}]))

            # 标记连接就绪
            self._ready.set()

            # Ping task
            async def send_pings():
                while not self._stop.is_set():
                    await asyncio.sleep(ping_interval)
                    await ws.send("2")

            self._ping_task = asyncio.create_task(send_pings())

            try:
                async for msg in ws:
                    if self._stop.is_set():
                        break
                    if msg == "3" or msg == "2":
                        if msg == "2":
                            await ws.send("3")
                        continue

                    parsed = parse_message(msg)
                    if parsed:
                        for cb in self._callbacks:
                            cb(parsed)
            except websockets.ConnectionClosed:
                pass
            finally:
                if self._ping_task:
                    self._ping_task.cancel()


if __name__ == "__main__":
    def print_message(data):
        text = data.get("text", "")
        status = data.get("status", "")
        
        # print(f"[{status}] {text}")
        # if text:
        #     print(f"[{status}] {text}")

    asyncio.run(listen(on_message=print_message))
