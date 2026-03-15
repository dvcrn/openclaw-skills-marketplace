#!/usr/bin/env python3

import argparse
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict
import sys
import numpy as np
import pinocchio as pin


@dataclass
class IKResult:
    success: bool
    iterations: int
    error_norm: float
    q: np.ndarray
    joints_rad: Dict[str, float]


class SOArmPinocchioController:
    ACTUATED_JOINTS = [
        "shoulder_pan",
        "shoulder_lift",
        "elbow_flex",
        "wrist_flex",
        "wrist_roll",
    ]

    def __init__(self, urdf_path: str, ee_frame: str):
        self.model = pin.buildModelFromUrdf(urdf_path)
        self.data = self.model.createData()
        if not self.model.existFrame(ee_frame):
            raise ValueError(f"End-effector frame '{ee_frame}' not found in URDF.")
        self.ee_frame = ee_frame
        self.ee_frame_id = self.model.getFrameId(ee_frame)
        self.joint_idx_q = self._build_joint_q_index()

    def _build_joint_q_index(self) -> Dict[str, int]:
        out = {}
        for name in self.ACTUATED_JOINTS:
            jid = self.model.getJointId(name)
            if jid == 0:
                raise ValueError(f"Joint '{name}' not found in URDF model.")
            out[name] = self.model.joints[jid].idx_q
        return out

    def seed_q(self) -> np.ndarray:
        return pin.neutral(self.model).copy()

    def set_seed_from_real(self, q: np.ndarray, real_joint_deg: Dict[str, float]) -> np.ndarray:
        for jn, deg in real_joint_deg.items():
            if jn in self.joint_idx_q:
                q[self.joint_idx_q[jn]] = math.radians(float(deg))
        return q

    def solve_position_ik(
        self,
        target_xyz: np.ndarray,
        q_init: np.ndarray,
        max_iter: int,
        tol: float,
        damping: float,
        step_size: float,
        gain: float,
    ) -> IKResult:
        q = q_init.copy()
        lo = self.model.lowerPositionLimit
        hi = self.model.upperPositionLimit

        err_norm = 1e9
        for it in range(1, max_iter + 1):
            pin.forwardKinematics(self.model, self.data, q)
            pin.updateFramePlacements(self.model, self.data)
            cur = self.data.oMf[self.ee_frame_id].translation
            err = target_xyz - cur
            err_norm = float(np.linalg.norm(err))
            if err_norm < tol:
                joints = {jn: float(q[idx]) for jn, idx in self.joint_idx_q.items()}
                return IKResult(True, it, err_norm, q, joints)

            j6 = pin.computeFrameJacobian(
                self.model, self.data, q, self.ee_frame_id, pin.ReferenceFrame.LOCAL_WORLD_ALIGNED
            )
            j = j6[:3, :]
            jj_t = j @ j.T
            v = j.T @ np.linalg.solve(jj_t + damping * np.eye(3), gain * err)
            q = pin.integrate(self.model, q, v * step_size)
            q = np.minimum(np.maximum(q, lo), hi)

        joints = {jn: float(q[idx]) for jn, idx in self.joint_idx_q.items()}
        return IKResult(False, max_iter, err_norm, q, joints)


def build_real_robot(port: str, robot_id: str):
    from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig

    cfg = SO101FollowerConfig(
        port=port,
        id=robot_id,
        cameras={},
        use_degrees=True,
        max_relative_target=None,
        disable_torque_on_disconnect=False,
    )
    return SO101Follower(cfg)


def drive_real_arm(
    joints_rad: Dict[str, float],
    port: str,
    robot_id: str,
    calibrate_on_connect: bool,
    max_joint_speed_deg: float,
    command_hz: float,
    wait_done: bool,
    wait_timeout: float,
    goal_threshold_deg: float,
    open_gripper: bool,
    gripper_open_value: float,
    keep_connected: bool = False,
) -> None:
    robot = build_real_robot(port, robot_id)
    robot.connect(calibrate=calibrate_on_connect)
    try:
        obs = robot.get_observation()
        gripper = float(obs.get("gripper.pos", 50.0))
        gripper_target = float(max(0.0, min(100.0, gripper_open_value))) if open_gripper else gripper
        action_target = {
            "shoulder_pan.pos": math.degrees(joints_rad["shoulder_pan"]),
            "shoulder_lift.pos": math.degrees(joints_rad["shoulder_lift"]),
            "elbow_flex.pos": math.degrees(joints_rad["elbow_flex"]),
            "wrist_flex.pos": math.degrees(joints_rad["wrist_flex"]),
            "wrist_roll.pos": math.degrees(joints_rad["wrist_roll"]),
            "gripper.pos": gripper_target,
        }
        action_start = {
            "shoulder_pan.pos": float(obs["shoulder_pan.pos"]),
            "shoulder_lift.pos": float(obs["shoulder_lift.pos"]),
            "elbow_flex.pos": float(obs["elbow_flex.pos"]),
            "wrist_flex.pos": float(obs["wrist_flex.pos"]),
            "wrist_roll.pos": float(obs["wrist_roll.pos"]),
            "gripper.pos": gripper,
        }

        max_delta = max(
            abs(action_target[k] - action_start[k])
            for k in ["shoulder_pan.pos", "shoulder_lift.pos", "elbow_flex.pos", "wrist_flex.pos", "wrist_roll.pos"]
        )
        max_joint_speed_deg = max(1.0, float(max_joint_speed_deg))
        command_hz = max(5.0, float(command_hz))
        duration = max_delta / max_joint_speed_deg
        steps = max(1, int(duration * command_hz))

        for i in range(1, steps + 1):
            t = i / steps
            action = {k: action_start[k] + (action_target[k] - action_start[k]) * t for k in action_target}
            robot.send_action(action)
            time.sleep(1.0 / command_hz)
        print(
            f"Real arm command sent with speed limit {max_joint_speed_deg:.1f} deg/s, "
            f"duration {duration:.2f}s, steps {steps}."
        )
        if open_gripper:
            print(f"Gripper target set to {gripper_target:.1f}/100 (open mode).")

        if wait_done:
            start = time.monotonic()
            while True:
                cur = robot.get_observation()
                cur_deg = {
                    "shoulder_pan.pos": float(cur["shoulder_pan.pos"]),
                    "shoulder_lift.pos": float(cur["shoulder_lift.pos"]),
                    "elbow_flex.pos": float(cur["elbow_flex.pos"]),
                    "wrist_flex.pos": float(cur["wrist_flex.pos"]),
                    "wrist_roll.pos": float(cur["wrist_roll.pos"]),
                }
                max_err = max(abs(cur_deg[k] - action_target[k]) for k in cur_deg)
                if max_err <= goal_threshold_deg:
                    print(f"Reached target. max_err={max_err:.3f} deg")
                    break
                if time.monotonic() - start >= wait_timeout:
                    print(f"Wait timeout after {wait_timeout:.1f}s. max_err={max_err:.3f} deg")
                    break
                time.sleep(0.05)
    finally:
        if not keep_connected and robot.is_connected:
            robot.disconnect()
        elif keep_connected and robot.is_connected:
            print("✓ 机械臂保持连接状态")


def parse_args():
    p = argparse.ArgumentParser(
        description="Pinocchio position IK for SO-ARM101: xyz -> joint angles -> optional real-arm drive."
    )
    p.add_argument("--x", type=float, required=True, help="Target x in base frame (m)")
    p.add_argument("--y", type=float, required=True, help="Target y in base frame (m)")
    p.add_argument("--z", type=float, required=True, help="Target z in base frame (m)")
    # 默认 URDF 路径：基于脚本位置查找
    default_urdf = Path(__file__).parent.parent / "references" / "so101_new_calib.urdf"
    if not default_urdf.exists():
        # 回退到常见路径
        default_urdf = Path.home() / "Documents/SO-ARM100/Simulation/SO101/so101_new_calib.urdf"

    p.add_argument(
        "--urdf",
        type=str,
        default=str(default_urdf),
    )
    p.add_argument("--ee-frame", type=str, default="gripper_frame_link")
    p.add_argument("--max-iter", type=int, default=300)
    p.add_argument("--tol", type=float, default=0.008, help="Position error tolerance (m)")
    p.add_argument("--damping", type=float, default=1e-3)
    p.add_argument("--step-size", type=float, default=0.2)
    p.add_argument("--gain", type=float, default=1.0)
    p.add_argument("--seed-from-real", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--drive-real", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--port", type=str, default="/dev/ttyACM0")
    p.add_argument("--robot-id", type=str, default="openclaw_soarm")
    p.add_argument("--calibrate-on-connect", action=argparse.BooleanOptionalAction, default=False)
    p.add_argument(
        "--max-joint-speed-deg",
        type=float,
        default=30.0,
        help="Approximate max joint speed in deg/s for commanded interpolation.",
    )
    p.add_argument(
        "--command-hz",
        type=float,
        default=30.0,
        help="Command streaming frequency while interpolating to target.",
    )
    p.add_argument("--wait-done", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--wait-timeout", type=float, default=8.0)
    p.add_argument("--goal-threshold-deg", type=float, default=2.0)
    p.add_argument(
        "--open-gripper",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Open gripper while moving to target.",
    )
    p.add_argument(
        "--gripper-open-value",
        type=float,
        default=100.0,
        help="Gripper target when --open-gripper is enabled (0..100).",
    )
    p.add_argument(
        "--keep-connected",
        action="store_true",
        help="Keep the robot connected after movement, don't release the arm.",
    )
    return p.parse_args()


def main():
    args = parse_args()
    target = np.array([args.x, args.y, args.z], dtype=float)

    solver = SOArmPinocchioController(args.urdf, args.ee_frame)
    q0 = solver.seed_q()

    if args.seed_from_real or args.drive_real:
        robot = build_real_robot(args.port, args.robot_id)
        robot.connect(calibrate=args.calibrate_on_connect)
        try:
            obs = robot.get_observation()
            seed_deg = {
                "shoulder_pan": float(obs["shoulder_pan.pos"]),
                "shoulder_lift": float(obs["shoulder_lift.pos"]),
                "elbow_flex": float(obs["elbow_flex.pos"]),
                "wrist_flex": float(obs["wrist_flex.pos"]),
                "wrist_roll": float(obs["wrist_roll.pos"]),
            }
            q0 = solver.set_seed_from_real(q0, seed_deg)
        finally:
            if robot.is_connected:
                robot.disconnect()

    result = solver.solve_position_ik(
        target_xyz=target,
        q_init=q0,
        max_iter=args.max_iter,
        tol=args.tol,
        damping=args.damping,
        step_size=args.step_size,
        gain=args.gain,
    )

    if not result.success:
        print(f"IK failed. iter={result.iterations}, final_err={result.error_norm:.6f} m")
        sys.exit(4)

    print(f"IK success. iter={result.iterations}, final_err={result.error_norm:.6f} m")
    print("Joint angles:")
    for j in SOArmPinocchioController.ACTUATED_JOINTS:
        rad = result.joints_rad[j]
        deg = math.degrees(rad)
        print(f"  {j}: {rad:.6f} rad ({deg:.3f} deg)")

    if args.drive_real:
        drive_real_arm(
            joints_rad=result.joints_rad,
            port=args.port,
            robot_id=args.robot_id,
            calibrate_on_connect=args.calibrate_on_connect,
            max_joint_speed_deg=args.max_joint_speed_deg,
            command_hz=args.command_hz,
            wait_done=args.wait_done,
            wait_timeout=args.wait_timeout,
            goal_threshold_deg=args.goal_threshold_deg,
            open_gripper=args.open_gripper,
            gripper_open_value=args.gripper_open_value,
            keep_connected=args.keep_connected,
        )


if __name__ == "__main__":
    main()
