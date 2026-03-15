#!/usr/bin/env python3
"""
SOARM 机械臂状态读取脚本
获取当前机械臂的关节角度、夹爪位置等信息
"""

import argparse
import json
import sys
import math


def get_robot_status(port: str, robot_id: str) -> dict:
    """获取机械臂状态"""
    try:
        from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig

        print(f"正在连接机械臂 (port={port}, id={robot_id})...")
        cfg = SO101FollowerConfig(
            port=port,
            id=robot_id,
            cameras={},
            use_degrees=True,
            max_relative_target=None,
            disable_torque_on_disconnect=True,
        )
        robot = SO101Follower(cfg)

        try:
            robot.connect(calibrate=False)
            print("已连接，读取状态...")
            obs = robot.get_observation()

            # 提取关键信息
            status = {
                "joints": {
                    "shoulder_pan": float(obs.get("shoulder_pan.pos", 0)),
                    "shoulder_lift": float(obs.get("shoulder_lift.pos", 0)),
                    "elbow_flex": float(obs.get("elbow_flex.pos", 0)),
                    "wrist_flex": float(obs.get("wrist_flex.pos", 0)),
                    "wrist_roll": float(obs.get("wrist_roll.pos", 0)),
                },
                "gripper": float(obs.get("gripper.pos", 0)),
            }

            return status

        finally:
            robot.disconnect()

    except Exception as e:
        print(f"✗ 读取状态失败: {e}", file=sys.stderr)
        sys.exit(1)


def print_status(status: dict, json_output: bool = False):
    """打印状态信息"""
    if json_output:
        print(json.dumps(status, indent=2))
        return

    print("\n" + "="*50)
    print("SOARM 机械臂当前状态")
    print("="*50)

    print("\n关节角度 (度):")
    print(f"  shoulder_pan  : {status['joints']['shoulder_pan']:8.3f}°")
    print(f"  shoulder_lift : {status['joints']['shoulder_lift']:8.3f}°")
    print(f"  elbow_flex    : {status['joints']['elbow_flex']:8.3f}°")
    print(f"  wrist_flex    : {status['joints']['wrist_flex']:8.3f}°")
    print(f"  wrist_roll    : {status['joints']['wrist_roll']:8.3f}°")

    print(f"\n夹爪位置: {status['gripper']:6.1f}/100")
    print("  (0=完全关闭, 100=完全打开)")

    print("="*50 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="获取 SOARM 机械臂当前状态"
    )
    parser.add_argument("--port", type=str, default="/dev/ttyACM0",
                       help="串口设备（默认：/dev/ttyACM0）")
    parser.add_argument("--robot-id", type=str, default="openclaw_soarm",
                       help="机器人ID（默认：openclaw_soarm）")
    parser.add_argument("--json", action="store_true",
                       help="以 JSON 格式输出")
    args = parser.parse_args()

    status = get_robot_status(args.port, args.robot_id)
    print_status(status, args.json)


if __name__ == "__main__":
    main()
