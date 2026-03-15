#!/usr/bin/env python3
"""
SOARM 机械臂关节角度控制脚本
直接设置每个关节的角度，不经过 IK 计算
"""

import argparse
import time
from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig


def main():
    parser = argparse.ArgumentParser(description="设置机械臂关节角度")
    parser.add_argument("--shoulder-pan", type=float, required=True, help="肩部旋转角度 (度)")
    parser.add_argument("--shoulder-lift", type=float, required=True, help="肩部抬起角度 (度)")
    parser.add_argument("--elbow-flex", type=float, required=True, help="肘部弯曲角度 (度)")
    parser.add_argument("--wrist-flex", type=float, required=True, help="腕部弯曲角度 (度)")
    parser.add_argument("--wrist-roll", type=float, required=True, help="腕部旋转角度 (度)")
    parser.add_argument("--gripper", type=float, default=None, help="夹爪位置 (0-100)")
    parser.add_argument("--speed", type=float, default=30, help="移动速度 (度/秒)")
    parser.add_argument("--port", type=str, default="/dev/ttyACM0", help="串口设备")
    parser.add_argument("--robot-id", type=str, default="openclaw_soarm", help="机器人ID")
    parser.add_argument("--keep-connected", action="store_true", help="移动完成后保持连接，不释放机械臂")
    args = parser.parse_args()

    joint_names = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll"]
    target_joints = {
        "shoulder_pan": args.shoulder_pan,
        "shoulder_lift": args.shoulder_lift,
        "elbow_flex": args.elbow_flex,
        "wrist_flex": args.wrist_flex,
        "wrist_roll": args.wrist_roll,
    }

    # 连接机械臂
    print(f"连接机械臂 (port={args.port})...")
    cfg = SO101FollowerConfig(
        port=args.port,
        id=args.robot_id,
        cameras={},
        use_degrees=True,
    )
    robot = SO101Follower(cfg)
    robot.connect()
    print("已连接")

    try:
        # 读取当前位置
        obs = robot.get_observation()
        start_joints = {name: float(obs[f"{name}.pos"]) for name in joint_names}

        # 夹爪处理
        gripper_start = float(obs.get("gripper.pos", 0))
        gripper_target = args.gripper if args.gripper is not None else gripper_start

        print(f"\n当前关节角度:")
        for name in joint_names:
            print(f"  {name}: {start_joints[name]:.2f}°")

        print(f"\n目标关节角度:")
        for name in joint_names:
            print(f"  {name}: {target_joints[name]:.2f}°")

        if args.gripper is not None:
            print(f"夹爪: {gripper_target}")

        # 计算运动参数
        max_delta = max(abs(target_joints[name] - start_joints[name]) for name in joint_names)
        duration = max(1.0, max_delta / args.speed)
        hz = 30
        steps = max(1, int(duration * hz))

        print(f"\n移动中 (速度: {args.speed} deg/s, 预计 {duration:.2f}s)...")

        # 插值移动
        for i in range(1, steps + 1):
            t = i / steps
            action = {}
            for name in joint_names:
                action[f"{name}.pos"] = start_joints[name] + (target_joints[name] - start_joints[name]) * t
            action["gripper.pos"] = gripper_start + (gripper_target - gripper_start) * t
            robot.send_action(action)
            time.sleep(1.0 / hz)

        # 等待稳定
        time.sleep(0.5)
        print("✓ 移动完成")

    finally:
        if not args.keep_connected:
            robot.disconnect()
        else:
            print("✓ 机械臂保持连接状态")


if __name__ == "__main__":
    main()