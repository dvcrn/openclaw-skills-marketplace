#!/usr/bin/env python3
"""
Trip Planner OpenClaw Skill 脚本（零外部依赖）
用法: python3 trip_chat.py "<消息>" [当前城市] [session_id]
"""

import json
import os
import sys
import threading
import time
import uuid
import urllib.request
import urllib.error


BASE_URL = os.getenv("TRIP_PLANNER_URL", "http://10.200.5.213:8900")


def _health_check() -> bool:
    try:
        req = urllib.request.Request(f"{BASE_URL}/health", method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False


class Heartbeat:
    """每隔 interval 秒输出一行心跳，防止调用方认为脚本卡死。"""

    def __init__(self, interval=5):
        self._interval = interval
        self._stop = threading.Event()
        self._tick = 0
        self._last_status = "处理中"
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self._thread.start()

    def update(self, status: str):
        self._last_status = status

    def stop(self):
        self._stop.set()

    def _run(self):
        while not self._stop.wait(self._interval):
            self._tick += 1
            elapsed = self._tick * self._interval
            print(f"[进度] ({elapsed}s) {self._last_status}", flush=True)


def main():
    message = sys.argv[1] if len(sys.argv) > 1 else ""
    city = sys.argv[2] if len(sys.argv) > 2 else "北京市"
    session_id = sys.argv[3] if len(sys.argv) > 3 else str(uuid.uuid4())

    if not message:
        print(json.dumps({"error": "请提供用户消息作为第一个参数"}, ensure_ascii=False))
        sys.exit(1)

    if not _health_check():
        print(json.dumps({
            "error": f"无法连接 trip planner 服务: {BASE_URL}",
            "hint": "请确认服务已启动且 TRIP_PLANNER_URL 配置正确"
        }, ensure_ascii=False))
        sys.exit(1)

    body = json.dumps({
        "user_id": os.getenv("TRIP_PLANNER_USER_ID", ""),
        "user_token": os.getenv("TRIP_PLANNER_TOKEN", ""),
        "session_id": session_id,
        "message": message,
        "stream": True,
        "data": {"current_city": city},
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{BASE_URL}/api/v1/trip/chat",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    full_text = ""
    trip_data = {}
    sid = ""

    hb = Heartbeat(interval=5)
    print("[进度] 正在连接 trip planner 服务...", flush=True)
    hb.start()

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            hb.update("已连接，agent 正在规划行程")
            print("[进度] 已连接，等待 agent 处理...", flush=True)
            for raw_line in resp:
                line = raw_line.decode("utf-8").strip()
                if not line or not line.startswith("data: "):
                    continue
                try:
                    payload = json.loads(line[6:])
                except json.JSONDecodeError:
                    continue

                event = payload.get("event", "")
                if not sid:
                    sid = payload.get("session_id", "")

                if event == "thinking":
                    content = payload.get("content", "")
                    hb.update(content)
                    print(f"[进度] {content}", flush=True)
                elif event == "chunk":
                    full_text += payload.get("content", "")
                    hb.update("正在生成行程方案")
                elif event == "data":
                    trip_data = payload.get("data", {})
                elif event == "done":
                    if not full_text:
                        full_text = payload.get("response", "")
                    if not trip_data:
                        trip_data = payload.get("data", {})
    finally:
        hb.stop()

    print("[进度] 完成！正在输出结果...", flush=True)

    result = {"response": full_text, "session_id": sid or session_id}
    if trip_data:
        result["data"] = trip_data

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
