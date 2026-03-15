#!/usr/bin/env python3
"""
读取机械臂当前末端位置（XYZ 坐标）
用于将当前位置定义为新的预设位置
"""

import argparse
import sys
import numpy as np
import pinocchio as pin


def get_current_xyz(port: str, robot_id: str, urdf_path: str, ee_frame: str) -> np.ndarray:
    """获取机械臂当前末端位置"""
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
            print("已连接，读取关节角度...")
            obs = robot.get_observation()

            # 读取关节角度
            joint_deg = {
                "shoulder_pan": float(obs["shoulder_pan.pos"]),
                "shoulder_lift": float(obs["shoulder_lift.pos"]),
                "elbow_flex": float(obs["elbow_flex.pos"]),
                "wrist_flex": float(obs["wrist_flex.pos"]),
                "wrist_roll": float(obs["wrist_roll.pos"]),
            }

            print("\n当前关节角度：")
            for jn, deg in joint_deg.items():
                print(f"  {jn}: {deg:.3f}°")

            # 使用 Pinocchio 计算末端位置
            print(f"\n加载 URDF: {urdf_path}")
            model = pin.buildModelFromUrdf(urdf_path)
            data = model.createData()

            # 设置关节角度
            q = pin.neutral(model).copy()
            for jn, deg in joint_deg.items():
                jid = model.getJointId(jn)
                if jid > 0:
                    idx = model.joints[jid].idx_q
                    q[idx] = np.radians(deg)

            # 正运动学
            pin.forwardKinematics(model, data, q)
            pin.updateFramePlacements(model, data)

            # 获取末端位置
            ee_id = model.getFrameId(ee_frame)
            xyz = data.oMf[ee_id].translation

            return xyz

        finally:
            robot.disconnect()

    except Exception as e:
        print(f"✗ 读取位置失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="读取机械臂当前末端位置（XYZ 坐标）"
    )
    parser.add_argument("--port", type=str, default="/dev/ttyACM0",
                       help="串口设备（默认：/dev/ttyACM0）")
    parser.add_argument("--robot-id", type=str, default="openclaw_soarm",
                       help="机器人ID（默认：openclaw_soarm）")
    parser.add_argument("--urdf", type=str,
                       default="/home/seeed/Documents/openclaw_soarm/SO-ARM100/Simulation/SO101/so101_new_calib.urdf",
                       help="URDF 文件路径")
    parser.add_argument("--ee-frame", type=str, default="gripper_frame_link",
                       help="末端执行器坐标系")
    args = parser.parse_args()

    xyz = get_current_xyz(args.port, args.robot_id, args.urdf, args.ee_frame)

    print("\n" + "="*50)
    print("机械臂当前末端位置")
    print("="*50)
    print(f"X (前后): {xyz[0]:.6f} m  {'前为正' if xyz[0] > 0 else '后为正'}")
    print(f"Y (左右): {xyz[1]:.6f} m  {'左为正' if xyz[1] > 0 else '右为正'}")
    print(f"Z (上下): {xyz[2]:.6f} m  {'上为正' if xyz[2] > 0 else '下为正'}")
    print("="*50)
    print(f"\n命令格式:")
    print(f"  python scripts/soarm_easy_control.py --x {xyz[0]:.6f} --y {xyz[1]:.6f} --z {xyz[2]:.6f}")
    print("="*50)


if __name__ == "__main__":
    main()
