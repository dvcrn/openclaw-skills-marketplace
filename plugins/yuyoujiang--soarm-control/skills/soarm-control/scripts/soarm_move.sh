#!/bin/bash
# SOARM 机械臂移动命令封装
# 使用方法: ./soarm_move.sh <x> <y> <z> [speed]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 默认值
X=${1:-0.18}
Y=${2:-0.00}
Z=${3:-0.14}
SPEED=${4:-30}

echo "移动机械臂到坐标: X=$X, Y=$Y, Z=$Z (速度: $SPEED deg/s)"

conda run -n lerobot python "$SCRIPT_DIR/pinocchio_xyz_drive.py" \
    --x "$X" --y "$Y" --z "$Z" \
    --port /dev/ttyACM0 \
    --robot-id openclaw_soarm \
    --max-joint-speed-deg "$SPEED"
