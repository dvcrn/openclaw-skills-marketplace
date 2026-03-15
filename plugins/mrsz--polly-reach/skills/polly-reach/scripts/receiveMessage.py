#!/usr/bin/env python3
"""Connection 解耦架构：启动长连接 + 注册回调 """

import asyncio
import sys
from pathlib import Path
# 强制 stdout 无缓冲，确保 OpenClaw 能实时读取输出
sys.stdout.reconfigure(line_buffering=True)

sys.path.insert(0, str(Path(__file__).parent))

from wss import Connection


async def main():
    conn = Connection()

    # Step 1: 注册回调 + 启动长连接（连接建立后自动监听回复）
    def on_reply(data):
        # print(f"[回复] {'data'}", flush=True)
        
        status = data.get("status", "")
        if status:
            print(f"[回复] {status}", flush=True)
            
        if _tag := data.get("_tag"):
            if _tag == "contact_search":
                text = data.get("text", "")
                if text :
                   print(f"[回复] {text}", flush=True)
                   return
            elif _tag == "booking_plan":
                content = data.get("content", "")
                if content :
                   print(f"[回复] {content}", flush=True)
                   return
            elif _tag == "booking_summary":
                text = data.get("text", "")
                if text:
                   print(f"[回复] {text}", flush=True)
        
        # text = data.get("text", "")
        # content = data.get("content", "")
        # steps = data.get("steps", "")
        # status = data.get("status", "")
        # if text :
        #     print(f"[回复] {text}", flush=True)
        #     return
        # if content:
        #     print(f"[回复] {content}", flush=True)
        # if steps:
        #     md = "\n".join(f"- **{s['label']}**: {s['detail']}" for s in steps)
        #     print(f"[回复] {md}", flush=True)
        # if status:
        #     print(f"[回复] {status}", flush=True)
            


    conn.on_message(on_reply)

    print("🔌 正在建立 WebSocket 长连接...")
    connect_task = asyncio.create_task(conn.connect())

    try:
        await conn.wait_ready()
    except asyncio.TimeoutError:
        print("❌ 连接超时")
        return

    print("✅ 长连接已建立，准备就绪（Ctrl+C 退出）\n")

    # 长连接一直保持，直到手动 Ctrl+C 或回调里调用 conn.stop()
    await connect_task


if __name__ == "__main__":
    asyncio.run(main())
