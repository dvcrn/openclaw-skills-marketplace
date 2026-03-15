#!/usr/bin/env python3
"""
SOARM 机械臂使能脚本
连接机械臂，确保伺服电机有扭矩
"""

import argparse
import sys
import time


def enable_robot(port: str, robot_id: str, keep_connected: bool = True) -> None:
    """连接机械臂并保持扭矩"""
    try:
        from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig

        print(f"正在连接机械臂 (port={port}, id={robot_id})...")
        
        # 注意：不设置 disable_torque_on_disconnect，或者设为 False
        cfg = SO101FollowerConfig(
            port=port,
            id=robot_id,
            cameras={},
            use_degrees=True,
            max_relative_target=None,
            disable_torque_on_disconnect=False,  # 断开时不禁用扭矩
        )
        robot = SO101Follower(cfg)
        robot.connect(calibrate=False)

        print("机械臂已连接，扭矩已启用")
        
        # 读取当前状态
        obs = robot.get_observation()
        print("\n当前关节位置:")
        for name in ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll"]:
            print(f"  {name}: {obs[f'{name}.pos']:.2f}°")
        
        gripper = obs.get("gripper.pos", 0)
        print(f"夹爪: {gripper:.1f}%")
        
        if keep_connected:
            print("\n✓ 机械臂已使能，保持连接状态")
            # 保持连接，不断开
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n正在断开连接...")
                robot.disconnect()
                print("✓ 已断开连接")
        else:
            print("\n正在断开连接...")
            robot.disconnect()
            print("✓ 已断开连接")

    except Exception as e:
        print(f"✗ 使能失败: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="使能 SOARM 机械臂（连接并启用扭矩）"
    )
    parser.add_argument("--port", type=str, default="/dev/ttyACM0",
                       help="串口设备（默认：/dev/ttyACM0）")
    parser.add_argument("--robot-id", type=str, default="openclaw_soarm",
                       help="机器人ID（默认：openclaw_soarm）")
    parser.add_argument("--disconnect", action="store_true",
                       help="连接后立即断开（测试用）")
    args = parser.parse_args()

    enable_robot(args.port, args.robot_id, keep_connected=not args.disconnect)


if __name__ == "__main__":
    main()