#!/usr/bin/env python3
"""安装 @omni-shield/openclaw-cli 并调用 omni-shield-openclaw。

步骤：

1. 执行全局安装命令：

   npm install -g @omni-shield/openclaw-cli

2. 检查 `omni-shield-openclaw` 命令是否可用：

   - 如果不可用，则提示用户检查 npm 全局安装路径 / PATH 配置。

3. 仅执行带固定 apiKey/appId 的 `omni-shield-openclaw` 命令，不做输出解析或浏览器跳转。
"""

import shutil
import subprocess
import sys
from typing import List


NPM_INSTALL_CMD: List[str] = [
    "npm",
    "install",
    "-g",
    "@omni-shield/openclaw-cli",
]


def run_install(cmd: List[str]) -> int:
    """运行 npm 全局安装命令。

    返回值为底层命令的退出码，0 表示成功，其它值表示失败。
    """

    print("[install-openclaw-splugins] 开始安装 @omni-shield/openclaw-cli …")

    try:
        # 不使用 check=True，这样可以将退出码直接向上传递给调用方
        result = subprocess.run(cmd)
    except FileNotFoundError:
        print(
            "[install-openclaw-splugins] 错误：未找到 npm 命令，请先安装 Node.js 和 npm。",
            file=sys.stderr,
        )
        return 1

    if result.returncode == 0:
        print("[install-openclaw-splugins] 安装命令执行完成（退出码 0）。")
    else:
        print(
            f"[install-openclaw-splugins] 安装命令执行失败，退出码：{result.returncode}。",
            file=sys.stderr,
        )

    return result.returncode


def is_command_available(cmd: str) -> bool:
    """检查给定命令是否在 PATH 中可用。"""

    return shutil.which(cmd) is not None


def run_omni_shield_openclaw() -> tuple[int, str]:
    """调用 `omni-shield-openclaw` 命令并返回 (退出码, 合并输出)。

    按需求仅执行以下命令，不做额外处理：

        omni-shield-openclaw \
          --apiKey A662C838-DE32-44E6-834B-B0850F8C7431 \
          --appId app-d6nbc5c5dvtjq4oq6ic0
    """

    cmd = [
        "omni-shield-openclaw",
        "--apiKey",
        "A662C838-DE32-44E6-834B-B0850F8C7431",
        "--appId",
        "app-d6nbc5c5dvtjq4oq6ic0",
    ]
    print("[install-openclaw-splugins] 正在调用 omni-shield-openclaw 进行安装…")

    try:
        result = subprocess.run(
            cmd,
            text=True,
            capture_output=True,
        )
    except FileNotFoundError:
        # 正常情况下不会到这里（事先已经做了 which 检查），防御性处理
        print(
            "[install-openclaw-splugins] 错误：未找到 omni-shield-openclaw 命令。",
            file=sys.stderr,
        )
        return 1, ""

    full_output = (result.stdout or "") + "\n" + (result.stderr or "")

    # 无论成功或失败，都将输出原样返回给调用方；如需查看，可在上层打印
    if result.returncode != 0:
        print(
            f"[install-openclaw-splugins] omni-shield-openclaw 执行失败，退出码：{result.returncode}。",
            file=sys.stderr,
        )

    return result.returncode, full_output


def main() -> int:
    """脚本入口。

    1. 执行 npm 全局安装。
    2. 检查并调用 omni-shield-openclaw。
    3. 调用 omni-shield-openclaw进行安装
    """

    # 第一步：安装 CLI
    install_code = run_install(NPM_INSTALL_CMD)
    if install_code != 0:
        # 保持与 npm 安装命令相同的退出码
        return install_code

    # 第二步：检查 omni-shield-openclaw 是否在 PATH 中
    if not is_command_available("omni-shield-openclaw"):
        print(
            "[install-openclaw-splugins] 警告：未在 PATH 中找到 omni-shield-openclaw 命令。",
            file=sys.stderr,
        )
        print(
            "[install-openclaw-splugins] 请检查 npm 全局安装目录是否已加入 PATH，"
            "并确认 omni-shield-openclaw 命令可在终端直接执行。",
            file=sys.stderr,
        )
        return 1

    # 第三步：调用 omni-shield-openclaw进行安装
    omni_code, output = run_omni_shield_openclaw()
    # 如需调试完整输出，可在此打印 output
    if output.strip():
        print("[install-openclaw-splugins] omni-shield-openclaw 输出:\n" + output.strip())

    return omni_code


if __name__ == "__main__":  # pragma: no cover - 简单脚本入口
    sys.exit(main())
