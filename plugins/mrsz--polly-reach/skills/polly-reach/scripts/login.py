"""获取设备唯一 ID 并通过设备登录获取 Token"""

import platform
import subprocess
import requests
import os, re
import sys

sys.stdout.reconfigure(line_buffering=True)

def get_device_id() -> str:
    """
    获取当前设备的唯一标识符。

    - macOS: 使用 IOPlatformUUID (硬件级唯一 ID)
    - Linux: 使用 /etc/machine-id
    - Windows: 使用注册表 MachineGuid

    Returns:
        str: 设备唯一 ID
    """
    system = platform.system()

    if system == "Darwin":
        output = subprocess.check_output(
            ["/usr/sbin/ioreg", "-rd1", "-c", "IOPlatformExpertDevice"],
            text=True,
        )
        for line in output.splitlines():
            if "IOPlatformUUID" in line:
                return line.split('"')[-2]

    elif system == "Linux":
        with open("/etc/machine-id", "r") as f:
            return f.read().strip()

    elif system == "Windows":
        output = subprocess.check_output(
            ["reg", "query", r"HKLM\SOFTWARE\Microsoft\Cryptography", "/v", "MachineGuid"],
            text=True,
        )
        for line in output.splitlines():
            if "MachineGuid" in line:
                return line.split()[-1]

    raise RuntimeError(f"不支持的操作系统: {system}")


def get_user_name():
    """
    获取用户名，按优先级查找 USER.md：
    1. $OPENCLAW_WORKSPACE/USER.md  (环境变量，如果有)
    2. ~/.openclaw/workspace/USER.md (默认工作区)
    3. 技能目录的 workspace/USER.md   (旧兼容)
    4. 返回 "openclaw"               (fallback)
    """
    # 优先级 1: 环境变量 OPENCLAW_WORKSPACE
    env_workspace = os.environ.get("OPENCLAW_WORKSPACE")
    if env_workspace:
        path = os.path.join(env_workspace, "USER.md")
        try:
            with open(path) as f:
                for line in f:
                    m = re.search(r"\*\*Name:\*\*\s*(.+)", line)
                    if m:
                        name = m.group(1).strip()
                        return name if name else "openclaw"
        except:
            pass
    
    # 优先级 2: 默认 ~/.openclaw/workspace/USER.md
    home = os.path.expanduser("~")
    default_workspace = os.path.join(home, ".openclaw", "workspace", "USER.md")
    try:
        with open(default_workspace) as f:
            for line in f:
                m = re.search(r"\*\*Name:\*\*\s*(.+)", line)
                if m:
                    name = m.group(1).strip()
                    return name if name else "openclaw"
    except:
        pass
    
    # 优先级 3: 技能目录的 workspace/USER.md (旧兼容)
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    workspace = os.path.dirname(os.path.dirname(skill_dir))
    path = os.path.join(workspace, "USER.md")
    try:
        with open(path) as f:
            for line in f:
                m = re.search(r"\*\*Name:\*\*\s*(.+)", line)
                if m:
                    name = m.group(1).strip()
                    return name if name else "openclaw"
    except:
        pass
    
    # 优先级 4: fallback
    return "openclaw"


def signin_device(base_url: str = "https://www.visuai.me") -> str:
    """
    用设备 ID 调用登录接口获取 Token。

    Returns:
        str: 认证 token
    """
    device_id = get_device_id()
    url = f"{base_url}/api/v1/auths/signin/device"
    response = requests.post(url, json={"device_id": device_id, "claw_name": get_user_name()})
    response.raise_for_status()
    return response.json()

def login_auth(base_url: str = "https://www.visuai.me") -> str:
    """
    用设备 ID 调用登录接口获取 Token,确认是否已经绑定。

    Returns:
        str: 登录状态和信息
    """
    device_id = get_device_id()
    url = f"{base_url}/api/v1/auths/signin/device"
    response = requests.post(url, json={"device_id": device_id, "claw_name": get_user_name()})
    response.raise_for_status()
    if response.json().get("role") == "pending":
        message = {"status":"failed", "message":"login failed, please bind your device with the following url: "+ response.json().get("activation_url", "")}
        return message
    elif response.json().get("role") == "user":
        message = {"status":"success", "message":"login successfully!"}
        return message

if __name__ == "__main__":
    login_auth = login_auth()
    print(login_auth, flush=True)