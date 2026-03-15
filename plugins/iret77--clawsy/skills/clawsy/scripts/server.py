#!/usr/bin/env python3
"""
Clawsy Server (Skill)
Runs on Agent/VPS. Listens for Clawsy client connections.
"""

import asyncio
import websockets
import json
import base64
import os
import sys
import argparse
import subprocess
import time

# --- Config ---
HOST = "0.0.0.0" # Listen on all interfaces
DEFAULT_PORT = 8765

CONNECTED_CLIENT = None
SERVER_PROCESS = None

def notify_agent(message):
    try:
        subprocess.Popen([
            "openclaw", "system", "event",
            "--text", message,
            "--mode", "now"
        ])
    except Exception as e:
        print(f"⚠️ Failed to notify agent: {e}")

async def handle_client(websocket):
    global CONNECTED_CLIENT
    
    # Close existing connection if any (one active client policy)
    if CONNECTED_CLIENT and CONNECTED_CLIENT != websocket:
        try:
            await CONNECTED_CLIENT.close(reason="New client connected")
        except:
            pass
            
    CONNECTED_CLIENT = websocket
    client_addr = websocket.remote_address
    print(f"✅ Clawsy Client connected from {client_addr}")
    notify_agent(f"🔌 Clawsy Client connected from {client_addr[0]}! 🦞")

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                msg_type = data.get("type")
                
                if msg_type == "hello":
                    hostname = data.get("hostname", "Unknown Mac")
                    print(f"👋 Hello from {hostname}")
                    notify_agent(f"👋 Connected to {hostname}")
                
                elif msg_type == "screenshot":
                    print("📸 Received screenshot!")
                    img_data = base64.b64decode(data.get("data"))
                    # Save with timestamp
                    ts = int(time.time())
                    filename = f"clawsy_screenshot_{ts}.png"
                    # Also update "latest" link/file
                    with open(filename, "wb") as f:
                        f.write(img_data)
                    
                    # Create symlink or copy to standard name for agent usage
                    standard_name = "clawsy_screenshot.png"
                    if os.path.exists(standard_name):
                        os.remove(standard_name)
                    try:
                        os.symlink(filename, standard_name)
                    except OSError:
                        # Fallback to copy if symlink fails
                        with open(standard_name, "wb") as f:
                            f.write(img_data)
                            
                    print(f"💾 Saved to {filename} (linked to {standard_name})")
                    notify_agent(f"📸 Screenshot received: {filename}")
                    
                elif msg_type == "clipboard":
                    content = data.get("data")
                    print(f"📋 Clipboard content received ({len(content)} chars)")
                    # Save to file for agent to read easily
                    with open("clawsy_clipboard.txt", "w") as f:
                        f.write(content)
                    notify_agent(f"📋 Clipboard received ({len(content)} chars). Saved to clawsy_clipboard.txt")
                
                elif msg_type == "ack":
                    status = data.get("status", "ok")
                    print(f"✅ Command acknowledged: {status}")
                    
                elif msg_type == "error":
                    err_msg = data.get("message", "Unknown error")
                    print(f"❌ Error from client: {err_msg}")
                    notify_agent(f"⚠️ Clawsy Error: {err_msg}")
                    
                else:
                    print(f"📩 Received unknown message type: {msg_type}")
                    
            except json.JSONDecodeError:
                print("⚠️ Received invalid JSON")
                
    except websockets.exceptions.ConnectionClosed:
        print("❌ Client disconnected")
        if CONNECTED_CLIENT == websocket:
            CONNECTED_CLIENT = None
            notify_agent("🔌 Clawsy Client disconnected")

async def input_loop():
    print("⌨️  Interactive Mode: type command (screenshot, clipboard, set <text>)")
    while True:
        try:
            cmd = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not cmd:
                break
            cmd = cmd.strip()
            
            if not CONNECTED_CLIENT:
                if cmd:
                    print("⚠️  No client connected")
                continue
                
            if cmd == "screenshot":
                await CONNECTED_CLIENT.send(json.dumps({"command": "screenshot"}))
                print("🚀 Sent screenshot command")
                
            elif cmd == "clipboard":
                await CONNECTED_CLIENT.send(json.dumps({"command": "get_clipboard"}))
                print("🚀 Sent get_clipboard command")
                
            elif cmd.startswith("set "):
                text = cmd[4:]
                await CONNECTED_CLIENT.send(json.dumps({"command": "set_clipboard", "content": text}))
                print(f"🚀 Sent set_clipboard command: {text}")
        except Exception as e:
            print(f"Error in input loop: {e}")

async def main():
    parser = argparse.ArgumentParser(description="Clawsy Server")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to listen on")
    args = parser.parse_args()

    print(f"🦞 Clawsy Server starting on {HOST}:{args.port}")
    
    server = await websockets.serve(handle_client, HOST, args.port, max_size=50*1024*1024)
    
    # Notify start
    notify_agent(f"🦞 Clawsy Server started on port {args.port}")
    
    # Run server and input loop concurrently
    await asyncio.gather(
        server.wait_closed(),
        input_loop()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Server stopping...")
