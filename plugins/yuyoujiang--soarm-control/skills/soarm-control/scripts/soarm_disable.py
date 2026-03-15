#!/usr/bin/env python3
"""
SOARM 机械臂失能脚本
断开机械臂连接，禁用伺服电机
"""

import argparse
import sys
import time


def disable_robot(port: str, robot_id: str) -> None:
    """断开机械臂连接"""
    try:
        from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig

        print(f"正在连接机械臂 (port={port}, id={robot_id})...")
        cfg = SO101FollowerConfig(
            port=port,
            id=robot_id,
            cameras={},
            use_degrees=True,
            max_relative_target=None,
            disable_torque_on_disconnect=True,  # 断开时禁用扭矩
        )
        robot = SO101Follower(cfg)
        robot.connect(calibrate=False)

        try:
            print("机械臂已连接，准备失能...")
            print("等待1秒以确保连接稳定...")
            time.sleep(1.0)
        finally:
            print("正在断开连接并失能机械臂...")
            robot.disconnect()
            print("✓ 机械臂已失能，连接已断开")

    except Exception as e:
        print(f"✗ 失能失败: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="失能 SOARM 机械臂（断开连接，禁用伺服电机）"
    )
    parser.add_argument("--port", type=str, default="/dev/ttyACM0",
                       help="串口设备（默认：/dev/ttyACM0）")
    parser.add_argument("--robot-id", type=str, default="openclaw_soarm",
                       help="机器人ID（默认：openclaw_soarm）")
    args = parser.parse_args()

    disable_robot(args.port, args.robot_id)


if __name__ == "__main__":
    main()
